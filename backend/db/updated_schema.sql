-- ChasePay Project: Updated SQL Schema

-- 1. Users Table (Syncs with auth.users)
CREATE TABLE public.users (
  id TEXT PRIMARY KEY, -- Matches auth.users.id
  email TEXT UNIQUE NOT NULL,
  first_name TEXT,
  last_name TEXT,
  plan TEXT DEFAULT 'free' CHECK (plan IN ('free', 'pro', 'agency')),
  gmail_connected BOOLEAN DEFAULT FALSE,
  gmail_access_token TEXT,
  gmail_refresh_token TEXT
);

-- 2. Clients Table
CREATE TABLE public.clients (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT REFERENCES public.users(id) ON DELETE CASCADE,
  company_name TEXT NOT NULL,
  contact_name TEXT,
  email TEXT NOT NULL,
  phone TEXT,
  address TEXT,
  relationship TEXT DEFAULT 'Regular Client',
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Invoices Table
CREATE TABLE public.invoices (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT REFERENCES public.users(id) ON DELETE CASCADE,
  invoice_number TEXT,
  invoice_date DATE DEFAULT CURRENT_DATE,
  client_name TEXT NOT NULL,
  client_email TEXT NOT NULL,
  amount NUMERIC NOT NULL,
  currency TEXT DEFAULT 'USD',
  due_date DATE NOT NULL,
  description TEXT,
  status TEXT DEFAULT 'unpaid' CHECK (status IN ('unpaid', 'paid')),
  last_reminder TEXT, -- Tracks the last reminder sent (day1, day3, day7)
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Reminders Table (Logs sent emails)
CREATE TABLE public.reminders (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  invoice_id UUID REFERENCES public.invoices(id) ON DELETE CASCADE,
  type TEXT CHECK (type IN ('day1', 'day3', 'day7')),
  sent_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security (RLS)
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.clients ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reminders ENABLE ROW LEVEL SECURITY;

-- 5. Security Policies

-- User Policies
CREATE POLICY "Users can see their own profile" ON public.users 
FOR SELECT USING (auth.uid()::text = id);

CREATE POLICY "Users can update their own profile" ON public.users 
FOR UPDATE USING (auth.uid()::text = id);

-- Client Policies
CREATE POLICY "Users can manage their own clients" ON public.clients 
FOR ALL USING (auth.uid()::text = user_id);

-- Invoice Policies
CREATE POLICY "Users can manage their own invoices" ON public.invoices 
FOR ALL USING (auth.uid()::text = user_id);

-- Reminder Policies
CREATE POLICY "Users can manage their own reminders" ON public.reminders 
FOR ALL USING (EXISTS (
    SELECT 1 FROM public.invoices 
    WHERE public.invoices.id = invoice_id 
    AND public.invoices.user_id = auth.uid()::text
));

-- 6. Auth Trigger (Auto-create public.users on signup)
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.users (id, email)
  VALUES (new.id::text, new.email);
  RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();
