import asyncio
from backend.db.supabase import supabase_admin
from datetime import datetime

async def backfill_invoice_numbers():
    # Fetch all invoices without a number
    invoices_res = supabase_admin.table("invoices").select("*").is_("invoice_number", "null").order("created_at", asc=True).execute()
    invoices = invoices_res.data
    
    if not invoices:
        print("No invoices to backfill.")
        return

    print(f"Backfilling {len(invoices)} invoices...")
    
    user_year_counts = {} # {(user_id, year): current_max}

    for inv in invoices:
        user_id = inv["user_id"]
        created_at = datetime.fromisoformat(inv["created_at"].replace('Z', '+00:00'))
        year = created_at.year
        year_prefix = f"INV-{year}-"
        
        key = (user_id, year)
        if key not in user_year_counts:
            # Get current max for this user/year
            res = supabase_admin.table("invoices") \
                .select("invoice_number") \
                .eq("user_id", user_id) \
                .like("invoice_number", f"{year_prefix}%") \
                .order("invoice_number", desc=True) \
                .limit(1) \
                .execute()
            
            if res.data and res.data[0]["invoice_number"]:
                try:
                    last_num = int(res.data[0]["invoice_number"].split("-")[-1])
                    user_year_counts[key] = last_num
                except:
                    user_year_counts[key] = 0
            else:
                user_year_counts[key] = 0
        
        user_year_counts[key] += 1
        new_number = f"{year_prefix}{user_year_counts[key]:03d}"
        
        supabase_admin.table("invoices").update({"invoice_number": new_number}).eq("id", inv["id"]).execute()
        print(f"Updated invoice {inv['id']} to {new_number}")

if __name__ == "__main__":
    asyncio.run(backfill_invoice_numbers())
