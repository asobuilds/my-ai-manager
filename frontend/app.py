"""Aso Data Assistant — glassmorphism dashboard."""
from __future__ import annotations

import base64
import io
import streamlit as st
import httpx
from streamlit_kanban import st_kanban
from streamlit_mic_recorder import mic_recorder
import speech_recognition as sr
from facade import theme, Card, Button, Metric, Tabs, Textarea, Input, Toggle, Radio, Select, Accordion, Alert, Badge, Separator
from neonui import set_page_background

# Must be first Streamlit call
st.set_page_config(page_title="Aso Data Assistant", page_icon="🤖", layout="wide")

BASE_URL = "http://127.0.0.1:8000/api/v1"

PLATFORMS = [
    {"name": "Gmail", "emoji": "📧", "connected": False},
    {"name": "WhatsApp Business", "emoji": "💬", "connected": False},
    {"name": "LinkedIn", "emoji": "💼", "connected": False},
    {"name": "Facebook Messenger", "emoji": "📘", "connected": False},
    {"name": "Twitter / X", "emoji": "🐦", "connected": False},
]

THEME_COLORS = ["blue", "cyan", "purple", "pink", "emerald", "amber"]
THEME_HEX = {
    "blue": "#3b82f6",
    "cyan": "#06b6d4",
    "purple": "#8b5cf6",
    "pink": "#ec4899",
    "emerald": "#10b981",
    "amber": "#f59e0b",
}

# Maps each accent color to a dark gradient (lighter tint, darker tint)
THEME_GRADIENTS = {
    "blue":    ("#0f1a2e", "#020617"),
    "cyan":    ("#0a1e2a", "#020c14"),
    "purple":  ("#1a0f2e", "#0a0217"),
    "pink":    ("#2e0f1e", "#17020e"),
    "emerald": ("#0f1e1a", "#021410"),
    "amber":   ("#1e1a0f", "#141002"),
}


# ── API helpers ──────────────────────────────────────────────────────────────

def get_headers() -> dict[str, str]:
    token = st.session_state.get("access_token")
    return {"Authorization": f"Bearer {token}"} if token else {}


def login(email: str, password: str) -> tuple[bool, str]:
    try:
        resp = httpx.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password}, timeout=10.0)
        if resp.status_code == 200:
            st.session_state["access_token"] = resp.json()["access_token"]
            st.session_state["logged_in"] = True
            st.session_state["email"] = email
            return True, ""
        return (False, "Invalid email or password.") if resp.status_code == 401 else (False, f"Login failed ({resp.status_code}).")
    except httpx.ConnectError:
        return False, "Cannot connect to server. Is the backend running?"
    except Exception as e:
        return False, f"Login error: {e}"


def register(email: str, password: str, full_name: str) -> tuple[bool, str]:
    try:
        resp = httpx.post(f"{BASE_URL}/auth/register", json={"email": email, "password": password, "full_name": full_name}, timeout=10.0)
        if resp.status_code == 200:
            return True, "Account created! Please sign in."
        return False, resp.json().get("detail", f"Registration failed ({resp.status_code}).")
    except httpx.ConnectError:
        return False, "Cannot connect to server."
    except Exception as e:
        return False, f"Registration error: {e}"


def send_message(message: str, conv_id: str | None = None) -> tuple[str, str | None]:
    try:
        payload: dict = {"message": message}
        if conv_id:
            payload["conversation_id"] = conv_id
        resp = httpx.post(f"{BASE_URL}/chat/", json=payload, headers=get_headers(), timeout=60.0)
        if resp.status_code == 401:
            st.session_state["logged_in"] = False
            st.error("Session expired. Please log in again.")
            return "", None
        if resp.status_code != 200:
            return f"Error: {resp.status_code}", None
        data = resp.json()
        return data["response"], data.get("conversation_id")
    except httpx.ConnectError:
        return "Cannot connect to server. Is the backend running?", None
    except Exception as e:
        return f"Chat error: {e}", None


def sync_emails() -> tuple[bool, str]:
    try:
        resp = httpx.post(f"{BASE_URL}/messages/sync", headers=get_headers(), timeout=30.0)
        if resp.status_code == 401:
            st.session_state["logged_in"] = False
            return False, "Session expired."
        if resp.status_code != 200:
            return False, f"Sync failed ({resp.status_code})."
        return True, f"Synced {resp.json().get('synced', 0)} messages."
    except httpx.ConnectError:
        return False, "Cannot connect to server."
    except Exception as e:
        return False, f"Sync error: {e}"


