import plotly.express as px
import pandas as pd
import streamlit as st

from category_management import render_category_management
from organization_management import render_organization_management

# 1. Cấu hình trang Streamlit
st.set_page_config(
    page_title="Hệ thống Quản lý Nhân sự - Bệnh viện Bưu điện",
    page_icon="🏥",
    layout="wide",
)

# 2. Thanh Menu Sidebar bên trái với 18 chức năng + Icon đẹp mắt
st.sidebar.title("MENU QUẢN TRỊ CÁN BỘ")
menu_choice = st.sidebar.radio(
    "Chọn chức năng:",
    [
        "📊 1. Dashboard Tổng quan",
        "⚙️ 2. Danh mục Hệ thống",
        "🏢 3. Quản lý Cơ cấu Tổ chức",
        "📁 4. Quản lý Hồ sơ Cán bộ",
        "🎯 5. Quản lý Tuyển dụng",
        "📝 6. Quản lý Hợp đồng Lao động",
        "🔄 7. Điều động - Bổ nhiệm",
        "⏰ 8. Chấm công - Ca trực - Phân lịch",
        "📅 9. Quản lý Nghỉ phép & Điền từ",
        "💰 10. Quản lý Tiền lương & Phụ cấp",
        "📜 11. Quản lý Chứng chỉ hành nghề Y tế",
        "🎓 12. Quản lý Đào tạo & Sổ giờ CML",
        "📈 13. Đánh giá KPI & An toàn Người bệnh",
        "🎖️ 14. Thi đua - Khen thưởng & Kỷ luật",
        "🏥 15. Quản lý Sức khỏe & Phôi chiếu",
        "📄 16. Quản lý Văn bản - Quyết định",
        "📊 17. Báo cáo - Thống kê - CSDL Y tế",
        "🔐 18. Quản lý Hệ thống & Phân quyền",
    ],
)


