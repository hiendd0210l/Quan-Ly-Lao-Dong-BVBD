import io
import json
import os
import pandas as pd
import streamlit as st
from supabase import create_client


# ---------------------------------------------------------
# 1. KẾT NỐI SUPABASE AN TOÀN
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


supabase = init_supabase()

# ---------------------------------------------------------
# 2. DỮ LIỆU CẤU TRÚC MẪU SƠ YẾU LÝ LỊCH (MẪU 2C/TCTW-9 & BNV)
# ---------------------------------------------------------
DEFAULT_EMPLOYEES_DF = pd.DataFrame({
    "Mã CB": ["CB0012", "CB0145", "CB0233"],
    "Họ và tên": ["Nguyễn Văn An", "Trần Thị Bích", "Lê Hoàng Cường"],
    "Tên gọi khác": ["Không", "Không", "Không"],
    "Ngày sinh": ["15/08/1985", "20/10/1990", "12/03/1982"],
    "Giới tính": ["Nam", "Nữ", "Nam"],
    "Quê quán": [
        "Ninh Giang, Hải Dương",
        "Thanh Xuân, Hà Nội",
        "Ý Yên, Nam Định",
    ],
    "Nơi ở hiện nay": ["Thanh Xuân, Hà Nội", "Cầu Giấy, Hà Nội", "Hà Đông, Hà Nội"],
    "Số CCCD / CMND": ["001085001234", "001190005678", "001082009012"],
    "Dân tộc": ["Kinh", "Kinh", "Kinh"],
    "Tôn giáo": ["Không", "Không", "Không"],
    "Thành phần gia đình": ["Cán bộ", "Công chức", "Nông dân"],
    "Chức vụ / Chức danh": [
        "Phó khoa Ngoại",
        "Điều dưỡng trưởng",
        "Bác sĩ điều trị",
    ],
    "Khoa / Phòng": [
        "Khoa Ngoại tổng hợp",
        "Khoa Khám bệnh",
        "Khoa Cấp cứu",
    ],
    "Mã ngạch": ["V.08.01.02", "V.08.05.12", "V.08.01.03"],
    "Tên ngạch": ["Bác sĩ chính (Hạng II)", "Điều dưỡng (Hạng IV)", "Bác sĩ (Hạng III)"],
    "Bậc lương": [4, 6, 3],
    "Hệ số lương": [5.42, 2.86, 3.00],
    "Ngày hưởng lương": ["01/01/2022", "01/06/2021", "01/01/2023"],
    "Phụ cấp chức vụ": [0.5, 0.3, 0.0],
    "Trình độ chuyên môn": [
        "Thạc sĩ Y khoa",
        "Cử nhân Điều dưỡng",
        "Bác sĩ CKI",
    ],
    "Học hàm / Học vị": ["Thạc sĩ", "Cử nhân", "BSCKI"],
    "Lý luận chính trị": ["Trung cấp", "Sơ cấp", "Sơ cấp"],
    "Ngoại ngữ": ["Anh văn B1", "Anh văn A2", "Anh văn B1"],
    "Tin học": ["Đạt chuẩn CNTT", "Đạt chuẩn CNTT", "Đạt chuẩn CNTT"],
    "Ngày vào Đảng": ["22/05/2015", "", "10/10/2018"],
    "Ngày chính thức": ["22/05/2016", "", "10/10/2019"],
    "Ngày tuyển dụng": ["12/01/2010", "01/06/2014", "15/08/2008"],
    "Số CCHN Y tế": ["001234/HNO-CCHN", "005678/HNO-CCHN", "009012/HNO-CCHN"],
    "Trạng thái": ["Đang công tác", "Đang công tác", "Đang công tác"],
    "Ghi chú": ["", "", ""],
})


# ---------------------------------------------------------
# 3. HÀM TƯƠNG TÁC CSDL SUPABASE
# ---------------------------------------------------------
def load_employees_data():
    if not supabase:
        return DEFAULT_EMPLOYEES_DF

    try:
        res = (
            supabase.table("categories")
            .select("content")
            .eq("cat_key", "employees_profile")
            .execute()
        )
        data = res.data
        if data and len(data) > 0 and data[0]["content"]:
            return pd.DataFrame(data[0]["content"])
        else:
            # Lưu mẫu ban đầu vào DB nếu chưa có
            save_employees_data(DEFAULT_EMPLOYEES_DF)
            return DEFAULT_EMPLOYEES_DF
    except Exception:
        return DEFAULT_EMPLOYEES_DF