def fetch_messages() -> list[dict]:
    try:
        resp = httpx.get(f"{BASE_URL}/messages", headers=get_headers(), timeout=15.0)
        if resp.status_code == 401:
            st.session_state["logged_in"] = False
        return resp.json() if resp.status_code == 200 else []
    except httpx.ConnectError:
        return []
    except Exception:
        return []


def fetch_jobs() -> list[dict]:
    try:
        resp = httpx.get(f"{BASE_URL}/jobs", headers=get_headers(), timeout=15.0)
        if resp.status_code == 401:
            st.session_state["logged_in"] = False
        return resp.json() if resp.status_code == 200 else []
    except httpx.ConnectError:
        return []
    except Exception:
        return []


def create_job(data: dict) -> tuple[bool, str]:
    try:
        resp = httpx.post(f"{BASE_URL}/jobs", json=data, headers=get_headers(), timeout=15.0)
        if resp.status_code == 401:
            st.session_state["logged_in"] = False
            return False, "Session expired."
        if resp.status_code == 201:
            return True, "Job application added!"
        return False, f"Failed ({resp.status_code})."
    except httpx.ConnectError:
        return False, "Cannot connect to server."
    except Exception as e:
        return False, f"Error: {e}"


def update_job(job_id: str, data: dict) -> tuple[bool, str]:
    try:
        resp = httpx.patch(f"{BASE_URL}/jobs/{job_id}", json=data, headers=get_headers(), timeout=15.0)
        if resp.status_code == 401:
            st.session_state["logged_in"] = False
            return False, "Session expired."
        if resp.status_code == 200:
            return True, "Job updated!"
        return False, f"Failed ({resp.status_code})."
    except httpx.ConnectError:
        return False, "Cannot connect to server."
    except Exception as e:
        return False, f"Error: {e}"


def fetch_profile() -> dict | None:
    try:
        resp = httpx.get(f"{BASE_URL}/auth/me", headers=get_headers(), timeout=10.0)
        if resp.status_code == 401:
            st.session_state["logged_in"] = False
            return None
        return resp.json() if resp.status_code == 200 else None
    except httpx.ConnectError:
        return None
    except Exception:
        return None


def get_connection_status() -> dict:
    try:
        resp = httpx.get(f"{BASE_URL}/me/connections/status", headers=get_headers(), timeout=10.0)
        if resp.status_code == 401:
            st.session_state["logged_in"] = False
        return resp.json() if resp.status_code == 200 else {"gmail_connected": False}
    except httpx.ConnectError:
        return {"gmail_connected": False}
    except Exception:
        return {"gmail_connected": False}


def update_profile(data: dict) -> tuple[bool, str]:
    try:
        resp = httpx.put(f"{BASE_URL}/profile", json=data, headers=get_headers(), timeout=15.0)
        if resp.status_code == 401:
            st.session_state["logged_in"] = False
            return False, "Session expired."
        if resp.status_code == 200:
            return True, "Profile updated!"
        return False, f"Failed ({resp.status_code})."
    except httpx.ConnectError:
        return False, "Cannot connect to server."
    except Exception as e:
        return False, f"Error: {e}"


def generate_draft(message_id: str) -> tuple[str, str]:
    try:
        resp = httpx.post(f"{BASE_URL}/messages/draft", json={"message_id": message_id}, headers=get_headers(), timeout=30.0)
        if resp.status_code == 401:
            st.session_state["logged_in"] = False
            return "", "Session expired."
        if resp.status_code == 404:
            return "", "Message not found."
        if resp.status_code != 200:
            return "", f"Failed ({resp.status_code})."
        return resp.json().get("draft", ""), ""
    except httpx.ConnectError:
        return "", "Cannot connect to server."
    except Exception as e:
        return "", f"Error: {e}"


