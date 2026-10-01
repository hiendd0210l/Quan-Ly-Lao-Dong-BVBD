import io
import json
import os
import pandas as pd
import streamlit as st
from supabase import create_client


# ---------------------------------------------------------
# KẾT NỐI SUPABASE AN TOÀN (BẮT LỖI DNS / MẠNG)
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

# ---------------------------------------------------------
# MẪU DỮ LIỆU CHUẨN NGHỊ ĐỊNH 204/2004/NĐ-CP (BẢNG LƯƠNG SỐ 3)
# ---------------------------------------------------------
DF_NGACH_LUONG_ND204 = pd.DataFrame({
    "Mã Ngạch": [
        "1.08.01.01",
        "1.08.01.02",
        "1.08.01.03",
        "1.08.01.12",
        "1.08.01.13",
    ],
    "Tên Ngạch lương": [
        "Bác sĩ cao cấp / Dược sĩ cao cấp (Hạng I)",
        "Bác sĩ chính / Dược sĩ chính (Hạng II)",
        "Bác sĩ / Dược sĩ (Hạng III)",
        "Y sĩ / Điều dưỡng / KTV (Hạng IV)",
        "Dược sĩ trung cấp / Y sĩ trung cấp",
    ],
    "Nhóm ngạch": ["A3.1", "A2.1", "A1", "B", "C1"],
    "Loại ngạch": [
        "Viên chức loại A3",
        "Viên chức loại A2",
        "Viên chức loại A1",
        "Viên chức loại B",
        "Viên chức loại C",
    ],
    "Bậc tối đa": [6, 8, 9, 12, 12],
    "Bậc 1": [6.20, 4.40, 2.34, 1.86, 1.65],
    "Bậc 2": [6.56, 4.74, 2.67, 2.06, 1.80],
    "Bậc 3": [6.92, 5.08, 3.00, 2.26, 1.95],
    "Bậc 4": [7.28, 5.42, 3.33, 2.46, 2.10],
    "Bậc 5": [7.64, 5.76, 3.66, 2.66, 2.25],
    "Bậc 6": [8.00, 6.10, 3.99, 2.86, 2.40],
    "Bậc 7": ["", 6.44, 4.32, 3.06, 2.55],
    "Bậc 8": ["", 6.78, 4.65, 3.26, 2.70],
    "Bậc 9": ["", "", 4.98, 3.46, 2.85],
    "Bậc 10": ["", "", "", 3.66, 3.00],
    "Bậc 11": ["", "", "", 3.86, 3.15],
    "Bậc 12": ["", "", "", 4.06, 3.30],
})

DEFAULT_CATEGORIES = {
    "chuc_danh": {
        "title": "📌 Chức danh & Mã ngạch",
        "df": pd.DataFrame({
            "Mã CĐ": ["BS", "BSCK1", "BSCK2", "ĐĐ", "KTV", "DS"],
            "Tên Chức Danh": [
                "Bác sĩ",
                "Bác sĩ CKI",
                "Bác sĩ CKII",
                "Điều dưỡng",
                "Kỹ thuật viên",
                "Dược sĩ",
            ],
            "Mã Ngạch": [
                "V.08.01.03",
                "V.08.01.02",
                "V.08.01.01",
                "V.08.05.12",
                "V.08.07.23",
                "V.08.08.20",
            ],
            "Ghi chú": [
                "Lâm sàng",
                "Chuyên khoa 1",
                "Chuyên khoa 2",
                "Chăm sóc",
                "Cận lâm sàng",
                "Khoa Dược",
            ],
        }),
    },
    "trinh_do": {
        "title": "🎓 Trình độ chuyên môn",
        "df": pd.DataFrame({
            "Mã TĐ": ["TS", "ThS", "BSCKII", "BSCKI", "CN", "CĐ", "TC"],
            "Tên Trình độ": [
                "Tiến sĩ",
                "Thạc sĩ",
                "Bác sĩ Chuyên khoa II",
                "Bác sĩ Chuyên khoa I",
                "Cử nhân / Đại học",
                "Cao đẳng",
                "Trung cấp",
            ],
            "Ghi chú": [
                "Sau đại học",
                "Sau đại học",
                "Sau đại học",
                "Sau đại học",
                "Đại học",
                "Cao đẳng",
                "Trung cấp",
            ],
        }),
    },
    "loai_hop_dong": {
        "title": "📝 Loại Hợp đồng Lao động",
        "df": pd.DataFrame({
            "Mã HĐ": ["KTH", "12T", "36T", "TV"],
            "Tên Loại Hợp đồng": [
                "HĐLĐ Không xác định thời hạn",
                "HĐLĐ Xác định thời hạn 12 tháng",
                "HĐLĐ Xác định thời hạn 36 tháng",
                "Hợp đồng Thử việc",
            ],
            "Thời hạn (Tháng)": ["Vô thời hạn", "12", "36", "02"],
            "Ghi chú": ["Chính thức", "Chính thức", "Chính thức", "Thử việc"],
        }),
    },
    "phu_cap": {
        "title": "💰 Danh mục Phụ cấp / Lương",
        "df": pd.DataFrame({
            "Mã PC": ["PC_CV", "PC_UD", "PC_TN", "PC_DH"],
            "Tên Loại Phụ cấp": [
                "Phụ cấp Chức vụ",
                "Phụ cấp Ưu đãi nghề Y tế",
                "Phụ cấp Thâm niên",
                "Phụ cấp Độc hại / Nguy hiểm",
            ],
            "Tỷ lệ / Mức hưởng": ["0.4", "40%", "10%", "0.2"],
            "Ghi chú": [
                "Trưởng/Phó khoa",
                "Cán bộ y tế",
                "Trên 5 năm",
                "Môi trường độc hại",
            ],
        }),
    },
    "ngach_luong": {
        "title": "🏛️ Ngạch bậc lương cơ bản (NĐ 204/2004)",
        "df": DF_NGACH_LUONG_ND204,
    },
}


