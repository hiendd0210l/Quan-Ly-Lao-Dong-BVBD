import streamlit as st
from category_management import render_category_management
from organization_management import render_organization_management

# 1. Cấu hình trang Streamlit
st.set_page_config(
    page_title="Hệ thống Quản lý Nhân sự - Bệnh viện Bưu điện",
    page_icon="🏥",
    layout="wide",
)

# 2. Tạo Menu điều hướng bên thanh Sidebar
st.sidebar.title("MENU QUẢN TRỊ CÁN BỘ")
menu_choice = st.sidebar.radio(
    "Chọn chức năng:",
    [
        "1. Dashboard Tổng quan",
        "2. Danh mục Hệ thống",
        "3. Quản lý Cơ cấu Tổ chức",
        "4. Quản lý Hồ sơ Cán bộ",
    ],
)

# 3. Điều hướng giao diện theo lựa chọn của người dùng
if menu_choice == "1. Dashboard Tổng quan":
    st.title("🏥 BỆNH VIỆN BƯU ĐIỆN")
    st.subheader("BÁO CÁO TỔNG QUAN NHÂN SỰ")
    st.info("Giao diện Dashboard tổng quan...")

elif menu_choice == "2. Danh mục Hệ thống":
    render_category_management()

elif menu_choice == "3. Quản lý Cơ cấu Tổ chức":
    render_organization_management()

elif menu_choice == "4. Quản lý Hồ sơ Cán bộ":
    st.title("📋 QUẢN LÝ HỒ SƠ CÁN BỘ")
    st.info("Giao diện Quản lý hồ sơ cán bộ...")
