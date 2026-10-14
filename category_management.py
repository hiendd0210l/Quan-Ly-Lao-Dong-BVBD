import pandas as pd
import streamlit as st

# Thử import thư viện requests để kết nối Supabase
try:
    import requests
except ImportError:
    requests = None


def get_supabase_categories():
    """Hàm kết nối và lấy danh mục từ Supabase, tự động dùng danh mục cục bộ nếu lỗi kết nối."""
    # Khởi tạo danh mục dự phòng mặc định (Fallback Data)
    fallback_data = [
        {
            "Ma_CB": "BS",
            "Ten_Chuc_Danh": "Bác sĩ",
            "Ma_Ngach": "V.08.01.03",
            "Nhom_Nghiep_Vu": "Lâm sàng",
        },
        {
            "Ma_CB": "BSCK1",
            "Ten_Chuc_Danh": "Bác sĩ CKI",
            "Ma_Ngach": "V.08.01.02",
            "Nhom_Nghiep_Vu": "Chuyên khoa 1",
        },
        {
            "Ma_CB": "BSCK2",
            "Ten_Chuc_Danh": "Bác sĩ CKII",
            "Ma_Ngach": "V.08.01.01",
            "Nhom_Nghiep_Vu": "Chuyên khoa 2",
        },
        {
            "Ma_CB": "DD",
            "Ten_Chuc_Danh": "Điều dưỡng",
            "Ma_Ngach": "V.08.05.12",
            "Nhom_Nghiep_Vu": "Chăm sóc",
        },
        {
            "Ma_CB": "KTV",
            "Ten_Chuc_Danh": "Kỹ thuật viên",
            "Ma_Ngach": "V.08.07.15",
            "Nhom_Nghiep_Vu": "Cận lâm sàng",
        },
        {
            "Ma_CB": "DS",
            "Ten_Chuc_Danh": "Dược sĩ",
            "Ma_Ngach": "V.08.08.20",
            "Nhom_Nghiep_Vu": "Khoa Dược",
        },
    ]

    # Kiểm tra biến Secret/Cấu hình Supabase trong st.secrets
    supabase_url = st.secrets.get("SUPABASE_URL", None)
    supabase_key = st.secrets.get("SUPABASE_KEY", None)

    if not supabase_url or not supabase_key or requests is None:
        return pd.DataFrame(fallback_data), "local"

    try:
        # Thử thực hiện kết nối API đến Supabase
        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json",
        }
        endpoint = f"{supabase_url.rstrip('/')}/rest/v1/chuc_danh_ngach?select=*"
        response = requests.get(endpoint, headers=headers, timeout=3)

        if response.status_code == 200:
            data = response.json()
            if data and isinstance(data, list) and len(data) > 0:
                return pd.DataFrame(data), "supabase"

        return pd.DataFrame(fallback_data), "local"
    except Exception:
        # Bắt toàn bộ lỗi kết nối DNS ([Errno -2] Name or service not known) và chuyển về dữ liệu mượt mà
        return pd.DataFrame(fallback_data), "local"


def render_category_management():
    st.markdown(
        "### 📑 Chi tiết danh mục hệ thống (Kết nối CSDL Supabase / Dự phòng)"
    )

    df_cat, source_status = get_supabase_categories()

    if source_status == "supabase":
        st.success("🟢 Đã kết nối thành công với cơ sở dữ liệu Supabase.")
    else:
        st.info(
            "ℹ️ Đang chạy ở chế độ **Dữ liệu danh mục nội bộ** (Chưa thiết"
            " lập hoặc kết nối CSDL Supabase không khả dụng)."
        )

    st.markdown("---")

    # Hiển thị các Tab nghiệp vụ danh mục
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏷️ Chức danh & Mã ngạch",
        "🎓 Trình độ chuyên môn",
        "📜 Loại Hợp đồng Lao động",
        "⚙️ Thiết lập khác",
    ])

    with tab1:
        st.markdown(
            "##### 📋 Danh mục Chức danh & Mã ngạch viên chức Bệnh viện"
        )
        st.dataframe(df_cat, use_container_width=True, hide_index=True)

    with tab2:
        df_degree = pd.DataFrame({
            "Mã TĐ": ["TS", "ThS", "BSCK2", "BSCK1", "ĐH", "CĐ", "TC"],
            "Tên trình độ": [
                "Tiến sĩ",
                "Thạc sĩ",
                "Bác sĩ Chuyên khoa II",
                "Bác sĩ Chuyên khoa I",
                "Đại học",
                "Cao đẳng",
                "Trung cấp",
            ],
        })
        st.dataframe(df_degree, use_container_width=True, hide_index=True)

    with tab3:
        df_contract = pd.DataFrame({
            "Mã HĐ": ["HĐ-KXĐ", "HĐ-12M", "HĐ-36M", "TV"],
            "Loại hợp đồng": [
                "Hợp đồng không xác định thời hạn",
                "Hợp đồng xác định thời hạn 12 tháng",
                "Hợp đồng xác định thời hạn 36 tháng",
                "Thử việc",
            ],
        })
        st.dataframe(df_contract, use_container_width=True, hide_index=True)

    with tab4:
        st.write(
            "Tùy chỉnh thêm/sửa/xóa các danh mục dùng chung cho toàn hệ"
            " thống."
        )


if __name__ == "__main__":
    render_category_management()