def save_employees_data(df):
    if not supabase:
        return False

    try:
        clean_df = df.fillna("")
        records = clean_df.to_dict(orient="records")
        payload = {
            "cat_key": "employees_profile",
            "title": "👨‍⚕️ Quản lý Hồ sơ Cán bộ",
            "content": records,
        }
        supabase.table("categories").upsert(payload).execute()
        return True
    except Exception as e:
        st.error(f"Lỗi khi lưu vào CSDL: {e}")
        return False


# ---------------------------------------------------------
# 4. HÀM HỖ TRỢ EXCEL VÀ CONFIG CỘT
# ---------------------------------------------------------
def convert_df_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="HoSoCanBo")
    output.seek(0)
    return output


def build_safe_column_config(df):
    column_config = {}
    if df is None or df.empty:
        return column_config

    for col in df.columns:
        col_str_series = df[col].fillna("").astype(str)
        max_data_len = (
            col_str_series.str.len().max() if not col_str_series.empty else 0
        )
        max_len = max(int(max_data_len or 0), len(str(col)))

        if max_len <= 10:
            width_type = "small"
        elif max_len <= 25:
            width_type = "medium"
        else:
            width_type = "large"

        column_config[str(col)] = st.column_config.Column(
            label=str(col), width=width_type
        )
    return column_config


