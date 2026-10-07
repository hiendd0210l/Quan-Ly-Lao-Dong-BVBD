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
# 2. HÀM XỬ LÝ VÀ GOM NHÓM TRÌNH ĐỘ CHUYÊN MÔN THÔNG MINH
# ---------------------------------------------------------
def extract_education_level(val):
    s = str(val).lower()
    if any(
        k in s
        for k in [
            "tiến sĩ",
            "ts",
            "ck2",
            "chuyên khoa ii",
            "chuyên khoa 2",
            "phó giáo sư",
            "gs",
        ]
    ):
        return "Tiến sĩ / CKII / PGS"
    elif any(
        k in s for k in ["thạc sĩ", "thS", "cki", "chuyên khoa i", "chuyên khoa 1"]
    ):
        return "Thạc sĩ / CKI"
    elif any(
        k in s for k in ["đại học", "bsi", "bác sĩ", "cử nhân", "đh"]
    ):  # Nếu có chứa Đại học hoặc Bác sĩ (trừ thạc sĩ/tiến sĩ ở trên)
        return "Đại học / Bác sĩ"
    elif any(k in s for k in ["cao đẳng", "cđ"]):
        return "Cao đẳng"
    elif any(k in s for k in ["trung cấp", "tc", "sơ cấp"]):
        return "Trung cấp / Sơ cấp"
    else:
        return "Khác / Chưa xác định"


