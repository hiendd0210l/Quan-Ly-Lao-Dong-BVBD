import pandas as pd
import plotly.express as px
import streamlit as st

from category_management import render_category_management
from organization_management import render_organization_management

# ---------------------------------------------------------
# 1. CẤU HÌNH TRANG STREAMLIT
# ---------------------------------------------------------
st.set_page_config(
    page_title="Hệ thống Quản lý Nhân sự - Bệnh viện Bưu điện",
    page_icon="🏥",
    layout="wide",
)


# ---------------------------------------------------------
# 2. HÀM HIỂN THỊ DASHBOARD TỔNG QUAN
# ---------------------------------------------------------
def render_dashboard():
    # --- LOGO VÀ TIÊU ĐỀ BỆNH VIỆN BƯU ĐIỆN ---
    col_logo, col_header = st.columns([2, 5])
    with col_logo:
        try:
            # Kích thước logo đã tăng lên 300px
            st.image("logo.png", width=300)
        except Exception:
            st.markdown("🏥")

    with col_header:
        st.markdown(
            "<h1 style='margin-bottom: 0px; color: #0056b3; font-size:"
            " 36px;'>BỆNH VIỆN BƯU ĐIỆN</h1>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<h3 style='color: #555; margin-top: 5px; font-size: 22px;'>HỆ"
            " THỐNG QUẢN TRỊ NHÂN SỰ & CÁN BỘ</h3>",
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # --- 1. THỐNG KÊ CƠ CẤU LAO ĐỘNG THEO CHỨC DANH ---
    st.subheader(
        "📊 THỐNG KÊ CƠ CẤU LAO ĐỘNG THEO CHỨC DANH TOÀN BỆNH VIỆN"
    )

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
        # Biểu đồ cột đứng (Vertical Bar Chart)
        fig_bar = px.bar(
            df_chuc_danh,
            x="Chức danh công tác",
            y="Số lượng",
            text="Số lượng",
            color="Chức danh công tác",
            labels={
                "Số lượng": "Số lượng (người)",
                "Chức danh công tác": "Chức danh công tác",
            },
        )

        fig_bar.update_traces(
            textposition="outside", texttemplate="%{text} người", cliponaxis=False
        )

        fig_bar.update_layout(
            title="<b>Tỷ lệ phân bổ Nhân sự theo Chức danh</b>",
            xaxis_title="Chức danh công tác",
            yaxis_title="Số lượng (Người)",
            showlegend=False,
            height=380,
            margin=dict(l=20, r=20, t=40, b=20),
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

    st.markdown("---")

    # --- 2. THỐNG KÊ CẢNH BÁO THỜI HẠN NHÂN SỰ ---
    st.subheader("⚠️ THỐNG KÊ CẢNH BÁO THỜI HẠN NHÂN SỰ")

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric("Đến hạn nâng lương", "18 cán bộ", "In 30 ngày")
    with c2:
        st.metric("Hết hạn hợp đồng", "12 người", "In 30 ngày")
    with c3:
        st.metric("Nâng thâm niên nghề", "05 người", "In 30 ngày")
    with c4:
        st.metric("Gia hạn CCHN / Bổ sung", "08 bác sĩ", "Chưa cập nhật")
    with c5:
        st.metric("Đến tuổi nghỉ hưu", "03 cán bộ", "In 6 tháng")

    st.write("")
    st.markdown("##### 🔔 Danh sách Cán bộ đến hạn cần xử lý")

    df_canh_bao = pd.DataFrame({
        "Mã CB": ["CB0012", "CB0145", "CB0233", "CB0089", "CB0512"],
        "Họ và Tên": [
            "Nguyễn Văn An",
            "Trần Thị Bích",
            "Lê Hoàng Cường",
            "Phạm Minh Đức",
            "Vũ Thị Dung",
        ],
        "Khoa / Phòng": [
            "Khoa Khám bệnh",
            "Khoa Cấp cứu",
            "Khoa Ngoại tổng hợp",
            "Khoa Dược",
            "Phòng Tổ chức Cán bộ",
        ],
        "Loại cảnh báo": [
            "Đến hạn nâng bậc lương",
            "Hết hạn HĐLĐ 36 tháng",
            "Đến hạn nâng thâm niên",
            "Gia hạn CCHN Y tế",
            "Thông báo chuẩn bị nghỉ hưu",
        ],
        "Thời hạn": [
            "15/10/2026",
            "20/10/2026",
            "25/10/2026",
            "05/11/2026",
            "12/12/2026",
        ],
        "Trạng thái": [
            "Chưa xử lý",
            "Chưa xử lý",
            "Đang duyệt",
            "Chưa xử lý",
            "Đã thông báo",
        ],
    })

    st.dataframe(df_canh_bao, use_container_width=True, hide_index=True)


# ---------------------------------------------------------
# 3. THANH MENU BÊN TRÁI (SIDEBAR) VỚI ICONS ĐẦY ĐỦ
# ---------------------------------------------------------
st.sidebar.title("MENU QUẢN TRỊ CÁN BỘ")
st.sidebar.markdown("---")

menu_choice = st.sidebar.radio(
    "Chọn chức năng:",
    [
        "1. 📊 Dashboard Tổng quan",
        "2. 📁 Danh mục Hệ thống",
        "3. 🏢 Quản lý Cơ cấu Tổ chức",
        "4. 👨‍⚕️ Quản lý Hồ sơ Cán bộ",
        "5. 📑 Quản lý Tuyển dụng",
        "6. 📝 Quản lý Hợp đồng Lao động",
        "7. 🔄 Điều động - Điều chuyển",
        "8. ⏰ Chấm công - Ca trực - Phân lịch",
        "9. 🏖️ Quản lý Nghỉ phép & Miễn trực",
        "10. 💰 Quản lý Tiền lương & Phụ cấp",
        "11. 🩺 Quản lý Chứng chỉ Hành nghề Y",
        "12. 🎓 Quản lý Đào tạo & Bồi dưỡng CML",
        "13. 🏆 Đánh giá & Đánh giá An toàn Bệnh viện",
        "14. 🎖️ Thi đua - Khen thưởng & Kỷ luật",
        "15. 🏥 Quản lý Sức khỏe & Báo hiểm",
        "16. 📋 Quản lý Tài sản - Quy trình",
        "17. 📈 Báo cáo - Thống kê - CSDL Y tế",
        "18. ⚙️ Quản lý Hệ thống & Phân quyền",
    ],
)

# ---------------------------------------------------------
# 4. ĐIỀU HƯỚNG MÀN HÌNH THEO MENU
# ---------------------------------------------------------
if "1. 📊 Dashboard Tổng quan" in menu_choice:
    render_dashboard()
elif "2. 📁 Danh mục Hệ thống" in menu_choice:
    render_category_management()
elif "3. 🏢 Quản lý Cơ cấu Tổ chức" in menu_choice:
    render_organization_management()
else:
    st.title(menu_choice)
    st.info("Chức năng đang được nâng cấp và phát triển.")
