import io
import pandas as pd
import streamlit as st
from supabase import create_client


# ---------------------------------------------------------
# 1. KẾT NỐI SUPABASE
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


# ---------------------------------------------------------
# 2. HÀM TRUY VẤN VÀ LỌC DANH MỤC TỪ CSDL
# ---------------------------------------------------------
def load_all_categories(supabase_client):
    """Tải toàn bộ danh mục thực tế từ CSDL, lọc bỏ DUY NHẤT các Bảng chấm công theo tháng (ví dụ: tk_2026_09)"""
    default_cats = {
        "don_vi": "Đơn vị / Khoa / Phòng",
        "chuc_vu": "Chức vụ / Chức danh",
        "trinh_do": "Trình độ chuyên môn",
        "ngach_luong": "Ngạch công chức",
        "loai_hd": "Loại Hợp đồng Lao động",
        "phu_cap": "Phụ cấp / Lương",
        "tk_rules": "Quy ước Ký hiệu Chấm công",
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

                # Lọc bỏ DUY NHẤT các bảng chấm công tháng phát sinh tự động (như tk_2026_09)
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


# ---------------------------------------------------------
# 3. GIAO DIỆN QUẢN LÝ DANH MỤC HỆ THỐNG ĐẦY ĐỦ CÔNG CỤ
# ---------------------------------------------------------
def render_category_management():
    st.markdown(
        "<h3 style='color: #003366;'>⚙️ Quản lý Danh mục Hệ thống & Đơn"
        " vị</h3>",
        unsafe_allow_html=True,
    )

    supabase = init_supabase()

    # Tải danh sách danh mục thực tế
    cat_dict = load_all_categories(supabase)

    # --- KHU VỰC 1: QUẢN LÝ DANH SÁCH DANH MỤC (THÊM / XÓA / SỬA TÊN TAB) ---
    with st.expander(
        "➕ QUẢN LÝ DANH SÁCH DANH MỤC (THÊM / XÓA / SỬA TÊN TAB DANH MỤC)",
        expanded=False,
    ):
        tab_add, tab_edit, tab_del = st.tabs([
            "➕ Thêm Danh mục mới",
            "✏️ Đổi tên Danh mục",
            "🗑️ Xóa Danh mục",
        ])

        with tab_add:
            with st.form("form_add_category", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    new_key = st.text_input(
                        "Mã danh mục (Viết liền không dấu, ví dụ: trinh_do):"
                    )
                with c2:
                    new_title = st.text_input(
                        "Tên hiển thị Danh mục (Ví dụ: Trình độ chuyên môn):"
                    )
                btn_add_cat = st.form_submit_button("Thêm Danh mục vào Hệ thống")

                if btn_add_cat:
                    if not new_key or not new_title:
                        st.error("⚠️️ Vui lòng nhập đầy đủ Mã và Tên danh mục!")
                    else:
                        clean_key = new_key.strip().lower()
                        if supabase:
                            supabase.table("categories").upsert({
                                "cat_key": clean_key,
                                "title": new_title.strip(),
                                "content": [],
                            }).execute()
                        st.toast(
                            f"✅ Đã thêm danh mục '{new_title}'!", icon="🎉"
                        )
                        st.success(f"✅ Đã tạo mới danh mục '{new_title}'!")
                        st.rerun()

        with tab_edit:
            selected_edit_key = st.selectbox(
                "Chọn danh mục cần đổi tên:",
                options=list(cat_dict.keys()),
                format_func=lambda x: cat_dict[x],
                key="sel_cat_to_rename",
            )
            new_renamed_title = st.text_input(
                "Tên hiển thị mới:", value=cat_dict[selected_edit_key]
            )
            if st.button("✏️ Cập nhật Tên Danh mục"):
                if new_renamed_title and supabase:
                    # Lấy content cũ
                    res = (
                        supabase.table("categories")
                        .select("content")
                        .eq("cat_key", selected_edit_key)
                        .execute()
                    )
                    old_content = (
                        res.data[0]["content"]
                        if res.data and res.data[0].get("content")
                        else []
                    )

                    supabase.table("categories").upsert({
                        "cat_key": selected_edit_key,
                        "title": new_renamed_title.strip(),
                        "content": old_content,
                    }).execute()
                    st.toast("✅ Đã cập nhật tên danh mục!", icon="✏️")
                    st.rerun()

        with tab_del:
            selected_del_key = st.selectbox(
                "Chọn danh mục muốn xóa khỏi hệ thống:",
                options=list(cat_dict.keys()),
                format_func=lambda x: cat_dict[x],
                key="sel_cat_to_delete",
            )
            if st.button("❌ Xóa Danh mục đã chọn", type="primary"):
                if supabase and selected_del_key:
                    supabase.table("categories").delete().eq(
                        "cat_key", selected_del_key
                    ).execute()
                    st.toast("✅ Đã xóa danh mục thành công!", icon="🗑️")
                    st.rerun()

    st.markdown("---")

    # --- KHU VỰC 2: THANH CHỌN DANH MỤC HIỆN TẠI ---
    selected_cat_key = st.radio(
        "Chọn danh mục làm việc:",
        options=list(cat_dict.keys()),
        format_func=lambda x: cat_dict[x],
        horizontal=True,
        key="radio_cat_selection_main",
    )

    current_cat_title = cat_dict[selected_cat_key]

    # Load dữ liệu bảng chi tiết
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
        except Exception:
            pass

    # --- KHU VỰC 3: NHẬP DỮ LIỆU TỪ EXCEL / TẢI FILE EXCEL MẪU ---
    with st.expander("📤 NHẬP DỮ LIỆU TỪ EXCEL / TẢI FILE EXCEL MẪU"):
        col_ex1, col_ex2 = st.columns(2)
        with col_ex1:
            # Tạo file mẫu
            out_sample = io.BytesIO()
            with pd.ExcelWriter(out_sample, engine="openpyxl") as writer:
                sample_cols = (
                    df_cat.columns.tolist()
                    if not df_cat.empty
                    else ["Mã", "Tên", "Ghi chú"]
                )
                pd.DataFrame(columns=sample_cols).to_excel(
                    writer, index=False, sheet_name="DanhMuc"
                )
            out_sample.seek(0)
            st.download_button(
                label=f"📥 Tải File Mẫu Excel ({current_cat_title})",
                data=out_sample,
                file_name=f"Mau_Danh_Muc_{selected_cat_key}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        with col_ex2:
            up_cat_excel = st.file_uploader(
                f"Tải lên file Excel cho {current_cat_title}:",
                type=["xlsx", "xls"],
                key=f"up_ex_{selected_cat_key}",
            )
            if up_cat_excel:
                try:
                    df_up = pd.read_excel(up_cat_excel).fillna("").astype(str)
                    if supabase:
                        supabase.table("categories").upsert({
                            "cat_key": selected_cat_key,
                            "title": current_cat_title,
                            "content": df_up.to_dict(orient="records"),
                        }).execute()
                    st.toast("✅ Tải dữ liệu Excel thành công!", icon="🎉")
                    st.success("✅ Đã cập nhật bảng danh mục từ tệp Excel!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Lỗi đọc file Excel: {e}")

    # --- KHU VỰC 4: QUẢN LÝ CỘT TIÊU ĐỀ HỒ SƠ (THÊM / XÓA CỘT) ---
    with st.expander("🛠️ QUẢN LÝ CỘT TIÊU ĐỀ (THÊM / XÓA CỘT)"):
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            new_col_name = st.text_input(
                "Tên cột tiêu đề mới:", key="input_new_col_name"
            )
            if st.button("➕ Thêm cột vào Bảng"):
                if new_col_name:
                    if df_cat.empty:
                        df_cat = pd.DataFrame(columns=[new_col_name.strip()])
                    else:
                        df_cat[new_col_name.strip()] = ""
                    if supabase:
                        supabase.table("categories").upsert({
                            "cat_key": selected_cat_key,
                            "title": current_cat_title,
                            "content": df_cat.to_dict(orient="records"),
                        }).execute()
                    st.toast(
                        f"✅ Đã thêm cột '{new_col_name}' thành công!", icon="➕"
                    )
                    st.rerun()

        with col_c2:
            if not df_cat.empty:
                del_col_name = st.selectbox(
                    "Chọn cột cần xóa:",
                    options=df_cat.columns.tolist(),
                    key="sel_col_to_del",
                )
                if st.button("❌ Xóa cột đã chọn"):
                    df_cat.drop(columns=[del_col_name], inplace=True)
                    if supabase:
                        supabase.table("categories").upsert({
                            "cat_key": selected_cat_key,
                            "title": current_cat_title,
                            "content": df_cat.to_dict(orient="records"),
                        }).execute()
                    st.toast(
                        f"✅ Đã xóa cột '{del_col_name}' thành công!", icon="🗑️"
                    )
                    st.rerun()

    st.markdown("---")
    st.write(f"📋 **Chi tiết dữ liệu: {current_cat_title}**")

    # --- KHU VỰC 5: BẢNG DỮ LIỆU TƯƠNG TÁC (DATA EDITOR) ---
    edited_df = st.data_editor(
        df_cat,
        use_container_width=True,
        num_rows="dynamic",
        key=f"editor_cat_main_{selected_cat_key}",
    )

    if st.button(f"💾 Lưu cập nhật {current_cat_title}", type="primary"):
        clean_edited = edited_df.fillna("").astype(str)
        if supabase:
            try:
                supabase.table("categories").upsert({
                    "cat_key": selected_cat_key,
                    "title": current_cat_title,
                    "content": clean_edited.to_dict(orient="records"),
                }).execute()
                st.toast(
                    f"✅ Đã lưu thành công dữ liệu {current_cat_title}!",
                    icon="💾",
                )
                st.success(
                    f"✅ Đã lưu dữ liệu {current_cat_title} vào CSDL vĩnh viễn!"
                )
            except Exception as e:
                st.error(f"Lỗi khi lưu CSDL: {e}")
        else:
            st.toast("✅ Đã cập nhật phiên làm việc!", icon="ℹ️")
            st.success("✅ Đã cập nhật tạm thời trong phiên làm việc!")
