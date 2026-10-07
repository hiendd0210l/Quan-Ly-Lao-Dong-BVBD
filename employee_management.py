import io
import pandas as pd
import streamlit as st


def render_employee_management():
    st.markdown(
        "### 👥 Quản lý Hồ sơ Cán bộ (Mẫu Sơ yếu lý lịch chuẩn Bộ Nội vụ)"
    )

    # --- KHU VỰC TẢI FILE MẪU VÀ TẢI LÊN FILE DỮ LIỆU ---
    col_dl, col_ul = st.columns([1, 2])

    with col_dl:
        st.markdown("##### 📥 Tải file mẫu")
        # Tạo template Excel mẫu chuẩn gồm cột Chức vụ và Chức danh nằm cạnh nhau
        template_data = {
            "Mã NV": ["BV00001", "BV00002"],
            "Số CCCD/BHYT": ["001092000001", "001092000002"],
            "Họ và tên": ["Nguyễn Văn A", "Trần Thị B"],
            "Ngày sinh": ["01/01/1980", "15/05/1990"],
            "Giới tính": ["Nam", "Nữ"],
            "Quê quán": ["Hà Nội", "Hải Phòng"],
            "Địa chỉ": ["Đống Đa, Hà Nội", "Cầu Giấy, Hà Nội"],
            "Số điện thoại": ["0901234567", "0909876543"],
            "Dân tộc": ["Kinh", "Kinh"],
            "Tôn giáo": ["Không", "Không"],
            "Đơn vị công tác": ["Phòng Khám - Tổng hợp", "Khoa Nội tổng hợp"],
            "Chữ ký số": ["Có", "Không"],
            "Đang làm việc": ["Đang", "Đang"],
            "Chức vụ": ["Trưởng phòng", "Phó Trưởng phòng"],
            "Chức danh": [
                "Bác sĩ Chuyên khoa II",
                "Thạc sĩ - Bác sĩ",
            ],  # Cột Chức danh đặt ngay cạnh phải Chức vụ
            "Ngạch, Bậc": ["VC.01", "VC.02"],
            "Mã lương": ["Viên chức A1", "Viên chức A2"],
            "Hệ số lương": [4.32, 3.66],
            "Ngày hưởng lương": ["01/01/2024", "01/01/2024"],
            "Phụ cấp chức vụ": [0.8, 0.5],
        }
        df_template = pd.DataFrame(template_data)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df_template.to_excel(writer, index=False, sheet_name="Mau_Ho_So")
        excel_data = output.getvalue()

        st.download_button(
            label="📥 Tải file mẫu Excel",
            data=excel_data,
            file_name="Mau_So_Yeu_Ly_Lich_Can_Bo.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Tải xuống tệp Excel mẫu để điền thông tin cán bộ theo đúng cấu trúc.",
        )

    with col_ul:
        uploaded_file = st.file_uploader(
            "Tải lên tệp dữ liệu Hồ sơ cán bộ (.xlsx, .csv)",
            type=["xlsx", "csv"],
            key="emp_file_uploader_main",
        )

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                df_upload = pd.read_csv(uploaded_file)
            else:
                df_upload = pd.read_excel(uploaded_file)

            # Xử lý đưa cột "Chức danh" vào ngay bên cạnh phải cột "Chức vụ"
            cols = list(df_upload.columns)
            if "Chức danh" not in cols:
                pos_idx = -1
                for idx, c in enumerate(cols):
                    if (
                        any(k in str(c).lower() for k in ["chức vụ", "chuc_vu"])
                        and "chức danh" not in str(c).lower()
                    ):
                        pos_idx = idx
                        break

                if pos_idx != -1:
                    cols.insert(pos_idx + 1, "Chức danh")
                    df_upload["Chức danh"] = ""
                    df_upload = df_upload[cols]
                else:
                    df_upload["Chức danh"] = ""

            st.session_state["employees_profile"] = df_upload
            st.success(
                f"✅ Đã tải lên và lưu thành công {len(df_upload)} hồ sơ cán"
                " bộ!"
            )
        except Exception as e:
            st.error(f"Lỗi khi đọc tệp dữ liệu: {e}")

    # Lấy dữ liệu từ session_state
    df_display = pd.DataFrame()
    if "employees_profile" in st.session_state:
        df_display = st.session_state["employees_profile"]

    if df_display.empty:
        st.info(
            "ℹ️ Chưa có dữ liệu hồ sơ. Vui lòng tải file mẫu về, điền thông"
            " tin và tải lên tệp Excel ở khung phía trên để hiển thị danh"
            " sách."
        )
        return

    # --- SẮP XẾP VÀ ĐẢM BẢO THỨ TỰ CỘT HIỂN THỊ ---
    cols_current = list(df_display.columns)
    if "Chức danh" not in cols_current:
        for idx, c in enumerate(cols_current):
            if any(k in str(c).lower() for k in ["chức vụ", "chuc_vu"]):
                cols_current.insert(idx + 1, "Chức danh")
                df_display["Chức danh"] = ""
                break
        df_display = df_display[cols_current]
    else:
        try:
            pos_idx = -1
            for idx, c in enumerate(cols_current):
                if (
                    any(k in str(c).lower() for k in ["chức vụ", "chuc_vu"])
                    and "chức danh" not in str(c).lower()
                ):
                    pos_idx = idx
                    break
            if pos_idx != -1 and "Chức danh" in cols_current:
                cols_current.remove("Chức danh")
                cols_current.insert(pos_idx + 1, "Chức danh")
                df_display = df_display[cols_current]
        except Exception:
            pass

    st.markdown("---")
    st.markdown(
        "##### 📋 Danh sách Hồ sơ Cán bộ hiện tại (Hiển thị đồng bộ theo"
        " thứ tự tệp Excel):"
    )

    # Hiển thị bảng dữ liệu tương tác
    st.dataframe(df_display, use_container_width=True, hide_index=True)

    # Nút xóa / làm mới dữ liệu trong phiên làm việc
    col_btn1, col_btn2 = st.columns([2, 8])
    with col_btn1:
        if st.button("🗑️ Làm mới / Xóa dữ liệu", type="secondary"):
            if "employees_profile" in st.session_state:
                del st.session_state["employees_profile"]
            st.rerun()
