import calendar
from datetime import datetime
import io
import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
import pandas as pd
import streamlit as st
from supabase import create_client


# ---------------------------------------------------------
# 1. KẾT NỐI SUPABASE
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


# ---------------------------------------------------------
# 2. KIỂM TRA NGÀY LỄ VIỆT NAM (01/09, 02/09, 30/04, 01/05, TẾT...)
# ---------------------------------------------------------
def is_vietnam_holiday(day, month, year=2026):
    """Xác định các ngày nghỉ lễ chính thức theo quy định"""
    # Các ngày lễ cố định hàng năm
    fixed_holidays = [
        (1, 1),   # Tết Dương lịch
        (30, 4),  # 30/4 Giải phóng miền Nam
        (1, 5),   # 1/5 Quốc tế Lao động
        (1, 9),   # 1/9 Nghỉ Quốc khánh
        (2, 9),   # 2/9 Quốc khánh
    ]
    if (day, month) in fixed_holidays:
        return True

    # Ngày lễ âm lịch / nghỉ bù năm 2026
    if year == 2026:
        lunar_holidays = [(16, 2), (17, 2), (18, 2), (19, 2), (20, 2), (21, 2), (26, 4)]
        if (day, month) in lunar_holidays:
            return True

    return False


# ---------------------------------------------------------
# 3. LẤY DANH SÁCH ĐƠN VỊ TỪ MENU 2 ("DANH MỤC HỆ THỐNG")
# ---------------------------------------------------------
def load_system_units(supabase_client):
    """Đọc động danh sách Đơn vị từ mục 'Danh mục Hệ thống' (cat_key = don_vi)"""
    units = []

    if supabase_client:
        try:
            res = (
                supabase_client.table("categories")
                .select("content")
                .eq("cat_key", "don_vi")
                .execute()
            )
            if res.data and res.data[0].get("content"):
                df_dv = pd.DataFrame(res.data[0]["content"])
                for col in ["Tên đơn vị", "Tên Đơn vị", "Tên khoa / phòng", "Tên Khoa / Phòng", "Đơn vị", "Tên phòng ban"]:
                    if col in df_dv.columns:
                        units = [str(x).strip() for x in df_dv[col].dropna().tolist() if str(x).strip()]
                        if units:
                            break
        except Exception:
            pass

    if not units:
        units = ["Ban Giám đốc", "Khoa Cấp cứu", "Khoa Ngoại Tổng hợp", "Phòng Nhân sự - Tổng hợp", "Phòng Tài chính - Kế toán"]

    return units


# ---------------------------------------------------------
# 4. LỌC CHÍNH XÁC NHÂN SỰ THEO ĐƠN VỊ (LOẠI BỎ TÊN ĐƠN VỊ BỊ LẪN)
# ---------------------------------------------------------
def get_employees_by_unit(unit_name, all_units):
    """Lấy danh sách cán bộ thực sự thuộc Đơn vị chọn, loại bỏ hoàn toàn tên các phòng ban"""
    df_emp = pd.DataFrame()

    # 1. Lấy từ session_state
    if "employees_profile" in st.session_state:
        df_ses = st.session_state["employees_profile"]
        if isinstance(df_ses, pd.DataFrame) and not df_ses.empty:
            df_emp = df_ses.copy()

    # 2. Lấy từ Supabase
    if df_emp.empty:
        supabase = init_supabase()
        if supabase:
            try:
                res = (
                    supabase.table("categories")
                    .select("content")
                    .eq("cat_key", "employees_profile")
                    .execute()
                )
                if res.data and res.data[0].get("content"):
                    df_emp = pd.DataFrame(res.data[0]["content"])
            except Exception:
                pass

    if df_emp.empty:
        return pd.DataFrame(columns=["Mã NV", "Họ và tên", "Chức vụ", "Đơn vị"])

    # 3. Chuẩn hóa tên cột
    col_mapping = {}
    for col in df_emp.columns:
        c_str = str(col).strip().lower()
        if c_str in ["mã nv", "mã cb", "mã nhân viên", "ma nv", "mã cán bộ"]:
            col_mapping[col] = "Mã NV"
        elif c_str in ["họ và tên", "họ tên", "ho va ten", "tên cán bộ", "tên nhân viên"]:
            col_mapping[col] = "Họ và tên"
        elif c_str in ["chức vụ", "chức danh", "chức vụ / chức danh", "vị trí"]:
            col_mapping[col] = "Chức vụ"
        elif c_str in ["đơn vị", "khoa / phòng", "khoa/phòng", "phòng ban", "bộ phận"]:
            col_mapping[col] = "Đơn vị"

    df_emp.rename(columns=col_mapping, inplace=True)

    if "Họ và tên" not in df_emp.columns:
        return pd.DataFrame(columns=["Mã NV", "Họ và tên", "Chức vụ", "Đơn vị"])

    # 4. LỌC LOẠI BỎ TRIỆT ĐỂ BẤT KỲ DÒNG NÀO LÀ TÊN ĐƠN VỊ / PHÒNG BAN
    unit_set_lower = set(u.lower() for u in all_units)
    dept_keywords = ["phòng ", "khoa ", "ban ", "tổ ", "trung tâm "]

    def is_real_person(row):
        name = str(row.get("Họ và tên", "")).strip()
        if not name or name.lower() in ["nan", "none"]:
            return False
        # Nếu trùng đúng tên đơn vị trong danh mục
        if name.lower() in unit_set_lower:
            return False
        # Nếu bắt đầu bằng tiền tố phòng ban
        for kw in dept_keywords:
            if name.lower().startswith(kw) and name.lower() != "ban giám đốc":
                return False
        return True

    df_emp = df_emp[df_emp.apply(is_real_person, axis=1)].copy()

    # 5. Lọc theo đơn vị chọn
    if unit_name and unit_name != "Tất cả" and "Đơn vị" in df_emp.columns:
        target_unit = str(unit_name).strip().lower()

        def is_match_unit(val):
            v_str = str(val).strip().lower()
            return (target_unit == v_str) or (target_unit in v_str) or (v_str in target_unit)

        df_filtered = df_emp[df_emp["Đơn vị"].apply(is_match_unit)].copy()
        return df_filtered

    return df_emp