def send_draft(message_id: str, draft_text: str) -> tuple[bool, str]:
    try:
        resp = httpx.post(f"{BASE_URL}/messages/send", json={"message_id": message_id, "draft_text": draft_text}, headers=get_headers(), timeout=15.0)
        if resp.status_code == 401:
            st.session_state["logged_in"] = False
            return False, "Session expired."
        if resp.status_code == 404:
            return False, "Message not found."
        if resp.status_code == 200:
            return True, "success"
        return False, f"Failed ({resp.status_code})."
    except httpx.ConnectError:
        return False, "Cannot connect to server."
    except Exception as e:
        return False, f"Error: {e}"


def explain_draft(message_id: str, draft_text: str) -> tuple[str, str]:
    try:
        resp = httpx.post(f"{BASE_URL}/chat/explain", json={"message_id": message_id, "draft_text": draft_text}, headers=get_headers(), timeout=30.0)
        if resp.status_code == 401:
            st.session_state["logged_in"] = False
            return "", "Session expired."
        if resp.status_code == 404:
            return "", "Message not found."
        if resp.status_code != 200:
            return "", f"Failed ({resp.status_code})."
        return resp.json().get("explanation", ""), ""
    except httpx.ConnectError:
        return "", "Cannot connect to server."
    except Exception as e:
        return "", f"Error: {e}"


def _transcribe_audio(audio_bytes: bytes, sample_rate: int) -> str:
    """Transcribe recorded audio using speech_recognition (offline)."""
    try:
        rh = sr.Recognizer()
        with sr.AudioFile(io.BytesIO(audio_bytes), sample_rate=sample_rate) as src:
            audio = rh.record(src)
        return rh.recognize_google(audio).strip()
    except Exception:
        return ""


# ── Session init ─────────────────────────────────────────────────────────────

def init_session():
    defaults = {
        "logged_in": False, "access_token": None, "email": None,
        "messages": [], "conversation_id": None,
        "nav_page": "💬 Chat",
        "theme_color": "blue", "dark_mode": True, "layout_style": "Grid",
    }
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)
    for p in PLATFORMS:
        st.session_state.setdefault(f"connected_{p['name']}", False)


# ── Pages ────────────────────────────────────────────────────────────────────

def render_chat():
    st.markdown("### 💬 Chat")
    st.caption("Talk to Aso. Ask questions about your inbox, draft emails, or manage your schedule.")

    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    col_input, col_mic = st.columns([5, 1])
    with col_input:
        prompt = st.chat_input("Type your message...")
    with col_mic:
        audio = mic_recorder(
            start_prompt="🎤",
            stop_prompt="⏹",
            just_once=True,
            key="chat_mic",
        )
    if audio is not None:
        text = _transcribe_audio(audio["bytes"], audio["sample_rate"])
        if text:
            prompt = text

    if prompt:
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response, conv_id = send_message(prompt, st.session_state["conversation_id"])
                if response.startswith("Error") or response.startswith("Cannot connect"):
                    st.error(response)
                    return
                st.markdown(response)
        st.session_state["messages"].append({"role": "assistant", "content": response})
        if conv_id:
            st.session_state["conversation_id"] = conv_id


