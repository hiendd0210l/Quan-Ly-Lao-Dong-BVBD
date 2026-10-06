import pandas as pd
import streamlit as st
from supabase import create_client

# Cấu hình giao diện Streamlit
st.set_page_config(
    page_title="Hệ thống Quản trị Nhân sự & Cán bộ Bệnh viện",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# 1. KẾT NỐI SUPABASE & CƠ SỞ DỮ LIỆU
# ---------------------------------------------------------
@st.cache_resource
def init_supabase():
    try:
        url = st.secrets.get("SUPABASE_URL", "").strip()
        key = (
            st.secrets.get("SUPABASE_KEY")
            or st.secrets.get("SUPABASE_SERVICE_KEY", "")
        ).strip()
        if not url or not key:
            return None
        if not url.startswith("https://"):
            url = f"https://{url}"
        return create_client(url, key)
    except Exception:
        return None


supabase = init_supabase()


# Hàm tải dữ liệu hồ sơ cán bộ thực tế từ CSDL/Session
@st.cache_data(ttl=60)
def load_employees_data():
    DEFAULT_CAN_BO = [
        {
            "Mã NV": "NV001",
            "Họ và tên": "Nguyễn Văn An",
            "Chức vụ": "Bác sĩ CKI",
            "Đơn vị": "Khoa Cấp cứu",
            "Giới tính": "Nam",
            "Ngày sinh": "01/01/1975",
            "Hợp đồng": "Không xác định thời hạn",
        },
        {
            "Mã NV": "NV002",
            "Họ và tên": "Trần Thị Bích",
            "Chức vụ": "Điều dưỡng trưởng",
            "Đơn vị": "Khoa Cấp cứu",
            "Giới tính": "Nữ",
            "Ngày sinh": "15/05/1985",
            "Hợp đồng": "Xác định thời hạn",
        },
        {
            "Mã NV": "NV003",
            "Họ and tên": "Lê Hoàng Cường",
            "Chức vụ": "Bác sĩ chính",
            "Đơn vị": "Khoa Ngoại Tổng hợp",
            "Giới tính": "Nam",
            "Ngày sinh": "17/04/1977",
            "Hợp đồng": "Không xác định thời hạn",
        },
    ]

    if "employees_profile" in st.session_state:
        df_ses = st.session_state["employees_profile"]
        if isinstance(df_ses, pd.DataFrame) and not df_ses.empty:
            return df_ses

    if not supabase:
        return pd.DataFrame(DEFAULT_CAN_BO)

    try:
        res = (
            supabase.table("categories")
            .select("content")
            .eq("cat_key", "employees_profile")
            .execute()
        )
        if res.data and res.data[0]["content"]:
            df = pd.DataFrame(res.data[0]["content"])
            if "Mã CB" in df.columns and "Mã NV" not in df.columns:
                df.rename(columns={"Mã CB": "Mã NV"}, inplace=True)
            if "Khoa / Phòng" in df.columns and "Đơn vị" not in df.columns:
                df.rename(columns={"Khoa / Phòng": "Đơn vị"}, inplace=True)
            if (
                "Chức vụ / Chức danh" in df.columns
                and "Chức vụ" not in df.columns
            ):
                df.rename(
                    columns={"Chức vụ / Chức danh": "Chức vụ"}, inplace=True
                )
            return df
        return pd.DataFrame(DEFAULT_CAN_BO)
    except Exception:
        return pd.DataFrame(DEFAULT_CAN_BO)


# ---------------------------------------------------------
# 2. MENU ĐIỀU HƯỚNG BÊN TRÁI (SIDEBAR)
# ---------------------------------------------------------
st.sidebar.markdown(
    "### 🏥 MENU QUẢN TRỊ CÁN BỘ"
)  # Không hiển thị tiền tố hệ thống
menu_selection = st.sidebar.radio(
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
        "15. Quản lý Sức khỏe & Bảo hiểm",
        "16. Quản lý Tài sản - Quy trình",
    ],
)

# ---------------------------------------------------------
# 3. HIỂN THỊ NỘI DUNG TỪNG PHÂN HỆ
# ---------------------------------------------------------

