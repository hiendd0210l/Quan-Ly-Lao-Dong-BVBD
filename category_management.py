import pandas as pd
import streamlit as st


def init_categories():
    """Khởi tạo dữ liệu danh mục mặc định nếu chưa có trong session_state."""
    if "categories" not in st.session_state:
        st.session_state["categories"] = {
            "Chức danh & Mã ngạch": pd.DataFrame([
                {
                    "Mã CD": "BS",
                    "Tên Chức Danh": "Bác sĩ",
                    "Mạch Ngạch": "V.08.01.03",
                    "Ghi chú": "Lâm sàng",
                },
                {
                    "Mã CD": "BSCK1",
                    "Tên Chức Danh": "Bác sĩ CKI",
                    "Mạch Ngạch": "V.08.01.02",
                    "Ghi chú": "Chuyên khoa 1",
                },
                {
                    "Mã CD": "BSCK2",
                    "Tên Chức Danh": "Bác sĩ CKII",
                    "Mạch Ngạch": "V.08.01.01",
                    "Ghi chú": "Chuyên khoa 2",
                },
                {
                    "Mã CD": "DD",
                    "Tên Chức Danh": "Điều dưỡng",
                    "Mạch Ngạch": "V.08.05.12",
                    "Ghi chú": "Chăm sóc",
                },
                {
                    "Mã CD": "KTV",
                    "Tên Chức Danh": "Kỹ thuật viên",
                    "Mạch Ngạch": "V.08.07.23",
                    "Ghi chú": "Cận lâm sàng",
                },
                {
                    "Mã CD": "DS",
                    "Tên Chức Danh": "Dược sĩ",
                    "Mạch Ngạch": "V.08.08.26",
                    "Ghi chú": "Khoa Dược",
                },
            ]),
            "Trình độ chuyên môn": pd.DataFrame([
                {
                    "Mã TRD": "TD01",
                    "Tên Trình Độ": "Tiến sĩ Y khoa",
                    "Cấp Bằng": "Đại học",
                },
                {
                    "Mã TRD": "TD02",
                    "Tên Trình Độ": "Thạc sĩ Y khoa",
                    "Cấp Bằng": "Đại học",
                },
                {
                    "Mã TRD": "TD03",
                    "Tên Trình Độ": "Bác sĩ Chuyên khoa II",
                    "Cấp Bằng": "Sau đại học",
                },
                {
                    "Mã TRD": "TD04",
                    "Tên Trình Độ": "Bác sĩ Chuyên khoa I",
                    "Cấp Bằng": "Sau đại học",
                },
                {
                    "Mã TRD": "TD05",
                    "Tên Trình Độ": "Đại học Điều dưỡng",
                    "Cấp Bằng": "Đại học",
                },
                {
                    "Mã TRD": "TD06",
                    "Tên Trình Độ": "Cao đẳng Kỹ thuật",
                    "Cấp Bằng": "Cao đẳng",
                },
            ]),
            "Loại Hợp đồng Lao động": pd.DataFrame([
                {
                    "Mã HĐ": "HD01",
                    "TenLoaiHD": "Hợp đồng không xác định thời hạn",
                    "Thời hạn (tháng)": "Vĩnh viễn",
                },
                {
                    "Mã HĐ": "HD02",
                    "TenLoaiHD": "Hợp đồng xác định thời hạn 12-36 tháng",
                    "Thời hạn (tháng)": "12-36",
                },
                {
                    "Mã HĐ": "HD03",
                    "TenLoaiHD": "Hợp đồng thử việc",
                    "Thời hạn (tháng)": "02",
                },
            ]),
            "Danh mục Phụ cấp Y tế": pd.DataFrame([
                {
                    "Mã PC": "PC01",
                    "Tên Phụ cấp": "Phụ cấp Ưu đãi nghề",
                    "Mức hưởng (%)": "40% - 70%",
                },
                {
                    "Mã PC": "PC02",
                    "Tên Phụ cấp": "Phụ cấp Độc hại nguy hiểm",
                    "Mức hưởng (%)": "0.1 - 0.4",
                },
                {
                    "Mã PC": "PC03",
                    "Tên Phụ cấp": "Phụ cấp Trực 24/24",
                    "Mức hưởng (%)": "Theo ca trực",
                },
            ]),
            "Ngạch bậc lương cơ bản": pd.DataFrame([
                {"Mã": "01", "Tên giá trị": "Mẫu mặc định", "Ghi chú": ""}
            ]),
        }


