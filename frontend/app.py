"""Aso Data Assistant — glassmorphism dashboard."""
from __future__ import annotations

import streamlit as st
import httpx
from streamlit_kanban import st_kanban

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


# ── CSS ──────────────────────────────────────────────────────────────────────

def _css(dark: bool, theme: str) -> str:
    hex_color = THEME_HEX.get(theme, "#3b82f6")
    gradient = THEME_GRADIENTS.get(theme, ("#0f1a2e", "#020617"))
    light_tint, dark_tint = gradient
    if dark:
        txt = "#f8fafc"
        muted = "#94a3b8"
        card_bg = "rgba(255,255,255,0.05)"
        card_border = "rgba(255,255,255,0.08)"
    else:
        txt = "#1e293b"
        muted = "#64748b"
        card_bg = "rgba(255,255,255,0.65)"
        card_border = "rgba(255,255,255,0.80)"

    return f"""
    <style>
    /* ── Theme variables ─────────────────────────────────── */
    :root {{
        --accent: {hex_color};
        --accent-muted: {hex_color};
    }}

    /* ── Main app background — tinted per theme ─────────── */
    [data-testid="stAppViewContainer"] > div:first-child {{
        background: linear-gradient(135deg, {light_tint} 0%, {dark_tint} 100%) !important;
    }}
    .stApp {{
        background: linear-gradient(135deg, {light_tint} 0%, {dark_tint} 100%) !important;
    }}

    /* ── Global text colors ─────────────────────────────── */
    h1, h2, h3, h4, h5, h6,
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
    label, .stMarkdown strong {{
        color: {txt} !important;
    }}
    p, span, li, a, .stMarkdown,
    .stTextInput label, .stSelectbox label, .stRadio label {{
        color: {muted} !important;
    }}

    /* ── Primary button override ────────────────────────── */
    .stButton > button[kind="primary"],
    .stButton > button[aria-label*="primary"] {{
        background: var(--accent) !important;
        border-color: var(--accent) !important;
        color: #fff !important;
        font-weight: 600;
        border-radius: 10px !important;
        transition: opacity 0.15s;
    }}
    .stButton > button[kind="primary"]:hover {{
        opacity: 0.8;
    }}

    /* ── Secondary / default buttons ────────────────────── */
    .stButton > button:not([kind="primary"]) {{
        background: {card_bg} !important;
        color: {txt} !important;
        border: 1px solid var(--accent-muted) !important;
        border-radius: 10px !important;
    }}

    /* ── Input fields ───────────────────────────────────── */
    .stTextInput > div > div > input,
    .stSelectbox > div > div:first-child > div:first-child {{
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid var(--accent-muted) !important;
        border-radius: 8px !important;
        color: {txt} !important;
    }}
    .stTextInput > div > div > input::placeholder {{
        color: {muted} !important;
    }}

    /* ── Chat bubbles ───────────────────────────────────── */
    [data-testid="stChatBubble"] {{
        border-radius: 14px !important;
    }}
    .stChatMessage[data-testid="stChatMessageUser"] [data-testid="stChatBubble"] {{
        background: var(--accent) !important;
    }}

    /* ── Sidebar ─────────────────────────────────────────── */
    section[data-testid="stSidebar"] {{
        background: rgba(0,0,0,0.25) !important;
        border-right: 1px solid var(--accent-muted) !important;
    }}
    section[data-testid="stSidebar"] label {{
        color: {txt} !important;
    }}
    /* Sidebar selected radio */
    section[data-testid="stSidebar"] .stRadio > label {{
        color: var(--accent) !important;
        font-weight: 600;
    }}

    /* ── Main content vertical blocks (compact glass cards) ─── */
    section.main > div > div:nth-child(2) > div > div {{
        background: {card_bg} !important;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid var(--accent-muted) !important;
        border-radius: 14px !important;
        padding: 0.75rem 1rem !important;
        margin-bottom: 0.5rem !important;
    }}

    /* ── Toast / notification ──────────────────────────── */
    .stAlert {{
        background: {card_bg} !important;
        backdrop-filter: blur(12px);
        border: 1px solid var(--accent-muted) !important;
        border-radius: 10px !important;
        color: {txt} !important;
    }}

    /* ── Divider ────────────────────────────────────────── */
    hr {{
        border-color: var(--accent-muted) !important;
    }}

    /* ── Chat input ─────────────────────────────────────── */
    .stChatInputContainer textarea {{
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid var(--accent-muted) !important;
        border-radius: 12px !important;
        color: {txt} !important;
    }}

    /* ── KPI summary cards ──────────────────────────────── */
    .aso-kpi {{
        background: rgba(255,255,255,0.05) !important;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 16px !important;
        padding: 1.25rem 1.5rem !important;
        text-align: center;
    }}
    .aso-kpi .kpi-value {{
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        line-height: 1.1 !important;
        margin: 0 !important;
    }}
    .aso-kpi .kpi-label {{
        font-size: 0.85rem !important;
        color: #94a3b8 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.25rem !important;
    }}

    /* ── Message expanders ──────────────────────────────── */
    .aso-expander summary {{
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 10px !important;
        padding: 0.6rem 1rem !important;
        color: #f1f5f9 !important;
        font-weight: 500;
    }}
    .aso-expander[open] summary {{
        border-bottom-left-radius: 0 !important;
        border-bottom-right-radius: 0 !important;
    }}
    .aso-expander .expander-content {{
        background: rgba(255,255,255,0.03) !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        border-top: none !important;
        border-radius: 0 0 10px 10px !important;
        padding: 1rem !important;
        color: #94a3b8 !important;
    }}

    /* ── Category tabs ──────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] button[role="tab"] {{
        color: #94a3b8 !important;
        font-size: 0.9rem;
    }}
    .stTabs [data-baseweb="tab-list"] button[role="tab"][aria-selected="true"] {{
        color: var(--accent) !important;
        border-bottom-color: var(--accent) !important;
    }}
    .stTabs [data-baseweb="tab-indicator"] {{
        background: var(--accent) !important;
    }}
    </style>
    """


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

    if prompt := st.chat_input("Type your message..."):
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
        st.info("No messages found. Connect Gmail and sync to get started.")
        return

    critical = [m for m in msgs if m.get("priority_score", 0) >= 9]
    action   = [m for m in msgs if 7 <= m.get("priority_score", 0) <= 8]
    low      = [m for m in msgs if m.get("priority_score", 0) < 7]

    # ── KPI cards ──────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 1.5rem;">
      <div class="aso-kpi">
        <p class="kpi-value" style="color:#ef4444">{len(critical)}</p>
        <p class="kpi-label">🔴 Critical</p>
        <p style="font-size:12px; color:#94a3b8; margin-top:4px">Needs immediate attention</p>
      </div>
      <div class="aso-kpi">
        <p class="kpi-value" style="color:#f59e0b">{len(action)}</p>
        <p class="kpi-label">🟡 Action Needed</p>
        <p style="font-size:12px; color:#94a3b8; margin-top:4px">Follow up within 48 hours</p>
      </div>
      <div class="aso-kpi">
        <p class="kpi-value" style="color:#10b981">{len(low)}</p>
        <p class="kpi-label">🟢 Low Priority</p>
        <p style="font-size:12px; color:#94a3b8; margin-top:4px">Review when you have time</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Tabs by category ───────────────────────────────────────────────────
    all_msgs = msgs.copy()
    categories = list({m.get("category") for m in msgs if m.get("category")} | {"All"})
    categories.sort(key=lambda c: (c != "All", c))

    tab_labels = ["All"] + [c for c in categories if c != "All"]
    tabs = st.tabs(tab_labels)

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
                with st.expander(head, expanded=False):
                    st.markdown(body)
                    if st.button("Draft Reply", key=f"reply_{label}_{idx}_{m.get('id','')}"):
                        with st.spinner("Generating draft…"):
                            draft, err = generate_draft(m["id"])
                        if err:
                            st.error(err)
                        else:
                            st.session_state[f"draft_{m['id']}"] = draft
                    if f"draft_{m['id']}" in st.session_state:
                        st.text_area(
                            "Draft Reply",
                            value=st.session_state[f"draft_{m['id']}"],
                            height=150,
                            key=f"editor_{label}_{m['id']}",
                            label_visibility="collapsed",
                        )
                        if st.button("Send Draft", key=f"send_{label}_{idx}_{m['id']}", type="primary"):
                            st.toast("Draft sent! (Wire up actual send in next phase)")
                            del st.session_state[f"draft_{m['id']}"]


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

    st.divider()

    st.markdown("**➕ Add New Application**")
    with st.form("add_job_form"):
        comp = st.text_input("Company Name", key="in_company")
        title = st.text_input("Job Title", key="in_title")
        status = st.selectbox("Status", ["applied", "saved", "interviewing", "rejected", "offered"], index=0, key="in_status")
        notes = st.text_area("Notes", height=60, key="in_notes")
        submitted = st.form_submit_button("Add", type="primary")
        if submitted:
            if not comp or not title:
                st.error("Company and Job Title are required.")
            else:
                ok, msg = create_job({
                    "company_name": comp,
                    "job_title": title,
                    "status": status,
                    "notes": notes or None,
                })
                st.toast(msg, icon="✅" if ok else "❌")
                if ok:
                    st.rerun()


