import os
import pandas as pd
import plotly.express as px
import streamlit as st

from category_management import render_category_management
from organization_management import render_organization_management

# 1. Cấu hình trang Streamlit
st.set_page_config(
    page_title="Hệ thống Quản lý Nhân sự - Bệnh viện Bưu điện",
    page_icon="🏥",
    layout="wide",
)

# 2. Thanh Menu Sidebar bên trái với 18 chức năng + Icon
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


# Hàm hiển thị Trang Dashboard Tổng quan
def render_dashboard():
    # -------------------------------------------------------------------------
    # PHẦN 1: HEADER TRÊN CÙNG (LOGO PHÓNG TO GẤP ĐÔI & TIÊU ĐỀ)
    # -------------------------------------------------------------------------
    # Tăng kích thước cột chứa Logo từ [1, 6] thành [2, 6] để đủ không gian hiển thị
    col_logo, col_title = st.columns([2, 6])

    with col_logo:
        # Danh sách đường dẫn tới file logo
        logo_paths = [
            "blocks/main/logo.png",
            "blocks/main/Logo.png",
            "logo.png",
            "Logo.png",
        ]
        logo_found = False
        for path in logo_paths:
            if os.path.exists(path):
                # Tăng width từ 120 lên 240 (gấp đôi kích thước cũ)
                st.image(path, width=240)
                logo_found = True
                break

        if not logo_found:
            st.markdown("## 🏥")

    with col_title:
        st.title("BỆNH VIỆN BƯU ĐIỆN")
        st.caption("HỆ THỐNG QUẢN TRỊ TỔNG THỂ NHÂN SỰ & CÁN BỘ Y TẾ")

    st.divider()

    # -------------------------------------------------------------------------
    # PHẦN 2: THỐNG KÊ CƠ CẤU LAO ĐỘNG THEO CHỨC DANH + BIỂU ĐỒ
    # -------------------------------------------------------------------------
   
def render_dashboard():
    st.subheader(
        "📊 THỐNG KÊ CƠ CẤU LAO ĐỘNG THEO CHỨC DANH TOÀN BỆNH VIỆN"
    )

    # 1. Khởi tạo dữ liệu chức danh
    df_chuc_danh = pd.DataFrame({
        "Chức danh công tác": [
            "Bác sĩ",
            "Điều dưỡng",
            "Kỹ thuật viên",
            "Dược sĩ",
            "Hành chính / Khác",
        ],
        "Số lượng": [485, 518, 158, 43, 46],
        "Tỷ lệ (%)": [38.8, 41.4, 12.7, 3.4, 3.7],
    })

    col_chart, col_table = st.columns([3, 2])

    with col_chart:
        # 2. Tạo biểu đồ cột đứng (Vertical Bar Chart)
        fig_bar = px.bar(
            df_chuc_danh,
            x="Chức danh công tác",
            y="Số lượng",
            text="Số lượng",  # Hiển thị số lượng trực tiếp trên đỉnh cột
            color="Chức danh công tác",  # Màu sắc phân biệt từng cột
            labels={
                "Số lượng": "Số lượng (người)",
                "Chức danh công tác": "Chức danh công tác",
            },
        )

        # 3. Định dạng hiển thị chữ trên đầu cột
        fig_bar.update_traces(
            textposition="outside", texttemplate="%{text} người", cliponaxis=False
        )

        fig_bar.update_layout(
            title="<b>Tỷ lệ phân bổ Nhân sự theo Chức danh</b>",
            xaxis_title="Chức danh công tác",
            yaxis_title="Số lượng (Người)",
            showlegend=False,  # Ẩn chú thích bên phải vì tên đã nằm dưới trục X
            height=420,
            margin=dict(l=20, r=20, t=50, b=20),
        )

        st.plotly_chart(fig_bar, use_container_width=True)

    with col_table:
        st.markdown("##### 📋 Số liệu chi tiết")
        st.dataframe(
            df_chuc_danh,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Chức danh công tác": st.column_config.Column(width="medium"),
                "Số lượng": st.column_config.NumberColumn(
                    "Số lượng (Người)", format="%d"
                ),
                "Tỷ lệ (%)": st.column_config.NumberColumn(
                    "Tỷ lệ (%)", format="%.1f%%"
                ),
            },
        )
        st.write("")
        st.metric("Tổng số Cán bộ - Nhân viên", "1,250 người")

    # -------------------------------------------------------------------------
    # PHẦN 3: THỐNG KÊ CÁC CẢNH BÁO THỜI HẠN CỦA NGƯỜI LAO ĐỘNG
    # -------------------------------------------------------------------------
    st.subheader("⚠️ THỐNG KÊ CẢNH BÁO THỜI HẠN NHÂN SỰ")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("🎂 Sinh nhật tháng này", "18 cán bộ", delta="Tháng 9")
    c2.metric("📈 Đến hạn nâng lương", "12 người", delta="Trong 30 ngày")
    c3.metric("📝 Hết hạn Hợp đồng", "05 người", delta="Trong 30 ngày")
    c4.metric("🎓 Đào tạo CME/Sổ giờ", "08 bác sĩ", delta="Chưa đủ giờ")
    c5.metric("🏖️ Đến tuổi hưu trí", "03 cán bộ", delta="Trong 6 tháng")

    st.write("")

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


# 3. Điều hướng giao diện
if "1. Dashboard Tổng quan" in menu_choice:
    render_dashboard()

elif "2. Danh mục Hệ thống" in menu_choice:
    render_category_management()

elif "3. Quản lý Cơ cấu Tổ chức" in menu_choice:
    render_organization_management()

else:
    st.title(f"📌 {menu_choice}")
    st.info("Chức năng đang trong quá trình cập nhật dữ liệu...")
