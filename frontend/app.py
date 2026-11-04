"""Streamlit dashboard for My AI Manager."""
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


def init_session():
    defaults = {
        "logged_in": False,
        "access_token": None,
        "email": None,
        "messages": [],
        "conversation_id": None,
        "nav_page": "💬 Chat",
        "theme_color": "blue",
        "dark_mode": False,
        "layout_preference": "Grid",
    }
    for key, val in defaults.items():
        st.session_state.setdefault(key, val)
    for plat in PLATFORMS:
        st.session_state.setdefault(f"connected_{plat['name']}", False)


def render_login():
    st.sidebar.title("Login")
    email = st.sidebar.text_input("Email", key="login_email")
    password = st.sidebar.text_input("Password", type="password", key="login_password")
    if st.sidebar.button("Log In", type="primary", use_container_width=True):
        if not email or not password:
            st.sidebar.error("Please enter both email and password.")
            return
        success, msg = login(email, password)
        if success:
            st.sidebar.success("Logged in successfully!")
            st.rerun()
        else:
            st.sidebar.error(msg)


def render_nav():
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**👤 {st.session_state['email']}**")
    st.sidebar.markdown("---")
    pages = ["💬 Chat", "🔌 Integrations", "⚙️ Settings", "👤 Profile"]
    page = st.sidebar.radio("Navigation", pages, key="nav_page")
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


def render_chat():
    st.title("💬 Chat")
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
    st.title("🔌 Integrations")
    st.caption("Connect your accounts to sync messages and data.")

    sync_ok, sync_msg = False, ""
    if st.button("📧 Sync Emails (Gmail)", type="secondary"):
        with st.spinner("Syncing..."):
            sync_ok, sync_msg = sync_emails()
        if sync_ok:
            st.success(sync_msg)
        else:
            st.error(sync_msg)

    st.divider()

    cols = st.columns(3)
    for i, plat in enumerate(PLATFORMS):
        with cols[i % 3]:
            connected = st.session_state.get(f"connected_{plat['name']}", False)
            card = st.container(border=True)
            card.markdown(f"## {plat['emoji']} {plat['name']}")
            if connected:
                card.success("✅ Connected")
            else:
                if card.button("Connect", key=f"btn_{plat['name']}", use_container_width=True):
                    msg = connect_platform(plat["name"])
                    st.toast(msg)
                    st.rerun()


def render_settings():
    st.title("⚙️ Settings")
    st.caption("Customize your dashboard experience.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Appearance")
        theme = st.selectbox("Theme Color", ["blue", "green", "purple", "red"], key="theme_color")
        dark = st.toggle("Dark Mode", value=False, key="dark_mode")
    with col2:
        st.markdown("### Layout")
        layout = st.radio("Layout Preference", ["Grid", "List"], key="layout_preference")

    st.divider()
    st.markdown("*These settings are UI placeholders and do not yet affect the app's appearance.*")


def render_profile():
    st.title("👤 Profile")
    st.caption("Your account information.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Account Details")
        st.markdown(f"**Email:** {st.session_state.get('email', 'N/A')}")
        st.markdown(f"**Account Tier:** Free Tier")
        st.markdown(f"**Status:** ✅ Active")
    with col2:
        st.markdown("### Quick Actions")
        if st.button("Download Data", use_container_width=True):
            st.info("Data export coming soon!")
        if st.button("Change Password", use_container_width=True):
            st.info("Password change coming soon!")

    st.divider()
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


def main():
    init_session()
    if not st.session_state.get("logged_in"):
        render_login()
    else:
        render_nav()
        PAGE_RENDERERS[st.session_state["nav_page"]]()


if __name__ == "__main__":
    main()
