import streamlit as st

# Thiết lập cấu hình trang Streamlit
st.set_page_config(
    page_title="Hệ thống Quản trị Nhân sự & Cán bộ - Bệnh viện Bưu điện",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# MENU QUẢN TRỊ CÁN BỘ (SIDEBAR)
# ---------------------------------------------------------
st.sidebar.markdown(
    "<h2 style='color: #003366; text-align: center;'>🏥 MENU QUẢN TRỊ CÁN BỘ</h2>",
    unsafe_allow_html=True,
)
st.sidebar.markdown("---")

menu_options = [
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
    "15. Quản lý Sức khỏe & Bảo hiểm",
    "16. Quản lý Tài sản - Quy trình",
]

# Chọn mặc định là Phân hệ 8 (Chấm công)
choice = st.sidebar.radio(
    "Chọn chức năng:",
    menu_options,
    index=7,
)

# ---------------------------------------------------------
# ĐIỀU HƯỚNG PHÂN HỆ
# ---------------------------------------------------------
if choice == "8. Chấm công - Ca trực - Phân lịch":
    try:
        from timekeeping_management import render_timekeeping_management

        render_timekeeping_management()
    except Exception as e:
        st.error(f"❌ Lỗi tải phân hệ Chấm công - Ca trực: {e}")
        st.exception(e)

else:
    st.markdown(
        f"<h3 style='color: #003366;'>📋 {choice}</h3>", unsafe_allow_html=True
    )
    st.info(
        f"Phân hệ **{choice}** đang được phát triển và tích hợp hệ thống. Vui lòng quay lại sau!"
    )
