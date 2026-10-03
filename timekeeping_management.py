import calendar
from datetime import date, datetime
import io
import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
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


supabase = init_supabase()

# ---------------------------------------------------------
# 2. QUY ƯỚC KÝ HIỆU CHẤM CÔNG MẶC ĐỊNH
# ---------------------------------------------------------
DEFAULT_TIMEKEEPING_RULES = [
    {"Ký hiệu": "X", "Diễn giải": "½ ngày công làm việc giờ hành chính"},
    {"Ký hiệu": "XX", "Diễn giải": "1 ngày công làm việc giờ hành chính"},
    {"Ký hiệu": "T", "Diễn giải": "1 ngày trực ngoài giờ hành chính"},
    {"Ký hiệu": "B", "Diễn giải": "½ ngày nghỉ bù trực hưởng nguyên lương"},
    {"Ký hiệu": "BB", "Diễn giải": "1 ngày nghỉ bù trực hưởng nguyên lương"},
    {"Ký hiệu": "P", "Diễn giải": "½ ngày nghỉ phép"},
    {"Ký hiệu": "PP", "Diễn giải": "1 ngày nghỉ phép"},
    {"Ký hiệu": "H", "Diễn giải": "½ ngày đi học"},
    {"Ký hiệu": "HH", "Diễn giải": "1 ngày đi học"},
    {"Ký hiệu": "CT", "Diễn giải": "½ ngày đi công tác"},
    {"Ký hiệu": "CTCT", "Diễn giải": "1 ngày đi công tác"},
    {"Ký hiệu": "Ô", "Diễn giải": "½ ngày nghỉ ốm"},
    {"Ký hiệu": "ÔÔ", "Diễn giải": "1 ngày nghỉ ốm"},
    {"Ký hiệu": "Co", "Diễn giải": "½ ngày nghỉ con ốm"},
    {"Ký hiệu": "CoCo", "Diễn giải": "1 ngày nghỉ con ốm"},
    {
        "Ký hiệu": "R",
        "Diễn giải": "½ ngày nghỉ việc riêng hưởng nguyên lương",
    },
    {"Ký hiệu": "RR", "Diễn giải": "1 ngày nghỉ việc riêng hưởng nguyên lương"},
    {"Ký hiệu": "Ko", "Diễn giải": "1 ngày nghỉ không hưởng lương"},
    {"Ký hiệu": "TS", "Diễn giải": "1 ngày nghỉ thai sản"},
]

DEFAULT_DON_VI = [
    "Khoa Cấp cứu",
    "Khoa Khám bệnh",
    "Khoa Ngoại tổng hợp",
    "Khoa Dược",
    "Khoa Hồi sức tích cực",
    "Phòng Tổ chức Cán bộ",
    "Phòng Tài chính Kế toán",
    "Phòng Kế hoạch Tổng hợp",
]

DEFAULT_CAN_BO = [
    {
        "Mã NV": "NV001",
        "Họ và tên": "Nguyễn Văn An",
        "Chức vụ": "Bác sĩ CKI",
        "Đơn vị": "Khoa Cấp cứu",
    },
    {
        "Mã NV": "NV002",
        "Họ và tên": "Trần Thị Bích",
        "Chức vụ": "Điều dưỡng trưởng",
        "Đơn vị": "Khoa Cấp cứu",
    },
    {
        "Mã NV": "NV003",
        "Họ và tên": "Lê Hoàng Cường",
        "Chức vụ": "Bác sĩ chính",
        "Đơn vị": "Khoa Ngoại tổng hợp",
    },
    {
        "Mã NV": "NV004",
        "Họ và tên": "Phạm Minh Đức",
        "Chức vụ": "Dược sĩ CKI",
        "Đơn vị": "Khoa Dược",
    },
    {
        "Mã NV": "NV005",
        "Họ và tên": "Vũ Thị Dung",
        "Chức vụ": "Chuyên viên TCCB",
        "Đơn vị": "Phòng Tổ chức Cán bộ",
    },
]


# ---------------------------------------------------------
# 3. KẾT NỐI VÀ LƯU TRỮ CSDL
# ---------------------------------------------------------
def load_timekeeping_rules():
    if not supabase:
        return pd.DataFrame(DEFAULT_TIMEKEEPING_RULES)
    try:
        res = (
            supabase.table("categories")
            .select("content")
            .eq("cat_key", "tk_rules")
            .execute()
        )
        if res.data and res.data[0]["content"]:
            df_res = pd.DataFrame(res.data[0]["content"])
            return df_res[["Ký hiệu", "Diễn giải"]]
        return pd.DataFrame(DEFAULT_TIMEKEEPING_RULES)
    except Exception:
        return pd.DataFrame(DEFAULT_TIMEKEEPING_RULES)


