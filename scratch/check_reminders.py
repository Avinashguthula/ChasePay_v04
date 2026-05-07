from backend.db.supabase import supabase_admin
import json

try:
    res = supabase_admin.table("reminders").select("*").execute()
    print(json.dumps(res.data, indent=2))
except Exception as e:
    print(f"Error: {e}")
