import pandas as pd
import streamlit as st

try:
    import requests
except ImportError:
    requests = None


def get_supabase_client_info():
    """Lấy thông tin URL và Key từ st.secrets của Streamlit."""
    url = st.secrets.get("SUPABASE_URL", None)
    key = st.secrets.get("SUPABASE_KEY", None)
    return url, key


def fetch_categories_from_supabase():
    """Lấy danh sách danh mục từ Supabase."""
    url, key = get_supabase_client_info()
    fallback_data = [
        {
            "id": 1,
            "Ma_CB": "BS",
            "Ten_Chuc_Danh": "Bác sĩ",
            "Ma_Ngach": "V.08.01.03",
            "Nhom_Nghiep_Vu": "Lâm sàng",
        },
        {
            "id": 2,
            "Ma_CB": "BSCK1",
            "Ten_Chuc_Danh": "Bác sĩ CKI",
            "Ma_Ngach": "V.08.01.02",
            "Nhom_Nghiep_Vu": "Chuyên khoa 1",
        },
        {
            "id": 3,
            "Ma_CB": "DD",
            "Ten_Chuc_Danh": "Điều dưỡng",
            "Ma_Ngach": "V.08.05.12",
            "Nhom_Nghiep_Vu": "Chăm sóc",
        },
    ]

    if not url or not key or requests is None:
        return pd.DataFrame(fallback_data), "local"

    try:
        headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }
        endpoint = f"{url.rstrip('/')}/rest/v1/chuc_danh_ngach?select=*"
        response = requests.get(endpoint, headers=headers, timeout=3)

        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                return pd.DataFrame(data), "supabase"
        return pd.DataFrame(fallback_data), "local"
    except Exception:
        return pd.DataFrame(fallback_data), "local"


def add_category_to_supabase(ma_cb, ten_chuc_danh, ma_ngach, nhom_nv):
    """Thêm mới một bản ghi danh mục lên Supabase."""
    url, key = get_supabase_client_info()
    if not url or not key or requests is None:
        return False, "Chưa cấu hình Supabase Secrets."

    try:
        headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }
        payload = {
            "Ma_CB": ma_cb,
            "Ten_Chuc_Danh": ten_chuc_danh,
            "Ma_Ngach": ma_ngach,
            "Nhom_Nghiep_Vu": nhom_nv,
        }
        endpoint = f"{url.rstrip('/')}/rest/v1/chuc_danh_ngach"
        response = requests.post(
            endpoint, json=payload, headers=headers, timeout=5
        )
        if response.status_code in [200, 201]:
            return True, "Thêm mới thành công!"
        else:
            return (
                False,
                f"Lỗi từ Supabase: {response.status_code} - {response.text}",
            )
    except Exception as e:
        return False, f"Lỗi kết nối: {str(e)}"


def delete_category_from_supabase(record_id):
    """Xóa bản ghi danh mục theo ID trên Supabase."""
    url, key = get_supabase_client_info()
    if not url or not key or requests is None:
        return False, "Chưa cấu hình Supabase Secrets."

    try:
        headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }
        endpoint = f"{url.rstrip('/')}/rest/v1/chuc_danh_ngach?id=eq.{record_id}"
        response = requests.delete(endpoint, headers=headers, timeout=5)
        if response.status_code in [200, 204]:
            return True, "Đã xóa bản ghi thành công!"
        else:
            return False, f"Lỗi xóa: {response.text}"
    except Exception as e:
        return False, f"Lỗi kết nối: {str(e)}"


def render_category_management():
    st.markdown("### 📑 Quản lý Danh mục Hệ thống (Kết nối Supabase / CRUD)")

    df_cat, source_status = fetch_categories_from_supabase()

    if source_status == "supabase":
        st.success(
            "🟢 Đang kết nối trực tiếp với CSDL Supabase (Cho phép Thêm/Xóa"
            " dữ liệu thực tế)."
        )
    else:
        st.warning(
            "⚠️ Đang chạy ở chế độ **Dữ liệu giả lập cục bộ**. Để bật chế độ"
            " thao tác thật, vui lòng cấu hình `SUPABASE_URL` và `SUPABASE_KEY`"
            " trong Streamlit Secrets."
        )

    st.markdown("---")

    # Các Tab nghiệp vụ
    tab1, tab2, tab3 = st.tabs([
        "🏷️ Chức danh & Mã ngạch",
        "➕ Thêm mới danh mục",
        "🗑️ Xóa danh mục",
    ])

    with tab1:
        st.markdown("##### 📋 Danh sách Chức danh & Mã ngạch hiện tại")
        if not df_cat.empty:
            st.dataframe(df_cat, use_container_width=True, hide_index=True)
        else:
            st.info("Chưa có dữ liệu danh mục nào.")

    with tab2:
        st.markdown("##### ➕ Thêm mới bản ghi Chức danh & Mã ngạch")
        with st.form("form_add_category"):
            col1, col2 = st.columns(2)
            with col1:
                in_ma_cb = st.text_input("Mã chức vụ / Cán bộ (Ví dụ: BS, ĐD)")
                in_ten_cd = st.text_input("Tên chức danh (Ví dụ: Bác sĩ)")
            with col2:
                in_ma_ngach = st.text_input(
                    "Mã ngạch (Ví dụ: V.08.01.03)"
                )
                in_nhom_nv = st.text_input(
                    "Nhóm nghiệp vụ (Ví dụ: Lâm sàng)"
                )

            submitted = st.form_submit_button(
                "Lưu bản ghi lên Supabase", type="primary"
            )
            if submitted:
                if not in_ma_cb or not in_ten_cd:
                    st.error("Vui lòng nhập đầy đủ Mã CB và Tên Chức danh!")
                else:
                    if source_status == "supabase":
                        success, msg = add_category_to_supabase(
                            in_ma_cb, in_ten_cd, in_ma_ngach, in_nhom_nv
                        )
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                    else:
                        st.info(
                            "Mô phỏng thêm thành công (Đang ở chế độ cục bộ,"
                            " dữ liệu sẽ reset khi tải lại trang)."
                        )

    with tab3:
        st.markdown("##### 🗑️ Xóa bản ghi danh mục")
        if source_status == "supabase" and not df_cat.empty and "id" in df_cat.columns:
            record_options = {
                f"ID {row['id']} - {row.get('Ten_Chuc_Danh', '')} ({row.get('Ma_CB', '')})": row[
                    "id"
                ]
                for _, row in df_cat.iterrows()
            }
            selected_label = st.selectbox(
                "Chọn bản ghi cần xóa:", list(record_options.keys())
            )
            if st.button("Xóa bản ghi đã chọn", type="primary"):
                rec_id = record_options[selected_label]
                success, msg = delete_category_from_supabase(rec_id)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
        else:
            st.info(
                "Chức năng xóa yêu cầu kết nối thành công với Supabase và bảng"
                " dữ liệu phải có cột định danh `id`."
            )


if __name__ == "__main__":
    render_category_management()