# ---------------------------------------------------------
# 5. TẠO FILE EXCEL MẪU TÔ MÀU NGHỈ LỄ & THỨ 7, CHỦ NHẬT
# ---------------------------------------------------------
def generate_timekeeping_excel(unit_name, month, year, df_employees):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"ChamCong_T{month}_{year}"

    # Tiêu đề đơn vị
    ws.merge_cells("A1:D1")
    ws["A1"] = "BỆNH VIỆN BƯU ĐIỆN"
    ws["A1"].font = Font(name="Arial", size=10, bold=True, color="002060")

    ws.merge_cells("A2:D2")
    ws["A2"] = str(unit_name).upper()
    ws["A2"].font = Font(name="Arial", size=10, bold=True, color="002060")

    days_in_month = calendar.monthrange(year, month)[1]
    last_col_idx = 4 + days_in_month + 5
    last_col_letter = get_column_letter(last_col_idx)

    ws.merge_cells(f"A4:{last_col_letter}4")
    ws["A4"] = f"BẢNG CHẤM CÔNG THÁNG {month}/{year} CỦA {str(unit_name).upper()}"
    ws["A4"].font = Font(name="Arial", size=12, bold=True, color="002060")
    ws["A4"].alignment = Alignment(horizontal="center", vertical="center")

    headers = ["STT", "Mã NV", "Họ và tên", "Chức vụ"]
    date_cols = [f"{d:02d}/{month:02d}" for d in range(1, days_in_month + 1)]
    summary_headers = ["Tổng công", "Số ngày nghỉ", "Phép", "Ôm / CO", "Trực"]

    all_headers = headers + date_cols + summary_headers

    # Tiêu đề cột (Dòng 5)
    for col_idx, h_text in enumerate(all_headers, start=1):
        cell = ws.cell(row=5, column=col_idx, value=h_text)
        cell.font = Font(name="Arial", size=9, bold=True, color="FFFFFF")
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

        fill_color = "1F497D"  # Xanh navy chuẩn
        if 5 <= col_idx <= 4 + days_in_month:
            d = col_idx - 4
            if is_vietnam_holiday(d, month, year):
                fill_color = "C00000"  # Đỏ rực cho Ngày Lễ
            else:
                dt = datetime(year, month, d)
                if dt.weekday() == 6:  # Chủ Nhật
                    fill_color = "C00000"  # Đỏ
                elif dt.weekday() == 5:  # Thứ 7
                    fill_color = "ED7D31"  # Cam

        cell.fill = PatternFill(start_color=fill_color, end_color=fill_color, fill_type="solid")

    # Điền danh sách cán bộ thực tế
    start_row = 6
    if not df_employees.empty and "Họ và tên" in df_employees.columns:
        for idx, (_, row_emp) in enumerate(df_employees.iterrows(), start=1):
            r = start_row + idx - 1
            ma_nv = str(row_emp.get("Mã NV") or row_emp.get("Mã CB") or "").strip()
            ho_ten = str(row_emp.get("Họ và tên") or row_emp.get("Họ tên") or "").strip()
            chuc_vu = str(row_emp.get("Chức vụ") or row_emp.get("Chức danh") or "").strip()

            ws.cell(row=r, column=1, value=idx)
            ws.cell(row=r, column=2, value=ma_nv)
            ws.cell(row=r, column=3, value=ho_ten)
            ws.cell(row=r, column=4, value=chuc_vu)

            ws.cell(row=r, column=1).alignment = Alignment(horizontal="center")
            ws.cell(row=r, column=2).alignment = Alignment(horizontal="center")
            ws.cell(row=r, column=3).alignment = Alignment(horizontal="left")
            ws.cell(row=r, column=4).alignment = Alignment(horizontal="left")

        max_row = start_row + len(df_employees) - 1
    else:
        max_row = start_row + 9
        for idx in range(1, 10):
            r = start_row + idx - 1
            ws.cell(row=r, column=1, value=idx)

    # Viền và Tô màu nền Ngày Lễ / Thứ 7 / Chủ Nhật
    thin_border = Border(
        left=Side(style="thin", color="D9D9D9"),
        right=Side(style="thin", color="D9D9D9"),
        top=Side(style="thin", color="D9D9D9"),
        bottom=Side(style="thin", color="D9D9D9"),
    )

    holiday_fill = PatternFill(start_color="FADBD8", end_color="FADBD8", fill_type="solid") # Hồng đỏ nhạt cho Ngày Lễ
    sun_fill = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid")     # Cam nhạt cho Chủ Nhật
    sat_fill = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")     # Vàng nhạt cho Thứ 7

    for r in range(6, max_row + 1):
        for c in range(1, last_col_idx + 1):
            cell = ws.cell(row=r, column=c)
            cell.border = thin_border
            cell.font = Font(name="Arial", size=9)

            if 5 <= c <= 4 + days_in_month:
                cell.alignment = Alignment(horizontal="center", vertical="center")
                d = c - 4
                if is_vietnam_holiday(d, month, year):
                    cell.fill = holiday_fill  # Tô màu nền hồng đỏ cho Ngày Lễ
                else:
                    dt = datetime(year, month, d)
                    if dt.weekday() == 6:
                        cell.fill = sun_fill
                    elif dt.weekday() == 5:
                        cell.fill = sat_fill
            elif c > 4 + days_in_month:
                cell.alignment = Alignment(horizontal="center", vertical="center")

    # Căn chỉnh độ rộng cột
    ws.column_dimensions["A"].width = 6
    ws.column_dimensions["B"].width = 14
    ws.column_dimensions["C"].width = 25
    ws.column_dimensions["D"].width = 20
    for c in range(5, 5 + days_in_month):
        ws.column_dimensions[get_column_letter(c)].width = 7
    for c in range(5 + days_in_month, last_col_idx + 1):
        ws.column_dimensions[get_column_letter(c)].width = 11

    out = io.BytesIO()
    wb.save(out)
    out.seek(0)
    return out


