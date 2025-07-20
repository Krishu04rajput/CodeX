
import streamlit as st
from streamlit_ace import st_ace
import subprocess
import tempfile
import os
import supabase
from supabase import create_client, Client
from pathlib import Path

# --- Configuration ---
SUPABASE_URL = "https://<your-project>.supabase.co"
SUPABASE_KEY = "<your-api-key>"

# --- Setup Supabase ---
@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase_client = init_supabase()

# --- Authentication ---
def login():
    st.subheader("Login to CodeX")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        try:
            user = supabase_client.auth.sign_in_with_password({"email": email, "password": password})
            st.session_state["user"] = user
            st.success("Logged in successfully!")
        except Exception as e:
            st.error(f"Login failed: {e}")

def logout():
    if st.button("Logout"):
        st.session_state.pop("user", None)

# --- Code Runner ---
def run_code(code):
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as temp:
        temp.write(code.encode())
        temp_path = temp.name

    try:
        result = subprocess.run(["python", temp_path], capture_output=True, text=True, timeout=10)
        output = result.stdout + ("
" + result.stderr if result.stderr else "")
    except Exception as e:
        output = str(e)
    finally:
        os.remove(temp_path)

    return output

# --- File Upload ---
def handle_file_upload():
    uploaded_file = st.file_uploader("Upload Python File", type="py")
    if uploaded_file is not None:
        code = uploaded_file.read().decode("utf-8")
        return code
    return ""

# --- UI ---
def codex_ui():
    st.title("🚀 CodeX - Python Replit Clone")
    uploaded_code = handle_file_upload()
    code = st_ace(language="python", theme="monokai", height=400, value=uploaded_code or "print('Hello from CodeX!')")

    if st.button("▶ Run Code"):
        st.subheader("📤 Output")
        output = run_code(code)
        st.code(output, language="text")

    st.download_button("⬇ Download Code", code, file_name="code.py")
    logout()

# --- Main App ---
if "user" not in st.session_state:
    login()
else:
    codex_ui()
