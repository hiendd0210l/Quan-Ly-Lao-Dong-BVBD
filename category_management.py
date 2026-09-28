import os
import pandas as pd
import streamlit as st

# Tệp CSDL lưu trữ vĩnh viễn
DATA_FILE = "danh_muc_chuc_danh.csv"


# 1. Hàm nạp dữ liệu từ tệp lưu trữ hoặc khởi tạo mặc định
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            return pd.read_csv(DATA_FILE)
        except Exception:
            pass

    # Dữ liệu mặc định ban đầu
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


# 2. Hàm ghi lưu dữ liệu vĩnh viễn
def save_data(df):
    try:
        df.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")
        return True
    except Exception as e:
        st.error(f"Lỗi khi lưu dữ liệu: {e}")
        return False


def render_category_management():
    st.subheader("Chi tiết danh mục: Chức danh & Mã ngạch")

    # Khởi tạo dữ liệu trong session_state nếu chưa có
    if "df_chuc_danh" not in st.session_state:
        st.session_state["df_chuc_danh"] = load_data()

    # -------------------------------------------------------------------------
    # KHU VỰC 1: CẬP NHẬT TỪ FILE EXCEL & TẢI FILE EXCEL MẪU
    # -------------------------------------------------------------------------
    with st.expander("📊 CẬP NHẬT TỪ FILE EXCEL / TẢI EXCEL MẪU", expanded=True):
        col_ex1, col_ex2 = st.columns([3, 2])

        with col_ex1:
            uploaded_file = st.file_uploader(
                "Tải lên file Excel (.xlsx, .xls) để nhập danh mục hàng loạt:",
                type=["xlsx", "xls"],
            )

        with col_ex2:
            st.markdown("**Tải tệp mẫu để nhập liệu:**")
            # Tạo file mẫu cho người dùng tải xuống
            sample_df = pd.DataFrame({
                "Mã CĐ": ["BS01", "DD01"],
                "Tên Chức Danh": ["Bác sĩ Chuyên khoa", "Điều dưỡng Trưởng"],
                "Mã Ngạch": ["V.08.01.02", "V.08.05.11"],
                "Ghi chú": ["Mẫu nhập liệu", "Mẫu nhập liệu"],
            })
            sample_csv = sample_df.to_csv(index=False, encoding="utf-8-sig")
            st.download_button(
                label="📥 Tải File Excel / CSV Mẫu",
                data=sample_csv,
                file_name="mau_danh_muc_chuc_danh.csv",
                mime="text/csv",
            )

        if uploaded_file is not None:
            try:
                df_excel = pd.read_excel(uploaded_file)
                st.write("📌 **Xem trước dữ liệu tải lên:**")
                st.dataframe(df_excel.head(5), use_container_width=True)

                col_b1, col_b2 = st.columns([1, 1])
                with col_b1:
                    if st.button("➕ Nhập nối tiếp vào bảng hiện tại"):
                        st.session_state["df_chuc_danh"] = pd.concat(
                            [st.session_state["df_chuc_danh"], df_excel],
                            ignore_index=True,
                        ).drop_duplicates()
                        save_data(st.session_state["df_chuc_danh"])
                        st.success("✅ Đã thêm dữ liệu mới từ Excel!")
                        st.rerun()

                with col_b2:
                    if st.button(
                        "🔄 Ghi đè toàn bộ dữ liệu cũ", type="primary"
                    ):
                        st.session_state["df_chuc_danh"] = df_excel
                        save_data(st.session_state["df_chuc_danh"])
                        st.success("✅ Đã thay thế toàn bộ bằng dữ liệu từ Excel!")
                        st.rerun()
            except Exception as e:
                st.error(f"Lỗi đọc file Excel: {e}. Vui lòng cài đặt openpyxl.")

    st.write("")

    # -------------------------------------------------------------------------
    # KHU VỰC 2: QUẢN LÝ CỘT TIÊU ĐỀ
    # -------------------------------------------------------------------------
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
                    else:
                        st.warning("Cột đã tồn tại!")

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

    # -------------------------------------------------------------------------
    # KHU VỰC 3: BẢNG CHỈNH SỬA & NÚT LƯU VĨNH VIỄN
    # -------------------------------------------------------------------------
    st.write("")
    st.caption("💡 Chỉnh sửa trực tiếp trên bảng, sau đó bấm nút Lưu bên dưới:")

    edited_df = st.data_editor(
        st.session_state["df_chuc_danh"],
        use_container_width=True,
        num_rows="dynamic",
        key="cat_editor",
    )

    col_save, col_reload = st.columns([2, 1])
    with col_save:
        if st.button(
            "💾 Lưu danh mục Chức danh & Mã ngạch", type="primary"
        ):
            st.session_state["df_chuc_danh"] = edited_df
            if save_data(edited_df):
                st.success(
                    "✅ Dữ liệu đã được lưu vĩnh viễn vào CSDL! Không bị mất khi làm mới trang."
                )

    with col_reload:
        if st.button("🔄 Tải lại từ CSDL"):
            st.session_state["df_chuc_danh"] = load_data()
            st.rerun()


if __name__ == "__main__":
    render_category_management()