# ---------------------------------------------------------
# HÀM XỬ LÝ DỮ LIỆU CSDL SUPABASE (THÊM TRY/EXCEPT AN TOÀN)
# ---------------------------------------------------------
def load_category_list():
    default_list = {
        cat_key: item["title"] for cat_key, item in DEFAULT_CATEGORIES.items()
    }
    if not supabase:
        return default_list

    try:
        res = supabase.table("categories").select("cat_key, title").execute()
        data = res.data
        if data and len(data) > 0:
            return {item["cat_key"]: item["title"] for item in data}
        else:
            for k, v in DEFAULT_CATEGORIES.items():
                save_category_data(k, v["df"], v["title"])
            return default_list
    except Exception:
        return default_list


def load_category_data(cat_key, default_df):
    if not supabase:
        return default_df

    try:
        res = (
            supabase.table("categories")
            .select("content")
            .eq("cat_key", cat_key)
            .execute()
        )
        data = res.data
        if data and len(data) > 0 and data[0]["content"]:
            return pd.DataFrame(data[0]["content"])
    except Exception:
        pass
    return default_df


def save_category_data(cat_key, df, title=None):
    if not supabase:
        st.warning(
            "⚠️ Chưa kết nối Supabase, dữ liệu tạm lưu trên bộ nhớ phiên."
        )
        return False

    try:
        clean_df = df.fillna("")
        records = clean_df.to_dict(orient="records")
        payload = {"cat_key": cat_key, "content": records}
        if title:
            payload["title"] = title

        supabase.table("categories").upsert(payload).execute()
        return True
    except Exception as e:
        st.error(f"Lỗi khi lưu vào Supabase: {e}")
        return False


def delete_category_from_db(cat_key):
    if supabase:
        try:
            supabase.table("categories").delete().eq("cat_key", cat_key).execute()
            return True
        except Exception as e:
            st.error(f"Lỗi khi xóa danh mục: {e}")
    return False


# ---------------------------------------------------------
# HÀM TẠO FILE EXCEL VÀ CẤU HÌNH CỘT
# ---------------------------------------------------------
def convert_df_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    output.seek(0)
    return output


def build_safe_column_config(df):
    column_config = {}
    if df is None or df.empty:
        return column_config

    for col in df.columns:
        col_str_series = df[col].fillna("").astype(str)
        max_data_len = (
            col_str_series.str.len().max() if not col_str_series.empty else 0
        )
        max_len = max(int(max_data_len or 0), len(str(col)))

        if max_len <= 10:
            width_type = "small"
        elif max_len <= 25:
            width_type = "medium"
        else:
            width_type = "large"

        column_config[str(col)] = st.column_config.Column(
            label=str(col), width=width_type
        )
    return column_config


