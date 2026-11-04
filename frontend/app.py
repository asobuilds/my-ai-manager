"""Streamlit chat interface for My AI Manager."""
from __future__ import annotations

import streamlit as st
import httpx

BASE_URL = "http://127.0.0.1:8000/api/v1"


def get_headers() -> dict[str, str]:
    """Return request headers with Bearer token if logged in."""
    token = st.session_state.get("access_token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


def login(email: str, password: str) -> tuple[bool, str]:
    """Attempt to log in and store token if successful."""
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
    """Send a message to the chat API and return (response_text, conversation_id)."""
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
    """Trigger email sync and return success status and message."""
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


def init_session():
    """Initialize session state variables."""
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if "access_token" not in st.session_state:
        st.session_state["access_token"] = None
    if "email" not in st.session_state:
        st.session_state["email"] = None
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "conversation_id" not in st.session_state:
        st.session_state["conversation_id"] = None


def show_login_form():
    """Display login form in sidebar."""
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


def show_chat_interface():
    """Display chat interface after login."""
    st.title("My AI Manager")
    st.caption(f"Welcome, {st.session_state['email']}")

    # Sidebar actions
    with st.sidebar:
        st.header("Actions")
        if st.button("Sync Emails", use_container_width=True):
            with st.spinner("Syncing..."):
                success, msg = sync_emails()
            if success:
                st.success(msg)
            else:
                st.error(msg)
        if st.button("Log Out", use_container_width=True):
            st.session_state["logged_in"] = False
            st.session_state["access_token"] = None
            st.session_state["email"] = None
            st.session_state["messages"] = []
            st.session_state["conversation_id"] = None
            st.rerun()

        st.markdown("---")
        st.markdown("*Tip: Your inbox context is automatically included in each message.*")

    # Chat history
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
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


def main():
    init_session()
    if st.session_state.get("logged_in"):
        show_chat_interface()
    else:
        show_login_form()


if __name__ == "__main__":
    main()