def render_data_inventory():
    st.markdown("### 📦 Command Center")
    st.caption("This is your central command center. Aso filters your connected data by priority so you can focus on what matters most. Sync your inbox to see updates.")

    msgs = fetch_messages()

    if not msgs:
        Alert("No messages found. Connect Gmail and sync to get started.", variant="info")
        return

    critical = [m for m in msgs if m.get("priority_score", 0) >= 9]
    action   = [m for m in msgs if 7 <= m.get("priority_score", 0) <= 8]
    low      = [m for m in msgs if m.get("priority_score", 0) < 7]

    # ── KPI cards ──────────────────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    with c1:
        Metric("🔴 Critical", len(critical), key="kpi_critical")
        st.caption("Needs immediate attention")
    with c2:
        Metric("🟡 Action Needed", len(action), key="kpi_action")
        st.caption("Follow up within 48 hours")
    with c3:
        Metric("🟢 Low Priority", len(low), key="kpi_low")
        st.caption("Review when you have time")

    # ── Tabs by category ───────────────────────────────────────────────────
    all_msgs = msgs.copy()
    categories = list({m.get("category") for m in msgs if m.get("category")} | {"All"})
    categories.sort(key=lambda c: (c != "All", c))

    tab_labels = ["All"] + [c for c in categories if c != "All"]
    tabs = Tabs(tab_labels)

    for tab, label in zip(tabs, tab_labels):
        with tab:
            pool = all_msgs if label == "All" else [m for m in all_msgs if m.get("category") == label]
            if not pool:
                st.caption("No messages here. Sync your inbox!")
                continue
            for idx, m in enumerate(pool):
                platform = m.get("platform", "").upper() or "—"
                sender   = m.get("sender") or "Unknown"
                score    = m.get("priority_score", 0)
                subject  = m.get("subject") or "No subject"
                content  = m.get("content") or "No content"
                cat      = m.get("category") or "—"
                head = f"**[{platform}]** {sender} — **Priority:** {score}"
                cat_desc = {
                    "work": "Professional communication from your job or clients.",
                    "job": "Recruitment and career-related messages.",
                    "personal": "Messages from friends, family, or personal accounts.",
                    "newsletter": "Marketing emails, updates, and subscriptions.",
                    "urgent": "Time-sensitive items requiring immediate response.",
                }
                cat_text = cat_desc.get((m.get("category") or "").lower(), f"Message categorized as {cat}.")
                body = f"**Subject:** {subject}\n\n**Category:** {cat} — {cat_text}\n\n{content[:500]}"
                if len(content) > 500:
                    body += "\n\n…(truncated)"
                with Accordion(head, expanded=False):
                    st.markdown(body)
                    if Button("Draft Reply", variant="outline", key=f"reply_{label}_{idx}_{m.get('id','')}"):
                        with st.spinner("Generating draft…"):
                            draft, err = generate_draft(m["id"])
                        if err:
                            Alert(err, variant="error")
                        else:
                            st.session_state[f"draft_{m['id']}"] = draft
                    if f"draft_{m['id']}" in st.session_state:
                        draft_text = Textarea(
                            placeholder="Edit your reply here…",
                            height=150,
                            key=f"editor_{label}_{m['id']}",
                        )
                        btn_col1, btn_col2 = st.columns(2)
                        with btn_col1:
                            if Button("Send Draft", variant="default", key=f"send_{label}_{idx}_{m['id']}"):
                                ok, msg = send_draft(m["id"], draft_text or st.session_state.get(f"draft_{m['id']}", ""))
                                if ok:
                                    Alert("Draft sent successfully!", variant="success")
                                    del st.session_state[f"draft_{m['id']}"]
                                    st.rerun()
                                else:
                                    Alert(msg, variant="error")
                        with btn_col2:
                            if Button("Explain", variant="outline", key=f"explain_{label}_{idx}_{m['id']}"):
                                with st.spinner("Explaining…"):
                                    explanation, err = explain_draft(m["id"], draft_text or st.session_state.get(f"draft_{m['id']}", ""))
                                if err:
                                    Alert(err, variant="error")
                                else:
                                    st.markdown(f"**Why this draft:**\n\n{explanation}")


def render_job_tracker():
    st.markdown("### 💼 Job Tracker")
    st.caption("Manage your career pipeline. Drag and drop applications between stages, or add a new application manually.")

    jobs = fetch_jobs()

    status_order = ["saved", "applied", "interviewing", "rejected", "offered"]
    status_colors = {
        "saved": "#6366f1",
        "applied": "#3b82f6",
        "interviewing": "#f59e0b",
        "rejected": "#ef4444",
        "offered": "#10b981",
    }

    columns: list[dict] = []
    for s in status_order:
        cards = []
        for j in jobs:
            if j.get("status", "").lower() == s:
                cards.append({
                    "id": str(j["id"]),
                    "title": f"{j.get('company_name') or j.get('company', '?')} — {j.get('job_title') or j.get('position', '?')}",
                    "tag": s.capitalize(),
                    "priority": "high" if j.get("priority_score", 0) > 5 else "low",
                })
        columns.append({
            "id": s,
            "title": s.capitalize(),
            "color": status_colors[s],
            "cards": cards,
        })

    st_kanban(columns, key="job_kanban")

    Separator()

    st.markdown("**➕ Add New Application**")
    with st.form("add_job_form"):
        comp = Input(placeholder="Company Name", key="in_company")
        title = Input(placeholder="Job Title", key="in_title")
        raw_status = Select(options=["applied", "saved", "interviewing", "rejected", "offered"], placeholder="Status", key="in_status")
        status = raw_status or "applied"
        notes = Textarea(placeholder="Notes", height=60, key="in_notes")
        submitted = st.form_submit_button("Add", type="primary")
        if submitted:
            if not comp or not title:
                st.error("Company and Job Title are required.")
            else:
                ok, msg = create_job({
                    "company_name": comp,
                    "job_title": title,
                    "status": status or "applied",
                    "notes": notes or None,
                })
                if ok:
                    Alert(msg, variant="success")
                else:
                    Alert(msg, variant="error")
                if ok:
                    st.rerun()


