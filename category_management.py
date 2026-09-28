import json
import os
import pandas as pd
import streamlit as st

# Thư mục lưu dữ liệu vĩnh viễn
DATA_DIR = "data_categories"
os.makedirs(DATA_DIR, exist_ok=True)
CONFIG_FILE = os.path.join(DATA_DIR, "category_list.json")

# Danh sách danh mục mặc định ban đầu
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
        "title": "🏛️ Ngạch bậc lương cơ bản",
        "df": pd.DataFrame({
            "Mã Ngạch": ["V.08.01.01", "V.08.01.02", "V.08.01.03", "V.08.05.12"],
            "Tên Ngạch lương": [
                "Bác sĩ cao cấp (Hạng I)",
                "Bác sĩ chính (Hạng II)",
                "Bác sĩ (Hạng III)",
                "Điều dưỡng (Hạng III)",
            ],
            "Hệ số Bậc 1": ["6.20", "4.40", "2.34", "2.34"],
            "Bậc tối đa": ["8", "8", "12", "12"],
        }),
    },
}


def load_category_list():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    initial_list = {
        cat_key: item["title"] for cat_key, item in DEFAULT_CATEGORIES.items()
    }
    save_category_list(initial_list)
    return initial_list


def save_category_list(cat_dict):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cat_dict, f, ensure_ascii=False, indent=2)


def load_category_data(cat_key, default_df):
    file_path = os.path.join(DATA_DIR, f"{cat_key}.csv")
    if os.path.exists(file_path):
        try:
            return pd.read_csv(file_path)
        except Exception:
            pass
    return default_df


def save_category_data(cat_key, df):
    file_path = os.path.join(DATA_DIR, f"{cat_key}.csv")
    try:
        df.to_csv(file_path, index=False, encoding="utf-8-sig")
        return True
    except Exception as e:
        st.error(f"Lỗi khi lưu dữ liệu: {e}")
        return False


# =============================================================================
# HÀM BỎ SỬ DỤNG DẠNG OBJECT JSON NGUY HIỂM - CHỈ CẤU HÌNH KÍCH THƯỚC CHIỀU RỘNG CHUẨN
# =============================================================================
def build_column_auto_size_config(df):
    column_config = {}
    for col in df.columns:
        # Lấy chiều dài chuỗi dài nhất trong cột (kể cả Tiêu đề cột)
        max_len = max(
            df[col].astype(str).map(len).max() if not df.empty else 0, len(str(col))
        )
        # Tính chiều rộng pixel tương ứng
        calc_width = max(120, min(max_len * 11 + 40, 500))
        column_config[col] = st.column_config.TextColumn(
            label=str(col), width=calc_width
        )
    return column_config


