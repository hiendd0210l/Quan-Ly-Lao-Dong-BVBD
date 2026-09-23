import streamlit as st
from category_management import render_category_management
from organization_management import render_organization_management

# 1. Cấu hình trang Streamlit
st.set_page_config(
    page_title="Hệ thống Quản lý Nhân sự - Bệnh viện Bưu điện",
    page_icon="🏥",
    layout="wide",
)

# 2. Tạo Menu điều hướng bên thanh Sidebar đầy đủ các mục
st.sidebar.title("MENU QUẢN TRỊ CÁN BỘ")
menu_choice = st.sidebar.radio(
    "Chọn chức năng:",
    [
        "1. Dashboard Tổng quan",
        "2. Danh mục Hệ thống",
        "3. Quản lý Cơ cấu Tổ chức",
        "4. Quản lý Hồ sơ Cán bộ",
        "5. Quản lý Tuyển dụng",
        "6. Quản lý Hợp đồng Lao động",
        "7. Điều động - Bổ nhiệm",
        "8. Chấm công - Ca trực - Phân lịch",
        "9. Quản lý Nghỉ phép & Điền từ",
        "10. Quản lý Tiền lương & Phụ cấp",
        "11. Quản lý Chứng chỉ hành nghề Y tế",
        "12. Quản lý Đào tạo & Sổ giờ CML",
        "13. Đánh giá KPI & An toàn Người bệnh",
        "14. Thi đua - Khen thưởng & Kỷ luật",
        "15. Quản lý Sức khỏe & Phôi chiếu",
        "16. Quản lý Văn bản - Quyết định",
        "17. Báo cáo - Thống kê - CSDL Y tế",
        "18. Quản lý Hệ thống & Phân quyền",
    ],
)


# Hàm hiển thị Trang Dashboard Tổng quan ban đầu
def render_dashboard():
    # Logo và tiêu đề Bệnh viện Bưu điện
    col_logo, col_title = st.columns([1, 6])
    with col_logo:
        st.image(
            "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Logo_VNPT.svg/1200px-Logo_VNPT.svg.png",
            width=90,
        )
    with col_title:
        st.title("BỆNH VIỆN BƯU ĐIỆN")
        st.caption(
            "HỆ THỐNG QUẢN TRỊ TỔNG THỂ NHÂN SỰ & CÁN BỘ Y TẾ (CẤU HÌNH MỞ)"
        )

    st.divider()

    # Thống kê nhanh chỉ số HR
    st.subheader("📊 BÁO CÁO TỔNG QUAN NHÂN SỰ")

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric(label="Tổng số Cán bộ - Nhân viên", value="1,250 người", delta="12")
    kpi2.metric(label="Bác sĩ & Dược sĩ CKI/CKII", value="385 người", delta="5")
    kpi3.metric(label="Điều dưỡng & KTV", value="620 người", delta="8")
    kpi4.metric(label="Tỷ lệ lấp đầy định biên", value="94.8%", delta="1.2%")

    st.divider()

    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("📈 Cơ cấu nhân sự theo Khoa/Phòng")
        st.info("Biểu đồ và số liệu phân bổ nhân sự theo các khối...")

    with col_right:
        st.subheader("⚠️ Cảnh báo Nhân sự & Chứng chỉ")
        st.warning("• 05 Cán bộ sắp hết hạn Hợp đồng lao động trong 30 ngày")
        st.warning("• 03 Bác sĩ cần cập nhật Sổ giờ đào tạo liên tục (CML)")


# 3. Điều hướng giao diện theo Lựa chọn của Menu
if menu_choice == "1. Dashboard Tổng quan":
    render_dashboard()

elif menu_choice == "2. Danh mục Hệ thống":
    render_category_management()

elif menu_choice == "3. Quản lý Cơ cấu Tổ chức":
    render_organization_management()

else:
    # Các chức năng khác tạm thời hiển thị giao diện chờ
    st.title(f"📌 {menu_choice}")
    st.info("Chức năng đang được kết nối dữ liệu...")
