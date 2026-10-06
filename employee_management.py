import io
import pandas as pd
import streamlit as st
from supabase import create_client


# ---------------------------------------------------------
# 1. KẾT NỐI CSDL SUPABASE
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


def load_employees_data(supabase_client):
    """Tải danh sách cán bộ thực tế từ Session State hoặc Supabase CSDL"""
    if "employees_profile" in st.session_state:
        df_ses = st.session_state["employees_profile"]
        if isinstance(df_ses, pd.DataFrame) and not df_ses.empty:
            return df_ses

    default_cols = [
        "Mã NV",
        "Họ và tên",
        "Ngày sinh",
        "Giới tính",
        "Quê quán",
        "Đơn vị",
        "Chức vụ",
        "Hợp đồng",
        "Trạng thái",
        "Điện thoại",
    ]

    if not supabase_client:
        return pd.DataFrame(columns=default_cols)

    try:
        res = (
            supabase_client.table("categories")
            .select("content")
            .eq("cat_key", "employees_profile")
            .execute()
        )
        if res.data and res.data[0].get("content"):
            df = pd.DataFrame(res.data[0]["content"])
            # Chuẩn hóa tên cột
            if "Mã CB" in df.columns and "Mã NV" not in df.columns:
                df.rename(columns={"Mã CB": "Mã NV"}, inplace=True)
            if "Khoa / Phòng" in df.columns and "Đơn vị" not in df.columns:
                df.rename(columns={"Khoa / Phòng": "Đơn vị"}, inplace=True)
            if (
                "Chức vụ / Chức danh" in df.columns
                and "Chức vụ" not in df.columns
            ):
                df.rename(
                    columns={"Chức vụ / Chức danh": "Chức vụ"}, inplace=True
                )
            return df
        return pd.DataFrame(columns=default_cols)
    except Exception:
        return pd.DataFrame(columns=default_cols)


# ---------------------------------------------------------
# 2. GIAO DIỆN QUẢN LÝ HỒ SƠ CÁN BỘ (DUY NHẤT 1 BẢNG)
# ---------------------------------------------------------
def render_employee_management():
    st.markdown(
        "<h3 style='color: #003366;'>👤 Quản lý Hồ sơ Cán bộ (Mẫu Sơ yếu lý"
        " lịch chuẩn Bộ Nội vụ)</h3>",
        unsafe_allow_html=True,
    )

    supabase = init_supabase()
    df_emp_current = load_employees_data(supabase)

    # Khung công cụ thao tác
    col_btn1, col_btn2 = st.columns([2, 3])

    with col_btn1:
        # Tạo tệp Excel mẫu
        output_template = io.BytesIO()
        with pd.ExcelWriter(output_template, engine="openpyxl") as writer:
            sample_df = pd.DataFrame(
                columns=[
                    "Mã NV",
                    "Họ và tên",
                    "Ngày sinh",
                    "Giới tính",
                    "Quê quán",
                    "Đơn vị",
                    "Chức vụ",
                    "Hợp đồng",
                    "Trạng thái",
                    "Điện thoại",
                ]
            )
            sample_df.to_excel(writer, index=False, sheet_name="HoSoCanBo")
        output_template.seek(0)

        st.download_button(
            label="📥 Tải File Excel Mẫu Hồ Sơ",
            data=output_template,
            file_name="Mau_So_Yeu_Ly_Lich_Can_Bo.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="secondary",
        )

    with col_btn2:
        uploaded_emp_file = st.file_uploader(
            "📤 Tải lên File dữ liệu Hồ sơ (.xlsx, .xls)",
            type=["xlsx", "xls"],
            key="up_emp_single_file",
        )

    if uploaded_emp_file:
        try:
            df_uploaded = pd.read_excel(uploaded_emp_file).fillna("")
            if (
                "Mã CB" in df_uploaded.columns
                and "Mã NV" not in df_uploaded.columns
            ):
                df_uploaded.rename(columns={"Mã CB": "Mã NV"}, inplace=True)
            if (
                "Khoa / Phòng" in df_uploaded.columns
                and "Đơn vị" not in df_uploaded.columns
            ):
                df_uploaded.rename(
                    columns={"Khoa / Phòng": "Đơn vị"}, inplace=True
                )
            if (
                "Chức vụ / Chức danh" in df_uploaded.columns
                and "Chức vụ" not in df_uploaded.columns
            ):
                df_uploaded.rename(
                    columns={"Chức vụ / Chức danh": "Chức vụ"}, inplace=True
                )

            st.session_state["employees_profile"] = df_uploaded

            if supabase:
                supabase.table("categories").upsert({
                    "cat_key": "employees_profile",
                    "title": "Hồ sơ Cán bộ Nhân viên",
                    "content": df_uploaded.to_dict(orient="records"),
                }).execute()

            st.success(
                f"✅ Đã tải lên thành công {len(df_uploaded)} hồ sơ cán bộ!"
            )
            st.rerun()
        except Exception as e:
            st.error(f"Lỗi khi đọc file Excel: {e}")

    st.markdown("---")
    st.write(
        "📋 **Danh sách Hồ sơ Cán bộ hiện tại (Cho phép Thêm / Sửa / Xóa dòng"
        " trực tiếp):**"
    )

    # Lưới chỉnh sửa duy nhất
    edited_employees = st.data_editor(
        df_emp_current,
        use_container_width=True,
        num_rows="dynamic",
        key="editor_single_employee_table",
    )

    if st.button("💾 Lưu thay đổi Hồ sơ Cán bộ vào CSDL", type="primary"):
        st.session_state["employees_profile"] = edited_employees
        if supabase:
            try:
                supabase.table("categories").upsert({
                    "cat_key": "employees_profile",
                    "title": "Hồ sơ Cán bộ Nhân viên",
                    "content": edited_employees.to_dict(orient="records"),
                }).execute()
                st.success(
                    "✅ Đã lưu thành công dữ liệu hồ sơ cán bộ vào cơ sở dữ"
                    " liệu vĩnh viễn!"
                )
                st.rerun()
            except Exception as e:
                st.error(f"Lỗi khi lưu CSDL: {e}")
        else:
            st.success(
                "✅ Đã lưu dữ liệu tạm thời vào hệ thống phiên làm việc!"
            )