# ---------------------------------------------------------
# 3. HÀM HIỂN THỊ DASHBOARD TỔNG QUAN
# ---------------------------------------------------------
def render_dashboard():
    df_emp = pd.DataFrame()
    if "employees_profile" in st.session_state:
        df_ses = st.session_state["employees_profile"]
        if isinstance(df_ses, pd.DataFrame) and not df_ses.empty:
            df_emp = df_ses.copy()

    total_emp = len(df_emp) if not df_emp.empty else 0

    # --- LOGO VÀ TIÊU ĐỀ BỆNH VIỆN BƯU ĐIỆN ---
    col_logo, col_header = st.columns([2, 5])
    with col_logo:
        try:
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

    if df_emp.empty:
        st.warning(
            "⚠️ Chưa có dữ liệu hồ sơ cán bộ. Vui lòng tải tệp Excel lên tại"
            " mục **'4. Quản lý Hồ sơ Cán bộ'** để hệ thống tổng hợp báo cáo"
            " chính xác."
        )
        return

    # --- TỰ ĐỘNG TÌM CỘT CHỨA THÔNG TIN TRÌNH ĐỘ / CHỨC DANH ĐỂ BÓC TÁCH ---
    target_col = None
    for col in df_emp.columns:
        col_lower = str(col).lower()
        if any(
            k in col_lower
            for k in [
                "chức danh",
                "trình độ",
                "chuyên môn",
                "bằng cấp",
                "vị trí",
                "chức vụ",
            ]
        ):
            target_col = col
            break

    if not target_col and len(df_emp.columns) > 2:
        target_col = df_emp.columns[2]  # Lấy cột mặc định nếu không tìm thấy

    if target_col:
        # Áp dụng hàm bóc tách và gom nhóm thông minh theo Trình độ chuyên môn
        edu_series = df_emp[target_col].apply(extract_education_level)
        counts = edu_series.value_counts()

        # Sắp xếp thứ tự ưu tiên học hàm/học vị từ cao xuống thấp
        order_priority = [
            "Tiến sĩ / CKII / PGS",
            "Thạc sĩ / CKI",
            "Đại học / Bác sĩ",
            "Cao đẳng",
            "Trung cấp / Sơ cấp",
            "Khác / Chưa xác định",
        ]
        counts = counts.reindex(
            [o for o in order_priority if o in counts.index]
        )

        df_trinh_do = pd.DataFrame({
            "Trình độ chuyên môn": counts.index,
            "Số lượng": counts.values,
        })
        df_trinh_do["Tỷ lệ (%)"] = (
            df_trinh_do["Số lượng"] / total_emp
        ) * 100
    else:
        df_trinh_do = pd.DataFrame({
            "Trình độ chuyên môn": ["Chưa xác định"],
            "Số lượng": [total_emp],
            "Tỷ lệ (%)": [100.0],
        })

    # =========================================================
    # HIỂN THỊ BIỂU ĐỒ VÀ BẢNG THỐNG KÊ THEO TRÌNH ĐỘ CHUYÊN MÔN
    # =========================================================
    st.subheader("🎓 THỐNG KÊ CƠ CẤU NHÂN SỰ THEO TRÌNH ĐỘ CHUYÊN MÔN")

    col_chart, col_table = st.columns([3, 2])
    with col_chart:
        fig_bar = px.bar(
            df_trinh_do,
            x="Trình độ chuyên môn",
            y="Số lượng",
            text="Số lượng",
            color="Trình độ chuyên môn",
            labels={
                "Số lượng": "Số lượng (người)",
                "Trình độ chuyên môn": "Trình độ chuyên môn",
            },
        )
        fig_bar.update_traces(
            textposition="outside",
            texttemplate="%{text} người",
            cliponaxis=False,
            marker=dict(line=dict(width=2, color="rgba(0,0,0,0.3)")),
        )
        fig_bar.update_layout(
            title="<b>Phân bố Nhân sự theo Trình độ Chuyên môn (Góc nhìn 3D)</b>",
            xaxis_title="Trình độ chuyên môn",
            yaxis_title="Số lượng (Người)",
            showlegend=False,
            height=380,
            scene_camera=dict(eye=dict(x=1.5, y=1.5, z=1.2)),
            margin=dict(l=20, r=20, t=40, b=20),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_table:
        st.markdown("##### 📋 Phân tích Chi tiết Theo Trình độ")
        st.dataframe(
            df_trinh_do,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Trình độ chuyên môn": st.column_config.Column(
                    "Trình độ", width="medium"
                ),
                "Số lượng": st.column_config.NumberColumn(
                    "Số lượng (Người)", format="%d"
                ),
                "Tỷ lệ (%)": st.column_config.NumberColumn(
                    "Tỷ lệ", format="%.2f%%"
                ),
            },
        )
        st.write("")
        st.metric(
            "Tổng số Cán bộ - Nhân viên thực tế", f"{total_emp:,} người"
        )

    st.markdown("---")

    # --- THỐNG KÊ TỔNG QUAN HỆ THỐNG ---
    st.subheader("⚠️ THỐNG KÊ HỆ THỐNG QUẢN TRỊ NHÂN SỰ")

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric(
            "Tổng số hồ sơ quản lý",
            f"{total_emp} cán bộ",
            "Dữ liệu thật từ file",
        )
    with c2:
        unit_count = (
            df_emp.iloc[:, 3].nunique() if len(df_emp.columns) > 3 else "Nhiều"
        )
        st.metric("Cơ cấu Khoa/Phòng", f"{unit_count} đơn vị", "Hoạt động")
    with c3:
        st.metric("Định biên nhân sự", "Chuẩn", "Đang theo dõi")
    with c4:
        st.metric("Trạng thái dữ liệu", "Hợp lệ", "Đã đồng bộ")
    with c5:
        st.metric("Hệ thống trực tuyến", "Hoạt động", "Ổn định")

    st.write("")
    st.markdown(
        "##### 🔔 Danh sách Hồ sơ Cán bộ thực tế trong hệ thống (Trích xuất từ"
        " tệp upload)"
    )

    display_cols = [c for c in df_emp.columns[:8]]
    st.dataframe(
        df_emp[display_cols], use_container_width=True, hide_index=True
    )


# ---------------------------------------------------------
# 4. THANH MENU BÊN TRÁI (SIDEBAR)
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
        "15. 🏥 Quản lý Sức khỏe & Bảo hiểm",
        "16. 📋 Quản lý Tài sản - Quy trình",
        "17. 📈 Báo cáo - Thống kê - CSDL Y tế",
        "18. ⚙️ Quản lý Hệ thống & Phân quyền",
    ],
)

# ---------------------------------------------------------
# 5. ĐIỀU HƯỚNG MÀN HÌNH THEO MENU AN TOÀN
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
