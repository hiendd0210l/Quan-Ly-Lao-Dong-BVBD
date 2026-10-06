import pandas as pd
import streamlit as st
from supabase import create_client


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


def get_all_system_categories(supabase_client):
    """Tải tất cả danh mục từ CSDL, lọc bỏ duy nhất các Bảng chấm công hàng tháng (ví dụ: tk_2026_09)"""
    default_cats = {
        "don_vi": "1. Danh mục Đơn vị / Khoa / Phòng",
        "chuc_vu": "2. Danh mục Chức vụ / Chức danh",
        "ngach_luong": "3. Danh mục Ngạch / Bậc lương",
        "loai_hd": "4. Danh mục Loại Hợp đồng Lao động",
        "tk_rules": "5. Quy ước Ký hiệu Chấm công",
        "phu_cap": "6. Danh mục Phụ cấp / Mức hưởng",
    }

    if not supabase_client:
        return default_cats

    try:
        res = (
            supabase_client.table("categories")
            .select("cat_key, title")
            .execute()
        )
        if res.data:
            cat_dict = {}
            for row in res.data:
                k = str(row.get("cat_key", "")).strip()
                t = str(row.get("title", "")).strip() or k

                # Bỏ qua duy nhất các bảng chấm công tháng phát sinh tự động (như tk_2026_09)
                # Giữ nguyên tk_rules (Quy ước chấm công) và tất cả danh mục quản trị khác
                if k.startswith("tk_20") or k.startswith("tk_19") or (
                    "bảng chấm công tháng" in t.lower() and k != "tk_rules"
                ):
                    continue

                cat_dict[k] = t

            if cat_dict:
                return cat_dict
    except Exception:
        pass

    return default_cats


def render_category_management():
    st.markdown(
        "<h3 style='color: #003366;'>⚙️ Quản lý Danh mục Hệ thống & Đơn"
        " vị</h3>",
        unsafe_allow_html=True,
    )

    supabase = init_supabase()

    # Tải động toàn bộ danh mục thực tế từ CSDL
    categories_dict = get_all_system_categories(supabase)

    selected_cat_key = st.selectbox(
        "Chọn Danh mục Quản trị Hệ thống:",
        options=list(categories_dict.keys()),
        format_func=lambda x: categories_dict[x],
        key="sel_system_category_dynamic",
    )

    cat_title = categories_dict[selected_cat_key]

    # Load dữ liệu bảng chi tiết của danh mục đang chọn
    df_cat = pd.DataFrame()
    if supabase:
        try:
            res = (
                supabase.table("categories")
                .select("content")
                .eq("cat_key", selected_cat_key)
                .execute()
            )
            if res.data and res.data[0].get("content"):
                df_cat = pd.DataFrame(res.data[0]["content"])
        except Exception as e:
            st.error(f"Lỗi truy vấn CSDL: {e}")

    st.markdown("---")
    st.write(f"📋 **Chi tiết dữ liệu: {cat_title}**")

    edited_df = st.data_editor(
        df_cat,
        use_container_width=True,
        num_rows="dynamic",
        key=f"editor_cat_{selected_cat_key}",
    )

    if st.button(f"💾 Lưu cập nhật {cat_title}", type="primary"):
        if supabase:
            try:
                payload = {
                    "cat_key": selected_cat_key,
                    "title": cat_title,
                    "content": edited_df.fillna("").to_dict(orient="records"),
                }
                supabase.table("categories").upsert(payload).execute()
                st.toast(f"✅ Đã lưu thành công {cat_title}!", icon="💾")
                st.success(f"✅ Đã lưu dữ liệu {cat_title} vào CSDL vĩnh viễn!")
            except Exception as e:
                st.error(f"Lỗi khi lưu CSDL: {e}")
        else:
            st.toast("✅ Đã cập nhật phiên làm việc!", icon="ℹ️")
            st.success("✅ Đã cập nhật tạm thời trong phiên làm việc!")