def render_integrations():
    st.markdown("### 🔌 Integrations")
    st.caption("Connect your platforms. Once connected, Aso will automatically ingest, filter, and prioritize your data.")

    if st.button("📧 Sync Emails (Gmail)", key="sync_btn"):
        with st.spinner("Syncing..."):
            ok, msg = sync_emails()
        st.success(msg) if ok else st.error(msg)

    st.divider()

    layout = st.session_state["layout_style"]

    if layout == "Grid":
        cols = st.columns(3)
        for i, plat in enumerate(PLATFORMS):
            with cols[i % 3]:
                connected = st.session_state.get(f"connected_{plat['name']}", False)
                with st.container(border=True):
                    st.markdown(f"**{plat['emoji']}  {plat['name']}**")
                    if connected:
                        st.success("✅ Connected", icon="✅")
                    else:
                        if st.button("Connect", key=f"conn_{plat['name']}", use_container_width=True):
                            st.session_state[f"connected_{plat['name']}"] = True
                            st.toast(f"Successfully connected to {plat['name']}!")
                            st.rerun()
    else:
        for plat in PLATFORMS:
            connected = st.session_state.get(f"connected_{plat['name']}", False)
            with st.container(border=True):
                cols = st.columns([3, 1])
                with cols[0]:
                    st.markdown(f"**{plat['emoji']}  {plat['name']}**")
                with cols[1]:
                    if connected:
                        st.success("✅", icon="✅")
                    else:
                        if st.button("Connect", key=f"conn_l_{plat['name']}", use_container_width=True):
                            st.session_state[f"connected_{plat['name']}"] = True
                            st.toast(f"Successfully connected to {plat['name']}!")
                            st.rerun()


