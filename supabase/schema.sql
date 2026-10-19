create extension if not exists pgcrypto;
create table if not exists public.projects (id uuid primary key default gen_random_uuid(), title text not null check (char_length(title) between 1 and 100), slug text not null unique check (slug ~ '^[a-z0-9-]+$'), category text not null check (category in ('Data Analytics','Data Science','Dashboards & BI','Web Development','Full-Stack & APIs','Automation & Software Tools','Game Development')), summary text not null check (char_length(summary) between 1 and 350), description text not null default '', cover_url text, live_url text, source_url text, status text not null default 'draft' check (status in ('draft','published')), featured boolean not null default false, created_at timestamptz not null default now(), updated_at timestamptz not null default now());
alter table public.projects enable row level security;
drop policy if exists "Published projects are public" on public.projects;
create policy "Published projects are public" on public.projects for select to anon, authenticated using (status='published');
-- Replace YOUR_AUTH_USER_UUID with the owner user's UUID from Supabase Authentication > Users before enabling admin edits.
drop policy if exists "Owner manages projects" on public.projects;
create policy "Owner manages projects" on public.projects for all to authenticated using (auth.uid() = '00000000-0000-0000-0000-000000000000'::uuid) with check (auth.uid() = '00000000-0000-0000-0000-000000000000'::uuid);
insert into storage.buckets (id,name,public,file_size_limit,allowed_mime_types) values ('project-screenshots','project-screenshots',true,5242880,array['image/png','image/jpeg','image/webp']) on conflict (id) do nothing;
drop policy if exists "Public read project screenshots" on storage.objects;
create policy "Public read project screenshots" on storage.objects for select to anon, authenticated using (bucket_id='project-screenshots');
-- Upload screenshots through Supabase Storage dashboard. Public uploads are deliberately not enabled.