def save_timekeeping_rules(df_rules):
    if not supabase:
        return True
    try:
        clean_df = df_rules[["Ký hiệu", "Diễn giải"]].fillna("")
        payload = {
            "cat_key": "tk_rules",
            "title": "Quy ước Ký hiệu Chấm công",
            "content": clean_df.to_dict(orient="records"),
        }
        supabase.table("categories").upsert(payload).execute()
        return True
    except Exception as e:
        st.error(f"Lỗi khi lưu quy ước: {e}")
        return False


def load_employees():
    if not supabase:
        return pd.DataFrame(DEFAULT_CAN_BO)
    try:
        res = (
            supabase.table("categories")
            .select("content")
            .eq("cat_key", "employees_profile")
            .execute()
        )
        if res.data and res.data[0]["content"]:
            df = pd.DataFrame(res.data[0]["content"])
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
            return df[["Mã NV", "Họ và tên", "Chức vụ", "Đơn vị"]]
        return pd.DataFrame(DEFAULT_CAN_BO)
    except Exception:
        return pd.DataFrame(DEFAULT_CAN_BO)


def load_timekeeping_db(month, year):
    key_db = f"tk_{year}_{month:02d}"
    if not supabase:
        return st.session_state.get(key_db, pd.DataFrame())
    try:
        res = (
            supabase.table("categories")
            .select("content")
            .eq("cat_key", key_db)
            .execute()
        )
        if res.data and res.data[0]["content"]:
            return pd.DataFrame(res.data[0]["content"])
        return pd.DataFrame()
    except Exception:
        return st.session_state.get(key_db, pd.DataFrame())


def save_timekeeping_db(df, month, year):
    key_db = f"tk_{year}_{month:02d}"
    st.session_state[key_db] = df
    if not supabase:
        return True
    try:
        clean_df = df.fillna("")
        payload = {
            "cat_key": key_db,
            "title": f"Bảng chấm công Tháng {month}/{year}",
            "content": clean_df.to_dict(orient="records"),
        }
        supabase.table("categories").upsert(payload).execute()
        return True
    except Exception as e:
        st.error(f"Lỗi lưu CSDL: {e}")
        return False