def render_category_management():
    """Giao diện Quản lý Danh mục Hệ thống Dùng chung hỗ trợ tùy chỉnh Cột động."""
    init_categories()

    st.subheader("⚙️ QUẢN LÝ DANH MỤC HỆ THỐNG DÙNG CHUNG")
    st.caption(
        "Khai báo linh hoạt danh mục, thêm/bớt cột tiêu đề và chỉnh sửa các dòng dữ liệu."
    )

    # -------------------------------------------------------------------------
    # 1. QUẢN LÝ TÊN DANH MỤC LỚN (THÊM / XÓA DANH MỤC)
    # -------------------------------------------------------------------------
    with st.expander("🛠️ **QUẢN LÝ DANH MỤC LỚN (THÊM / XÓA DANH MỤC)**"):
        col_c1, col_c2 = st.columns([3, 2])

        with col_c1:
            new_cat_name = st.text_input("➕ Nhập tên Danh mục mới muốn thêm:")
            if st.button("Tạo Danh mục mới"):
                if not new_cat_name.strip():
                    st.warning("Vui lòng nhập tên danh mục!")
                elif new_cat_name in st.session_state["categories"]:
                    st.warning("Danh mục này đã tồn tại!")
                else:
                    st.session_state["categories"][new_cat_name] = pd.DataFrame(
                        [{"Mã": "01", "Tên giá trị": "Mẫu mặc định", "Ghi chú": ""}]
                    )
                    st.success(f"Đã tạo danh mục '{new_cat_name}' thành công!")
                    st.rerun()

        with col_c2:
            delete_cat_name = st.selectbox(
                "🗑️ Chọn Danh mục muốn xóa:",
                options=list(st.session_state["categories"].keys()),
            )
            if st.button("❌ Xóa Danh mục chọn", type="primary"):
                if len(st.session_state["categories"]) <= 1:
                    st.error("Hệ thống phải duy trì ít nhất 01 danh mục!")
                else:
                    del st.session_state["categories"][delete_cat_name]
                    st.success(f"Đã xóa danh mục '{delete_cat_name}'!")
                    st.rerun()

    st.divider()

    # -------------------------------------------------------------------------
    # 2. CHỈNH SỬA CHI TIẾT BẢNG VÀ CẤU TRÚC CỘT TIÊU ĐỀ
    # -------------------------------------------------------------------------
    category_names = list(st.session_state["categories"].keys())

    if not category_names:
        st.info("Chưa có danh mục nào được khởi tạo.")
        return

    tabs = st.tabs([f"📌 {name}" for name in category_names])

    for idx, name in enumerate(category_names):
        with tabs[idx]:
            st.write(f"### Chi tiết danh mục: **{name}**")
            df_cat = st.session_state["categories"][name]

            # Quản lý Cột tiêu đề (Thêm / Đổi tên / Xóa cột)
            with st.expander("📐 **QUẢN LÝ CỘT TIÊU ĐỀ CỦA BẢNG (THÊM / SỬA / XÓA CỘT)**", expanded=False):
                c_add, c_rename, c_del = st.columns(3)

                # --- 1. Thêm cột mới ---
                with c_add:
                    st.markdown("**➕ Thêm cột mới**")
                    new_col_name = st.text_input(
                        "Nhập tên cột mới:", key=f"input_add_col_{name}"
                    )
                    if st.button("Thêm cột", key=f"btn_add_col_{name}"):
                        if not new_col_name.strip():
                            st.warning("Vui lòng nhập tên cột!")
                        elif new_col_name in df_cat.columns:
                            st.warning("Cột này đã có trong bảng!")
                        else:
                            st.session_state["categories"][name][new_col_name] = ""
                            st.success(f"Đã thêm cột '{new_col_name}' thành công!")
                            st.rerun()

                # --- 2. Đổi tên cột ---
                with c_rename:
                    st.markdown("**✏️ Đổi tên cột tiêu đề**")
                    col_to_rename = st.selectbox(
                        "Chọn cột cần đổi tên:",
                        options=list(df_cat.columns),
                        key=f"select_rename_col_{name}",
                    )
                    renamed_col_name = st.text_input(
                        "Nhập tên mới:", key=f"input_rename_col_{name}"
                    )
                    if st.button("Đổi tên", key=f"btn_rename_col_{name}"):
                        if not renamed_col_name.strip():
                            st.warning("Vui lòng nhập tên cột mới!")
                        elif renamed_col_name in df_cat.columns:
                            st.warning("Tên cột mới trùng với cột đã tồn tại!")
                        else:
                            st.session_state["categories"][name] = (
                                st.session_state["categories"][name].rename(
                                    columns={col_to_rename: renamed_col_name}
                                )
                            )
                            st.success(f"Đã đổi tên cột '{col_to_rename}' ➔ '{renamed_col_name}'!")
                            st.rerun()

                # --- 3. Xóa cột ---
                with c_del:
                    st.markdown("**🗑️ Xóa cột khỏi bảng**")
                    col_to_delete = st.selectbox(
                        "Chọn cột cần xóa:",
                        options=list(df_cat.columns),
                        key=f"select_del_col_{name}",
                    )
                    if st.button("Xóa cột", key=f"btn_del_col_{name}", type="primary"):
                        if len(df_cat.columns) <= 1:
                            st.error("Bảng phải giữ lại ít nhất 01 cột!")
                        else:
                            st.session_state["categories"][name] = (
                                st.session_state["categories"][name].drop(
                                    columns=[col_to_delete]
                                )
                            )
                            st.success(f"Đã xóa cột '{col_to_delete}'!")
                            st.rerun()

            st.caption("💡 *Kích đôi vào ô để sửa nội dung, hoặc thêm/xóa dòng dữ liệu trực tiếp trên bảng bên dưới:*")

            # Bảng chỉnh sửa dữ liệu
            edited_df = st.data_editor(
                st.session_state["categories"][name],
                num_rows="dynamic",
                use_container_width=True,
                key=f"editor_{name}",
            )

            # Nút Lưu thay đổi
            c_save, _ = st.columns([1, 5])
            with c_save:
                if st.button(f"💾 Lưu danh mục {name}", key=f"btn_save_{name}"):
                    st.session_state["categories"][name] = edited_df
                    st.success(f"Đã lưu dữ liệu cho danh mục '{name}'!")
                    st.rerun()


def get_category_data(category_name):
    """Hàm hỗ trợ lấy dữ liệu danh mục để sử dụng ở các mô-đun khác."""
    init_categories()
    if category_name in st.session_state["categories"]:
        return st.session_state["categories"][category_name]
    return pd.DataFrame()