def render_settings():
    st.markdown("### ⚙️ Settings")
    st.caption("Customize your dashboard. Changes apply instantly.")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Theme Color**")
        new_theme = st.selectbox("Color", THEME_COLORS, index=THEME_COLORS.index(st.session_state["theme_color"]), key="_theme_sel")
        st.markdown("**Dark Mode**")
        new_dark = st.toggle("Dark", value=st.session_state["dark_mode"], key="_dark_tog")
    with c2:
        st.markdown("**Layout**")
        new_layout = st.radio("Style", ["Grid", "List"], index=["Grid", "List"].index(st.session_state["layout_style"]), key="_layout_rad")

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
        st.error("Could not load profile. Please log in again.")
        return

    current_phone = profile.get("phone") or ""
    current_location = profile.get("location") or ""
    current_bio = profile.get("bio") or ""

    st.markdown(f"**Email:** {profile.get('email', 'N/A')}")
    st.markdown(f"**Full Name:** {profile.get('full_name') or '—'}")

    st.divider()
    st.markdown("**Edit Profile**")

    with st.form("profile_form"):
        phone = st.text_input("Phone", value=current_phone, key="prof_phone")
        location = st.text_input("Location", value=current_location, key="prof_location")
        bio = st.text_area("Bio", value=current_bio, height=80, key="prof_bio")
        submitted = st.form_submit_button("Save Profile", type="primary")
        if submitted:
            ok, msg = update_profile({
                "phone": phone or None,
                "location": location or None,
                "bio": bio or None,
            })
            st.toast(msg, icon="✅" if ok else "❌")
            if ok:
                st.rerun()

    st.divider()
    if st.button("Log Out", key="logout_btn", use_container_width=True):
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
    tab1, tab2 = st.tabs(["Sign In", "Sign Up"])

    with tab1:
        st.markdown("<h3>Welcome back</h3>", unsafe_allow_html=True)
        email = st.text_input("Email", key="l_email")
        password = st.text_input("Password", type="password", key="l_pwd")
        if st.button("Log In", type="primary", use_container_width=True, key="l_btn"):
            if not email or not password:
                st.error("Enter both email and password.")
                return
            ok, msg = login(email, password)
            if ok:
                st.success("Logged in!")
                st.rerun()
            else:
                st.error(msg)

    with tab2:
        st.markdown("<h3>Create an account</h3>", unsafe_allow_html=True)
        full_name = st.text_input("Full Name", key="r_name")
        email = st.text_input("Email", key="r_email")
        password = st.text_input("Password", type="password", key="r_pwd")
        confirm = st.text_input("Confirm Password", type="password", key="r_confirm")
        if st.button("Sign Up", type="primary", use_container_width=True, key="r_btn"):
            if not email or not password:
                st.error("Enter both email and password.")
                return
            if password != confirm:
                st.error("Passwords do not match.")
                return
            ok, msg = register(email, password, full_name or None)
            if ok:
                st.success(msg)
            else:
                st.error(msg)


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
    theme = st.session_state["theme_color"]

    st.markdown(_css(dark, theme), unsafe_allow_html=True)

    if st.session_state.get("logged_in"):
        render_sidebar()
        PAGES[st.session_state["nav_page"]]()
    else:
        render_login()


if __name__ == "__main__":
    main()