# ---------------------------------------------------------
# 4. TẠO FILE EXCEL MẪU TỰ ĐỘNG CHUẨN ĐỊNH DẠNG & BỐ CỤC
# ---------------------------------------------------------
def generate_timekeeping_template(
    df_emp_unit, month, year, unit_name, df_rules
):
    wb = openpyxl.Workbook()

    # --- SHEET 2: QUY UOC KY HIEU ---
    ws_rules = wb.active
    ws_rules.title = "QuyUocKyHieu"
    ws_rules["A1"] = "BẢNG QUY ƯỚC KÝ HIỆU CHẤM CÔNG CHUẨN BỘ Y TẾ & BỘ NỘI VỤ"
    ws_rules["A1"].font = Font(name="Arial", size=12, bold=True, color="003366")

    header_font = Font(name="Arial", size=10, bold=True, color="FFFFFF")
    rule_headers = ["STT", "Ký hiệu", "Tên ký hiệu / Diễn giải"]
    ws_rules.append([])
    ws_rules.append(rule_headers)

    thin_border = Border(
        left=Side(style="thin", color="CCCCCC"),
        right=Side(style="thin", color="CCCCCC"),
        top=Side(style="thin", color="CCCCCC"),
        bottom=Side(style="thin", color="CCCCCC"),
    )

    for col_idx in range(1, len(rule_headers) + 1):
        cell = ws_rules.cell(row=3, column=col_idx)
        cell.font = header_font
        cell.fill = PatternFill(
            start_color="2F5597", end_color="2F5597", fill_type="solid"
        )
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border

    # Danh sách ký hiệu cơ bản từ cấu hình
    all_symbols_dict = []
    for idx, (_, r_row) in enumerate(df_rules.iterrows(), start=1):
        sym = str(r_row.get("Ký hiệu", "")).strip().upper()
        if sym and sym != "TT":  # Loại bỏ ký hiệu TT nếu có
            all_symbols_dict.append({
                "sym": sym,
                "desc": r_row.get("Diễn giải", ""),
            })

    # Tự động sinh danh sách các tổ hợp ghép 2 ký tự (Loại bỏ tuyệt đối "TT")
    single_codes = ["X", "B", "P", "H", "CT", "Ô", "O", "R", "K", "T"]
    existing_syms = {item["sym"] for item in all_symbols_dict}

    for c1 in single_codes:
        for c2 in single_codes:
            pair = f"{c1}{c2}"
            if pair != "TT" and pair not in existing_syms:
                all_symbols_dict.append({
                    "sym": pair,
                    "desc": f"Tổ hợp ghép: Sáng ({c1}) - Chiều ({c2})",
                })
                existing_syms.add(pair)

    # Ghi toàn bộ ký hiệu hợp lệ vào Sheet QuyUocKyHieu
    for idx, item in enumerate(all_symbols_dict, start=1):
        ws_rules.append([idx, item["sym"], item["desc"]])

    last_rule_row = 3 + len(all_symbols_dict)

    for r in range(4, last_rule_row + 1):
        for c in range(1, 4):
            cell = ws_rules.cell(row=r, column=c)
            cell.border = thin_border
            cell.font = Font(name="Arial", size=10)
            cell.alignment = Alignment(
                horizontal="center" if c in [1, 2] else "left",
                vertical="center",
            )

    ws_rules.column_dimensions["A"].width = 8
    ws_rules.column_dimensions["B"].width = 15
    ws_rules.column_dimensions["C"].width = 50

    ws_rules.protection.sheet = True
    ws_rules.protection.password = "123456"

    # --- SHEET 1: BẢNG CHẤM CÔNG ---
    ws_main = wb.create_sheet(title=f"ChamCong_T{month}_{year}", index=0)

    unit_title = (
        unit_name.upper()
        if unit_name != "Tất cả đơn vị"
        else "TOÀN BỆNH VIỆN"
    )

    # 1. HÀNG 1: BỆNH VIỆN BƯU ĐIỆN
    ws_main["A1"] = "BỆNH VIỆN BƯU ĐIỆN"
    ws_main["A1"].font = Font(name="Arial", size=11, bold=False, color="000000")
    ws_main["A1"].alignment = Alignment(horizontal="left", vertical="center")

    # 2. HÀNG 2: TÊN KHOA / PHÒNG / TRUNG TÂM
    ws_main["A2"] = unit_title
    ws_main["A2"].font = Font(name="Arial", size=11, bold=True, color="003366")
    ws_main["A2"].alignment = Alignment(horizontal="left", vertical="center")

    num_days = calendar.monthrange(year, month)[1]

    # 3. HÀNG 3: TIÊU ĐỀ BẢNG CHẤM CÔNG
    day_headers = [f"{d:02d}/{month:02d}" for d in range(1, num_days + 1)]
    headers = ["STT", "Mã NV", "Họ và tên", "Chức vụ"] + day_headers

    title_text = f"BẢNG CHẤM CÔNG THÁNG {month}/{year} CỦA {unit_title}"
    last_col_letter = openpyxl.utils.get_column_letter(len(headers))
    ws_main.merge_cells(f"A3:{last_col_letter}3")
    cell_title = ws_main["A3"]
    cell_title.value = title_text
    cell_title.font = Font(name="Arial", size=14, bold=True, color="003366")
    cell_title.alignment = Alignment(horizontal="center", vertical="center")

    # 4. HÀNG 5: HEADER BẢNG
    header_fill_default = PatternFill(
        start_color="1F4E79", end_color="1F4E79", fill_type="solid"
    )

    fill_sat = PatternFill(
        start_color="D9E1F2", end_color="D9E1F2", fill_type="solid"
    )
    fill_sun = PatternFill(
        start_color="FFF2CC", end_color="FFF2CC", fill_type="solid"
    )
    fill_holiday = PatternFill(
        start_color="FCE4D6", end_color="FCE4D6", fill_type="solid"
    )

    fixed_holidays = ["01/01", "30/04", "01/05", "02/09"]

    day_fills = {}
    for d in range(1, num_days + 1):
        dt = date(year, month, d)
        day_str = f"{d:02d}/{month:02d}"

        if day_str in fixed_holidays:
            day_fills[d] = fill_holiday
        elif dt.weekday() == 5:
            day_fills[d] = fill_sat
        elif dt.weekday() == 6:
            day_fills[d] = fill_sun
        else:
            day_fills[d] = None

    ws_main.append([])  # Hàng 4 trống

    for c_idx, h_text in enumerate(headers, start=1):
        cell = ws_main.cell(row=5, column=c_idx)
        cell.value = h_text
        cell.font = header_font
        cell.fill = header_fill_default
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border

    num_emp = len(df_emp_unit)
    for idx, (_, row) in enumerate(df_emp_unit.iterrows(), start=1):
        current_row = 5 + idx

        ws_main.cell(row=current_row, column=1, value=idx)
        ws_main.cell(row=current_row, column=2, value=row.get("Mã NV", ""))
        ws_main.cell(row=current_row, column=3, value=row.get("Họ và tên", ""))
        ws_main.cell(
            row=current_row, column=4, value=row.get("Chức vụ", "")
        )

        for c in range(1, 5):
            cell = ws_main.cell(row=current_row, column=c)
            cell.border = thin_border
            cell.font = Font(name="Arial", size=10)
            cell.alignment = Alignment(
                horizontal="left" if c in [3, 4] else "center",
                vertical="center",
            )

        for d_num in range(1, num_days + 1):
            col_pos = 4 + d_num
            cell = ws_main.cell(row=current_row, column=col_pos, value="")
            cell.border = thin_border
            cell.font = Font(name="Arial", size=10)
            cell.alignment = Alignment(horizontal="center", vertical="center")

            if day_fills.get(d_num):
                cell.fill = day_fills[d_num]

    # DATA VALIDATION: Tham chiếu trực tiếp đến Bảng Quy Ước (Không bao gồm TT)
    rules_range_formula = f"QuyUocKyHieu!$B$4:$B${last_rule_row}"

    dv = DataValidation(
        type="list",
        formula1=rules_range_formula,
        allow_blank=True,
        errorStyle="stop",
        showErrorMessage=True,
        showInputMessage=True,
    )

    dv.errorTitle = "❌ KÝ HIỆU KHÔNG HỢP LỆ"
    dv.error = (
        "Ký hiệu nhập vào không đúng hoặc bị thừa ký tự T (Không được nhập"
        " 'TT')!"
    )
    dv.promptTitle = "💡 QUY TẮC CHẤM CÔNG"
    dv.prompt = (
        "Ký hiệu 'T' đại diện cho 1 ngày trực. Bất kỳ tổ hợp nào chứa 'TT' là"
        " không hợp lệ."
    )

    ws_main.add_data_validation(dv)

    first_data_row = 6
    last_data_row = 5 + (num_emp if num_emp > 0 else 50)
    first_day_col = openpyxl.utils.get_column_letter(5)
    last_day_col = openpyxl.utils.get_column_letter(4 + num_days)

    dv.add(f"{first_day_col}{first_data_row}:{last_day_col}{last_data_row}")

    # --- KHU VỰC CHỮ KÝ IN ẤN A4 NẰM NGANG ---
    sign_row_header = last_data_row + 3

    ws_main.merge_cells(f"A{sign_row_header}:D{sign_row_header}")
    cell_sign_left = ws_main[f"A{sign_row_header}"]
    cell_sign_left.value = "NGƯỜI CHẤM CÔNG"
    cell_sign_left.font = Font(name="Arial", size=11, bold=True)
    cell_sign_left.alignment = Alignment(
        horizontal="center", vertical="center"
    )

    sign_right_start_col = openpyxl.utils.get_column_letter(len(headers) - 6)
    sign_right_end_col = openpyxl.utils.get_column_letter(len(headers))

    ws_main.merge_cells(
        f"{sign_right_start_col}{sign_row_header}:{sign_right_end_col}{sign_row_header}"
    )
    cell_sign_right = ws_main[f"{sign_right_start_col}{sign_row_header}"]
    cell_sign_right.value = f"LÃNH ĐẠO {unit_title}"
    cell_sign_right.font = Font(name="Arial", size=11, bold=True)
    cell_sign_right.alignment = Alignment(
        horizontal="center", vertical="center"
    )

    sign_sub_row = sign_row_header + 1
    ws_main.merge_cells(f"A{sign_sub_row}:D{sign_sub_row}")
    cell_sub_left = ws_main[f"A{sign_sub_row}"]
    cell_sub_left.value = "(Ký và ghi rõ họ tên)"
    cell_sub_left.font = Font(name="Arial", size=9, italic=True)
    cell_sub_left.alignment = Alignment(horizontal="center", vertical="center")

    ws_main.merge_cells(
        f"{sign_right_start_col}{sign_sub_row}:{sign_right_end_col}{sign_sub_row}"
    )
    cell_sub_right = ws_main[f"{sign_right_start_col}{sign_sub_row}"]
    cell_sub_right.value = "(Ký tên, đóng dấu)"
    cell_sub_right.font = Font(name="Arial", size=9, italic=True)
    cell_sub_right.alignment = Alignment(
        horizontal="center", vertical="center"
    )

    ws_main.column_dimensions["A"].width = 6
    ws_main.column_dimensions["B"].width = 12
    ws_main.column_dimensions["C"].width = 25
    ws_main.column_dimensions["D"].width = 22
    for col_idx in range(5, len(headers) + 1):
        col_letter = openpyxl.utils.get_column_letter(col_idx)
        ws_main.column_dimensions[col_letter].width = 9

    ws_main.page_setup.orientation = ws_main.ORIENTATION_LANDSCAPE
    ws_main.page_setup.paperSize = ws_main.PAPERSIZE_A4
    ws_main.page_setup.fitToWidth = 1
    ws_main.page_setup.fitToHeight = 0
    ws_main.sheet_properties.pageSetUpPr.fitToPage = True

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output


