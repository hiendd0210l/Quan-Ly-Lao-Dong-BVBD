import calendar
from datetime import datetime
import pandas as pd
import streamlit as st

# Thiết lập cấu hình trang Streamlit
st.set_page_config(
    page_title="Hệ thống Quản trị Nhân sự & Cán bộ - Bệnh viện Bưu điện",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# KẾT NỐI SUPABASE AN TOÀN
# ---------------------------------------------------------
try:
    from supabase import create_client
except ImportError:
    create_client = None


@st.cache_resource
def init_supabase():
    if create_client is None:
        return None
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

# ---------------------------------------------------------
# MENU QUẢN TRỊ CÁN BỘ (SIDEBAR)
# ---------------------------------------------------------
st.sidebar.markdown(
    "<h2 style='color: #003366; text-align: center;'>🏥 MENU QUẢN TRỊ CÁN"
    " BỘ</h2>",
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

choice = st.sidebar.radio(
    "Chọn chức năng:",
    menu_options,
    index=0,
)


def load_employees():
    """Hàm tải danh sách cán bộ từ Session State hoặc Supabase"""
    if "employees_profile" in st.session_state:
        df = st.session_state["employees_profile"]
        if isinstance(df, pd.DataFrame) and not df.empty:
            return df
    if supabase:
        try:
            res = (
                supabase.table("categories")
                .select("content")
                .eq("cat_key", "employees_profile")
                .execute()
            )
            if res.data and res.data[0].get("content"):
                df = pd.DataFrame(res.data[0]["content"])
                st.session_state["employees_profile"] = df
                return df
        except Exception:
            pass
    return pd.DataFrame()


# ---------------------------------------------------------
# ĐIỀU HƯỚNG CÁC PHÂN HỆ
# ---------------------------------------------------------

# =========================================================
# 1. DASHBOARD TỔNG QUAN
# =========================================================
if choice == "1. Dashboard Tổng quan":
    loaded = False
    for mod_name in [
        "dashboard_management",
        "dashboard",
        "1_dashboard",
        "dashboard_overview",
    ]:
        try:
            mod = __import__(mod_name)
            if hasattr(mod, "render_dashboard_overview"):
                mod.render_dashboard_overview()
            elif hasattr(mod, "render_dashboard"):
                mod.render_dashboard()
            elif hasattr(mod, "main"):
                mod.main()
            loaded = True
            break
        except ImportError:
            continue
        except Exception as e:
            st.error(f"Lỗi khi tải module {mod_name}: {e}")

    if not loaded:
        st.markdown(
            "<h3 style='color: #003366;'>📊 Dashboard Tổng quan Nhân sự & Bệnh"
            " viện</h3>",
            unsafe_allow_html=True,
        )
        df_emp = load_employees()
        total_emp = len(df_emp) if not df_emp.empty else 0

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Tổng số Cán bộ - NV", f"{total_emp} người")
        col2.metric("Số Đơn vị / Khoa Phòng", "16 Đơn vị")
        col3.metric("Số Ca trực hôm nay", "24 Bác sĩ / ĐD")
        col4.metric("Tỷ lệ đi làm chuẩn", "98.5%")

        st.markdown("---")
        st.subheader("📋 Danh sách Cán bộ Nhân sự Hiện tại")
        if not df_emp.empty:
            st.dataframe(df_emp, use_container_width=True)
        else:
            st.info(
                "Chưa có dữ liệu hồ sơ cán bộ. Vui lòng vào **4. Quản lý Hồ sơ"
                " Cán bộ** để tải lên hoặc cập nhật."
            )

# =========================================================
# 2. DANH MỤC HỆ THỐNG
# =========================================================
elif choice == "2. Danh mục Hệ thống":
    loaded = False
    for mod_name in [
        "categories_management",
        "system_categories",
        "categories",
        "2_categories",
    ]:
        try:
            mod = __import__(mod_name)
            if hasattr(mod, "render_categories_management"):
                mod.render_categories_management()
            elif hasattr(mod, "render_categories"):
                mod.render_categories()
            elif hasattr(mod, "main"):
                mod.main()
            loaded = True
            break
        except ImportError:
            continue
        except Exception as e:
            st.error(f"Lỗi khi tải module {mod_name}: {e}")

    if not loaded:
        st.markdown(
            "<h3 style='color: #003366;'>⚙️ Danh mục Hệ thống</h3>",
            unsafe_allow_html=True,
        )
        if supabase:
            try:
                res = supabase.table("categories").select("*").execute()
                if res.data:
                    st.success("✅ Đã kết nối CSDL Supabase - Danh mục hệ thống")
                    df_cat = pd.DataFrame(res.data)
                    st.dataframe(df_cat, use_container_width=True)
                else:
                    st.info("Chưa có danh mục nào được khai báo trong CSDL.")
            except Exception as e:
                st.error(f"Lỗi đọc danh mục từ CSDL: {e}")
        else:
            st.info(
                "Quản lý các danh mục: Chức vụ, Đơn vị khoa phòng, Trình độ,"
                " Ngạch bậc lương."
            )

# =========================================================
# 3. QUẢN LÝ CƠ CẤU TỔ CHỨC
# =========================================================
elif choice == "3. Quản lý Cơ cấu Tổ chức":
    loaded = False
    for mod_name in [
        "organization_management",
        "organization",
        "org_structure",
        "3_organization",
    ]:
        try:
            mod = __import__(mod_name)
            if hasattr(mod, "render_organization_management"):
                mod.render_organization_management()
            elif hasattr(mod, "render_organization"):
                mod.render_organization()
            elif hasattr(mod, "main"):
                mod.main()
            loaded = True
            break
        except ImportError:
            continue
        except Exception as e:
            st.error(f"Lỗi khi tải module {mod_name}: {e}")

    if not loaded:
        st.markdown(
            "<h3 style='color: #003366;'>🏢 Quản lý Cơ cấu Tổ chức Bệnh"
            " viện</h3>",
            unsafe_allow_html=True,
        )
        st.info(
            "Phân hệ quản lý Sơ đồ tổ chức, Danh sách Khoa / Phòng / Trung tâm"
            " / Ban Giám đốc."
        )

# =========================================================
# 4. QUẢN LÝ HỒ SƠ CÁN BỘ
# =========================================================
elif choice == "4. Quản lý Hồ sơ Cán bộ":
    loaded = False
    for mod_name in [
        "employees_management",
        "employee_profile",
        "employee_management",
        "4_employees",
        "employees_profile",
    ]:
        try:
            mod = __import__(mod_name)
            if hasattr(mod, "render_employees_management"):
                mod.render_employees_management()
            elif hasattr(mod, "render_employee_profile"):
                mod.render_employee_profile()
            elif hasattr(mod, "render_employees"):
                mod.render_employees()
            elif hasattr(mod, "main"):
                mod.main()
            loaded = True
            break
        except ImportError:
            continue
        except Exception as e:
            st.error(f"Lỗi khi tải module {mod_name}: {e}")

    if not loaded:
        st.markdown(
            "<h3 style='color: #003366;'>👥 Quản lý Hồ sơ Cán bộ - Nhân"
            " sự</h3>",
            unsafe_allow_html=True,
        )
        df_emp = load_employees()
        if not df_emp.empty:
            search_kw = st.text_input(
                "🔍 Tìm kiếm nhanh cán bộ (Họ tên, Mã NV, Chức vụ, Khoa"
                " phòng):"
            )
            if search_kw:
                mask = df_emp.astype(str).apply(
                    lambda x: x.str.contains(search_kw, case=False)
                ).any(axis=1)
                df_filtered = df_emp[mask]
                st.dataframe(df_filtered, use_container_width=True)
            else:
                st.dataframe(df_emp, use_container_width=True)
        else:
            st.info("Chưa tìm thấy dữ liệu Hồ sơ cán bộ.")

# =========================================================
# 8. CHẤM CÔNG - CA TRỰC - PHÂN LỊCH
# =========================================================
elif choice == "8. Chấm công - Ca ứng - Phân lịch" or "8." in choice:
    try:
        from timekeeping_management import render_timekeeping_management

        render_timekeeping_management()
    except Exception as e:
        st.error(f"❌ Lỗi tải phân hệ Chấm công - Ca trực: {e}")
        st.exception(e)

# =========================================================
# CÁC PHÂN HỆ KHÁC
# =========================================================
else:
    st.markdown(
        f"<h3 style='color: #003366;'>📋 {choice}</h3>", unsafe_allow_html=True
    )
    st.info(
        f"Phân hệ **{choice}** đang được tích hợp hệ thống. Vui lòng chọn Menu"
        " 1, 2, 3, 4 hoặc 8."
    )
