import pandas as pd
import streamlit as st


def render_employee_management():
    st.markdown(
        "### 👥 Quản lý Hồ sơ Cán bộ (Mẫu Sơ yếu lý lịch chuẩn Bộ Nội vụ)"
    )

    # --- KHU VỰC TẢI LÊN FILE EXCEL (UPLOAD) ---
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
            "ℹ️ Chưa có dữ liệu hồ sơ. Vui lòng tải tệp Excel lên ở khung phía"
            " trên để hiển thị danh sách."
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
        # Đảm bảo Chức danh luôn đứng cạnh phải Chức vụ nếu đã tồn tại nhưng sai vị trí
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