# ---------------------------------------------------------
# 5. TÍNH TOÁN DỮ LIỆU TỔNG HỢP (KÝ TỰ "T" TÍNH 1 TRỰC)
# ---------------------------------------------------------
def parse_and_summarize(df_tk):
    if df_tk.empty:
        return pd.DataFrame()

    day_cols = [
        c
        for c in df_tk.columns
        if str(c).startswith("Ngày ") or "/" in str(c)
    ]

    summary_list = []
    for idx, row in df_tk.iterrows():
        res = {
            "c_cong": 0.0,
            "c_truc": 0.0,
            "c_b": 0.0,
            "c_p": 0.0,
            "c_o": 0.0,
            "c_khl": 0.0,
        }

        for d in day_cols:
            val = str(row.get(d, "")).strip().upper()
            if not val or "TT" in val:  # Bỏ qua ô trống hoặc ô vi phạm TT
                continue

            # 1. Nếu trong ô có chữ 'T' -> Tính tròn 1 ca trực
            if "T" in val:
                res["c_truc"] += 1.0

            # 2. Xử lý các thành phần công / nghỉ khác đi kèm trong ô
            # Loại bỏ ký tự T để xét các ký tự còn lại (ví dụ XT -> X, TB -> B)
            rem = val.replace("T", "")

            if rem == "XX":
                res["c_cong"] += 1.0
            elif rem == "X":
                res["c_cong"] += 0.5
            elif rem == "BB":
                res["c_b"] += 1.0
            elif rem == "B":
                res["c_b"] += 0.5
            elif rem == "PP":
                res["c_p"] += 1.0
            elif rem == "P":
                res["c_p"] += 0.5
            elif rem in ["ÔÔ", "OO", "COCO"]:
                res["c_o"] += 1.0
            elif rem in ["Ô", "O", "CO"]:
                res["c_o"] += 0.5
            elif rem in ["HH", "CTCT", "RR"]:
                res["c_cong"] += 1.0
            elif rem in ["H", "CT", "R"]:
                res["c_cong"] += 0.5
            elif rem == "KO":
                res["c_khl"] += 1.0
            elif len(rem) == 2:
                # Trường hợp ghép 2 ký tự khác (ví dụ: XB, PX...)
                for char in rem:
                    if char == "X":
                        res["c_cong"] += 0.5
                    elif char == "B":
                        res["c_b"] += 0.5
                    elif char == "P":
                        res["c_p"] += 0.5
                    elif char in ["Ô", "O"]:
                        res["c_o"] += 0.5
                    elif char in ["H", "R"]:
                        res["c_cong"] += 0.5

        rec = row.to_dict()
        rec["Tổng ngày công"] = res["c_cong"]
        rec["Số ca trực"] = res["c_truc"]
        rec["Nghỉ bù trực"] = res["c_b"]
        rec["Nghỉ phép"] = res["c_p"]
        rec["Nghỉ ốm/con ốm"] = res["c_o"]
        rec["Nghỉ không lương"] = res["c_khl"]
        summary_list.append(rec)

    return pd.DataFrame(summary_list)


