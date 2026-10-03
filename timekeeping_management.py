import calendar
from datetime import date, datetime
import io
import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
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
    {
        "Ký hiệu": "X",
        "Diễn giải": "½ ngày công làm việc giờ hành chính",
        "Công": 0.5,
        "Trực": 0.0,
        "Nghỉ bù": 0.0,
        "Nghỉ phép": 0.0,
        "Nghỉ ốm": 0.0,
        "Không lương": 0.0,
    },
    {
        "Ký hiệu": "XX",
        "Diễn giải": "1 ngày công làm việc giờ hành chính",
        "Công": 1.0,
        "Trực": 0.0,
        "Nghỉ bù": 0.0,
        "Nghỉ phép": 0.0,
        "Nghỉ ốm": 0.0,
        "Không lương": 0.0,
    },
    {
        "Ký hiệu": "T",
        "Diễn giải": "1 ngày trực ngoài giờ hành chính",
        "Công": 0.0,
        "Trực": 1.0,
        "Nghỉ bù": 0.0,
        "Nghỉ phép": 0.0,
        "Nghỉ ốm": 0.0,
        "Không lương": 0.0,
    },
    {
        "Ký hiệu": "B",
        "Diễn giải": "½ ngày nghỉ bù trực hưởng nguyên lương",
        "Công": 0.0,
        "Trực": 0.0,
        "Nghỉ bù": 0.5,
        "Nghỉ phép": 0.0,
        "Nghỉ ốm": 0.0,
        "Không lương": 0.0,
    },
    {
        "Ký hiệu": "BB",
        "Diễn giải": "1 ngày nghỉ bù trực hưởng nguyên lương",
        "Công": 0.0,
        "Trực": 0.0,
        "Nghỉ bù": 1.0,
        "Nghỉ phép": 0.0,
        "Nghỉ ốm": 0.0,
        "Không lương": 0.0,
    },
    {
        "Ký hiệu": "XTX",
        "Diễn giải": "1 ngày công hành chính + 1 ngày trực ngoài giờ",
        "Công": 1.0,
        "Trực": 1.0,
        "Nghỉ bù": 0.0,
        "Nghỉ phép": 0.0,
        "Nghỉ ốm": 0.0,
        "Không lương": 0.0,
    },
    {
        "Ký hiệu": "BTB",
        "Diễn giải": "1 ngày nghỉ bù trực + 1 ngày trực ngoài giờ",
        "Công": 0.0,
        "Trực": 1.0,
        "Nghỉ bù": 1.0,
        "Nghỉ phép": 0.0,
        "Nghỉ ốm": 0.0,
        "Không lương": 0.0,
    },
    {
        "Ký hiệu": "P",
        "Diễn giải": "½ ngày nghỉ phép",
        "Công": 0.0,
        "Trực": 0.0,
        "Nghỉ bù": 0.0,
        "Nghỉ phép": 0.5,
        "Nghỉ ốm": 0.0,
        "Không lương": 0.0,
    },
    {
        "Ký hiệu": "PP",
        "Diễn giải": "1 ngày nghỉ phép",
        "Công": 0.0,
        "Trực": 0.0,
        "Nghỉ bù": 0.0,
        "Nghỉ phép": 1.0,
        "Nghỉ ốm": 0.0,
        "Không lương": 0.0,
    },
    {
        "Ký hiệu": "H",
        "Diễn giải": "½ ngày đi học",
        "Công": 0.5,
        "Trực": 0.0,
        "Nghỉ bù": 0.0,
        "Nghỉ phép": 0.0,
        "Nghỉ ốm": 0.0,
        "Không lương": 0.0,
    },
    {
        "Ký hiệu": "HH",
        "Diễn giải": "1 ngày đi học",
        "Công": 1.0,
        "Trực": 0.0,
        "Nghỉ bù": 0.0,
        "Nghỉ phép": 0.0,
        "Nghỉ ốm": 0.0,
        "Không lương": 0.0,
    },
    {
        "Ký hiệu": "CT",
        "Diễn giải": "½ ngày đi công tác",
        "Công": 0.5,
        "Trực": 0.0,
        "Nghỉ bù": 0.0,
        "Nghỉ phép": 0.0,
        "Nghỉ ốm": 0.0,
        "Không lương": 0.0,
    },
    {
        "Ký hiệu": "CTCT",
        "Diễn giải": "1 ngày đi công tác",
        "Công": 1.0,
        "Trực": 0.0,
        "Nghỉ bù": 0.0,
        "Nghỉ phép": 0.0,
        "Nghỉ ốm": 0.0,
        "Không lương": 0.0,
    },
    {
        "Ký hiệu": "Ô",
        "Diễn giải": "½ ngày nghỉ ốm",
        "Công": 0.0,
        "Trực": 0.0,
        "Nghỉ bù": 0.0,
        "Nghỉ phép": 0.0,
        "Nghỉ ốm": 0.5,
        "Không lương": 0.0,
    },
    {
        "Ký hiệu": "ÔÔ",
        "Diễn giải": "1 ngày nghỉ ốm",
        "Công": 0.0,
        "Trực": 0.0,
        "Nghỉ bù": 0.0,
        "Nghỉ phép": 0.0,
        "Nghỉ ốm": 1.0,
        "Không lương": 0.0,
    },
    {
        "Ký hiệu": "Co",
        "Diễn giải": "½ ngày nghỉ con ốm",
        "Công": 0.0,
        "Trực": 0.0,
        "Nghỉ bù": 0.0,
        "Nghỉ phép": 0.0,
        "Nghỉ ốm": 0.5,
        "Không lương": 0.0,
    },
    {
        "Ký hiệu": "CoCo",
        "Diễn giải": "1 ngày nghỉ con ốm",
        "Công": 0.0,
        "Trực": 0.0,
        "Nghỉ bù": 0.0,
        "Nghỉ phép": 0.0,
        "Nghỉ ốm": 1.0,
        "Không lương": 0.0,
    },
    {
        "Ký hiệu": "R",
        "Diễn giải": "½ ngày nghỉ việc riêng hưởng nguyên lương",
        "Công": 0.5,
        "Trực": 0.0,
        "Nghỉ bù": 0.0,
        "Nghỉ phép": 0.0,
        "Nghỉ ốm": 0.0,
        "Không lương": 0.0,
    },
    {
        "Ký hiệu": "RR",
        "Diễn giải": "1 ngày nghỉ việc riêng hưởng nguyên lương",
        "Công": 1.0,
        "Trực": 0.0,
        "Nghỉ bù": 0.0,
        "Nghỉ phép": 0.0,
        "Nghỉ ốm": 0.0,
        "Không lương": 0.0,
    },
    {
        "Ký hiệu": "Ko",
        "Diễn giải": "1 ngày nghỉ không hưởng lương",
        "Công": 0.0,
        "Trực": 0.0,
        "Nghỉ bù": 0.0,
        "Nghỉ phép": 0.0,
        "Nghỉ ốm": 0.0,
        "Không lương": 1.0,
    },
    {
        "Ký hiệu": "TS",
        "Diễn giải": "1 ngày nghỉ thai sản",
        "Công": 0.0,
        "Trực": 0.0,
        "Nghỉ bù": 0.0,
        "Nghỉ phép": 0.0,
        "Nghỉ ốm": 0.0,
        "Không lương": 0.0,
    },
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
            return pd.DataFrame(res.data[0]["content"])
        return pd.DataFrame(DEFAULT_TIMEKEEPING_RULES)
    except Exception:
        return pd.DataFrame(DEFAULT_TIMEKEEPING_RULES)