# Giao diện quản lý nội dung của từng Danh mục
def render_single_category(cat_key, cat_title):
    session_key = f"df_{cat_key}"
    editor_key = f"editor_{cat_key}"

    default_df = pd.DataFrame(
        {"Mã": ["M01"], "Tên danh mục": ["Mẫu 01"], "Ghi chú": [""]}
    )
    if cat_key in DEFAULT_CATEGORIES:
        default_df = DEFAULT_CATEGORIES[cat_key]["df"]

    if session_key not in st.session_state:
        st.session_state[session_key] = load_category_data(
            cat_key, default_df
        )

    # 1. KHU VỰC NHẬP / XUẤT EXCEL MẪU
    with st.expander(
        "📊 NHẬP DỮ LIỆU TỪ EXCEL / TẢI FILE EXCEL MẪU", expanded=False
    ):
        col_ex1, col_ex2 = st.columns([1, 2])

        with col_ex1:
            st.markdown("**1. Tải file Excel/CSV mẫu:**")
            sample_csv = st.session_state[session_key].head(2).to_csv(
                index=False, encoding="utf-8-sig"
            )
            st.download_button(
                label=f"📥 Tải xuống File mẫu",
                data=sample_csv,
                file_name=f"Mau_{cat_key}.csv",
                mime="text/csv",
                key=f"btn_dl_{cat_key}",
            )

        with col_ex2:
            st.markdown("**2. Tải lên file Excel/CSV để cập nhật:**")
            uploaded_file = st.file_uploader(
                "Chọn file từ máy tính:",
                type=["xlsx", "xls", "csv"],
                key=f"upload_{cat_key}",
            )

        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith(".csv"):
                    df_excel = pd.read_csv(uploaded_file)
                else:
                    df_excel = pd.read_excel(uploaded_file)

                st.write("📌 **Xem trước dữ liệu tải lên:**")
                st.dataframe(df_excel.head(5), use_container_width=True)

                col_b1, col_b2 = st.columns(2)
                with col_b1:
                    if st.button(
                        "➕ Nhập nối tiếp vào bảng hiện tại",
                        key=f"btn_append_{cat_key}",
                    ):
                        st.session_state[session_key] = pd.concat(
                            [st.session_state[session_key], df_excel],
                            ignore_index=True,
                        ).drop_duplicates()
                        save_category_data(
                            cat_key, st.session_state[session_key]
                        )
                        if editor_key in st.session_state:
                            del st.session_state[editor_key]
                        st.success("✅ Đã cập nhật thành công!")
                        st.rerun()

                with col_b2:
                    if st.button(
                        "🔄 Ghi đè toàn bộ dữ liệu cũ",
                        type="primary",
                        key=f"btn_overwrite_{cat_key}",
                    ):
                        st.session_state[session_key] = df_excel
                        save_category_data(
                            cat_key, st.session_state[session_key]
                        )
                        if editor_key in st.session_state:
                            del st.session_state[editor_key]
                        st.success("✅ Đã ghi đè dữ liệu thành công!")
                        st.rerun()
            except Exception as e:
                st.error(f"Lỗi đọc file: {e}")

    # 2. KHU VỰC QUẢN LÝ CỘT TIÊU ĐỀ
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
                    save_category_data(cat_key, st.session_state[session_key])
                    if editor_key in st.session_state:
                        del st.session_state[editor_key]
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
                    save_category_data(cat_key, st.session_state[session_key])
                    if editor_key in st.session_state:
                        del st.session_state[editor_key]
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
                    save_category_data(cat_key, st.session_state[session_key])
                    if editor_key in st.session_state:
                        del st.session_state[editor_key]
                    st.success(f"Đã xóa cột '{col_to_del}'")
                    st.rerun()

    # -------------------------------------------------------------------------
    # BẢNG DỮ LIỆU ĐÃ ĐƯỢC TỰ ĐỘNG CÂN BẰNG CHIỀU RỘNG (AUTO-SIZE)
    # -------------------------------------------------------------------------
    st.write("")
    st.caption("💡 Các cột đã được Auto Size vừa vặn văn bản:")

    auto_configs = build_column_auto_size_config(st.session_state[session_key])

    edited_df = st.data_editor(
        st.session_state[session_key],
        use_container_width=False,
        column_config=auto_configs,
        num_rows="dynamic",
        key=editor_key,
    )

    col_save, col_reload = st.columns([2, 1])

    with col_save:
        if st.button(
            f"💾 Lưu danh mục {cat_title} vĩnh viễn",
            type="primary",
            key=f"btn_save_{cat_key}",
        ):
            st.session_state[session_key] = edited_df
            if save_category_data(cat_key, edited_df):
                st.success("✅ Dữ liệu danh mục đã được lưu vĩnh viễn!")

    with col_reload:
        if st.button("🔄 Tải lại dữ liệu", key=f"btn_reload_{cat_key}"):
            if editor_key in st.session_state:
                del st.session_state[editor_key]
            st.session_state[session_key] = load_category_data(
                cat_key, default_df
            )
            st.success("🔄 Đã tải lại dữ liệu mới nhất từ CSDL!")
            st.rerun()


# Hàm chính điều hướng danh mục
def render_category_management():
    st.subheader("Chi tiết danh mục hệ thống")

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

                    cat_list[new_key] = f"📁 {new_cat_title}"
                    save_category_list(cat_list)

                    init_df = pd.DataFrame({
                        "Mã": ["M01"],
                        "Tên " + new_cat_title: ["Nội dung 01"],
                        "Ghi chú": [""],
                    })
                    save_category_data(new_key, init_df)

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
                    cat_list[selected_edit_key] = renamed_cat_title
                    save_category_list(cat_list)
                    st.success("Đã đổi tên danh mục thành công!")
                    st.rerun()

        with col_cat_del:
            st.markdown("**🗑️ Xóa danh mục**")
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
                    del cat_list[selected_del_key]
                    save_category_list(cat_list)
                    st.success("Đã xóa danh mục khỏi hệ thống!")
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
