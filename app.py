import re
from datetime import datetime
from urllib.parse import urlparse
import streamlit as st
from supabase import create_client

CATEGORIES = ["Data Analytics", "Data Science", "Dashboards & BI", "Web Development", "Full-Stack & APIs", "Automation & Software Tools", "Game Development"]
st.set_page_config(page_title="Yustus Geofrey | Portfolio", page_icon="✳", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=DM+Mono:wght@400;500&display=swap');
html,body,[class*="css"]{font-family:Manrope,sans-serif}.stApp{background:#0b0d12;color:#e9edf4}
.block-container{max-width:1120px;padding-top:1.5rem}.eyebrow{font-family:'DM Mono',monospace;color:#c5ff5f;font-size:.72rem;letter-spacing:.17em;text-transform:uppercase}
.hero{padding:4rem 0 3rem;border-bottom:1px solid #292f3a;background-image:linear-gradient(rgba(255,255,255,.025) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.025) 1px,transparent 1px);background-size:42px 42px}
.hero h1{font-size:clamp(2.8rem,7vw,5.7rem);line-height:.99;letter-spacing:-.07em;font-weight:800}.lime{color:#c5ff5f}.subhead{font-size:1.1rem;color:#a4adbc;line-height:1.8;max-width:720px}
.pill{display:inline-block;border:1px solid #343a45;border-radius:99px;padding:.35rem .65rem;margin:.18rem;color:#c1c8d3;font-size:.73rem}
div.stButton>button,div.stFormSubmitButton>button{border-radius:8px;min-height:2.6rem;border:1px solid #343a45}
div.stButton>button[kind="primary"],div.stFormSubmitButton>button[kind="primary"]{background:#c5ff5f;color:#0b0d12;border-color:#c5ff5f;font-weight:800}
[data-testid="stMetric"]{background:#141821;border:1px solid #292f3a;padding:1rem;border-radius:10px}hr{border-color:#292f3a}
</style>""", unsafe_allow_html=True)

def secret(key):
    try: return str(st.secrets.get(key, "")).strip()
    except Exception: return ""

def db_client():
    url, key = secret("SUPABASE_URL"), secret("SUPABASE_ANON_KEY")
    if not url or not key: raise RuntimeError("Set Supabase secrets first.")
    return create_client(url, key)

def slugify(s):
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9-]+", "-", s.lower().strip())).strip("-")

def valid_url(s):
    if not s.strip(): return True
    u = urlparse(s.strip())
    return u.scheme == "https" and bool(u.netloc)

def list_published(db):
    return db.table("projects").select("*").eq("status", "published").order("featured", desc=True).order("created_at", desc=True).execute().data or []

def render_project(p):
    with st.container(border=True):
        if p.get("cover_url"): st.image(p["cover_url"], use_container_width=True)
        st.markdown(f'<div class="eyebrow">{p.get("category", "PROJECT")}</div>', unsafe_allow_html=True)
        st.markdown("### " + p.get("title", "Untitled"))
        st.write(p.get("summary", ""))
        if p.get("featured"): st.caption("✳ Featured project")
        links=[]
        if p.get("live_url"): links.append("[Live demo ↗](" + p["live_url"] + ")")
        if p.get("source_url"): links.append("[Source code ↗](" + p["source_url"] + ")")
        if links: st.markdown(" · ".join(links))

def owner_login():
    st.markdown('<div class="eyebrow">PRIVATE AREA</div>', unsafe_allow_html=True)
    st.markdown("## Admin sign in")
    with st.form("login"):
        email=st.text_input("Admin email")
        password=st.text_input("Password", type="password")
        go=st.form_submit_button("Sign in", type="primary", use_container_width=True)
    if go:
        expected=secret("ADMIN_EMAIL").lower()
        if not expected or email.strip().lower()!=expected:
            st.error("This email is not authorized."); return
        try:
            client=db_client()
            result=client.auth.sign_in_with_password({"email":email.strip(),"password":password})
            if not result.user or (result.user.email or "").lower()!=expected:
                st.error("Sign-in failed or account is not authorized."); return
            st.session_state["admin_client"]=client
            st.rerun()
        except Exception:
            st.error("Login failed. Check your Supabase Auth account and secrets.")

def admin_page():
    client=st.session_state.get("admin_client")
    if client is None:
        owner_login(); return
    try:
        user=client.auth.get_user().user
        if not user or (user.email or "").lower()!=secret("ADMIN_EMAIL").lower():
            st.session_state.pop("admin_client",None); st.warning("Please sign in again."); owner_login(); return
        projects=client.table("projects").select("*").order("created_at",desc=True).execute().data or []
    except Exception:
        st.session_state.pop("admin_client",None); st.warning("Your session expired, or the database is not configured."); owner_login(); return
    left,right=st.columns([4,1])
    with left:
        st.markdown('<div class="eyebrow">OWNER CONTROL ROOM</div>',unsafe_allow_html=True)
        st.markdown("## Project dashboard")
        st.caption("Signed in as " + user.email)
    with right:
        if st.button("Sign out",use_container_width=True):
            client.auth.sign_out(); st.session_state.pop("admin_client",None); st.rerun()
    a,b,c=st.columns(3)
    a.metric("Total projects",len(projects)); b.metric("Published",sum(p["status"]=="published" for p in projects)); c.metric("Drafts",sum(p["status"]=="draft" for p in projects))
    add,manage,notes=st.tabs(["Add project","Manage projects","Setup"])
    with add:
        with st.form("add_project",clear_on_submit=True):
            title=st.text_input("Title")
            slug=st.text_input("Slug (unique ID)",placeholder="my-data-dashboard")
            category=st.selectbox("Category",CATEGORIES)
            summary=st.text_area("Short summary",max_chars=350)
            description=st.text_area("Project details")
            cover=st.text_input("Screenshot URL (optional)")
            live=st.text_input("Live demo URL (optional)")
            source=st.text_input("Source code URL (optional)")
            image=st.file_uploader("Upload screenshot",type=["png","jpg","jpeg","webp"])
            status=st.radio("Status",["draft","published"],horizontal=True)
            featured=st.checkbox("Feature this project")
            save=st.form_submit_button("Save project",type="primary",use_container_width=True)
        if save:
            slug=slugify(slug or title)
            if not title.strip() or not slug or not summary.strip(): st.error("Title, slug and summary are required.")
            elif not all(valid_url(v) for v in [cover,live,source]): st.error("Links must use https://")
            else:
                if image:
                    try:
                        ext=image.name.rsplit(".",1)[-1].lower()
                        path=f"{slug}-{int(datetime.now().timestamp())}.{ext}"
                        client.storage.from_("project-screenshots").upload(path,image.getvalue(),{"content-type":image.type,"upsert":"true"})
                        cover=client.storage.from_("project-screenshots").get_public_url(path)
                    except Exception: st.error("Upload failed. Check the screenshot bucket and owner Storage policy."); st.stop()
                row={"title":title.strip(),"slug":slug,"category":category,"summary":summary.strip(),"description":description.strip(),"cover_url":cover.strip() or None,"live_url":live.strip() or None,"source_url":source.strip() or None,"status":status,"featured":featured}
                try: client.table("projects").insert(row).execute(); st.success("Project saved."); st.rerun()
                except Exception: st.error("Could not save. Check slug uniqueness and the owner UUID RLS policy.")
    with manage:
        if not projects: st.info("No projects yet.")
        else:
            choices={f'{p["title"]} · {p["status"]} · {p["slug"]}':p for p in projects}
            p=choices[st.selectbox("Choose project",list(choices))]
            with st.form("edit_project"):
                title=st.text_input("Title",value=p["title"])
                slug=st.text_input("Slug",value=p["slug"])
                category=st.selectbox("Category",CATEGORIES,index=CATEGORIES.index(p["category"]))
                summary=st.text_area("Summary",value=p["summary"],max_chars=350)
                description=st.text_area("Details",value=p.get("description") or "")
                cover=st.text_input("Screenshot URL",value=p.get("cover_url") or "")
                live=st.text_input("Live demo URL",value=p.get("live_url") or "")
                source=st.text_input("Source code URL",value=p.get("source_url") or "")
                image=st.file_uploader("Replace screenshot",type=["png","jpg","jpeg","webp"],key="replace_image")
                status=st.radio("Status",["draft","published"],index=1 if p["status"]=="published" else 0,horizontal=True)
                featured=st.checkbox("Featured",value=bool(p.get("featured")))
                update=st.form_submit_button("Update project",type="primary",use_container_width=True)
            if update:
                slug=slugify(slug)
                if not title.strip() or not slug or not summary.strip(): st.error("Title, slug and summary are required.")
                elif not all(valid_url(v) for v in [cover,live,source]): st.error("Links must use https://")
                else:
                    if image:
                        try:
                            ext=image.name.rsplit(".",1)[-1].lower(); path=f"{slug}-{int(datetime.now().timestamp())}.{ext}"
                            client.storage.from_("project-screenshots").upload(path,image.getvalue(),{"content-type":image.type,"upsert":"true"})
                            cover=client.storage.from_("project-screenshots").get_public_url(path)
                        except Exception: st.error("Screenshot upload failed. Check Storage policies."); st.stop()
                    row={"title":title.strip(),"slug":slug,"category":category,"summary":summary.strip(),"description":description.strip(),"cover_url":cover.strip() or None,"live_url":live.strip() or None,"source_url":source.strip() or None,"status":status,"featured":featured,"updated_at":datetime.now().astimezone().isoformat()}
                    try: client.table("projects").update(row).eq("id",p["id"]).execute(); st.success("Project updated."); st.rerun()
                    except Exception: st.error("Update failed. Check slug uniqueness and owner policy.")
            st.divider()
            confirm=st.checkbox("Confirm permanent deletion",key="confirm_delete")
            if st.button("Delete project",disabled=not confirm):
                try: client.table("projects").delete().eq("id",p["id"]).execute(); st.success("Deleted."); st.rerun()
                except Exception: st.error("Delete failed. Check owner RLS policy.")
    with notes:
        st.markdown("1. Create the owner user in Supabase Authentication.")
        st.markdown("2. Replace the placeholder owner UUID in the SQL policies with the real user UUID.")
        st.markdown("3. Add the three settings from the example secrets file.")
        st.warning("Do not use a service-role key. Database and Storage policies must be configured before production.")

def main():
    with st.sidebar:
        st.markdown("## YG<span style='color:#c5ff5f'>.</span>",unsafe_allow_html=True)
        st.caption("DATA · SOFTWARE · GAMES")
        page=st.radio("Navigate",["Portfolio","Admin"],label_visibility="collapsed")
    if page=="Admin":
        try: db_client()
        except Exception:
            st.error("Configure Supabase secrets before using admin."); st.code('SUPABASE_URL = "https://YOUR_PROJECT.supabase.co"\nSUPABASE_ANON_KEY = "YOUR_ANON_KEY"\nADMIN_EMAIL = "you@example.com"'); return
        admin_page(); return
    st.markdown('<div class="hero"><div class="eyebrow">DATA · SOFTWARE · INTELLIGENCE · GAMES</div><h1>I turn complex problems into<br><span class="lime">useful digital products.</span></h1><p class="subhead">I’m Yustus Geofrey — a data and software builder working across analytics, dashboards, full-stack applications, automation and game development.</p></div>',unsafe_allow_html=True)
    c1,c2,c3=st.columns([1,1,3])
    c1.link_button("Explore my work ↓","https://github.com/yustusgeo26-hub",use_container_width=True)
    c2.link_button("Email me ↗","mailto:yustusgeo26@gmail.com",use_container_width=True)
    c3.caption("BASED IN TANZANIA　 ·　 OPEN TO OPPORTUNITIES　 ·　 BUILDING IN PUBLIC")
    st.markdown('<div class="eyebrow">SELECTED WORK</div><h2>Projects in progress<span class="lime">.</span></h2>',unsafe_allow_html=True)
    st.caption("A growing collection of projects. Published items appear here automatically.")
    try: projects=list_published(db_client())
    except Exception: projects=[]; st.info("Configure Supabase and run the database schema to enable published projects.")
    if projects:
        cols=st.columns(3)
        for i,p in enumerate(projects):
            with cols[i%3]: render_project(p)
    else:
        with st.container(border=True):
            st.markdown('<div class="eyebrow">FIRST PROJECTS COMING SOON</div>',unsafe_allow_html=True)
            st.markdown("### Built to grow with you.")
            st.write("Publish your real analytics work, dashboards, websites, tools and games from the admin dashboard.")
            st.markdown(" ".join(f'<span class="pill">{x}</span>' for x in CATEGORIES),unsafe_allow_html=True)
    st.divider()
    st.markdown('<div class="eyebrow">SOFTWARE DOWNLOADS</div><h2>Get my desktop apps<span class="lime">.</span></h2>',unsafe_allow_html=True)
    st.caption("Download Windows applications built by Yustus Geofrey.")
    with st.container(border=True):
        app_left, app_right = st.columns([4, 1])
        with app_left:
            st.markdown("### 🌱 YusPlant")
            st.write("A Windows desktop application by Yustus Geofrey.")
            st.caption("Windows 10 / 11 · Version 1.0.0")
        with app_right:
            st.write("")
            yusplant_download_url = secret("YUSPLANT_DOWNLOAD_URL")
            if valid_url(yusplant_download_url):
                st.link_button("⬇ Download EXE", yusplant_download_url, type="primary", use_container_width=True)
            else:
                st.button("⬇ Coming Soon", key="yusplant_download_soon", disabled=True, use_container_width=True)
    st.markdown("")

    st.divider()
    st.markdown('<div class="eyebrow">CAPABILITIES</div><h2>What I work on<span class="lime">.</span></h2>',unsafe_allow_html=True)
    cols=st.columns(4)
    for col,(tag,title,desc) in zip(cols,[("01 / DATA","Analytics & data science","Cleaning, exploration, statistics and decision support."),("02 / BUILD","Web & full-stack","Websites, applications, APIs and integrations."),("03 / SYSTEMS","Automation & BI","Reporting workflows, dashboards and time-saving tools."),("04 / PLAY","Game development","Gameplay systems, prototypes and interactive experiences.")]):
        with col:
            with st.container(border=True):
                st.markdown(f'<div class="eyebrow">{tag}</div>',unsafe_allow_html=True); st.markdown("#### "+title); st.caption(desc)
    st.divider()
    about,contact=st.columns([3,2])
    with about:
        st.markdown('<div class="eyebrow">ABOUT</div><h2>Curiosity, then execution.</h2>',unsafe_allow_html=True)
        st.write("I enjoy working at the intersection of data and software: understanding a problem, shaping a clear solution, and building something people can actually use. This portfolio will evolve as I release new work.")
    with contact:
        st.markdown('<div class="eyebrow">LET’S CONNECT</div><h2>Build something useful.</h2>',unsafe_allow_html=True)
        st.write("For client projects, collaborations and employment opportunities.")
        st.link_button("Email Yustus ↗","mailto:yustusgeo26@gmail.com",use_container_width=True)
        st.link_button("GitHub ↗","https://github.com/yustusgeo26-hub",use_container_width=True)
    st.divider(); st.caption("© YUSTUS GEOFREY · A portfolio built to keep evolving.")

if __name__ == "__main__":
    main()
