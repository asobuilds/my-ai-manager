"""My Junior Assistant — futuristic glassmorphism dashboard."""
from __future__ import annotations

import streamlit as st
import httpx

BASE_URL = "http://127.0.0.1:8000/api/v1"

PLATFORMS = [
    {"name": "Gmail", "emoji": "📧", "connected": False},
    {"name": "WhatsApp Business", "emoji": "💬", "connected": False},
    {"name": "LinkedIn", "emoji": "💼", "connected": False},
    {"name": "Facebook Messenger", "emoji": "📘", "connected": False},
    {"name": "Twitter / X", "emoji": "🐦", "connected": False},
]


# ── Helpers ──────────────────────────────────────────────────────────────────

def _css(dark: bool, theme: str) -> str:
    if dark:
        bg = "linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%)"
        glass_bg = "rgba(255, 255, 255, 0.05)"
        glass_border = "rgba(255, 255, 255, 0.12)"
        text_primary = "#f1f5f9"
        text_secondary = "#94a3b8"
        accent = _theme_color(theme)
    else:
        bg = "linear-gradient(135deg, #e0e7ff 0%, #f0f9ff 50%, #faf5ff 100%)"
        glass_bg = "rgba(255, 255, 255, 0.55)"
        glass_border = "rgba(255, 255, 255, 0.7)"
        text_primary = "#1e293b"
        text_secondary = "#64748b"
        accent = _theme_color(theme)

    return f"""
    <style>
    /* ── Base ───────────────────────────────────────────── */
    .stApp {{
        background: {bg};
        background-clip: padding-box;
    }}
    section.main > div {{
        padding-top: 2rem;
    }}
    h1, h2, h3, h4, h5, h6 {{
        color: {text_primary} !important;
    }}
    p, span, label, li, a, .stMarkdown {{
        color: {text_secondary} !important;
    }}
    .stMarkdown strong, .stMarkdown b {{
        color: {text_primary} !important;
    }}

    /* ── Glass card ─────────────────────────────────────── */
    .glass-card {{
        background: {glass_bg};
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 24px;
        border: 1px solid {glass_border};
        padding: 1.5rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        margin-bottom: 1rem;
    }}
    .glass-card-sm {{
        background: {glass_bg};
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 18px;
        border: 1px solid {glass_border};
        padding: 1rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    }}

    /* ── Chat messages ──────────────────────────────────── */
    .chat-user {{
        background: {accent} !important;
        color: #fff !important;
        border-radius: 18px 18px 4px 18px !important;
        padding: 0.75rem 1rem !important;
        max-width: 80%;
        margin-left: auto;
    }}
    .chat-assistant {{
        background: rgba(255,255,255,0.08) !important;
        backdrop-filter: blur(12px);
        color: {text_primary} !important;
        border-radius: 18px 18px 18px 4px !important;
        padding: 0.75rem 1rem !important;
        max-width: 80%;
    }}
    [data-testid="stChatBubble"] {{
        border-radius: 18px !important;
    }}

    /* ── Buttons ────────────────────────────────────────── */
    .stButton > button {{
        background: {accent} !important;
        color: #fff !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.5rem 1.25rem !important;
        font-weight: 600;
        transition: all 0.2s ease;
    }}
    .stButton > button:hover {{
        opacity: 0.85;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }}
    .btn-connect {{
        background: transparent !important;
        border: 2px solid {accent} !important;
        color: {accent} !important;
        font-weight: 600;
        border-radius: 10px !important;
        padding: 0.4rem 1rem !important;
        transition: all 0.2s ease;
    }}
    .btn-connect:hover {{
        background: {accent} !important;
        color: #fff !important;
    }}

    /* ── Sidebar ────────────────────────────────────────── */
    section[data-testid="stSidebar"] {{
        background: rgba(0,0,0,0.2) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid {glass_border};
    }}
    section[data-testid="stSidebar"] .stSidebarNav {{
        padding-top: 1rem;
    }}
    section[data-testid="stSidebar"] label {{
        color: {text_primary} !important;
    }}
    section[data-testid="stSidebar"] [data-testid="stSidebarUserElement"] {{
        color: {text_secondary} !important;
    }}
    .css-1lcbjkc {{
        color: {text_secondary} !important;
    }}
    .css-1lcbjkc b, .css-1lcbjkc strong {{
        color: {text_primary} !important;
    }}

    /* ── Inputs & selects ──────────────────────────────── */
    .stTextInput input, .stSelectbox div, .stRadio label {{
        color: {text_primary} !important;
    }}
    .stTextInput input {{
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid {glass_border} !important;
        border-radius: 10px !important;
        color: {text_primary} !important;
    }}
    div[data-testid="stVerticalBlock"] > div > div {{
        background: rgba(255,255,255,0.04) !important;
        border-radius: 16px !important;
        padding: 1.25rem !important;
        margin-bottom: 1rem;
    }}

    /* ── Toasts & alerts ────────────────────────────────── */
    .stAlert {{
        background: rgba(255,255,255,0.1) !important;
        backdrop-filter: blur(12px);
        border: 1px solid {glass_border} !important;
        border-radius: 12px !important;
        color: {text_primary} !important;
    }}

    /* ── Divider ─────────────────────────────────────────── */
    hr {{
        border-color: {glass_border} !important;
    }}

    /* ── Chat input ─────────────────────────────────────── */
    .stChatInputContainer textarea {{
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid {glass_border} !important;
        border-radius: 16px !important;
        color: {text_primary} !important;
    }}
    .stChatInputContainer textarea:focus {{
        border-color: {accent} !important;
    }}
    </style>
    """