def render_integrations():
    st.markdown("### 🔌 Integrations")
    st.caption("Connect your platforms. Once connected, Aso will automatically ingest, filter, and prioritize your data.")

    status = get_connection_status()
    gmail_connected = status.get("gmail_connected", False)
    auth_url = status.get("authorization_url")

    # ── Gmail card ─────────────────────────────────────────────────────────
    if gmail_connected:
        Card(title="📧 Gmail", description="Connected — your emails are being synced.")
        Badge("Connected", variant="success")
        st.divider()
        if Button("Sync Now", variant="default", key="sync_btn"):
            with st.spinner("Syncing…"):
                ok, msg = sync_emails()
            Alert(msg, variant="success" if ok else "error")
    else:
        Card(title="📧 Gmail", description="Connect your Gmail account to sync emails and send replies.")
        if auth_url:
            st.markdown(f'🔗 [Connect with Google]({auth_url}) — opens in a new tab')
            st.caption("After connecting, click the button below to verify.")
            if Button("I've Connected — Verify", variant="outline", key="verify_conn"):
                new_status = get_connection_status()
                if new_status.get("gmail_connected"):
                    Alert("Gmail connected successfully!", variant="success")
                    st.rerun()
                else:
                    Alert("Connection not detected yet. Complete the Google sign-in flow first.", variant="warning")
        else:
            Alert("Google OAuth not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in your .env file.", variant="warning")

    st.divider()

    # ── Other platforms (placeholder cards) ────────────────────────────────
    for plat in PLATFORMS[1:]:
        Card(title=f"{plat['emoji']}  {plat['name']}")
        Badge("Coming soon", variant="muted")


def render_settings():
    st.markdown("### ⚙️ Settings")
    st.caption("Customize your dashboard. Changes apply instantly.")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Theme Color**")
        new_theme = Select(
            options=THEME_COLORS,
            placeholder="Choose a color…",
            label="Color",
            key="_theme_sel",
        )
        if new_theme is None:
            new_theme = st.session_state["theme_color"]
        st.markdown("**Dark Mode**")
        new_dark = Toggle("Dark", value=st.session_state["dark_mode"], key="_dark_tog")
    with c2:
        st.markdown("**Layout**")
        new_layout = Radio(
            options=["Grid", "List"],
            label="Style",
            index=["Grid", "List"].index(st.session_state["layout_style"]),
            key="_layout_rad",
        )

    # Live apply — rerun on any change
    if (new_theme != st.session_state["theme_color"]
            or new_dark != st.session_state["dark_mode"]
            or new_layout != st.session_state["layout_style"]):
        st.session_state["theme_color"] = new_theme
        st.session_state["dark_mode"] = new_dark
        st.session_state["layout_style"] = new_layout
        st.rerun()


def render_profile():
    st.markdown("### 👤 Profile")

    profile = fetch_profile()
    if not profile:
        Alert("Could not load profile. Please log in again.", variant="error")
        return

    current_phone = profile.get("phone") or ""
    current_location = profile.get("location") or ""
    current_bio = profile.get("bio") or ""

    Card(
        title=f"👤 {profile.get('full_name') or 'User'}",
        description=f"Email: {profile.get('email', 'N/A')} · Status: Active",
    )

    Separator()
    st.markdown("**Edit Profile**")

    with st.form("profile_form"):
        phone = Input(placeholder="Phone", value=current_phone, key="prof_phone")
        location = Input(placeholder="Location", value=current_location, key="prof_location")
        bio = Textarea(placeholder="Bio", value=current_bio, height=80, key="prof_bio")
        submitted = st.form_submit_button("Save Profile", type="primary")
        if submitted:
            ok, msg = update_profile({
                "phone": phone or None,
                "location": location or None,
                "bio": bio or None,
            })
            Alert(msg, variant="success" if ok else "error")
            if ok:
                st.rerun()

    Separator()
    st.markdown("**Avatar**")
    avatar = st.file_uploader("Upload avatar", type=["png", "jpg", "jpeg", "gif"], key="avatar_upload")
    if avatar is not None:
        st.image(avatar, width=120)
        st.caption("Avatar upload ready for next phase.")

    if Button("Log Out", variant="destructive", key="logout_btn"):
        st.session_state["logged_in"] = False
        st.session_state["access_token"] = None
        st.session_state["email"] = None
        st.session_state["messages"] = []
        st.session_state["conversation_id"] = None
        for k in list(st.session_state.keys()):
            if k.startswith("connected_"):
                del st.session_state[k]
        st.rerun()


