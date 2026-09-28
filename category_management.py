import os
import pandas as pd
import streamlit as st

# Tên file lưu trữ dữ liệu vĩnh viễn (CSDL dạng CSV)
DATA_FILE = "danh_muc_chuc_danh.csv"

# Danh sách cột chuẩn của Bảng
DEFAULT_COLUMNS = ["Mã CĐ", "Tên Chức Danh", "Mã Ngạch", "Ghi Chú"]


# 1. Hàm nạp dữ liệu từ ổ đĩa/CSDL
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)
            # Đảm bảo các cột tối thiểu luôn tồn tại
            for col in DEFAULT_COLUMNS:
                if col not in df.columns:
                    df[col] = ""
            return df
        except Exception as e:
            st.error(f"Lỗi đọc file dữ liệu: {e}")

    # Dữ liệu mặc định ban đầu nếu chưa có file dữ liệu
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
        "Ghi Chú": [
            "Lâm sàng",
            "Chuyên khoa 1",
            "Chuyên khoa 2",
            "Chăm sóc",
            "Cận lâm sàng",
            "Phân Dược",
        ],
    })


# 2. Hàm lưu dữ liệu bền vững xuống ổ đĩa
def save_data(df):
    try:
        df.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")
        return True
    except Exception as e:
        st.error(f"Không thể lưu dữ liệu: {e}")
        return False