def save_timekeeping_rules(df_rules):
    if not supabase:
        return True
    try:
        clean_df = df_rules.fillna("")
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
# 4. TẠO FILE EXCEL MẪU 2 SHEETS DÀNH CHO CÁC ĐƠN VỊ
# ---------------------------------------------------------
def generate_timekeeping_template(
    df_emp_unit, month, year, unit_name, df_rules
):
    wb = openpyxl.Workbook()

    # Sheet 1: Bảng chấm công
    ws_main = wb.active
    ws_main.title = f"ChamCong_T{month}_{year}"

    unit_title = (
        unit_name.upper()
        if unit_name != "Tất cả đơn vị"
        else "TOÀN BỆNH VIỆN"
    )
    title_text = f"BẢNG CHẤM CÔNG THÁNG {month}/{year} CỦA {unit_title}"

    ws_main.merge_cells("A1:AJ1")
    cell_title = ws_main["A1"]
    cell_title.value = title_text
    cell_title.font = Font(name="Arial", size=14, bold=True, color="003366")
    cell_title.alignment = Alignment(horizontal="center", vertical="center")

    num_days = calendar.monthrange(year, month)[1]
    headers = ["STT", "Mã NV", "Họ và tên", "Chức vụ", "Đơn vị"] + [
        f"Ngày {d:02d}" for d in range(1, num_days + 1)
    ]

    ws_main.append([])  # Dòng A2
    ws_main.append(headers)  # Dòng D3

    header_font = Font(name="Arial", size=10, bold=True, color="FFFFFF")
    header_fill = PatternFill(
        start_color="1F4E79", end_color="1F4E79", fill_type="solid"
    )
    thin_border = Border(
        left=Side(style="thin", color="CCCCCC"),
        right=Side(style="thin", color="CCCCCC"),
        top=Side(style="thin", color="CCCCCC"),
        bottom=Side(style="thin", color="CCCCCC"),
    )

    for col_idx in range(1, len(headers) + 1):
        cell = ws_main.cell(row=3, column=col_idx)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border

    # Trống bảng chấm công (Không điền sẵn ký hiệu)
    for idx, (_, row) in enumerate(df_emp_unit.iterrows(), start=1):
        row_data = [
            idx,
            row.get("Mã NV", ""),
            row.get("Họ và tên", ""),
            row.get("Chức vụ", ""),
            row.get("Đơn vị", unit_name),
        ] + [
            "" for _ in range(num_days)
        ]  # Để trống ô ngày
        ws_main.append(row_data)

    for r in range(4, 4 + len(df_emp_unit)):
        for c in range(1, len(headers) + 1):
            cell = ws_main.cell(row=r, column=c)
            cell.border = thin_border
            cell.font = Font(name="Arial", size=10)
            if c <= 5:
                cell.alignment = Alignment(
                    horizontal="left" if c in [3, 4, 5] else "center",
                    vertical="center",
                )
            else:
                cell.alignment = Alignment(
                    horizontal="center", vertical="center"
                )

    ws_main.column_dimensions["A"].width = 6
    ws_main.column_dimensions["B"].width = 12
    ws_main.column_dimensions["C"].width = 25
    ws_main.column_dimensions["D"].width = 20
    ws_main.column_dimensions["E"].width = 22
    for col_idx in range(6, len(headers) + 1):
        col_letter = openpyxl.utils.get_column_letter(col_idx)
        ws_main.column_dimensions[col_letter].width = 9

    # Sheet 2: Quy ước ký hiệu kèm theo
    ws_rules = wb.create_sheet(title="QuyUocKyHieu")
    ws_rules["A1"] = "BẢNG QUY ƯỚC KÝ HIỆU CHẤM CÔNG CHUẨN BỘ Y TẾ & BỘ NỘI VỤ"
    ws_rules["A1"].font = Font(name="Arial", size=12, bold=True, color="003366")

    rule_headers = ["STT", "Ký hiệu", "Tên ký hiệu / Diễn giải"]
    ws_rules.append([])
    ws_rules.append(rule_headers)

    for col_idx in range(1, len(rule_headers) + 1):
        cell = ws_rules.cell(row=3, column=col_idx)
        cell.font = header_font
        cell.fill = PatternFill(
            start_color="2F5597", end_color="2F5597", fill_type="solid"
        )
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border

    for idx, (_, r_row) in enumerate(df_rules.iterrows(), start=1):
        ws_rules.append([idx, r_row.get("Ký hiệu", ""), r_row.get("Diễn giải", "")])

    for r in range(4, 4 + len(df_rules)):
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

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output


