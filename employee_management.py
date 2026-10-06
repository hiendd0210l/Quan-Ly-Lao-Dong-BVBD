import io
import pandas as pd
import streamlit as st
from supabase import create_client

# DANH SÁCH THỨ TỰ CỘT CHUẨN THEO MẪU SƠ YẾU LÝ LỊCH BỘ NỘI VỤ / EXCEL UPLOAD
STANDARD_COLUMN_ORDER = [
    "Mã NV",
    "Mã VNPT",
    "Họ và tên",
    "Ngày sinh",
    "Giới tính",
    "Quê quán",
    "Dân tộc",
    "Tôn giáo",
    "Mã ngạch",
    "Tên ngạch",
    "Bậc lương",
    "Hệ số lương",
    "Đơn vị",
    "Chức vụ",
    "Chức danh",
    "Trạng thái",
    "Ngoại ngữ",
    "Tin học",
    "Số CCCD / CMND",
    "Số CCHN Y tế",
    "Tôn giáo khác",
    "Ngày vào Đảng",
    "Ngày chính thức",
    "Nơi ở hiện tại",
    "Hợp đồng",
    "Điện thoại",
    "Email",
]


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


def reorder_columns(df, custom_order=None):
    """Sắp xếp lại các cột theo đúng thứ tự ưu tiên của tệp Excel upload hoặc mẫu chuẩn"""
    if df.empty:
        return df

    order = custom_order or st.session_state.get(
        "employee_columns_order", STANDARD_COLUMN_ORDER
    )
    existing_cols = df.columns.tolist()

    ordered_cols = [c for c in order if c in existing_cols]
    extra_cols = [c for c in existing_cols if c not in ordered_cols]

    return df[ordered_cols + extra_cols]


def clean_dataframe_for_json(df):
    """Xử lý và chuyển đổi tất cả kiểu dữ liệu datetime/Timestamp sang chuỗi string để gửi JSON lên CSDL"""
    df_clean = df.copy().fillna("")
    for col in df_clean.columns:
        if pd.api.types.is_datetime64_any_dtype(df_clean[col]):
            df_clean[col] = (
                df_clean[col].dt.strftime("%d/%m/%Y").fillna("").astype(str)
            )
        else:
            df_clean[col] = (
                df_clean[col]
                .astype(str)
                .str.replace(" 00:00:00", "", regex=False)
                .str.replace("NaT", "", regex=False)
                .str.replace("nan", "", regex=False)
                .str.replace("None", "", regex=False)
            )
    return df_clean


def load_employees_data(supabase_client):
    """Tải danh sách cán bộ thực tế và chuẩn hóa sắp xếp các cột"""
    df = pd.DataFrame()

    if "employees_profile" in st.session_state:
        df_ses = st.session_state["employees_profile"]
        if isinstance(df_ses, pd.DataFrame) and not df_ses.empty:
            df = df_ses.copy()

    if df.empty and supabase_client:
        try:
            res = (
                supabase_client.table("categories")
                .select("content")
                .eq("cat_key", "employees_profile")
                .execute()
            )
            if res.data and res.data[0].get("content"):
                df = pd.DataFrame(res.data[0]["content"])
        except Exception:
            pass

    if df.empty:
        df = pd.DataFrame(columns=STANDARD_COLUMN_ORDER)

    # Đồng bộ chuẩn hóa tên cột
    if "Mã CB" in df.columns and "Mã NV" not in df.columns:
        df.rename(columns={"Mã CB": "Mã NV"}, inplace=True)
    if "Khoa / Phòng" in df.columns and "Đơn vị" not in df.columns:
        df.rename(columns={"Khoa / Phòng": "Đơn vị"}, inplace=True)
    if "Chức vụ / Chức danh" in df.columns and "Chức vụ" not in df.columns:
        df.rename(columns={"Chức vụ / Chức danh": "Chức vụ"}, inplace=True)

    return reorder_columns(df)


def render_employee_management():
    st.markdown(
        "<h3 style='color: #003366;'>👤 Quản lý Hồ sơ Cán bộ (Mẫu Sơ yếu lý"
        " lịch chuẩn Bộ Nội vụ)</h3>",
        unsafe_allow_html=True,
    )

    supabase = init_supabase()
    df_emp_current = load_employees_data(supabase)

    col_btn1, col_btn2 = st.columns([2, 3])

    with col_btn1:
        # Tạo file Excel mẫu theo đúng thứ tự cột chuẩn
        output_template = io.BytesIO()
        with pd.ExcelWriter(output_template, engine="openpyxl") as writer:
            sample_df = pd.DataFrame(columns=STANDARD_COLUMN_ORDER)
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

            # Chuyển đổi các cột kiểu datetime sang chuỗi văn bản
            df_uploaded = clean_dataframe_for_json(df_uploaded)

            # Ghi nhớ lại thứ tự cột gốc của file Excel
            uploaded_cols = df_uploaded.columns.tolist()
            st.session_state["employee_columns_order"] = uploaded_cols

            st.session_state["employees_profile"] = df_uploaded

            if supabase:
                supabase.table("categories").upsert({
                    "cat_key": "employees_profile",
                    "title": "Hồ sơ Cán bộ Nhân viên",
                    "content": df_uploaded.to_dict(orient="records"),
                }).execute()

            st.toast("✅ Đã tải lên và lưu dữ liệu hồ sơ!", icon="🎉")
            st.success(
                f"✅ Đã tải lên và lưu thành công {len(df_uploaded)} hồ sơ cán"
                " bộ!"
            )
        except Exception as e:
            st.error(f"❌ Lỗi khi xử lý file Excel: {e}")

    st.markdown("---")
    st.write(
        "📋 **Danh sách Hồ sơ Cán bộ hiện tại (Hiển thị đúng theo thứ tự cột"
        " tệp Excel):**"
    )

    df_display = reorder_columns(df_emp_current)

    edited_employees = st.data_editor(
        df_display,
        use_container_width=True,
        num_rows="dynamic",
        key="editor_single_employee_table",
    )

    if st.button("💾 Lưu thay đổi Hồ sơ Cán bộ vào CSDL", type="primary"):
        # Chuẩn hóa dữ liệu trước khi chuyển thành JSON lưu CSDL
        edited_clean = clean_dataframe_for_json(edited_employees)
        st.session_state["employees_profile"] = edited_clean

        if supabase:
            try:
                supabase.table("categories").upsert({
                    "cat_key": "employees_profile",
                    "title": "Hồ sơ Cán bộ Nhân viên",
                    "content": edited_clean.to_dict(orient="records"),
                }).execute()
                st.toast("✅ Đã lưu dữ liệu vào CSDL vĩnh viễn!", icon="💾")
                st.success(
                    "✅ Đã lưu thành công danh sách hồ sơ cán bộ vào cơ sở dữ"
                    " liệu!"
                )
            except Exception as e:
                st.error(f"❌ Lỗi khi lưu vào CSDL: {e}")
        else:
            st.toast("✅ Đã cập nhật phiên làm việc!", icon="ℹ️")
            st.success("✅ Đã cập nhật dữ liệu thành công vào bộ nhớ tạm!")
