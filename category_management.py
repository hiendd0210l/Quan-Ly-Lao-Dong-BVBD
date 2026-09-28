import os
import pandas as pd
import streamlit as st

# File CSDL lưu trữ dữ liệu vĩnh viễn
DATA_FILE = "danh_muc_chuc_danh.csv"


# 1. Hàm nạp dữ liệu từ CSDL
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            return pd.read_csv(DATA_FILE)
        except Exception:
            pass

    # Dữ liệu mặc định nếu chưa có file
    return pd.DataFrame({
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


# 2. Hàm lưu dữ liệu xuống file CSV vĩnh viễn
def save_data(df):
    try:
        df.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")
        return True
    except Exception as e:
        st.error(f"Lỗi khi lưu dữ liệu: {e}")
        return False


def render_category_management():
    st.subheader("Chi tiết danh mục: Chức danh & Mã ngạch")

    # Nạp dữ liệu vào state
    if "df_chuc_danh" not in st.session_state:
        st.session_state["df_chuc_danh"] = load_data()

    # =========================================================================
    # NÚT VÀ KHU VỰC CẬP NHẬT TỪ EXCEL (ĐẶT NGAY TRÊN CÙNG GIAO DIỆN)
    # =========================================================================
    with st.expander(
        "📊 NHẬP DỮ LIỆU TỪ EXCEL / TẢI FILE EXCEL MẪU", expanded=True
    ):
        col_download, col_upload = st.columns([1, 2])

        # NÚT 1: TẠO VÀ TẢI FILE EXCEL MẪU
        with col_download:
            st.markdown("**1. Tải file Excel mẫu:**")
            sample_df = pd.DataFrame({
                "Mã CĐ": ["BS01", "DD01"],
                "Tên Chức Danh": ["Bác sĩ Chuyên khoa", "Điều dưỡng Trưởng"],
                "Mã Ngạch": ["V.08.01.02", "V.08.05.11"],
                "Ghi chú": ["Ví dụ mẫu", "Ví dụ mẫu"],
            })
            # Xuất dạng CSV tương thích Excel
            sample_csv = sample_df.to_csv(index=False, encoding="utf-8-sig")

            st.download_button(
                label="📥 Tải xuống File mẫu (.csv/.xlsx)",
                data=sample_csv,
                file_name="Mau_Danh_Muc_Chuc_Danh.csv",
                mime="text/csv",
                help="Bấm vào đây để tải file mẫu về điền thông tin",
            )

        # NÚT 2: IMPORT FILE EXCEL VÀO HỆ THỐNG
        with col_upload:
            st.markdown("**2. Tải lên file Excel để Cập nhật:**")
            uploaded_file = st.file_uploader(
                "Chọn file Excel hoặc CSV từ máy tính:",
                type=["xlsx", "xls", "csv"],
                key="excel_uploader",
            )

        # XỬ LÝ KHI NGƯỜI DÙNG TẢI FILE LÊN
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith(".csv"):
                    df_excel = pd.read_csv(uploaded_file)
                else:
                    df_excel = pd.read_excel(uploaded_file)

                st.write("📌 **Xem trước dữ liệu tải lên:**")
                st.dataframe(df_excel.head(5), use_container_width=True)

                col_btn1, col_btn2 = st.columns([1, 1])

                with col_btn1:
                    if st.button("➕ Nhập nối tiếp vào bảng hiện tại"):
                        st.session_state["df_chuc_danh"] = pd.concat(
                            [st.session_state["df_chuc_danh"], df_excel],
                            ignore_index=True,
                        ).drop_duplicates()
                        save_data(st.session_state["df_chuc_danh"])
                        st.success("✅ Đã cập nhật thêm dữ liệu mới!")
                        st.rerun()

                with col_btn2:
                    if st.button(
                        "🔄 Ghi đè toàn bộ dữ liệu cũ", type="primary"
                    ):
                        st.session_state["df_chuc_danh"] = df_excel
                        save_data(st.session_state["df_chuc_danh"])
                        st.success("✅ Đã ghi đè dữ liệu thành công!")
                        st.rerun()

            except Exception as e:
                st.error(
                    f"Lỗi đọc file: {e}. Nếu đọc file .xlsx vui lòng kiểm tra thư viện openpyxl."
                )

    st.write("")

    # =========================================================================
    # QUẢN LÝ CỘT TIÊU ĐỀ (THÊM / SỬA / XÓA CỘT)
    # =========================================================================
    with st.expander("🛠️ QUẢN LÝ CỘT TIÊU ĐỀ CỦA BẢNG (THÊM / SỬA / XÓA CỘT)"):
        c_add, c_edit, c_del = st.columns(3)

        with c_add:
            st.markdown("**➕ Thêm cột mới**")
            new_col = st.text_input("Nhập tên cột mới:", key="cat_new_col")
            if st.button("Thêm cột", key="btn_add_col"):
                if new_col:
                    if new_col not in st.session_state["df_chuc_danh"].columns:
                        st.session_state["df_chuc_danh"][new_col] = ""
                        save_data(st.session_state["df_chuc_danh"])
                        st.success(f"Đã thêm cột {new_col}")
                        st.rerun()

        with c_edit:
            st.markdown("**✏️ Đổi tên cột tiêu đề**")
            cols = list(st.session_state["df_chuc_danh"].columns)
            col_to_rename = st.selectbox(
                "Chọn cột cần đổi tên:", cols, key="cat_sel_rename"
            )
            renamed_name = st.text_input(
                "Nhập tên mới:", key="cat_renamed_name"
            )
            if st.button("Đổi tên", key="btn_rename_col"):
                if renamed_name and col_to_rename:
                    st.session_state["df_chuc_danh"] = (
                        st.session_state["df_chuc_danh"].rename(
                            columns={col_to_rename: renamed_name}
                        )
                    )
                    save_data(st.session_state["df_chuc_danh"])
                    st.success("Đã đổi tên cột thành công!")
                    st.rerun()

        with c_del:
            st.markdown("**🗑️ Xóa cột khỏi bảng**")
            cols = list(st.session_state["df_chuc_danh"].columns)
            col_to_del = st.selectbox(
                "Chọn cột cần xóa:", cols, key="cat_sel_del"
            )
            if st.button("Xóa cột", type="primary", key="btn_del_col"):
                if col_to_del in st.session_state["df_chuc_danh"].columns:
                    st.session_state["df_chuc_danh"] = st.session_state[
                        "df_chuc_danh"
                    ].drop(columns=[col_to_del])
                    save_data(st.session_state["df_chuc_danh"])
                    st.success(f"Đã xóa cột {col_to_del}")
                    st.rerun()

    # =========================================================================
    # BẢNG DỮ LIỆU VÀ NÚT LƯU VĨNH VIỄN
    # =========================================================================
    st.write("")
    st.caption(
        "💡 Chỉnh sửa trực tiếp trên bảng bên dưới, sau đó bấm nút Lưu danh mục:"
    )

    edited_df = st.data_editor(
        st.session_state["df_chuc_danh"],
        use_container_width=True,
        num_rows="dynamic",
        key="cat_editor",
    )

    col_save, col_reload = st.columns([2, 1])

    with col_save:
        if st.button(
            "💾 Lưu danh mục Chức danh & Mã ngạch vĩnh viễn", type="primary"
        ):
            st.session_state["df_chuc_danh"] = edited_df
            if save_data(edited_df):
                st.success(
                    "✅ Dữ liệu đã được lưu vĩnh viễn xuống CSDL (file CSV)!"
                )

    with col_reload:
        if st.button("🔄 Tải lại dữ liệu"):
            st.session_state["df_chuc_danh"] = load_data()
            st.rerun()


if __name__ == "__main__":
    render_category_management()
