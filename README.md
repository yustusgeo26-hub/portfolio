# Yustus Geofrey — Personal Portfolio

Dark futuristic portfolio built with Next.js, Tailwind CSS and Supabase Auth/PostgreSQL. Includes public published-project cards and a private admin area for project management.

## Setup
1. Install Node.js 20+ and run `npm install`.
2. Copy `.env.example` to `.env.local`, then set your Supabase project URL, anon/publishable key and owner email.
3. Run `supabase/schema.sql` in Supabase Dashboard > SQL Editor.
4. Create the owner user manually in Supabase Authentication > Users using the same email as `ADMIN_EMAIL`.
5. Copy that user's UUID into the owner RLS policy in `supabase/schema.sql`, replacing the all-zero UUID, and rerun the policy section. Do not deploy admin editing until this is done.
6. Run `npm run dev`; visit `http://localhost:3000` and `/admin/login`.

## Admin
Sign in at `/admin/login`. Create, edit, delete, save drafts and publish projects. Supported categories: Data Analytics, Data Science, Dashboards & BI, Web Development, Full-Stack & APIs, Automation & Software Tools, Game Development. Published projects appear on the public homepage. Slugs must be unique.

## Screenshots
Upload images to the `project-screenshots` bucket from Supabase Storage, copy the public URL and paste it into the screenshot field. Bucket uploads are not public; only viewing screenshots is public. Upload policies are intentionally not opened to anonymous users.

## Deploy on Vercel
Import the GitHub repository, set `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, and `ADMIN_EMAIL` in Vercel environment variables, then deploy. Never commit `.env.local` or expose a Supabase service-role key. Verify owner RLS policy before enabling production admin editing.