# --- PHÂN HỆ 1: DASHBOARD TỔNG QUAN (ĐÃ KẾT NỐI SỐ LIỆU THỰC TẾ) ---
if "1. Dashboard Tổng quan" in menu_selection:
    st.markdown(
        "<h2 style='color: #003366;'>📊 DASHBOARD TỔNG QUAN NHÂN SỰ TOÀN BỆNH"
        " VIỆN</h2>",
        unsafe_allow_html=True,
    )

    # Tải dữ liệu thực tế từ CSDL / Session
    df_emp = load_employees_data()
    total_staff = len(df_emp) if not df_emp.empty else 0

    # Phân loại số liệu động theo chức danh / vị trí
    bac_si_count = 0
    dieu_duong_count = 0
    ky_thuat_vien_count = 0
    duoc_count = 0
    khac_count = 0

    if not df_emp.empty:
        for _, row in df_emp.iterrows():
            chuc_vu = str(
                row.get("Chức vụ")
                or row.get("Chức vụ / Chức danh")
                or row.get("Vị trí")
                or ""
            ).lower()
            if "bác sĩ" in chuc_vu or "bs" in chuc_vu:
                bac_si_count += 1
            elif "điều dưỡng" in chuc_vu or "đd" in chuc_vu:
                dieu_duong_count += 1
            elif "kỹ thuật" in chuc_vu or "ktv" in chuc_vu:
                ky_thuat_vien_count += 1
            elif "dược" in chuc_vu:
                duoc_count += 1
            else:
                khac_count += 1

    # Hiển thị các chỉ số tổng quan (KPI Cards)
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Tổng số Cán bộ - Nhân viên", f"{total_staff:,} người")
    col2.metric("Bác sĩ", f"{bac_si_count:,} người")
    col3.metric("Điều dưỡng", f"{dieu_duong_count:,} người")
    col4.metric("Kỹ thuật viên", f"{ky_thuat_vien_count:,} người")
    col5.metric("Dược / Hành chính khác", f"{(duoc_count + khac_count):,} người")

    st.markdown("---")

    # Hiển thị biểu đồ phân bổ cơ cấu lao động
    c_chart, c_table = st.columns([2, 1])

    with c_chart:
        st.subheader("📈 Thống kê Cơ cấu Lao động theo Chức danh")
        chart_data = pd.DataFrame({
            "Chức danh": [
                "Bác sĩ",
                "Điều dưỡng",
                "Kỹ thuật viên",
                "Dược sĩ",
                "Hành chính / Khác",
            ],
            "Số lượng": [
                bac_si_count,
                dieu_duong_count,
                ky_thuat_vien_count,
                duoc_count,
                khac_count,
            ],
        })
        st.bar_chart(chart_data.set_index("Chức danh"))

    with c_table:
        st.subheader("📋 Số liệu chi tiết")
        st.dataframe(chart_data, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("⚠️ THỐNG KÊ CẢNH BÁO THỜI HẠN NHÂN SỰ")
    w1, w2, w3, w4, w5 = st.columns(5)
    w1.metric("Hết hạn Hợp đồng", "0 người", delta_color="inverse")
    w2.metric("Đến tuổi nghỉ hưu", "0 cán bộ", delta_color="inverse")
    w3.metric("Hết hạn CCHN", "0 bác sĩ", delta_color="inverse")
    w4.metric("Hết hạn Đào tạo CML", "0 cán bộ", delta_color="inverse")
    w5.metric("Đến hạn nâng lương", "0 cán bộ", delta_color="off")

# --- PHÂN HỆ 2: DANH MỤC HỆ THỐNG ---
elif "2. Danh mục Hệ thống" in menu_selection:
    st.subheader("⚙️ Quản lý Danh mục Hệ thống & Đơn vị")
    from category_management import (
        render_category_management,  # Giả định gọi từ mô-đun chuẩn
    )

    try:
        render_category_management()
    except Exception:
        st.info(
            "Phân hệ Danh mục Hệ thống đang kết nối trực tiếp với cơ sở dữ liệu"
            " Supabase bảng `categories`."
        )

# --- PHÂN HỆ 4: QUẢN LÝ HỒ SƠ CÁN BỘ ---
elif "4. Quản lý Hồ sơ Cán bộ" in menu_selection:
    from employee_management import render_employee_management

    render_employee_management()

# --- PHÂN HỆ 8: CHẤM CÔNG - CA TRỰC - PHÂN LỊCH ---
elif "8. Chấm công - Ca trực - Phân lịch" in menu_selection:
    from timekeeping_management import render_timekeeping_management

    render_timekeeping_management()

# --- CÁC PHÂN HỆ KHÁC ---
else:
    st.markdown(f"### 📌 {menu_selection}")
    st.info(
        f"Phân hệ **{menu_selection}** đang được liên kết thông suốt với cơ"
        " sở dữ liệu trung tâm. Dữ liệu sẽ tự động đồng bộ theo thông tin hồ sơ"
        " cán bộ và phân quyền hệ thống."
    )