# ---------------------------------------------------------
# 5. TÍNH TOÁN DỮ LIỆU TỔNG HỢP
# ---------------------------------------------------------
def parse_and_summarize(df_tk, df_rules):
    if df_tk.empty:
        return pd.DataFrame()

    rules_dict = {}
    for _, r in df_rules.iterrows():
        k = str(r.get("Ký hiệu", "")).strip().upper()
        rules_dict[k] = {
            "cong": float(r.get("Công", 0.0) or 0.0),
            "truc": float(r.get("Trực", 0.0) or 0.0),
            "b": float(r.get("Nghỉ bù", 0.0) or 0.0),
            "p": float(r.get("Nghỉ phép", 0.0) or 0.0),
            "o": float(r.get("Nghỉ ốm", 0.0) or 0.0),
            "khl": float(r.get("Không lương", 0.0) or 0.0),
        }

    day_cols = [c for c in df_tk.columns if str(c).startswith("Ngày ")]

    summary_list = []
    for idx, row in df_tk.iterrows():
        c_cong, c_truc, c_b, c_p, c_o, c_khl = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

        for d in day_cols:
            val = str(row.get(d, "")).strip().upper()
            rule = rules_dict.get(val, None)
            if rule:
                c_cong += rule["cong"]
                c_truc += rule["truc"]
                c_b += rule["b"]
                c_p += rule["p"]
                c_o += rule["o"]
                c_khl += rule["khl"]

        rec = row.to_dict()
        rec["Tổng ngày công"] = c_cong
        rec["Số ca trực"] = c_truc
        rec["Nghỉ bù trực"] = c_b
        rec["Nghỉ phép"] = c_p
        rec["Nghỉ ốm/con ốm"] = c_o
        rec["Nghỉ không lương"] = c_khl
        summary_list.append(rec)

    return pd.DataFrame(summary_list)