def _theme_color(theme: str) -> str:
    colors = {
        "blue": "#3b82f6",
        "cyan": "#06b6d4",
        "purple": "#8b5cf6",
        "pink": "#ec4899",
        "emerald": "#10b981",
        "amber": "#f59e0b",
    }
    return colors.get(theme, "#3b82f6")


def get_headers() -> dict[str, str]:
    token = st.session_state.get("access_token")
    return {"Authorization": f"Bearer {token}"} if token else {}


def login(email: str, password: str) -> tuple[bool, str]:
    try:
        resp = httpx.post(
            f"{BASE_URL}/auth/login",
            json={"email": email, "password": password},
            timeout=10.0,
        )
        if resp.status_code == 200:
            data = resp.json()
            st.session_state["access_token"] = data["access_token"]
            st.session_state["logged_in"] = True
            st.session_state["email"] = email
            return True, ""
        elif resp.status_code == 401:
            return False, "Invalid email or password."
        else:
            return False, f"Login failed (status {resp.status_code})."
    except httpx.ConnectError:
        return False, "Cannot connect to server. Is the backend running?"
    except Exception as e:
        return False, f"Login error: {e}"


def send_message(message: str, conversation_id: str | None = None) -> tuple[str, str | None]:
    try:
        payload: dict = {"message": message}
        if conversation_id:
            payload["conversation_id"] = conversation_id
        resp = httpx.post(
            f"{BASE_URL}/chat/",
            json=payload,
            headers=get_headers(),
            timeout=60.0,
        )
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
        resp = httpx.post(
            f"{BASE_URL}/messages/sync",
            headers=get_headers(),
            timeout=30.0,
        )
        if resp.status_code == 401:
            st.session_state["logged_in"] = False
            return False, "Session expired. Please log in again."
        if resp.status_code != 200:
            return False, f"Sync failed (status {resp.status_code})."
        data = resp.json()
        return True, f"Synced {data.get('synced', 0)} messages."
    except httpx.ConnectError:
        return False, "Cannot connect to server. Is the backend running?"
    except Exception as e:
        return False, f"Sync error: {e}"


def connect_platform(platform_name: str) -> str:
    st.session_state[f"connected_{platform_name}"] = True
    return f"Successfully connected to {platform_name}!"


# ── Session init ─────────────────────────────────────────────────────────────

def init_session():
    defaults = {
        "logged_in": False,
        "access_token": None,
        "email": None,
        "messages": [],
        "conversation_id": None,
        "nav_page": "💬 Chat",
        "theme_color": "blue",
        "dark_mode": True,
        "layout_style": "Grid",
    }
    for key, val in defaults.items():
        st.session_state.setdefault(key, val)
    for plat in PLATFORMS:
        st.session_state.setdefault(f"connected_{plat['name']}", False)


# ── Pages ────────────────────────────────────────────────────────────────────

