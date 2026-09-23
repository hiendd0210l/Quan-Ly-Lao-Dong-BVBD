import streamlit as st
from auth import check_login, login_page, render_logout_button
from views import render_main_app

import streamlit as st
from organization_management import render_organization_management

# Gọi module cơ cấu tổ chức khi chuyển tab/menu
if menu_choice == "3. Quản lý Cơ cấu Tổ chức":
    render_organization_management()

# Cấu hình trang Streamlit
st.set_page_config(
    page_title="Hệ thống Quản lý Nhân sự - Bệnh viện Bưu điện",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Kiểm tra luồng Đăng nhập / Đăng xuất
if not check_login():
    login_page()
else:
    # Đã đăng nhập: Hiển thị Ứng dụng chính + Nút Thoát
    render_main_app()
    render_logout_button()