# ---------------------------------------------------------
# 6. GIAO DIỆN PHÂN HỆ CHẤM CÔNG
# ---------------------------------------------------------
def render_timekeeping_management():
    st.markdown(
        "<h3 style='color: #003366;'>📅 Chấm công - Ca trực - Phân lịch</h3>",
        unsafe_allow_html=True,
    )

    supabase = init_supabase()

    # 1. Đọc liên kết danh sách Đơn vị từ mục "Danh mục Hệ thống"
    all_units = load_system_units(supabase)

    col_f1, col_f2, col_f3 = st.columns([2, 2, 4])
    with col_f1:
        selected_month = st.selectbox("Chọn Tháng:", list(range(1, 13)), index=8) # Mặc định Tháng 9
    with col_f2:
        selected_year = st.selectbox("Chọn Năm:", [2025, 2026, 2027], index=1)
    with col_f3:
        selected_unit = st.selectbox("Chọn Đơn vị / Khoa / Phòng:", all_units)

    # 2. Truy vấn danh sách cán bộ thực sự của đơn vị chọn
    df_unit_emp = get_employees_by_unit(selected_unit, all_units)

    st.markdown("---")
    col_act1, col_act2 = st.columns([3, 4])

    with col_act1:
        excel_data = generate_timekeeping_excel(
            selected_unit, selected_month, selected_year, df_unit_emp
        )
        file_name_clean = selected_unit.replace(" ", "_")
        st.download_button(
            label=f"📥 Tải File Excel Mẫu Chấm Công ({len(df_unit_emp)} Cán bộ)",
            data=excel_data,
            file_name=f"Mau_Cham_Cong_{file_name_clean}_T{selected_month}_{selected_year}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
        )

    with col_act2:
        uploaded_file = st.file_uploader(
            "📤 Upload Tệp Bảng Chấm Công (.xlsx)",
            type=["xlsx", "xls"],
            key="up_tk_file",
        )

    if uploaded_file:
        try:
            df_up = pd.read_excel(uploaded_file, skiprows=4).fillna("")
            st.session_state[f"tk_{selected_unit}_{selected_month}_{selected_year}"] = df_up
            st.toast("✅ Đã tải lên thành công bảng chấm công!", icon="🎉")
            st.success("✅ Đã cập nhật thành công bảng chấm công từ file Excel!")
        except Exception as e:
            st.error(f"Lỗi đọc file chấm công: {e}")

    st.markdown("---")
    st.write(
        f"📋 **Bảng Chấm công Tháng {selected_month}/{selected_year} -"
        f" {selected_unit}:**"
    )

    days_in_month = calendar.monthrange(selected_year, selected_month)[1]
    tk_key = f"tk_{selected_unit}_{selected_month}_{selected_year}"

    if tk_key in st.session_state:
        df_tk_display = st.session_state[tk_key]
    else:
        cols = ["STT", "Mã NV", "Họ và tên", "Chức vụ"] + [
            f"{d:02d}/{selected_month:02d}" for d in range(1, days_in_month + 1)
        ]
        if not df_unit_emp.empty and "Họ và tên" in df_unit_emp.columns:
            data_rows = []
            for idx, (_, r) in enumerate(df_unit_emp.iterrows(), start=1):
                row_dict = {
                    "STT": idx,
                    "Mã NV": str(r.get("Mã NV") or r.get("Mã CB") or "").strip(),
                    "Họ và tên": str(r.get("Họ và tên") or r.get("Họ tên") or "").strip(),
                    "Chức vụ": str(r.get("Chức vụ") or r.get("Chức danh") or "").strip(),
                }
                # MẶC ĐỊNH ĐỂ TRỐNG Ô CHẤM CÔNG (KHÔNG TỰ Ý ĐIỀN CHỮ X VÔ NGHĨA)
                for d in range(1, days_in_month + 1):
                    row_dict[f"{d:02d}/{selected_month:02d}"] = ""
                data_rows.append(row_dict)
            df_tk_display = pd.DataFrame(data_rows)
        else:
            df_tk_display = pd.DataFrame(columns=cols)
            st.info(
                f"ℹ️ Đơn vị **{selected_unit}** hiện chưa có hồ sơ cán bộ đăng ký trong hệ thống. "
                f"Bạn có thể thêm dòng trực tiếp trên bảng bên dưới hoặc nhập danh sách tại mục **4. Quản lý Hồ sơ Cán bộ**."
            )

    # Tô màu Nền Ngày Lễ, Thứ 7, Chủ Nhật trên bảng giao diện Streamlit
    def highlight_days(col):
        col_name = str(col.name)
        if "/" in col_name:
            try:
                day_num = int(col_name.split("/")[0])
                # Tô màu Nền Ngày Lễ (như 01/09, 02/09)
                if is_vietnam_holiday(day_num, selected_month, selected_year):
                    return [
                        "background-color: #FADBD8; color: #78281F; font-weight: bold"
                    ] * len(col)
                dt = datetime(selected_year, selected_month, day_num)
                if dt.weekday() == 6:  # Chủ Nhật
                    return [
                        "background-color: #FCE4D6; color: #9C0006; font-weight: bold"
                    ] * len(col)
                elif dt.weekday() == 5:  # Thứ 7
                    return [
                        "background-color: #FFF2CC; color: #9C6500"
                    ] * len(col)
            except Exception:
                pass
        return [""] * len(col)

    styled_df = df_tk_display.style.apply(highlight_days, axis=0)

    edited_tk = st.data_editor(
        styled_df,
        use_container_width=True,
        num_rows="dynamic",
        key=f"editor_{tk_key}",
    )

    if st.button("💾 Lưu Bảng Chấm Công", type="primary"):
        st.session_state[tk_key] = edited_tk
        st.toast("✅ Đã lưu dữ liệu chấm công thành công!", icon="💾")
        st.success("✅ Đã lưu dữ liệu chấm công!")