def render_category_management():
    st.title("⚙️ QUẢN LÝ DANH MỤC HỆ THỐNG")

    # Khởi tạo state dữ liệu nếu chưa có
    if "df_chuc_danh" not in st.session_state:
        st.session_state["df_chuc_danh"] = load_data()

    # -------------------------------------------------------------------------
    # KHU VỰC 1: QUẢN LÝ CỘT TIÊU ĐỀ (THÊM / SỬA / XÓA CỘT)
    # -------------------------------------------------------------------------
    with st.expander("🛠️ QUẢN LÝ CỘT TIÊU ĐỀ CỦA BẢNG (THÊM / SỬA / XÓA CỘT)"):
        col_add, col_edit, col_del = st.columns(3)

        # Thêm cột
        with col_add:
            st.markdown("**➕ Thêm cột mới**")
            new_col_name = st.text_input(
                "Nhập tên cột mới:", key="input_new_col"
            )
            if st.button("Thêm cột"):
                if new_col_name:
                    if new_col_name not in st.session_state["df_chuc_danh"].columns:
                        st.session_state["df_chuc_danh"][new_col_name] = ""
                        save_data(st.session_state["df_chuc_danh"])
                        st.success(f"Đã thêm cột '{new_col_name}'")
                        st.rerun()
                    else:
                        st.warning("Tên cột đã tồn tại!")
                else:
                    st.warning("Vui lòng nhập tên cột!")

        # Đổi tên cột
        with col_edit:
            st.markdown("**✏️ Đổi tên cột tiêu đề**")
            cols_list = list(st.session_state["df_chuc_danh"].columns)
            selected_col_rename = st.selectbox(
                "Chọn cột cần đổi tên:", cols_list, key="select_col_rename"
            )
            renamed_title = st.text_input(
                "Nhập tên mới:", key="input_renamed_title"
            )
            if st.button("Đổi tên"):
                if renamed_title and selected_col_rename:
                    st.session_state["df_chuc_danh"] = (
                        st.session_state["df_chuc_danh"].rename(
                            columns={selected_col_rename: renamed_title}
                        )
                    )
                    save_data(st.session_state["df_chuc_danh"])
                    st.success("Đã đổi tên cột thành công!")
                    st.rerun()

        # Xóa cột
        with col_del:
            st.markdown("**🗑️ Xóa cột khỏi bảng**")
            selected_col_delete = st.selectbox(
                "Chọn cột cần xóa:", cols_list, key="select_col_delete"
            )
            if st.button("Xóa cột", type="primary"):
                if selected_col_delete in st.session_state["df_chuc_danh"].columns:
                    st.session_state["df_chuc_danh"] = st.session_state[
                        "df_chuc_danh"
                    ].drop(columns=[selected_col_delete])
                    save_data(st.session_state["df_chuc_danh"])
                    st.success(f"Đã xóa cột '{selected_col_delete}'")
                    st.rerun()

    st.divider()

    # -------------------------------------------------------------------------
    # KHU VỰC 2: NHẬP DỮ LIỆU HÀNG LOẠT TỪ FILE EXCEL
    # -------------------------------------------------------------------------
    with st.expander(
        "📊 CẬP NHẬT / NHẬP HÀNG LOẠT TỪ FILE EXCEL (.XLSX, .XLS)", expanded=False
    ):
        st.markdown(
            "Tải lên file Excel chứa danh sách chức danh để nhập hoặc cập nhật hàng loạt vào hệ thống."
        )

        uploaded_excel = st.file_uploader(
            "Chọn file Excel",
            type=["xlsx", "xls"],
            help="File Excel nên có các cột tiêu đề tương ứng với bảng",
        )

        col_opt1, col_opt2 = st.columns([2, 2])
        import_mode = col_opt1.radio(
            "Chế độ nhập:",
            ["Nối tiếp vào bảng hiện tại", "Ghi đè toàn bộ bảng cũ"],
            horizontal=True,
        )

        if uploaded_excel is not None:
            try:
                df_excel = pd.read_excel(uploaded_excel)
                st.markdown("**Bản xem trước dữ liệu từ Excel:**")
                st.dataframe(df_excel.head(5), use_container_width=True)

                if st.button("🚀 Tiến hành Cập nhật dữ liệu từ Excel"):
                    if import_mode == "Ghi đè toàn bộ bảng cũ":
                        st.session_state["df_chuc_danh"] = df_excel
                    else:
                        st.session_state["df_chuc_danh"] = pd.concat(
                            [st.session_state["df_chuc_danh"], df_excel],
                            ignore_index=True,
                        ).drop_duplicates()

                    if save_data(st.session_state["df_chuc_danh"]):
                        st.success(
                            f"🎉 Đã nhập thành công dữ liệu từ file Excel và lưu vĩnh viễn vào hệ thống!"
                        )
                        st.rerun()
            except Exception as e:
                st.error(f"Lỗi đọc file Excel: {e}")

    st.divider()

    # -------------------------------------------------------------------------
    # KHU VỰC 3: BẢNG CHỈNH SỬA VÀ NÚT LƯU VĨNH VIỄN
    # -------------------------------------------------------------------------
    st.subheader("📋 DANH MỤC CHỨC DANH VÀ MÃ NGẠCH")
    st.caption("💡 Chỉnh sửa trực tiếp trên bảng bên dưới, sau đó bấm nút Lưu.")

    # Cho phép chỉnh sửa bảng và thêm/xóa hàng linh hoạt
    edited_df = st.data_editor(
        st.session_state["df_chuc_danh"],
        use_container_width=True,
        num_rows="dynamic",
        key="editor_chuc_danh",
    )

    col_save, col_reset = st.columns([3, 1])

    with col_save:
        if st.button(
            "💾 Lưu danh mục Chức danh & Mã ngạch vĩnh viễn", type="primary"
        ):
            # 1. Cập nhật vào Session State
            st.session_state["df_chuc_danh"] = edited_df
            # 2. Lưu trực tiếp xuống ổ đĩa / CSDL
            if save_data(edited_df):
                st.success(
                    "✅ Dữ liệu đã được lưu vĩnh viễn! Lần sau truy cập sẽ không bị mất."
                )

    with col_reset:
        if st.button("🔄 Tải lại dữ liệu từ CSDL"):
            st.session_state["df_chuc_danh"] = load_data()
            st.rerun()


if __name__ == "__main__":
    render_category_management()
