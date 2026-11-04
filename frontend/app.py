"""Aso Data Assistant — glassmorphism dashboard."""
from __future__ import annotations

import streamlit as st
import httpx

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


# ── CSS ──────────────────────────────────────────────────────────────────────

def _css(dark: bool, theme: str) -> str:
    hex_color = THEME_HEX.get(theme, "#3b82f6")
    if dark:
        bg = f"linear-gradient(135deg, #0f172a 0%, #1e293b 60%, #0f172a 100%)"
        txt = "#f1f5f9"
        muted = "#94a3b8"
        card_bg = "rgba(255,255,255,0.06)"
        card_border = "rgba(255,255,255,0.10)"
    else:
        bg = f"linear-gradient(135deg, #eef2ff 0%, #f0f9ff 50%, #faf5ff 100%)"
        txt = "#1e293b"
        muted = "#64748b"
        card_bg = "rgba(255,255,255,0.65)"
        card_border = "rgba(255,255,255,0.80)"

    return f"""
    <style>
    /* ── Theme variable ─────────────────────────────────── */
    :root {{
        --aso-accent: {hex_color};
    }}

    /* ── App background ─────────────────────────────────── */
    .stApp {{
        background: {bg};
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
        background: var(--aso-accent) !important;
        border-color: var(--aso-accent) !important;
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
        border: 1px solid {card_border} !important;
        border-radius: 10px !important;
    }}

    /* ── Input fields ───────────────────────────────────── */
    .stTextInput > div > div > input,
    .stSelectbox > div > div:first-child > div:first-child {{
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid {card_border} !important;
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
        background: var(--aso-accent) !important;
    }}

    /* ── Sidebar ─────────────────────────────────────────── */
    section[data-testid="stSidebar"] {{
        background: rgba(0,0,0,0.15) !important;
        border-right: 1px solid {card_border} !important;
    }}
    section[data-testid="stSidebar"] label {{
        color: {txt} !important;
    }}

    /* ── Main content vertical blocks (compact cards) ─── */
    section.main > div > div:nth-child(2) > div > div {{
        background: {card_bg} !important;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid {card_border} !important;
        border-radius: 14px !important;
        padding: 0.75rem 1rem !important;
        margin-bottom: 0.5rem !important;
    }}

    /* ── Toast / notification ──────────────────────────── */
    .stAlert {{
        background: {card_bg} !important;
        backdrop-filter: blur(12px);
        border: 1px solid {card_border} !important;
        border-radius: 10px !important;
        color: {txt} !important;
    }}

    /* ── Divider ────────────────────────────────────────── */
    hr {{
        border-color: {card_border} !important;
    }}

    /* ── Chat input ─────────────────────────────────────── */
    .stChatInputContainer textarea {{
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid {card_border} !important;
        border-radius: 12px !important;
        color: {txt} !important;
    }}

    /* ── Spinner ─────────────────────────────────────────── */
    .stSpinner > div {{
        border-color: var(--aso-accent) !important;
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
    st.caption("Ask anything about your emails, jobs, or files.")

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


def render_integrations():
    st.markdown("### 🔌 Integrations")
    st.caption("Connect your accounts to sync messages and data.")

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

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Email:** " + st.session_state.get("email", "N/A"))
        st.markdown("**Account Tier:** Free Tier")
        st.markdown("**Status:** ✅ Active")
    with c2:
        if st.button("Download Data", key="dl_btn"):
            st.info("Coming soon!")
        if st.button("Change Password", key="pw_btn"):
            st.info("Coming soon!")

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


PAGES = {"💬 Chat": render_chat, "🔌 Integrations": render_integrations,
         "⚙️ Settings": render_settings, "👤 Profile": render_profile}


# ── Login ────────────────────────────────────────────────────────────────────

def render_login():
    st.markdown("<h2 style='text-align:center'>🤖 Aso Data Assistant</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#94a3b8'>Sign in to continue</p>", unsafe_allow_html=True)

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
