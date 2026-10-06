import pandas as pd
import streamlit as st
import io
from supabase import create_client

# Khởi tạo kết nối Supabase
@st.cache_resource
def init_supabase():
    try:
        url = st.secrets.get("SUPABASE_URL", "").strip()
        key = (st.secrets.get("SUPABASE_KEY") or st.secrets.get("SUPABASE_SERVICE_KEY", "")).strip()
        if not url or not key:
            return None
        return create_client(url, key)
    except Exception:
        return None

def load_employees_data(supabase):
    # Ưu tiên lấy từ session_state nếu có để thao tác mượt mà
    if "employees_profile" in st.session_state:
        df_ses = st.session_state["employees_profile"]
        if isinstance(df_ses, pd.DataFrame) and not df_ses.empty:
            return df_ses

    if not supabase:
        # Dữ liệu rỗng mặc định nếu không kết nối được
        return pd.DataFrame(columns=["Mã NV", "Họ và tên", "Ngày sinh", "Giới tính", "Đơn vị", "Chức vụ", "Hợp đồng"])

    try:
        res = supabase.table("categories").select("content").eq("cat_key", "employees_profile").execute()
        if res.data and res.data[0]["content"]:
            df = pd.DataFrame(res.data[0]["content"])
            # Đồng bộ tên cột
            if "Mã CB" in df.columns: df.rename(columns={"Mã CB": "Mã NV"}, inplace=True)
            if "Khoa / Phòng" in df.columns: df.rename(columns={"Khoa / Phòng": "Đơn vị"}, inplace=True)
            if "Chức vụ / Chức danh" in df.columns: df.rename(columns={"Chức vụ / Chức danh": "Chức vụ"}, inplace=True)
            return df
        return pd.DataFrame(columns=["Mã NV", "Họ và tên", "Ngày sinh", "Giới tính", "Đơn vị", "Chức vụ", "Hợp đồng"])
    except Exception:
        return pd.DataFrame(columns=["Mã NV", "Họ và tên", "Ngày sinh", "Giới tính", "Đơn vị", "Chức vụ", "Hợp đồng"])

def render_employee_management():
    st.markdown("### 👤 Quản lý Hồ sơ Cán bộ (Mẫu Sơ yếu lý lịch chuẩn Bộ Nội vụ)")
    supabase = init_supabase()
    df_emp_all = load_employees_data(supabase)

    # Chia cột cho các nút công cụ
    col_btn1, col_btn2, col_btn3 = st.columns([2, 2, 6])
    
    with col_btn1:
        # Tạo file Excel mẫu trong bộ nhớ
        output_template = io.BytesIO()
        with pd.ExcelWriter(output_template, engine="openpyxl") as writer:
            sample_df = pd.DataFrame(columns=["Mã NV", "Họ và tên", "Ngày sinh", "Giới tính", "Quê quán", "Đơn vị", "Chức vụ", "Hợp đồng", "Trạng thái", "Điện thoại"])
            sample_df.to_excel(writer, index=False, sheet_name="HoSoCanBo")
        output_template.seek(0)

        st.download_button(
            label="📥 Tải File Excel Mẫu",
            data=output_template,
            file_name="Mau_Ho_So_Can_Bo.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="secondary"
        )

    with col_btn2:
        uploaded_emp_file = st.file_uploader("📤 Upload File Hồ Sơ", type=["xlsx", "xls"], label_visibility="collapsed")

    # Xử lý khi người dùng upload file
    if uploaded_emp_file:
        try:
            df_uploaded = pd.read_excel(uploaded_emp_file).fillna("")
            # Chuẩn hóa tên cột
            if "Mã CB" in df_uploaded.columns: df_uploaded.rename(columns={"Mã CB": "Mã NV"}, inplace=True)
            if "Khoa / Phòng" in df_uploaded.columns: df_uploaded.rename(columns={"Khoa / Phòng": "Đơn vị"}, inplace=True)
            if "Chức vụ / Chức danh" in df_uploaded.columns: df_uploaded.rename(columns={"Chức vụ / Chức danh": "Chức vụ"}, inplace=True)

            st.session_state["employees_profile"] = df_uploaded
            if supabase:
                supabase.table("categories").upsert({
                    "cat_key": "employees_profile",
                    "title": "Hồ sơ Cán bộ Nhân viên",
                    "content": df_uploaded.to_dict(orient="records")
                }).execute()
            st.success(f"✅ Đã tải lên và cập nhật thành công {len(df_uploaded)} hồ sơ!")
            st.rerun()
        except Exception as e:
            st.error(f"Lỗi đọc file: {e}")

    st.markdown("---")
    st.write("📋 **Danh sách Hồ sơ Cán bộ (Thêm/Sửa/Xóa trực tiếp trên bảng):**")

    # Hiển thị bảng Data Editor cho phép CRUD trực tiếp
    edited_employees = st.data_editor(
        df_emp_all,
        use_container_width=True,
        num_rows="dynamic",
        key="editor_employees_profile"
    )

    # Nút lưu thay đổi sau khi chỉnh sửa trên lưới
    if st.button("💾 Lưu thay đổi vào CSDL", type="primary"):
        st.session_state["employees_profile"] = edited_employees
        if supabase:
            try:
                supabase.table("categories").upsert({
                    "cat_key": "employees_profile",
                    "title": "Hồ sơ Cán bộ Nhân viên",
                    "content": edited_employees.to_dict(orient="records")
                }).execute()
                st.success("✅ Đã lưu thành công dữ liệu hồ sơ vào hệ thống!")
                st.rerun()
            except Exception as e:
                st.error(f"Lỗi khi lưu CSDL: {e}")
        else:
            st.success("✅ Đã cập nhật dữ liệu tạm thời (Không có kết nối Supabase)!")
