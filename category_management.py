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


# CẤU HÌNH CỐ ĐỊNH CÁC DANH MỤC HỆ THỐNG CHUẨN (KHÔNG CHO PHÉP TỰ ĐỘNG PHÁT SINH MỤC MỚI)
CORE_SYSTEM_CATEGORIES = {
    "don_vi": "1. Danh mục Đơn vị / Khoa / Phòng",
    "chuc_vu": "2. Danh mục Chức vụ / Chức danh",
    "ngach_luong": "3. Danh mục Ngạch / Bậc lương",
    "loai_hd": "4. Danh mục Loại Hợp đồng Lao động",
    "tk_rules": "5. Quy ước Ký hiệu Chấm công",
    "phu_cap": "6. Danh mục Phụ cấp / Mức hưởng",
}


def render_category_management():
    st.markdown(
        "<h3 style='color: #003366;'>⚙️ Quản lý Danh mục Hệ thống & Đơn"
        " vị</h3>",
        unsafe_allow_html=True,
    )

    supabase = init_supabase()

    # Chỉ cho phép chọn trong danh mục cố định đã được duyệt, lọc bỏ hoàn toàn các bảng chấm công tháng (như tk_2026_09)
    selected_cat_key = st.selectbox(
        "Chọn Danh mục Quản trị Hệ thống:",
        options=list(CORE_SYSTEM_CATEGORIES.keys()),
        format_func=lambda x: CORE_SYSTEM_CATEGORIES[x],
        key="sel_core_category_only",
    )

    cat_title = CORE_SYSTEM_CATEGORIES[selected_cat_key]

    # Load dữ liệu của danh mục được chọn
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
                st.success(f"✅ Đã lưu dữ liệu {cat_title} vào CSDL!")
            except Exception as e:
                st.error(f"Lỗi khi lưu CSDL: {e}")
        else:
            st.success("✅ Đã cập nhật tạm thời trong phiên làm việc!")
