import streamlit as st


def check_login():
    """Kiểm tra trạng thái đăng nhập của người dùng."""
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""

    return st.session_state["logged_in"]


def login_page():
    """Giao diện trang Đăng nhập hệ thống."""
    st.markdown(
        """
        <style>
            .login-header {
                text-align: center;
                margin-bottom: 20px;
            }
        </style>
    """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown(
            "<h2 class='login-header'>🏥 BỆNH VIỆN BƯU ĐIỆN</h2>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<h4 style='text-align: center;'>HỆ THỐNG QUẢN TRỊ TỔNG THỂ NHÂN SỰ (BVBD-HRM)</h4>",
            unsafe_allow_html=True,
        )
        st.write("---")

        with st.form("login_form"):
            st.subheader("🔑 Đăng nhập hệ thống")
            username = st.text_input("Tên đăng nhập (Username):")
            password = st.text_input("Mật khẩu (Password):", type="password")
            submit = st.form_submit_button("Đăng nhập", use_container_width=True)

            if submit:
                # Kiểm tra tài khoản
                if username == "admin" and password == "admin123":
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = username
                    st.success("✅ Đăng nhập thành công với quyền Admin!")
                    st.rerun()
                else:
                    st.error("❌ Tên đăng nhập hoặc mật khẩu không chính xác!")


def logout():
    """Đăng xuất khỏi hệ thống."""
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""
    st.rerun()


def render_logout_button():
    """Hiển thị thông tin User và Nút Thoát ở Sidebar."""
    st.sidebar.markdown("---")
    st.sidebar.write(
        f"👤 Đang đăng nhập: **{st.session_state.get('username', 'Admin')}**"
    )
    if st.sidebar.button("🚪 Thoát (Đăng xuất)", use_container_width=True):
        logout()