# ---------------------------------------------------------
# GIAO DIỆN QUẢN LÝ DANH MỤC
# ---------------------------------------------------------
def render_single_category(cat_key, cat_title):
    session_key = f"df_{cat_key}"
    version_key = f"ver_{cat_key}"

    default_df = pd.DataFrame(
        {"Mã": ["M01"], "Tên danh mục": ["Mẫu 01"], "Ghi chú": [""]}
    )
    if cat_key in DEFAULT_CATEGORIES:
        default_df = DEFAULT_CATEGORIES[cat_key]["df"]

    if session_key not in st.session_state:
        st.session_state[session_key] = load_category_data(
            cat_key, default_df
        )

    if version_key not in st.session_state:
        st.session_state[version_key] = 0

    # 1. TẢI FILE EXCEL MẪU & NHẬP DỮ LIỆU
    with st.expander(
        "📊 NHẬP DỮ LIỆU TỪ EXCEL / TẢI FILE EXCEL MẪU", expanded=False
    ):
        col_ex1, col_ex2 = st.columns([1, 2])

        with col_ex1:
            st.markdown("**1. Tải file Excel mẫu (.xlsx):**")
            if cat_key == "ngach_luong":
                sample_excel_df = DF_NGACH_LUONG_ND204
            else:
                sample_excel_df = st.session_state[session_key]

            excel_data = convert_df_to_excel(sample_excel_df)
            st.download_button(
                label="📥 Tải xuống File mẫu (.xlsx)",
                data=excel_data,
                file_name=(
                    f"Mau_BangLuong_ND204_{cat_key}.xlsx"
                    if cat_key == "ngach_luong"
                    else f"Mau_{cat_key}.xlsx"
                ),
                mime=(
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                ),
                key=f"btn_dl_{cat_key}",
            )

        with col_ex2:
            st.markdown("**2. Tải lên file Excel/CSV để cập nhật:**")
            uploaded_file = st.file_uploader(
                "Chọn file từ máy tính:",
                type=["xlsx", "xls", "csv"],
                key=f"upload_{cat_key}_{st.session_state[version_key]}",
            )

        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith(".csv"):
                    df_excel = pd.read_csv(uploaded_file)
                else:
                    df_excel = pd.read_excel(uploaded_file)

                df_excel = df_excel.fillna("")
                st.write("📌 **Xem trước dữ liệu tải lên:**")
                st.dataframe(df_excel.head(5), use_container_width=True)

                col_b1, col_b2 = st.columns(2)
                with col_b1:
                    if st.button(
                        "➕ Nhập nối tiếp vào bảng hiện tại",
                        key=f"btn_append_{cat_key}",
                    ):
                        new_df = pd.concat(
                            [st.session_state[session_key], df_excel],
                            ignore_index=True,
                        ).drop_duplicates()
                        st.session_state[session_key] = new_df
                        save_category_data(cat_key, new_df, cat_title)
                        st.session_state[version_key] += 1
                        st.success("✅ Đã cập nhật nối tiếp thành công!")
                        st.rerun()

                with col_b2:
                    if st.button(
                        "🔄 Ghi đè toàn bộ dữ liệu cũ",
                        type="primary",
                        key=f"btn_overwrite_{cat_key}",
                    ):
                        st.session_state[session_key] = df_excel
                        save_category_data(cat_key, df_excel, cat_title)
                        st.session_state[version_key] += 1
                        st.success("✅ Đã ghi đè dữ liệu thành công!")
                        st.rerun()
            except Exception as e:
                st.error(f"Lỗi đọc file: {e}")

    # 2. QUẢN LÝ CỘT TIÊU ĐỀ
    with st.expander(
        "🛠️ QUẢN LÝ CỘT TIÊU ĐỀ CỦA BẢNG (THÊM / SỬA / XÓA CỘT)", expanded=False
    ):
        c_add, c_edit, c_del = st.columns(3)

        with c_add:
            st.markdown("**➕ Thêm cột mới**")
            new_col = st.text_input(
                "Nhập tên cột mới:", key=f"txt_add_col_{cat_key}"
            )
            if st.button("Thêm cột", key=f"btn_add_col_{cat_key}"):
                if (
                    new_col
                    and new_col not in st.session_state[session_key].columns
                ):
                    st.session_state[session_key][new_col] = ""
                    save_category_data(
                        cat_key, st.session_state[session_key], cat_title
                    )
                    st.session_state[version_key] += 1
                    st.success(f"Đã thêm cột '{new_col}'")
                    st.rerun()

        with c_edit:
            st.markdown("**✏️ Đổi tên cột tiêu đề**")
            cols = list(st.session_state[session_key].columns)
            col_to_rename = st.selectbox(
                "Chọn cột cần đổi:", cols, key=f"sel_rename_{cat_key}"
            )
            renamed_name = st.text_input(
                "Tên mới:", key=f"txt_rename_{cat_key}"
            )
            if st.button("Đổi tên", key=f"btn_rename_{cat_key}"):
                if renamed_name and col_to_rename:
                    st.session_state[session_key] = st.session_state[
                        session_key
                    ].rename(columns={col_to_rename: renamed_name})
                    save_category_data(
                        cat_key, st.session_state[session_key], cat_title
                    )
                    st.session_state[version_key] += 1
                    st.success("Đã đổi tên cột thành công!")
                    st.rerun()

        with c_del:
            st.markdown("**🗑️ Xóa cột khỏi bảng**")
            cols = list(st.session_state[session_key].columns)
            col_to_del = st.selectbox(
                "Chọn cột cần xóa:", cols, key=f"sel_del_{cat_key}"
            )
            if st.button(
                "Xóa cột", type="primary", key=f"btn_del_col_{cat_key}"
            ):
                if col_to_del in st.session_state[session_key].columns:
                    st.session_state[session_key] = st.session_state[
                        session_key
                    ].drop(columns=[col_to_del])
                    save_category_data(
                        cat_key, st.session_state[session_key], cat_title
                    )
                    st.session_state[version_key] += 1
                    st.success(f"Đã xóa cột '{col_to_del}'")
                    st.rerun()

    # 3. QUẢN LÝ XÓA HÀNG
    with st.expander("🗑️ XÓA HÀNG TRONG BẢNG DANH MỤC", expanded=False):
        current_df_del = st.session_state[session_key]
        if not current_df_del.empty:
            col_del_row1, col_del_row2 = st.columns([3, 1])

            with col_del_row1:
                first_col = current_df_del.columns[0]
                row_options = [
                    f"Hàng {idx + 1}: {row[first_col]}"
                    for idx, row in current_df_del.iterrows()
                ]
                selected_rows_to_del = st.multiselect(
                    "Chọn các hàng muốn xóa khỏi danh mục:",
                    options=range(len(row_options)),
                    format_func=lambda x: row_options[x],
                    key=f"msel_del_rows_{cat_key}",
                )

            with col_del_row2:
                st.write("")
                st.write("")
                if st.button(
                    "❌ Xóa hàng đã chọn",
                    type="primary",
                    key=f"btn_del_rows_{cat_key}",
                ):
                    if selected_rows_to_del:
                        updated_df = current_df_del.drop(
                            index=selected_rows_to_del
                        ).reset_index(drop=True)
                        st.session_state[session_key] = updated_df
                        save_category_data(cat_key, updated_df, cat_title)
                        st.session_state[version_key] += 1
                        st.success(
                            f"Đã xóa {len(selected_rows_to_del)} hàng!"
                        )
                        st.rerun()
                    else:
                        st.warning("Vui lòng chọn ít nhất 1 hàng để xóa.")
        else:
            st.info("Bảng hiện tại chưa có dữ liệu để xóa.")

    # 4. BẢNG DỮ LIỆU HIỂN THỊ
    st.write("")
    current_df = st.session_state[session_key].fillna("")
    safe_column_config = build_safe_column_config(current_df)

    editor_dynamic_key = (
        f"editor_{cat_key}_v{st.session_state[version_key]}"
    )

    edited_df = st.data_editor(
        current_df,
        use_container_width=False,
        column_config=safe_column_config,
        num_rows="dynamic",
        key=editor_dynamic_key,
    )

    col_save, col_reload, col_reset = st.columns([2, 1, 1])

    with col_save:
        if st.button(
            f"💾 Lưu danh mục {cat_title} vĩnh viễn",
            type="primary",
            key=f"btn_save_{cat_key}",
        ):
            st.session_state[session_key] = edited_df
            if save_category_data(cat_key, edited_df, cat_title):
                st.success(
                    "✅ Dữ liệu danh mục đã được lưu vĩnh viễn vào CSDL"
                    " Supabase!"
                )

    with col_reload:
        if st.button("🔄 Tải lại từ CSDL", key=f"btn_reload_{cat_key}"):
            st.session_state[session_key] = load_category_data(
                cat_key, default_df
            )
            st.session_state[version_key] += 1
            st.success("🔄 Đã tải lại dữ liệu mới nhất!")
            st.rerun()

    # Nút bấm RESET dành riêng cho Ngạch bậc lương NĐ 204
    with col_reset:
        if cat_key == "ngach_luong":
            if st.button("⚡ Reset mẫu NĐ 204", key=f"btn_reset_204_{cat_key}"):
                st.session_state[session_key] = DF_NGACH_LUONG_ND204
                save_category_data(cat_key, DF_NGACH_LUONG_ND204, cat_title)
                st.session_state[version_key] += 1
                st.success("✅ Đã khôi phục bảng lương về chuẩn Nghị định 204!")
                st.rerun()


