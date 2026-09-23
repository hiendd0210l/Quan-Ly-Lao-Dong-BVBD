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
        }


def render_category_management():
    """Giao diện chính Quản lý Danh mục Hệ thống Dùng chung linh hoạt."""
    init_categories()

    st.subheader("⚙️ QUẢN LÝ DANH MỤC HỆ THỐNG DÙNG CHUNG (CẤU HÌNH MỞ)")
    st.caption(
        "Quản trị viên có thể tự do khởi tạo thêm danh mục mới, chỉnh sửa hoặc bổ sung các tùy chọn con dùng chung cho toàn bộ hệ thống."
    )

    # -------------------------------------------------------------------------
    # 1. KHU VỰC QUẢN LÝ DANH MỤC LỚN (Thêm / Xóa danh mục)
    # -------------------------------------------------------------------------
    with st.expander("🛠️ **QUẢN LÝ TÊN DANH MỤC LỚN (THÊM / XÓA DANH MỤC)**"):
        col_c1, col_c2 = st.columns([3, 2])

        with col_c1:
            new_cat_name = st.text_input("➕ Nhập tên Danh mục mới muốn thêm:")
            if st.button("Tạo Danh mục mới"):
                if new_cat_name.strip() == "":
                    st.warning("Vui lòng nhập tên danh mục!")
                elif new_cat_name in st.session_state["categories"]:
                    st.warning("Danh mục này đã tồn tại!")
                else:
                    # Tạo dataframe trống mặc định cho danh mục mới
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
    # 2. KHU VỰC HIỂN THỊ TABS VÀ TỦY CHỈNH GIÁ TRỊ CON
    # -------------------------------------------------------------------------
    category_names = list(st.session_state["categories"].keys())

    if not category_names:
        st.info("Chưa có danh mục nào được khởi tạo.")
        return

    # Tạo các Tabs động tương ứng với số lượng Danh mục đang có
    tabs = st.tabs([f"📌 {name}" for name in category_names])

    for idx, name in enumerate(category_names):
        with tabs[idx]:
            st.write(f"### Chi tiết danh mục: **{name}**")

            df_cat = st.session_state["categories"][name]

            # Bảng chỉnh sửa trực tiếp dữ liệu (Data Editor)
            st.write(
                "💡 *Bạn có thể kích đôi vào ô để sửa nội dung, hoặc thêm/xóa trực tiếp trên bảng dưới đây:*"
            )

            edited_df = st.data_editor(
                df_cat,
                num_rows="dynamic",  # Cho phép thêm/xóa dòng động
                use_container_width=True,
                key=f"editor_{name}",
            )

            # Nút Lưu cập nhật
            c_save, c_reset = st.columns([1, 5])
            with c_save:
                if st.button(f"💾 Lưu danh mục {name}", key=f"btn_save_{name}"):
                    st.session_state["categories"][name] = edited_df
                    st.success(f"Đã lưu các thay đổi cho danh mục '{name}'!")
                    st.rerun()


def get_category_data(category_name):
    """Hàm bổ trợ để các mô-đun khác (Hồ sơ cán bộ, Tiền lương...) lấy danh sách tùy chọn."""
    init_categories()
    if category_name in st.session_state["categories"]:
        return st.session_state["categories"][category_name]
    return pd.DataFrame()