# ---------------------------------------------------------
# 6. GIAO DIỆN CHÍNH MÔ ĐUN CHẤM CÔNG
# ---------------------------------------------------------
def render_timekeeping_management():
    st.subheader("⏰ Quản lý Chấm công - Ca trực - Phân lịch")

    if "df_tk_rules" not in st.session_state:
        st.session_state["df_tk_rules"] = load_timekeeping_rules()

    df_rules = st.session_state["df_tk_rules"]

    tab1, tab2, tab3, tab4 = st.tabs([
        "📥 1. Tải Mẫu Chấm công",
        "📤 2. Upload Bảng Chấm công",
        "📊 3. Xem & Sửa Bảng Chấm công",
        "📈 4. Báo cáo Tổng hợp (Tháng/Quý/Năm)",
    ])

    df_emp_all = load_employees()
    unit_list = (
        list(df_emp_all["Đơn vị"].unique())
        if not df_emp_all.empty
        else DEFAULT_DON_VI
    )

    # -----------------------------------------------------
    # TAB 1: TẢI FILE MẪU EXCEL
    # -----------------------------------------------------
    with tab1:
        st.markdown(
            "##### 📥 Xuất mẫu Excel chấm công theo từng Khoa/Phòng/Trung"
            " tâm"
        )
        c1, c2, c3 = st.columns(3)
        with c1:
            sel_unit = st.selectbox(
                "Chọn Đơn vị / Khoa / Phòng:",
                options=["Tất cả đơn vị"] + unit_list,
                key="tk_sel_unit_dl",
            )
        with c2:
            sel_month = st.selectbox(
                "Chọn Tháng:",
                range(1, 13),
                index=date.today().month - 1,
                key="tk_sel_m_dl",
            )
        with c3:
            sel_year = st.number_input(
                "Chọn Năm:",
                min_value=2020,
                max_value=2030,
                value=date.today().year,
                key="tk_sel_y_dl",
            )

        if sel_unit == "Tất cả đơn vị":
            df_target = df_emp_all
        else:
            df_target = df_emp_all[df_emp_all["Đơn vị"] == sel_unit]

        st.info(
            f"📋 Tìm thấy **{len(df_target)}** nhân viên thuộc danh sách xuất"
            " file mẫu."
        )

        excel_file = generate_timekeeping_template(
            df_target, sel_month, sel_year, sel_unit, df_rules
        )
        st.download_button(
            label=(
                f"📥 Tải File Excel Mẫu Chấm Công Tháng {sel_month}/{sel_year}"
            ),
            data=excel_file,
            file_name=(
                f"Mau_Cham_Cong_{sel_unit.replace(' ', '_')}_T{sel_month}_{sel_year}.xlsx"
            ),
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
        )

        st.markdown("---")

        with st.expander(
            "⚙️ BẢNG QUY ƯỚC KÝ HIỆU CHẤM CÔNG CHUẨN BỘ Y TẾ & BỘ NỘI VỤ",
            expanded=True,
        ):
            c_add_rule, c_del_rule = st.columns([2, 1])

            with c_add_rule:
                st.markdown("**➕ Khai báo Ký hiệu Chấm công mới**")
                with st.form(key="form_add_rule_simple", clear_on_submit=True):
                    f1, f2 = st.columns([1, 2])
                    with f1:
                        f_kh = st.text_input(
                            "Ký hiệu mới (*):", placeholder="Ví dụ: TC"
                        )
                    with f2:
                        f_dg = st.text_input(
                            "Tên ký hiệu / Diễn giải (*):",
                            placeholder="Ví dụ: Tăng cường trực",
                        )

                    btn_add_r = st.form_submit_button(
                        "Thêm Ký hiệu vào Danh sách"
                    )

                    if btn_add_r:
                        if not f_kh or not f_dg:
                            st.error(
                                "⚠️ Vui lòng nhập Ký hiệu và Diễn giải!"
                            )
                        elif f_kh.upper() == "TT":
                            st.error(
                                "❌ Ký hiệu 'TT' không hợp lệ (Không được phép"
                                " thừa ký tự T)!"
                            )
                        else:
                            new_r = {
                                "Ký hiệu": f_kh.upper(),
                                "Diễn giải": f_dg,
                            }
                            st.session_state["df_tk_rules"] = pd.concat(
                                [
                                    st.session_state["df_tk_rules"],
                                    pd.DataFrame([new_r]),
                                ],
                                ignore_index=True,
                            ).drop_duplicates(subset=["Ký hiệu"], keep="last")
                            save_timekeeping_rules(
                                st.session_state["df_tk_rules"]
                            )
                            st.success(f"✅ Đã thêm ký hiệu '{f_kh.upper()}'!")
                            st.rerun()

            with c_del_rule:
                st.markdown("**🗑️ Xóa Ký hiệu**")
                current_kh_list = list(
                    st.session_state["df_tk_rules"]["Ký hiệu"].unique()
                )
                selected_del_kh = st.multiselect(
                    "Chọn ký hiệu cần xóa:",
                    options=current_kh_list,
                    key="msel_del_rules_simple",
                )
                if st.button(
                    "❌ Xóa Ký hiệu đã chọn",
                    type="primary",
                    key="btn_del_rules_simple",
                ):
                    if selected_del_kh:
                        st.session_state["df_tk_rules"] = st.session_state[
                            "df_tk_rules"
                        ][
                            ~st.session_state["df_tk_rules"]["Ký hiệu"].isin(
                                selected_del_kh
                            )
                        ].reset_index(
                            drop=True
                        )
                        save_timekeeping_rules(st.session_state["df_tk_rules"])
                        st.success("✅ Đã xóa ký hiệu thành công!")
                        st.rerun()
                    else:
                        st.warning("Vui lòng chọn ký hiệu muốn xóa.")

            st.markdown("---")
            st.markdown(
                "**✏️ Danh sách Ký hiệu Chấm công (Sửa trực tiếp và nhấn Lưu"
                " Bảng):**"
            )

            edited_rules = st.data_editor(
                st.session_state["df_tk_rules"][["Ký hiệu", "Diễn giải"]],
                use_container_width=True,
                num_rows="dynamic",
                key="editor_tk_rules_simple",
            )

            col_r_save, col_r_reload = st.columns([3, 1])
            with col_r_save:
                if st.button(
                    "💾 Lưu Bảng Quy ước Ký hiệu vĩnh viễn",
                    type="primary",
                    key="btn_save_tk_rules_simple",
                ):
                    st.session_state["df_tk_rules"] = edited_rules
                    if save_timekeeping_rules(edited_rules):
                        st.success("✅ Đã lưu Bảng Quy ước vào CSDL!")
                        st.rerun()

            with col_r_reload:
                if st.button(
                    "🔄 Khôi phục mặc định", key="btn_reload_tk_rules_simple"
                ):
                    st.session_state["df_tk_rules"] = load_timekeeping_rules()
                    st.rerun()

    # -----------------------------------------------------
    # TAB 2: UPLOAD BẢNG CHẤM CÔNG
    # -----------------------------------------------------
    with tab2:
        st.markdown("##### 📤 Tải lên file Excel Bảng chấm công đã khai báo")
        up_c1, up_c2 = st.columns(2)
        with up_c1:
            up_m = st.selectbox(
                "Chấm công cho Tháng:",
                range(1, 13),
                index=date.today().month - 1,
                key="up_m",
            )
        with up_c2:
            up_y = st.number_input(
                "Năm:",
                min_value=2020,
                max_value=2030,
                value=date.today().year,
                key="up_y",
            )

        uploaded_tk_file = st.file_uploader(
            "Chọn file Excel chấm công (.xlsx, .xls):",
            type=["xlsx", "xls"],
            key="up_tk_file",
        )

        if uploaded_tk_file:
            try:
                df_up = pd.read_excel(uploaded_tk_file, skiprows=4).fillna("")
                if "STT" in df_up.columns:
                    df_up.drop(columns=["STT"], inplace=True)

                day_cols = [
                    c
                    for c in df_up.columns
                    if str(c).startswith("Ngày ") or "/" in str(c)
                ]
                for d in day_cols:
                    df_up[d] = df_up[d].astype(str).str.upper()

                st.write(
                    "📌 **Dữ liệu đọc từ file chấm công (Đã tự động chuẩn hóa"
                    " IN HOA):**"
                )
                st.dataframe(df_up.head(10), use_container_width=True)

                if st.button(
                    "💾 Cập nhật dữ liệu vào Hệ thống CSDL", type="primary"
                ):
                    existing_df = load_timekeeping_db(up_m, up_y)
                    if not existing_df.empty and "Mã NV" in existing_df.columns:
                        combined_df = pd.concat(
                            [existing_df, df_up], ignore_index=True
                        ).drop_duplicates(subset=["Mã NV"], keep="last")
                    else:
                        combined_df = df_up

                    if save_timekeeping_db(combined_df, up_m, up_y):
                        st.success(
                            f"✅ Đã lưu dữ liệu chấm công Tháng {up_m}/{up_y}"
                            " thành công!"
                        )
                        st.rerun()
            except Exception as e:
                st.error(f"Lỗi xử lý file Excel: {e}")

    # -----------------------------------------------------
    # TAB 3: XEM & SỬA BẢNG CHẤM CÔNG TƯƠNG TÁC
    # -----------------------------------------------------
    with tab3:
        v_c1, v_c2, v_c3 = st.columns(3)
        with v_c1:
            view_m = st.selectbox(
                "Chọn Tháng xem:",
                range(1, 13),
                index=date.today().month - 1,
                key="view_m",
            )
        with v_c2:
            view_y = st.number_input(
                "Chọn Năm xem:",
                min_value=2020,
                max_value=2030,
                value=date.today().year,
                key="view_y",
            )
        with v_c3:
            filter_unit = st.selectbox(
                "Lọc theo Đơn vị:",
                ["Tất cả đơn vị"] + unit_list,
                key="view_unit",
            )

        df_view = load_timekeeping_db(view_m, view_y)

        if not df_view.empty:
            if filter_unit != "Tất cả đơn vị" and "Đơn vị" in df_view.columns:
                df_view_filtered = df_view[df_view["Đơn vị"] == filter_unit]
            else:
                df_view_filtered = df_view

            df_calculated = parse_and_summarize(df_view_filtered)

            st.markdown(
                f"##### 📋 Bảng Chi tiết Chấm công Tháng {view_m}/{view_y}"
            )
            edited_tk = st.data_editor(
                df_calculated,
                use_container_width=True,
                hide_index=True,
                key=f"editor_tk_{view_m}_{view_y}",
            )

            if st.button(
                "💾 Lưu chỉnh sửa Bảng Chấm công",
                type="primary",
                key="btn_save_tk_edit",
            ):
                if save_timekeeping_db(edited_tk, view_m, view_y):
                    st.success("✅ Đã cập nhật thành công CSDL Chấm công!")
                    st.rerun()
        else:
            st.warning(
                f"Chưa có dữ liệu chấm công cho Tháng {view_m}/{view_y}. Vui"
                " lòng upload file Excel ở Tab 2."
            )

    # -----------------------------------------------------
    # TAB 4: BÁO CÁO TỔNG HỢP TÙY CHỌN
    # -----------------------------------------------------
    with tab4:
        st.markdown(
            "##### 📈 Báo cáo Tổng hợp Chấm công - Trực - Nghỉ bù / Phép"
        )

        rep_type = st.radio(
            "Chọn loại báo cáo tổng hợp:",
            [
                "Theo Tháng",
                "Theo Quý",
                "Theo Năm",
                "Khoảng thời gian tùy chọn",
            ],
            horizontal=True,
        )

        selected_months = []
        rep_year = date.today().year

        if rep_type == "Theo Tháng":
            rc1, rc2 = st.columns(2)
            with rc1:
                rm = st.selectbox(
                    "Chọn Tháng báo cáo:",
                    range(1, 13),
                    index=date.today().month - 1,
                    key="rm_single",
                )
            with rc2:
                rep_year = st.number_input(
                    "Chọn Năm:",
                    min_value=2020,
                    max_value=2030,
                    value=date.today().year,
                    key="ry_single",
                )
            selected_months = [rm]

        elif rep_type == "Theo Quý":
            rc1, rc2 = st.columns(2)
            with rc1:
                r_q = st.selectbox(
                    "Chọn Quý:",
                    [
                        "Quý I (Tháng 1-3)",
                        "Quý II (Tháng 4-6)",
                        "Quý III (Tháng 7-9)",
                        "Quý IV (Tháng 10-12)",
                    ],
                )
            with rc2:
                rep_year = st.number_input(
                    "Chọn Năm:",
                    min_value=2020,
                    max_value=2030,
                    value=date.today().year,
                    key="ry_q",
                )

            if "Quý I" in r_q:
                selected_months = [1, 2, 3]
            elif "Quý II" in r_q:
                selected_months = [4, 5, 6]
            elif "Quý III" in r_q:
                selected_months = [7, 8, 9]
            else:
                selected_months = [10, 11, 12]

        elif rep_type == "Theo Năm":
            rep_year = st.number_input(
                "Chọn Năm Báo cáo:",
                min_value=2020,
                max_value=2030,
                value=date.today().year,
                key="ry_year",
            )
            selected_months = list(range(1, 13))

        else:
            rc1, rc2 = st.columns(2)
            with rc1:
                m_start = st.selectbox("Từ Tháng:", range(1, 13), index=0)
            with rc2:
                m_end = st.selectbox(
                    "Đến Tháng:", range(1, 13), index=date.today().month - 1
                )
            rep_year = st.number_input(
                "Năm:",
                min_value=2020,
                max_value=2030,
                value=date.today().year,
                key="ry_range",
            )
            selected_months = list(range(m_start, m_end + 1))

        all_dfs = []
        for m in selected_months:
            df_m = load_timekeeping_db(m, rep_year)
            if not df_m.empty:
                df_parsed = parse_and_summarize(df_m)
                all_dfs.append(df_parsed)

        if all_dfs:
            combined_rep = pd.concat(all_dfs, ignore_index=True)

            group_cols = ["Mã NV", "Họ và tên", "Chức vụ"]
            if "Đơn vị" in combined_rep.columns:
                group_cols.append("Đơn vị")

            sum_cols = [
                "Tổng ngày công",
                "Số ca trực",
                "Nghỉ bù trực",
                "Nghỉ phép",
                "Nghỉ ốm/con ốm",
                "Nghỉ không lương",
            ]

            for sc in sum_cols:
                if sc not in combined_rep.columns:
                    combined_rep[sc] = 0.0

            final_report = (
                combined_rep.groupby(group_cols)[sum_cols].sum().reset_index()
            )

            st.write(
                "📊 **BẢO CÁO TỔNG HỢP CÔNG - TRỰC - NGHỈ"
                f" ({rep_type.upper()} NĂM {rep_year})**"
            )
            st.dataframe(
                final_report, use_container_width=True, hide_index=True
            )

            out_rep = io.BytesIO()
            with pd.ExcelWriter(out_rep, engine="openpyxl") as writer:
                final_report.to_excel(
                    writer, index=False, sheet_name="BaoCaoTongHop"
                )
            out_rep.seek(0)

            st.download_button(
                label="📥 Tải xuống Báo cáo Tổng hợp Excel",
                data=out_rep,
                file_name=(
                    f"Bao_Cao_Tong_Hop_Cham_Cong_{rep_type}_{rep_year}.xlsx"
                ),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
            )
        else:
            st.warning(
                "Không tìm thấy dữ liệu chấm công trong khoảng thời gian đã"
                " chọn."
            )


if __name__ == "__main__":
    render_timekeeping_management()