# Hàm hiển thị Trang Dashboard Tổng quan Chuyên nghiệp
def render_dashboard():
    # -------------------------------------------------------------------------
    # PHẦN 1: HEADER TRÊN CÙNG (LOGO & HÌNH ẢNH BỆNH VIỆN BƯU ĐIỆN)
    # -------------------------------------------------------------------------
    col_logo, col_title = st.columns([1, 6])
    with col_logo:
        st.image(
            "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Logo_VNPT.svg/1200px-Logo_VNPT.svg.png",
            width=100,
        )
    with col_title:
        st.markdown(
            """
            <h1 style='margin-bottom: 0px; color: #0056b3;'>BỆNH VIỆN BƯU ĐIỆN</h1>
            <h4 style='margin-top: 0px; color: #555;'>HỆ THỐNG QUẢN TRỊ TỔNG THỂ NHÂN SỰ & CÁN BỘ Y TẾ</h4>
            """,
            unsafe_allow_html=True,  # Đã sửa lại tham số chính xác ở đây
        )

    # Banner ảnh Bệnh viện Bưu điện chuyên nghiệp
    st.image(
        "https://buudienhospital.vn/wp-content/uploads/2021/08/banner-benh-vien-buu-dien.jpg",
        use_column_width=True,
    )

    st.divider()

    # -------------------------------------------------------------------------
    # PHẦN 2: THỐNG KÊ CƠ CẤU LAO ĐỘNG THEO CHỨC DANH + BIỂU ĐỒ
    # -------------------------------------------------------------------------
    st.subheader("📊 THỐNG KÊ CƠ CẤU LAO ĐỘNG THEO CHỨC DANH TOÀN BỆNH VIỆN")

    # Dữ liệu thống kê cơ cấu chức danh
    df_structure = pd.DataFrame({
        "Chức danh": [
            "Bác sĩ",
            "Điều dưỡng",
            "Kỹ thuật viên",
            "Dược sĩ",
            "Hành chính / Khác",
        ],
        "Số lượng (Người)": [385, 520, 150, 45, 150],
    })
    df_structure["Tỷ lệ (%)"] = (
        df_structure["Số lượng (Người)"] / df_structure["Số lượng (Người)"].sum() * 100
    ).round(1)

    col_chart, col_table = st.columns([5, 4])

    with col_chart:
        # Biểu đồ tròn minh họa sinh động
        fig = px.pie(
            df_structure,
            values="Số lượng (Người)",
            names="Chức danh",
            title="Tỷ lệ phân bổ Nhân sự theo Chức danh",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        fig.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True)

    with col_table:
        st.markdown("#### 📋 Số liệu chi tiết")
        st.dataframe(
            df_structure,
            use_container_width=True,
            hide_index=True,
        )
        total_staff = df_structure["Số lượng (Người)"].sum()
        st.metric(label="Tổng số Cán bộ - Nhân viên", value=f"{total_staff:,} người")

    st.divider()

    # -------------------------------------------------------------------------
    # PHẦN 3: THỐNG KÊ CÁC CẢNH BÁO THỜI HẠN CỦA NGƯỜI LAO ĐỘNG
    # -------------------------------------------------------------------------
    st.subheader("⚠️ THỐNG KÊ CẢNH BÁO THỜI HẠN NHÂN SỰ")

    # Thống kê nhanh bằng thẻ Metric
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("🎂 Sinh nhật tháng này", "18 cán bộ", delta="Tháng 9")
    c2.metric("📈 Đến hạn nâng lương", "12 người", delta="Trong 30 ngày")
    c3.metric("📝 Hết hạn Hợp đồng", "05 người", delta="Trong 30 ngày")
    c4.metric("🎓 Đào tạo CME/Sổ giờ", "08 bác sĩ", delta="Chưa đủ giờ")
    c5.metric("🏖️ Đến tuổi hưu trí", "03 cán bộ", delta="Trong 6 tháng")

    st.write("")

    # Bảng chi tiết danh sách cảnh báo
    st.markdown("#### 🔔 Danh sách Cán bộ đến hạn cần xử lý")

    alert_data = pd.DataFrame([
        {
            "Mã CB": "NV0102",
            "Họ và tên": "Nguyễn Văn An",
            "Khoa / Phòng": "Khoa Khám bệnh",
            "Loại cảnh báo": "🎂 Sinh nhật trong tháng",
            "Thời hạn / Ngày tác nghiệp": "25/09/2026",
            "Trạng thái": "Cần gửi quà / chúc mừng",
        },
        {
            "Mã CB": "NV0215",
            "Họ và tên": "Trần Thị Bích",
            "Khoa / Phòng": "Trung tâm Hỗ trợ Sinh sản",
            "Loại cảnh báo": "📈 Đến hạn nâng bậc lương",
            "Thời hạn / Ngày tác nghiệp": "01/10/2026",
            "Trạng thái": "Chờ duyệt HĐLĐ/Lương",
        },
        {
            "Mã CB": "NV0308",
            "Họ và tên": "Lê Hoàng Nam",
            "Khoa / Phòng": "Khoa Cận lâm sàng",
            "Loại cảnh báo": "📝 Hết hạn Hợp đồng Lao động",
            "Thời hạn / Ngày tác nghiệp": "15/10/2026",
            "Trạng thái": "Chờ ký gia hạn HĐ",
        },
        {
            "Mã CB": "NV0142",
            "Họ và tên": "Phạm Thị Mai",
            "Khoa / Phòng": "Khoa Dược",
            "Loại cảnh báo": "🎓 Thiếu giờ đào tạo liên tục (CME)",
            "Thời hạn / Ngày tác nghiệp": "31/10/2026",
            "Trạng thái": "Cần đăng ký khóa học",
        },
        {
            "Mã CB": "NV0012",
            "Họ và tên": "Đỗ Văn Thắng",
            "Khoa / Phòng": "Phòng Hành chính - Quản trị",
            "Loại cảnh báo": "🏖️ Thông báo hưu trí",
            "Thời hạn / Ngày tác nghiệp": "31/12/2026",
            "Trạng thái": "Chuẩn bị thủ tục hưu trí",
        },
    ])

    st.dataframe(
        alert_data,
        use_container_width=True,
        hide_index=True,
    )


# 3. Điều hướng giao diện theo Lựa chọn của Menu
if "1. Dashboard Tổng quan" in menu_choice:
    render_dashboard()

elif "2. Danh mục Hệ thống" in menu_choice:
    render_category_management()

elif "3. Quản lý Cơ cấu Tổ chức" in menu_choice:
    render_organization_management()

else:
    st.title(f"📌 {menu_choice}")
    st.info("Chức năng đang trong quá trình cập nhật dữ liệu...")
