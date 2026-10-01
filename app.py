import pandas as pd
import plotly.express as px
import streamlit as st

from category_management import render_category_management
from organization_management import render_organization_management

# ---------------------------------------------------------
# 1. CẤU HÌNH TRANG STREAMLIT
# ---------------------------------------------------------
st.set_page_config(
    page_title="Hệ thống Quản lý Nhân sự - Bệnh viện",
    page_icon="🏥",
    layout="wide",
)


# ---------------------------------------------------------
# 2. HÀM HIỂN THỊ DASHBOARD TỔNG QUAN (BIỂU ĐỒ CỘT ĐỨNG)
# ---------------------------------------------------------
def render_dashboard():
    st.subheader(
        "📊 THỐNG KÊ CƠ CẤU LAO ĐỘNG THEO CHỨC DANH TOÀN BỆNH VIỆN"
    )

    # Dữ liệu chức danh công tác
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
            text="Số lượng",  # Hiển thị số lượng trực tiếp trên đỉnh cột
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


# ---------------------------------------------------------
# 3. THANH MENU BÊN TRÁI (SIDEBAR)
# ---------------------------------------------------------
st.sidebar.title("MENU QUẢN TRỊ CÁN BỘ")
st.sidebar.markdown("---")

menu_choice = st.sidebar.radio(
    "Chọn chức năng:",
    [
        "1. Dashboard Tổng quan",
        "2. Danh mục Hệ thống",
        "3. Quản lý Cơ cấu Tổ chức",
        "4. Quản lý Hồ sơ Cán bộ",
        "5. Quản lý Tuyển dụng",
        "6. Quản lý Hợp đồng Lao động",
        "7. Điều động - Điều chuyển",
        "8. Chấm công - Ca trực - Phân lịch",
        "9. Quản lý Nghỉ phép & Miễn trực",
        "10. Quản lý Tiền lương & Phụ cấp",
        "11. Quản lý Chứng chỉ Hành nghề Y",
        "12. Quản lý Đào tạo & Bồi dưỡng CML",
        "13. Đánh giá & Đánh giá An toàn Bệnh viện",
        "14. Thi đua - Khen thưởng & Kỷ luật",
        "15. Quản lý Sức khỏe & Báo hiểm",
        "16. Quản lý Tài sản - Quy trình",
        "17. Báo cáo - Thống kê - CSDL Y tế",
        "18. Quản lý Hệ thống & Phân quyền",
    ],
)

# ---------------------------------------------------------
# 4. ĐIỀU HƯỚNG MÀN HÌNH THEO MENU
# ---------------------------------------------------------
if menu_choice == "1. Dashboard Tổng quan":
    render_dashboard()
elif menu_choice == "2. Danh mục Hệ thống":
    render_category_management()
elif menu_choice == "3. Quản lý Cơ cấu Tổ chức":
    render_organization_management()
else:
    st.title(menu_choice)
    st.info("Chức năng đang được nâng cấp và phát triển.")