# ---------------------------------------------------------
# 5. GIAO DIỆN QUẢN LÝ HỒ SƠ CÁN BỘ CHÍNH
# ---------------------------------------------------------
def render_employee_management():
    st.subheader("👨‍⚕️ Quản lý Hồ sơ Cán bộ (Mẫu Sơ yếu lý lịch chuẩn Bộ Nội vụ)")

    session_key = "df_employees_profile"
    version_key = "ver_employees_profile"

    if session_key not in st.session_state:
        st.session_state[session_key] = load_employees_data()

    if version_key not in st.session_state:
        st.session_state[version_key] = 0

    # -----------------------------------------------------
    # TAB FUNCTIONALITIES: 1. Xem/Sửa danh sách | 2. Thêm cá nhân mới
    # -----------------------------------------------------
    tab_list, tab_add_single = st.tabs([
        "📋 Danh sách & Thao tác Bảng",
        "➕ Thêm Cán bộ Riêng lẻ (Sơ yếu lý lịch Form)",
    ])

    # =====================================================
    # TAB 1: BẢNG DỮ LIỆU & CÔNG CỤ QUẢN LÝ
    # =====================================================
    with tab_list:
        # A. EXPANDER 1: EXCEL IMPORT/EXPORT
        with st.expander(
            "📊 NHẬP DỮ LIỆU TỪ EXCEL / TẢI FILE EXCEL MẪU HỒ SƠ", expanded=False
        ):
            col_ex1, col_ex2 = st.columns([1, 2])

            with col_ex1:
                st.markdown("**1. Tải file Excel mẫu Hồ sơ (.xlsx):**")
                excel_data = convert_df_to_excel(DEFAULT_EMPLOYEES_DF)
                st.download_button(
                    label="📥 Tải xuống File mẫu Hồ sơ Cán bộ",
                    data=excel_data,
                    file_name="Mau_SoYeuLyLich_CanBo.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="btn_dl_employees_sample",
                )

            with col_ex2:
                st.markdown("**2. Tải lên file Excel/CSV để cập nhật:**")
                uploaded_file = st.file_uploader(
                    "Chọn file Excel hồ sơ từ máy tính:",
                    type=["xlsx", "xls", "csv"],
                    key=f"upload_emp_{st.session_state[version_key]}",
                )

            if uploaded_file is not None:
                try:
                    if uploaded_file.name.endswith(".csv"):
                        df_excel = pd.read_csv(uploaded_file)
                    else:
                        df_excel = pd.read_excel(uploaded_file)

                    df_excel = df_excel.fillna("")
                    st.write("📌 **Xem trước dữ liệu hồ sơ tải lên:**")
                    st.dataframe(df_excel.head(5), use_container_width=True)

                    col_b1, col_b2 = st.columns(2)
                    with col_b1:
                        if st.button(
                            "➕ Nhập nối tiếp vào bảng hiện tại",
                            key="btn_append_emp",
                        ):
                            new_df = pd.concat(
                                [st.session_state[session_key], df_excel],
                                ignore_index=True,
                            ).drop_duplicates()
                            st.session_state[session_key] = new_df
                            save_employees_data(new_df)
                            st.session_state[version_key] += 1
                            st.success("✅ Đã cập nhật nối tiếp thành công!")
                            st.rerun()

                    with col_b2:
                        if st.button(
                            "🔄 Ghi đè toàn bộ dữ liệu hồ sơ cũ",
                            type="primary",
                            key="btn_overwrite_emp",
                        ):
                            st.session_state[session_key] = df_excel
                            save_employees_data(df_excel)
                            st.session_state[version_key] += 1
                            st.success("✅ Đã ghi đè dữ liệu thành công!")
                            st.rerun()
                except Exception as e:
                    st.error(f"Lỗi đọc file: {e}")

        # B. EXPANDER 2: QUẢN LÝ CỘT TIÊU ĐỀ
        with st.expander(
            "🛠️ QUẢN LÝ CỘT TIÊU ĐỀ HỒ SƠ (THÊM / SỬA / XÓA CỘT)", expanded=False
        ):
            c_add, c_edit, c_del = st.columns(3)

            with c_add:
                st.markdown("**➕ Thêm cột thông tin mới**")
                new_col = st.text_input(
                    "Nhập tên cột mới (ví dụ: Nhóm máu, Kỹ năng...):",
                    key="txt_add_col_emp",
                )
                if st.button("Thêm cột", key="btn_add_col_emp"):
                    if (
                        new_col
                        and new_col
                        not in st.session_state[session_key].columns
                    ):
                        st.session_state[session_key][new_col] = ""
                        save_employees_data(st.session_state[session_key])
                        st.session_state[version_key] += 1
                        st.success(f"Đã thêm cột '{new_col}'")
                        st.rerun()

            with c_edit:
                st.markdown("**✏️ Đổi tên cột tiêu đề**")
                cols = list(st.session_state[session_key].columns)
                col_to_rename = st.selectbox(
                    "Chọn cột cần đổi:", cols, key="sel_rename_emp"
                )
                renamed_name = st.text_input("Tên mới:", key="txt_rename_emp")
                if st.button("Đổi tên", key="btn_rename_emp"):
                    if renamed_name and col_to_rename:
                        st.session_state[session_key] = st.session_state[
                            session_key
                        ].rename(columns={col_to_rename: renamed_name})
                        save_employees_data(st.session_state[session_key])
                        st.session_state[version_key] += 1
                        st.success("Đã đổi tên cột thành công!")
                        st.rerun()

            with c_del:
                st.markdown("**🗑️ Xóa cột khỏi hồ sơ**")
                cols = list(st.session_state[session_key].columns)
                col_to_del = st.selectbox(
                    "Chọn cột cần xóa:", cols, key="sel_del_emp"
                )
                if st.button("Xóa cột", type="primary", key="btn_del_col_emp"):
                    if col_to_del in st.session_state[session_key].columns:
                        st.session_state[session_key] = st.session_state[
                            session_key
                        ].drop(columns=[col_to_del])
                        save_employees_data(st.session_state[session_key])
                        st.session_state[version_key] += 1
                        st.success(f"Đã xóa cột '{col_to_del}'")
                        st.rerun()

        # C. EXPANDER 3: XÓA HÀNG CÁN BỘ
        with st.expander("🗑️ XÓA HỒ SƠ CÁN BỘ KHỎI DANH SÁCH", expanded=False):
            current_df_del = st.session_state[session_key]
            if not current_df_del.empty:
                col_del_row1, col_del_row2 = st.columns([3, 1])

                with col_del_row1:
                    row_options = [
                        f"Mã: {row.get('Mã CB', idx)} - {row.get('Họ và tên', 'Hàng ' + str(idx+1))}"
                        for idx, row in current_df_del.iterrows()
                    ]
                    selected_rows_to_del = st.multiselect(
                        "Chọn các cán bộ muốn xóa:",
                        options=range(len(row_options)),
                        format_func=lambda x: row_options[x],
                        key="msel_del_rows_emp",
                    )

                with col_del_row2:
                    st.write("")
                    st.write("")
                    if st.button(
                        "❌ Xóa hồ sơ đã chọn",
                        type="primary",
                        key="btn_del_rows_emp",
                    ):
                        if selected_rows_to_del:
                            updated_df = current_df_del.drop(
                                index=selected_rows_to_del
                            ).reset_index(drop=True)
                            st.session_state[session_key] = updated_df
                            save_employees_data(updated_df)
                            st.session_state[version_key] += 1
                            st.success(
                                f"Đã xóa {len(selected_rows_to_del)} cán bộ!"
                            )
                            st.rerun()
                        else:
                            st.warning("Vui lòng chọn ít nhất 1 cán bộ để xóa.")
            else:
                st.info("Danh sách hồ sơ hiện tại đang trống.")

        # D. BẢNG DỮ LIỆU CHỈNH SỬA TƯƠNG TÁC
        st.write("")
        current_df = st.session_state[session_key].fillna("")
        safe_column_config = build_safe_column_config(current_df)

        editor_dynamic_key = (
            f"editor_emp_v{st.session_state[version_key]}"
        )

        edited_df = st.data_editor(
            current_df,
            use_container_width=False,
            column_config=safe_column_config,
            num_rows="dynamic",
            key=editor_dynamic_key,
        )

        col_save, col_reload = st.columns([3, 1])

        with col_save:
            if st.button(
                "💾 Lưu thông tin Hồ sơ Cán bộ vĩnh viễn",
                type="primary",
                key="btn_save_emp",
            ):
                st.session_state[session_key] = edited_df
                if save_employees_data(edited_df):
                    st.success(
                        "✅ Dữ liệu Hồ sơ Cán bộ đã được lưu vĩnh viễn vào"
                        " CSDL Supabase!"
                    )

        with col_reload:
            if st.button("🔄 Tải lại từ CSDL", key="btn_reload_emp"):
                st.session_state[session_key] = load_employees_data()
                st.session_state[version_key] += 1
                st.success("🔄 Đã tải lại dữ liệu mới nhất từ CSDL!")
                st.rerun()

    # =====================================================
    # TAB 2: BIỂU MẪU NHẬP CÁ NHÂN CÁN BỘ RIÊNG LẺ
    # =====================================================
    with tab_add_single:
        st.markdown(
            "#### 📝 Biểu mẫu khai báo Sơ yếu lý lịch Cán bộ mới (Mẫu 2C/TCTW-9)"
        )

        with st.form(key="form_add_single_employee", clear_on_submit=True):
            st.markdown("##### I. THÔNG TIN CÁ NHÂN & THƯỜNG TRÚ")
            f_col1, f_col2, f_col3 = st.columns(3)
            with f_col1:
                macb = st.text_input("Mã Cán bộ (*):", placeholder="CB0001")
                fullname = st.text_input("Họ và tên khai sinh (*):")
                other_name = st.text_input("Các tên gọi khác:", value="Không")
            with f_col2:
                dob = st.text_input("Ngày sinh (dd/mm/yyyy):")
                gender = st.selectbox("Giới tính:", ["Nam", "Nữ"])
                cccd = st.text_input("Số CCCD/CMND (*):")
            with f_col3:
                dantoc = st.text_input("Dân tộc:", value="Kinh")
                tongiao = st.text_input("Tôn giáo:", value="Không")
                giadinh = st.text_input(
                    "Thành phần gia đình:", value="Cán bộ, công chức"
                )

            f_addr1, f_addr2 = st.columns(2)
            with f_addr1:
                quequan = st.text_input("Quê quán:")
            with f_addr2:
                noio = st.text_input("Nơi ở hiện nay:")

            st.markdown("---")
            st.markdown("##### II. CHỨC DANH, ĐƠN VỊ & NGẠCH LƯƠNG")
            f_job1, f_job2, f_job3 = st.columns(3)
            with f_job1:
                chucvu = st.text_input("Chức vụ / Chức danh công tác:")
                khoaphong = st.text_input("Khoa / Phòng / Đơn vị:")
                cchn = st.text_input("Số CCHN Y tế (nếu có):")
            with f_job2:
                mangach = st.text_input("Mã ngạch (vd: V.08.01.02):")
                tenngach = st.text_input("Tên ngạch lương:")
                bacluong = st.number_input("Bậc lương:", min_value=1, max_value=12, value=1)
            with f_job3:
                heso = st.number_input("Hệ số lương:", min_value=1.0, max_value=10.0, value=2.34, step=0.01)
                phucap = st.number_input("Phụ cấp chức vụ:", min_value=0.0, max_value=2.0, value=0.0, step=0.05)
                ngayluong = st.text_input("Ngày hưởng lương (dd/mm/yyyy):")

            st.markdown("---")
            st.markdown("##### III. TRÌNH ĐỘ ĐÀO TẠO & ĐẢNG / ĐOÀN")
            f_edu1, f_edu2, f_edu3 = st.columns(3)
            with f_edu1:
                trinhdo = st.text_input("Trình độ chuyên môn cao nhất:")
                hocvi = st.text_input("Học hàm / Học vị:")
            with f_edu2:
                lyluan = st.text_input("Lý luận chính trị:", value="Sơ cấp")
                ngoaingu = st.text_input("Ngoại ngữ:", value="Anh văn B1")
            with f_edu3:
                tinhoc = st.text_input("Tin học:", value="Đạt chuẩn CNTT")
                ngaytuyendung = st.text_input("Ngày tuyển dụng (dd/mm/yyyy):")

            f_pol1, f_pol2, f_pol3 = st.columns(3)
            with f_pol1:
                ngayvaodang = st.text_input("Ngày vào Đảng (nếu có):")
            with f_pol2:
                ngaychinhthuc = st.text_input("Ngày chính thức:")
            with f_pol3:
                trangthai = st.selectbox("Trạng thái:", ["Đang công tác", "Tạm nghỉ", "Chuyển công tác", "Nghỉ hưu"])

            btn_submit_single = st.form_submit_button(
                "➕ Thêm Cán bộ vào CSDL", type="primary"
            )

            if btn_submit_single:
                if not macb or not fullname:
                    st.error("⚠️ Vui lòng điền đầy đủ Mã Cán bộ và Họ tên!")
                else:
                    new_employee_record = {
                        "Mã CB": macb,
                        "Họ và tên": fullname,
                        "Tên gọi khác": other_name,
                        "Ngày sinh": dob,
                        "Giới tính": gender,
                        "Quê quán": quequan,
                        "Nơi ở hiện nay": noio,
                        "Số CCCD / CMND": cccd,
                        "Dân tộc": dantoc,
                        "Tôn giáo": tongiao,
                        "Thành phần gia đình": giadinh,
                        "Chức vụ / Chức danh": chucvu,
                        "Khoa / Phòng": khoaphong,
                        "Mã ngạch": mangach,
                        "Tên ngạch": tenngach,
                        "Bậc lương": bacluong,
                        "Hệ số lương": heso,
                        "Ngày hưởng lương": ngayluong,
                        "Phụ cấp chức vụ": phucap,
                        "Trình độ chuyên môn": trinhdo,
                        "Học hàm / Học vị": hocvi,
                        "Lý luận chính trị": lyluan,
                        "Ngoại ngữ": ngoaingu,
                        "Tin học": tinhoc,
                        "Ngày vào Đảng": ngayvaodang,
                        "Ngày chính thức": ngaychinhthuc,
                        "Ngày tuyển dụng": ngaytuyendung,
                        "Số CCHN Y tế": cchn,
                        "Trạng thái": trangthai,
                        "Ghi chú": "",
                    }

                    # Thêm vào DataFrame hiện tại
                    updated_df = pd.concat(
                        [st.session_state[session_key], pd.DataFrame([new_employee_record])],
                        ignore_index=True,
                    )
                    st.session_state[session_key] = updated_df
                    save_employees_data(updated_df)
                    st.session_state[version_key] += 1
                    st.success(f"🎉 Đã thêm hồ sơ cán bộ '{fullname}' thành công!")
                    st.rerun()


if __name__ == "__main__":
    render_employee_management()
