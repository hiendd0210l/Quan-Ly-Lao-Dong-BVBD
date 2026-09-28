import os
import pandas as pd
import streamlit as st

# Thư mục lưu dữ liệu vĩnh viễn
DATA_DIR = "data_categories"
os.makedirs(DATA_DIR, exist_ok=True)


# 1. Hàm nạp dữ liệu từ file CSV
def load_category_data(cat_key, default_df):
    file_path = os.path.join(DATA_DIR, f"{cat_key}.csv")
    if os.path.exists(file_path):
        try:
            return pd.read_csv(file_path)
        except Exception:
            pass
    return default_df


# 2. Hàm lưu dữ liệu bền vững xuống file CSV
def save_category_data(cat_key, df):
    file_path = os.path.join(DATA_DIR, f"{cat_key}.csv")
    try:
        df.to_csv(file_path, index=False, encoding="utf-8-sig")
        return True
    except Exception as e:
        st.error(f"Lỗi khi lưu dữ liệu: {e}")
        return False


# 3. Giao diện quản lý từng danh mục cụ thể
def render_single_category(cat_key, cat_title, default_df):
    session_key = f"df_{cat_key}"
    editor_key = f"editor_{cat_key}"

    # Khởi tạo dữ liệu vào session state
    if session_key not in st.session_state:
        st.session_state[session_key] = load_category_data(
            cat_key, default_df
        )

    # -------------------------------------------------------------------------
    # KHU VỰC 1: NHẬP / XUẤT EXCEL MẪU
    # -------------------------------------------------------------------------
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
                label=f"📥 Tải xuống File mẫu ({cat_title})",
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

    # -------------------------------------------------------------------------
    # KHU VỰC 2: QUẢN LÝ CỘT TIÊU ĐỀ (THÊM / SỬA / XÓA CỘT)
    # -------------------------------------------------------------------------
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
    # KHU VỰC 3: BẢNG DỮ LIỆU CHỈNH SỬA & LƯU / TẢI LẠI
    # -------------------------------------------------------------------------
    st.write("")
    st.caption(
        "💡 Thêm/Xóa/Sửa trực tiếp các dòng trên bảng bên dưới, sau đó bấm nút Lưu:"
    )

    edited_df = st.data_editor(
        st.session_state[session_key],
        use_container_width=True,
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
                st.success(
                    f"✅ Dữ liệu danh mục '{cat_title}' đã được lưu thành công!"
                )

    with col_reload:
        if st.button("🔄 Tải lại dữ liệu", key=f"btn_reload_{cat_key}"):
            # Xóa cache bộ nhớ của data_editor để buộc Streamlit load dữ liệu mới nhất
            if editor_key in st.session_state:
                del st.session_state[editor_key]
            st.session_state[session_key] = load_category_data(
                cat_key, default_df
            )
            st.success("🔄 Đã tải lại dữ liệu mới nhất từ CSDL!")
            st.rerun()


# -----------------------------------------------------------------------------
# HÀM CHÍNH - HIỂN THỊ ĐẦY ĐỦ CÁC TAB DANH MỤC
# -----------------------------------------------------------------------------
def render_category_management():
    st.subheader("Chi tiết danh mục hệ thống")

    # Tạo 5 Tab điều hướng danh mục
    tabs = st.tabs([
        "📌 Chức danh & Mã ngạch",
        "🎓 Trình độ chuyên môn",
        "📝 Loại Hợp đồng Lao động",
        "💰 Danh mục Phụ cấp / Lương",
        "🏛️ Ngạch bậc lương cơ bản",
    ])

    # Tab 1: Chức danh & Mã ngạch
    with tabs[0]:
        df_chuc_danh = pd.DataFrame({
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
        })
        render_single_category(
            "chuc_danh", "Chức danh & Mã ngạch", df_chuc_danh
        )

    # Tab 2: Trình độ chuyên môn
    with tabs[1]:
        df_trinh_do = pd.DataFrame({
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
        })
        render_single_category("trinh_do", "Trình độ chuyên môn", df_trinh_do)

    # Tab 3: Loại Hợp đồng Lao động
    with tabs[2]:
        df_hop_dong = pd.DataFrame({
            "Mã HĐ": ["KTH", "12T", "36T", "TV"],
            "Tên Loại Hợp đồng": [
                "HĐLĐ Không xác định thời hạn",
                "HĐLĐ Xác định thời hạn 12 tháng",
                "HĐLĐ Xác định thời hạn 36 tháng",
                "Hợp đồng Thử việc",
            ],
            "Thời hạn (Tháng)": ["Vô thời hạn", "12", "36", "02"],
            "Ghi chú": ["Chính thức", "Chính thức", "Chính thức", "Thử việc"],
        })
        render_single_category(
            "loai_hop_dong", "Loại Hợp đồng Lao động", df_hop_dong
        )

    # Tab 4: Danh mục Phụ cấp / Lương
    with tabs[3]:
        df_phu_cap = pd.DataFrame({
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
        })
        render_single_category(
            "phu_cap", "Danh mục Phụ cấp / Lương", df_phu_cap
        )

    # Tab 5: Ngạch bậc lương cơ bản
    with tabs[4]:
        df_ngach_luong = pd.DataFrame({
            "Mã Ngạch": ["V.08.01.01", "V.08.01.02", "V.08.01.03", "V.08.05.12"],
            "Tên Ngạch lương": [
                "Bác sĩ cao cấp (Hạng I)",
                "Bác sĩ chính (Hạng II)",
                "Bác sĩ (Hạng III)",
                "Điều dưỡng (Hạng III)",
            ],
            "Hệ số Bậc 1": ["6.20", "4.40", "2.34", "2.34"],
            "Bậc tối đa": ["8", "8", "12", "12"],
        })
        render_single_category(
            "ngach_luong", "Ngạch bậc lương cơ bản", df_ngach_luong
        )


if __name__ == "__main__":
    render_category_management()