# ---------------------------------------------------------
# 6. GIAO DIỆN CHÍNH MÔ ĐUN CHẤM CÔNG
# ---------------------------------------------------------
def render_timekeeping_management():
    st.subheader("⏰ Quản lý Chấm công - Ca trực - Phân lịch")

    # Nạp quy ước ký hiệu
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
    # TAB 1: TẢI FILE MẪU VÀ QUẢN LÝ THÊM / SỬA / XÓA / LƯU KÝ HIỆU
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

        # --- KHU VỰC THÊM / SỬA / XÓA / LƯU KÝ HIỆU CHẤM CÔNG ---
        with st.expander(
            "⚙️ BẢNG QUY ƯỚC KÝ HIỆU CHẤM CÔNG CHUẨN BỘ Y TẾ & BỘ NỘI VỤ",
            expanded=True,
        ):
            # BỘ CÔNG CỤ TƯƠNG TÁC: THÊM & XÓA KÝ HIỆU
            c_add_rule, c_del_rule = st.columns(2)

            with c_add_rule:
                st.markdown("**➕ Thêm / Khai báo Ký hiệu Chấm công mới**")
                with st.form(key="form_add_rule", clear_on_submit=True):
                    f_kh = st.text_input(
                        "Ký hiệu mới (*):", placeholder="Ví dụ: TC"
                    )
                    f_dg = st.text_input(
                        "Tên ký hiệu / Diễn giải (*):",
                        placeholder="Ví dụ: Tăng cường trực",
                    )

                    fc1, fc2, fc3 = st.columns(3)
                    with fc1:
                        f_cong = st.number_input(
                            "Quy đổi Công:", min_value=0.0, max_value=2.0, step=0.5, value=1.0
                        )
                        f_truc = st.number_input(
                            "Quy đổi Trực:", min_value=0.0, max_value=2.0, step=0.5, value=0.0
                        )
                    with fc2:
                        f_b = st.number_input(
                            "Nghỉ bù:", min_value=0.0, max_value=2.0, step=0.5, value=0.0
                        )
                        f_p = st.number_input(
                            "Nghỉ phép:", min_value=0.0, max_value=2.0, step=0.5, value=0.0
                        )
                    with fc3:
                        f_o = st.number_input(
                            "Nghỉ ốm:", min_value=0.0, max_value=2.0, step=0.5, value=0.0
                        )
                        f_khl = st.number_input(
                            "Không lương:", min_value=0.0, max_value=2.0, step=0.5, value=0.0
                        )

                    btn_add_r = st.form_submit_button("Thêm Ký hiệu vào Bảng")

                    if btn_add_r:
                        if not f_kh or not f_dg:
                            st.error(
                                "⚠️ Vui lòng điền Ký hiệu và Diễn giải!"
                            )
                        else:
                            new_r = {
                                "Ký hiệu": f_kh.upper(),
                                "Diễn giải": f_dg,
                                "Công": f_cong,
                                "Trực": f_truc,
                                "Nghỉ bù": f_b,
                                "Nghỉ phép": f_p,
                                "Nghỉ ốm": f_o,
                                "Không lương": f_khl,
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
                st.markdown("**🗑️ Xóa Ký hiệu Chấm công**")
                current_kh_list = list(
                    st.session_state["df_tk_rules"]["Ký hiệu"].unique()
                )
                selected_del_kh = st.multiselect(
                    "Chọn danh sách Ký hiệu muốn xóa:",
                    options=current_kh_list,
                    key="msel_del_rules",
                )
                if st.button(
                    "❌ Xóa Ký hiệu đã chọn",
                    type="primary",
                    key="btn_del_rules",
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
                        st.success("✅ Đã xóa thành công các ký hiệu đã chọn!")
                        st.rerun()
                    else:
                        st.warning("Vui lòng chọn ít nhất 1 ký hiệu để xóa.")

            st.markdown("---")
            st.markdown(
                "**✏️ Sửa trực tiếp quy ước và Nhấn nút 'Lưu Bảng Quy ước' để"
                " cập nhật CSDL:**"
            )

            # Bảng data_editor cho phép SỬA trực tiếp
            edited_rules = st.data_editor(
                st.session_state["df_tk_rules"],
                use_container_width=True,
                num_rows="dynamic",
                key="editor_tk_rules",
            )

            col_r_save, col_r_reload = st.columns([3, 1])
            with col_r_save:
                if st.button(
                    "💾 Lưu Bảng Quy ước Ký hiệu vĩnh viễn",
                    type="primary",
                    key="btn_save_tk_rules",
                ):
                    st.session_state["df_tk_rules"] = edited_rules
                    if save_timekeeping_rules(edited_rules):
                        st.success(
                            "✅ Đã lưu Bảng quy ước ký hiệu chấm công vào CSDL"
                            " Supabase thành công!"
                        )
                        st.rerun()

            with col_r_reload:
                if st.button(
                    "🔄 Khôi phục mặc định", key="btn_reload_tk_rules"
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
                df_up = pd.read_excel(uploaded_tk_file, skiprows=2).fillna("")
                if "STT" in df_up.columns:
                    df_up.drop(columns=["STT"], inplace=True)

                st.write("📌 **Dữ liệu đọc từ file chấm công:**")
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

            df_calculated = parse_and_summarize(df_view_filtered, df_rules)

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
                df_parsed = parse_and_summarize(df_m, df_rules)
                all_dfs.append(df_parsed)

        if all_dfs:
            combined_rep = pd.concat(all_dfs, ignore_index=True)

            group_cols = ["Mã NV", "Họ và tên", "Chức vụ", "Đơn vị"]
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