def render_chat():
    dark = st.session_state["dark_mode"]
    theme = st.session_state["theme_color"]
    accent = _theme_color(theme)
    tx = "#f1f5f9" if dark else "#1e293b"
    ts = "#94a3b8" if dark else "#64748b"

    st.markdown(f'<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:{tx}'>💬 Chat</h2>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='color:{ts};font-size:0.9rem'>Ask anything about your emails, jobs, or files.</p>",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # Chat history
    for msg in st.session_state["messages"]:
        if msg["role"] == "user":
            st.markdown(
                f'<div class="chat-user">{msg["content"]}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="chat-assistant">{msg["content"]}</div>',
                unsafe_allow_html=True,
            )

    # Chat input
    prompt = st.chat_input("Type your message...")
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


def render_integrations():
    dark = st.session_state["dark_mode"]
    theme = st.session_state["theme_color"]
    accent = _theme_color(theme)
    tx = "#f1f5f9" if dark else "#1e293b"
    ts = "#94a3b8" if dark else "#64748b"

    st.markdown(f'<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:{tx}'>🔌 Integrations</h2>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='color:{ts};font-size:0.9rem'>Connect your accounts to sync messages and data.</p>",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # Sync Emails
    sync_ok, sync_msg = False, ""
    if st.button("📧 Sync Emails (Gmail)", type="secondary"):
        with st.spinner("Syncing..."):
            sync_ok, sync_msg = sync_emails()
        if sync_ok:
            st.success(sync_msg)
        else:
            st.error(sync_msg)

    st.markdown("")
    layout = st.session_state["layout_style"]

    if layout == "Grid":
        cols = st.columns(3)
        for i, plat in enumerate(PLATFORMS):
            with cols[i % 3]:
                connected = st.session_state.get(f"connected_{plat['name']}", False)
                st.markdown(
                    f'<div class="glass-card-sm">',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<div style="font-size:2.5rem;text-align:center">{plat["emoji"]}</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<h4 style='text-align:center;color:{tx};margin:0.25rem 0'>{plat['name']}</h4>",
                    unsafe_allow_html=True,
                )
                if connected:
                    st.markdown(
                        f'<div style="text-align:center;color:{accent};font-weight:600">✅ Connected</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    if st.button("Connect", key=f"btn_{plat['name']}", use_container_width=True, type="primary"):
                        msg = connect_platform(plat["name"])
                        st.toast(msg)
                        st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
    else:
        for plat in PLATFORMS:
            connected = st.session_state.get(f"connected_{plat['name']}", False)
            st.markdown(
                f'<div class="glass-card-sm" style="display:flex;align-items:center;gap:1rem">',
                unsafe_allow_html=True,
            )
            st.markdown(f'<span style="font-size:2rem">{plat["emoji"]}</span>', unsafe_allow_html=True)
            st.markdown(f"<strong style='color:{tx}'>{plat['name']}</strong>", unsafe_allow_html=True)
            if connected:
                st.markdown(
                    f'<span style="color:{accent};margin-left:auto">✅ Connected</span>',
                    unsafe_allow_html=True,
                )
            else:
                if st.button("Connect", key=f"btn_list_{plat['name']}", type="primary"):
                    msg = connect_platform(plat["name"])
                    st.toast(msg)
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)


def render_settings():
    dark = st.session_state["dark_mode"]
    theme = st.session_state["theme_color"]
    accent = _theme_color(theme)
    tx = "#f1f5f9" if dark else "#1e293b"
    ts = "#94a3b8" if dark else "#64748b"

    st.markdown(f'<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:{tx}'>⚙️ Settings</h2>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='color:{ts};font-size:0.9rem'>Customize your dashboard experience. Changes apply instantly.</p>",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="glass-card-sm">', unsafe_allow_html=True)
        st.markdown(f"<h4 style='color:{tx}'>🎨 Appearance</h4>", unsafe_allow_html=True)
        new_theme = st.selectbox(
            "Theme Color",
            ["blue", "cyan", "purple", "pink", "emerald", "amber"],
            index=["blue", "cyan", "purple", "pink", "emerald", "amber"].index(st.session_state["theme_color"]),
            key="theme_color_select",
        )
        new_dark = st.toggle("Dark Mode", value=st.session_state["dark_mode"], key="dark_mode_toggle")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown(f'<div class="glass-card-sm">', unsafe_allow_html=True)
        st.markdown(f"<h4 style='color:{tx}'>📐 Layout</h4>", unsafe_allow_html=True)
        new_layout = st.radio(
            "Layout Preference",
            ["Grid", "List"],
            index=["Grid", "List"].index(st.session_state["layout_style"]),
            key="layout_style_radio",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # Apply changes
    changed = False
    if new_theme != st.session_state["theme_color"]:
        st.session_state["theme_color"] = new_theme
        changed = True
    if new_dark != st.session_state["dark_mode"]:
        st.session_state["dark_mode"] = new_dark
        changed = True
    if new_layout != st.session_state["layout_style"]:
        st.session_state["layout_style"] = new_layout
        changed = True

    if changed:
        st.rerun()

    st.markdown(f'<div class="glass-card-sm" style="margin-top:1rem">', unsafe_allow_html=True)
    st.markdown(
        f'<p style="color:{ts};font-size:0.85rem">💡 Tip: Toggle Dark Mode and pick a theme color to see the glassmorphism effect in action.</p>',
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)


def render_profile():
    dark = st.session_state["dark_mode"]
    theme = st.session_state["theme_color"]
    accent = _theme_color(theme)
    tx = "#f1f5f9" if dark else "#1e293b"
    ts = "#94a3b8" if dark else "#64748b"

    st.markdown(f'<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:{tx}'>👤 Profile</h2>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="glass-card-sm">', unsafe_allow_html=True)
        st.markdown(f"<h4 style='color:{tx}'>Account Details</h4>", unsafe_allow_html=True)
        st.markdown(f"**Email:** {st.session_state.get('email', 'N/A')}")
        st.markdown("**Account Tier:** Free Tier")
        st.markdown("**Status:** ✅ Active")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown(f'<div class="glass-card-sm">', unsafe_allow_html=True)
        st.markdown(f"<h4 style='color:{tx}'>Quick Actions</h4>", unsafe_allow_html=True)
        if st.button("Download Data", use_container_width=True):
            st.info("Data export coming soon!")
        if st.button("Change Password", use_container_width=True):
            st.info("Password change coming soon!")
        st.markdown("</div>", unsafe_allow_html=True)

    if st.button("Log Out", type="secondary", use_container_width=True):
        st.session_state["logged_in"] = False
        st.session_state["access_token"] = None
        st.session_state["email"] = None
        st.session_state["messages"] = []
        st.session_state["conversation_id"] = None
        for key in list(st.session_state.keys()):
            if key.startswith("connected_"):
                del st.session_state[key]
        st.rerun()


PAGE_RENDERERS = {
    "💬 Chat": render_chat,
    "🔌 Integrations": render_integrations,
    "⚙️ Settings": render_settings,
    "👤 Profile": render_profile,
}


# ── Login ────────────────────────────────────────────────────────────────────

def render_login():
    dark = True
    tx = "#f1f5f9"
    ts = "#94a3b8"
    accent = "#3b82f6"

    st.markdown(
        f"""
        <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:60vh;">
            <div class="glass-card" style="width:100%;max-width:380px;">
                <h2 style="color:{tx};text-align:center;margin-bottom:0.25rem;">🤖 My Junior Assistant</h2>
                <p style="color:{ts};text-align:center;font-size:0.9rem;margin-bottom:1.5rem;">Sign in to continue</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="glass-card" style="max-width:400px;margin:0 auto;">', unsafe_allow_html=True)
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Log In", type="primary", use_container_width=True):
        if not email or not password:
            st.error("Please enter both email and password.")
            return
        success, msg = login(email, password)
        if success:
            st.success("Logged in successfully!")
            st.rerun()
        else:
            st.error(msg)
    st.markdown("</div>", unsafe_allow_html=True)


# ── Sidebar ──────────────────────────────────────────────────────────────────

def render_sidebar():
    dark = st.session_state["dark_mode"]
    tx = "#f1f5f9" if dark else "#1e293b"
    ts = "#94a3b8" if dark else "#64748b"

    st.sidebar.markdown(f'<div class="glass-card-sm">', unsafe_allow_html=True)
    st.sidebar.markdown(
        f"<h3 style='color:{tx};margin:0.25rem 0'>🤖 My Junior Assistant</h3>",
        unsafe_allow_html=True,
    )
    st.sidebar.markdown(
        f'<p style="color:{ts};font-size:0.8rem;margin:0">Your AI-powered productivity hub</p>',
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("</div>", unsafe_allow_html=True)

    st.sidebar.markdown("")
    pages = ["💬 Chat", "🔌 Integrations", "⚙️ Settings", "👤 Profile"]
    page = st.sidebar.radio("Navigation", pages, key="nav_page")

    st.sidebar.markdown("---")
    st.sidebar.markdown(f'<div class="glass-card-sm">', unsafe_allow_html=True)
    st.sidebar.markdown(f"👤 **{st.session_state['email']}</div>", unsafe_allow_html=True)
    st.sidebar.markdown("</div>", unsafe_allow_html=True)

    if st.sidebar.button("Log Out", use_container_width=True):
        st.session_state["logged_in"] = False
        st.session_state["access_token"] = None
        st.session_state["email"] = None
        st.session_state["messages"] = []
        st.session_state["conversation_id"] = None
        for key in list(st.session_state.keys()):
            if key.startswith("connected_"):
                del st.session_state[key]
        st.rerun()


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    init_session()
    dark = st.session_state["dark_mode"]
    theme = st.session_state["theme_color"]

    st.set_page_config(
        page_title="My Junior Assistant",
        page_icon="🤖",
        layout="wide",
    )

    # Inject glassmorphism CSS
    st.markdown(_css(dark, theme), unsafe_allow_html=True)

    if not st.session_state.get("logged_in"):
        render_login()
    else:
        render_sidebar()
        PAGE_RENDERERS[st.session_state["nav_page"]]()


if __name__ == "__main__":
    main()
