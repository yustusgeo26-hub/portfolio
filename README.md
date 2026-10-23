# Yustus Geofrey — Streamlit Portfolio

A Python-first dark portfolio with Streamlit, Supabase Auth, PostgreSQL and Storage.

## Local setup (Windows)
1. Install Python 3.11 or newer.
2. In the repository folder, run:
   ```bat
   py -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Copy .streamlit/secrets.toml.example to .streamlit/secrets.toml and enter your Supabase URL, anon/publishable key, and admin email. When YusPlant is released, add `YUSPLANT_DOWNLOAD_URL = "https://github.com/yustusgeo26-hub/YuPlant/releases/download/TAG/FILE.zip"` using the real GitHub Release asset URL.
4. Create the owner account manually in Supabase Authentication > Users. Disable public signups if you do not need them.
5. Copy the owner's UUID from Supabase Auth. Replace both all-zero UUID placeholders in supabase/schema.sql with that UUID.
6. Run supabase/schema.sql in Supabase SQL Editor.
7. Start with `streamlit run app.py` and open the local URL, usually http://localhost:8501. Use the sidebar to switch to Admin.

## Free deployment
Push this repository to GitHub, create a Streamlit Community Cloud app at https://share.streamlit.io/, select app.py, then add the Supabase settings under App settings > Secrets. Once YusPlant is published, add `YUSPLANT_DOWNLOAD_URL` there with the exact public release asset URL; the portfolio download button will activate automatically. Supabase hosts the database, auth and screenshots. Check current free-plan quotas and policies before deploying.

## Security
- Never commit .streamlit/secrets.toml or expose the Supabase service-role key.
- Use only the anon/publishable key in this app.
- Replace the placeholder UUID in the SQL policies before production. PostgreSQL row-level security protects project changes and screenshot uploads; the app's email check is an additional gate.
- The screenshot bucket is public for image display, but uploads/updates/deletes are restricted to the configured owner UUID.
- Drafts are not visible publicly; only published records are shown.
