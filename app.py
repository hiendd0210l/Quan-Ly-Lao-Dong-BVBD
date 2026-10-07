import pandas as pd
import plotly.express as px
import streamlit as st
from category_management import render_category_management
from employee_management import render_employee_management
from organization_management import render_organization_management
from timekeeping_management import render_timekeeping_management

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
    # --- Đọc dữ liệu thực tế từ Session State ---
    df_emp = pd.DataFrame()
    if "employees_profile" in st.session_state:
        df_ses = st.session_state["employees_profile"]
        if isinstance(df_ses, pd.DataFrame) and not df_ses.empty:
            df_emp = df_ses.copy()

    total_emp = len(df_emp) if not df_emp.empty else 1250

    # --- LOGO VÀ TIÊU ĐỀ BỆNH VIỆN BƯU ĐIỆN ---
    col_logo, col_header = st.columns([2, 5])
    with col_logo:
        try:
            st.image("logo.png", width=300)
        except Exception:
            st.markdown("🏥")
    with col_header:
        st.markdown(
            "<h1 style='margin-bottom: 0px; color: #0056b3; font-size: 36px;'>BỆNH VIỆN BƯU ĐIỆN</h1>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<h3 style='color: #555; margin-top: 5px; font-size: 22px;'>HỆ THỐNG QUẢN TRỊ NHÂN SỰ & CÁN BỘ</h3>",
            unsafe_allow_html=True,
        )
    st.markdown("---")

    # --- 1. THỐNG KÊ CƠ CẤU LAO ĐỘNG THỰC TẾ ---
    st.subheader("📊 THỐNG KÊ CƠ CẤU LAO ĐỘNG TOÀN BỆNH VIỆN")
    
    if not df_emp.empty:
        # Tự động gom nhóm theo cột Chức vụ / Chức danh có sẵn trong file upload
        pos_col = None
        for col in df_emp.columns:
            if any(k in str(col).lower() for k in ["chức vụ", "chức danh", "vị trí"]):
                pos_col = col
                break
        
        if pos_col:
            df_chuc_danh = df_emp[pos_col].value_counts().reset_index()
            df_chuc_danh.columns = ["Chức danh công tác", "Số lượng"]
            df_chuc_danh["Tỷ lệ (%)"] = (df_chuc_danh["Số lượng"] / total_emp) * 100
        else:
            df_chuc_danh = pd.DataFrame({
                "Chức danh công tác": ["Toàn bộ nhân sự"],
                "Số lượng": [total_emp],
                "Tỷ lệ (%)": [100.0]
            })
    else:
        # Dữ liệu mặc định nếu chưa upload
        df_chuc_danh = pd.DataFrame({
            "Chức danh công tác": ["Bác sĩ", "Điều dưỡng", "Kỹ thuật viên", "Dược sĩ", "Hành chính / Khác"],
            "Số lượng": [485, 518, 158, 43, 46],
            "Tỷ lệ (%)": [38.8, 41.4, 12.7, 3.4, 3.7],
        })

    col_chart, col_table = st.columns([3, 2])
    with col_chart:
        fig_bar = px.bar(
            df_chuc_danh,
            x="Chức danh công tác",
            y="Số lượng",
            text="Số lượng",
            color="Chức danh công tác",
            labels={"Số lượng": "Số lượng (người)", "Chức danh công tác": "Chức danh công tác"},
        )
        fig_bar.update_traces(textposition="outside", texttemplate="%{text} người", cliponaxis=False)
        fig_bar.update_layout(
            title="<b>Tỷ lệ phân bổ Nhân sự thực tế</b>",
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
                "Số lượng": st.column_config.NumberColumn("Số lượng (Người)", format="%d"),
                "Tỷ lệ (%)": st.column_config.NumberColumn("Tỷ lệ (%)", format="%.1f%%"),
            },
        )
        st.write("")
        st.metric("Tổng số Cán bộ - Nhân viên", f"{total_emp:,} người")

    # (Phần cảnh báo thời hạn bên dưới giữ nguyên hoặc liên kết dữ liệu tương tự)

# ---------------------------------------------------------
# 3. THANH MENU BÊN TRÁI (SIDEBAR)
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
        "9. 🏖️️ Quản lý Nghỉ phép & Miễn trực",
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
# 4. ĐIỀU HƯỚNG MÀN HÌNH THEO MENU AN TOÀN
# ---------------------------------------------------------
if "Dashboard Tổng quan" in menu_choice:
    render_dashboard()
elif "Danh mục Hệ thống" in menu_choice:
    render_category_management()
elif "Quản lý Cơ cấu Tổ chức" in menu_choice:
    render_organization_management()
elif "Quản lý Hồ sơ Cán bộ" in menu_choice:
    render_employee_management()
elif "Chấm công" in menu_choice:
    render_timekeeping_management()
else:
    st.title(menu_choice)
    st.info("Chức năng đang được nâng cấp và phát triển.")