# ---------------------------------------------------------
# ĐIỀU HƯỚNG CHÍNH
# ---------------------------------------------------------
def render_category_management():
    st.subheader("Chi tiết danh mục hệ thống (Nghị định 204/2004/NĐ-CP)")

    cat_list = load_category_list()

    with st.expander(
        "⚙️ QUẢN LÝ DANH SÁCH DANH MỤC (THÊM / ĐỔI TÊN / XÓA TAB DANH MỤC)",
        expanded=False,
    ):
        col_cat_add, col_cat_edit, col_cat_del = st.columns(3)

        with col_cat_add:
            st.markdown("**➕ Thêm danh mục mới**")
            new_cat_title = st.text_input(
                "Tên danh mục mới:", key="input_new_cat_title"
            )
            if st.button("Tạo Danh mục Mới", key="btn_create_cat"):
                if new_cat_title:
                    import re

                    new_key = re.sub(
                        r"\W+", "_", new_cat_title.lower()
                    ).strip("_")
                    if not new_key:
                        new_key = f"cat_{len(cat_list) + 1}"

                    cat_title_full = f"📁 {new_cat_title}"
                    init_df = pd.DataFrame({
                        "Mã": ["M01"],
                        "Tên " + new_cat_title: ["Nội dung 01"],
                        "Ghi chú": [""],
                    })

                    save_category_data(new_key, init_df, cat_title_full)
                    st.success(f"Đã tạo danh mục '{new_cat_title}'!")
                    st.rerun()

        with col_cat_edit:
            st.markdown("**✏️ Đổi tên danh mục**")
            selected_edit_key = st.selectbox(
                "Chọn danh mục đổi tên:",
                options=list(cat_list.keys()),
                format_func=lambda x: cat_list[x],
                key="sel_edit_cat",
            )
            renamed_cat_title = st.text_input(
                "Tên mới danh mục:", key="input_rename_cat_title"
            )
            if st.button("Cập nhật Tên", key="btn_rename_cat"):
                if renamed_cat_title and selected_edit_key:
                    current_df = load_category_data(
                        selected_edit_key, pd.DataFrame()
                    )
                    save_category_data(
                        selected_edit_key, current_df, renamed_cat_title
                    )
                    st.success("Đã đổi tên danh mục thành công!")
                    st.rerun()

        with col_cat_del:
            st.markdown("**🗑️️ Xóa danh mục**")
            selected_del_key = st.selectbox(
                "Chọn danh mục cần xóa:",
                options=list(cat_list.keys()),
                format_func=lambda x: cat_list[x],
                key="sel_del_cat",
            )
            if st.button(
                "Xóa Danh Mục Này", type="primary", key="btn_delete_cat"
            ):
                if selected_del_key in cat_list:
                    delete_category_from_db(selected_del_key)
                    st.success("Đã xóa danh mục khỏi CSDL Supabase!")
                    st.rerun()

    st.write("")

    if not cat_list:
        st.info("Chưa có danh mục nào. Hãy thêm mới ở trên.")
        return

    cat_keys = list(cat_list.keys())
    cat_titles = [cat_list[k] for k in cat_keys]

    tabs = st.tabs(cat_titles)

    for idx, key in enumerate(cat_keys):
        with tabs[idx]:
            render_single_category(key, cat_list[key])


if __name__ == "__main__":
    render_category_management()