PAGES = {"💬 Chat": render_chat, "📦 Data Inventory": render_data_inventory,
         "💼 Job Tracker": render_job_tracker, "🔌 Integrations": render_integrations,
         "⚙️ Settings": render_settings, "👤 Profile": render_profile}


# ── Login ────────────────────────────────────────────────────────────────────

def render_login():
    tab1, tab2 = Tabs(["Sign In", "Sign Up"])

    with tab1:
        st.markdown("<h3>Welcome back</h3>", unsafe_allow_html=True)
        email = Input(placeholder="Email", key="l_email")
        password = st.text_input("Password", type="password", key="l_pwd")
        if Button("Log In", variant="default", key="l_btn"):
            if not email or not password:
                st.error("Enter both email and password.")
                return
            ok, msg = login(email, password)
            if ok:
                Alert("Logged in!", variant="success")
                st.rerun()
            else:
                Alert(msg, variant="error")

    with tab2:
        st.markdown("<h3>Create an account</h3>", unsafe_allow_html=True)
        full_name = Input(placeholder="Full Name", key="r_name")
        email = Input(placeholder="Email", key="r_email")
        password = st.text_input("Password", type="password", key="r_pwd")
        confirm = st.text_input("Confirm Password", type="password", key="r_confirm")
        if Button("Sign Up", variant="default", key="r_btn"):
            if not email or not password:
                st.error("Enter both email and password.")
                return
            if password != confirm:
                st.error("Passwords do not match.")
                return
            ok, msg = register(email, password, full_name or None)
            if ok:
                Alert(msg, variant="success")
            else:
                Alert(msg, variant="error")


# ── Sidebar ──────────────────────────────────────────────────────────────────

def render_sidebar():
    st.sidebar.markdown("### 🤖 Aso Data Assistant")
    page = st.sidebar.radio("Navigation", list(PAGES.keys()), key="nav_page")
    st.sidebar.markdown(f"**{st.session_state['email']}**")
    if st.sidebar.button("Log Out", key="s_logout"):
        st.session_state["logged_in"] = False
        st.session_state["access_token"] = None
        st.session_state["email"] = None
        st.session_state["messages"] = []
        st.session_state["conversation_id"] = None
        for k in list(st.session_state.keys()):
            if k.startswith("connected_"):
                del st.session_state[k]
        st.rerun()


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    init_session()
    dark = st.session_state["dark_mode"]
    theme_name = st.session_state["theme_color"]
    hex_color = THEME_HEX.get(theme_name, "#3b82f6")
    gradient = THEME_GRADIENTS.get(theme_name, ("#0f1a2e", "#020617"))
    light_tint, dark_tint = gradient

    # Apply facade theme tokens + neonui background
    theme.apply(
        preset="dark" if dark else "light",
        primary=hex_color,
        primary_foreground="#ffffff",
        background=dark_tint,
        foreground="#f8fafc" if dark else "#1e293b",
        muted="rgba(255,255,255,0.06)" if dark else "rgba(255,255,255,0.65)",
        muted_foreground="#94a3b8" if dark else "#64748b",
        border="rgba(255,255,255,0.10)" if dark else "rgba(255,255,255,0.80)",
        radius="10px",
    )
    set_page_background(gradient=f"linear-gradient(135deg, {light_tint} 0%, {dark_tint} 100%)")

    if st.session_state.get("logged_in"):
        render_sidebar()
        PAGES[st.session_state["nav_page"]]()
    else:
        render_login()


if __name__ == "__main__":
    main()
