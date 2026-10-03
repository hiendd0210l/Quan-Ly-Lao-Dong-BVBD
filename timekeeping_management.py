import io
import calendar
from datetime import datetime, date
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
        key = (st.secrets.get("SUPABASE_KEY") or st.secrets.get("SUPABASE_SERVICE_KEY", "")).strip()
        if not url or not key:
            return None
        if not url.startswith("https://"):
            url = f"https://{url}"
        return create_client(url, key)
    except Exception:
        return None

supabase = init_supabase()

# ---------------------------------------------------------
# 2. QUY ƯỚC KÝ HIỆU CHẤM CÔNG (THEO FILE TÀI LIỆU QUY ĐỊNH)
# ---------------------------------------------------------
TIMEKEEPING_RULES = {
    "X":    {"desc": "½ ngày công làm việc giờ hành chính", "cong": 0.5, "truc": 0, "p": 0, "b": 0, "o": 0, "khl": 0},
    "XX":   {"desc": "1 ngày công làm việc giờ hành chính", "cong": 1.0, "truc": 0, "p": 0, "b": 0, "o": 0, "khl": 0},
    "T":    {"desc": "1 ngày trực ngoài giờ hành chính", "cong": 0.0, "truc": 1.0, "p": 0, "b": 0, "o": 0, "khl": 0},
    "B":    {"desc": "½ ngày nghỉ bù trực hưởng nguyên lương", "cong": 0.0, "truc": 0, "p": 0, "b": 0.5, "o": 0, "khl": 0},
    "BB":   {"desc": "1 ngày nghỉ bù trực hưởng nguyên lương", "cong": 0.0, "truc": 0, "p": 0, "b": 1.0, "o": 0, "khl": 0},
    "XTX":  {"desc": "1 ngày công hành chính + 1 ngày trực ngoài giờ", "cong": 1.0, "truc": 1.0, "p": 0, "b": 0, "o": 0, "khl": 0},
    "BTB":  {"desc": "1 ngày nghỉ bù trực + 1 ngày trực ngoài giờ", "cong": 0.0, "truc": 1.0, "p": 0, "b": 1.0, "o": 0, "khl": 0},
    "P":    {"desc": "½ ngày nghỉ phép", "cong": 0.0, "truc": 0, "p": 0.5, "b": 0, "o": 0, "khl": 0},
    "PP":   {"desc": "1 ngày nghỉ phép", "cong": 0.0, "truc": 0, "p": 1.0, "b": 0, "o": 0, "khl": 0},
    "H":    {"desc": "½ ngày đi học", "cong": 0.5, "truc": 0, "p": 0, "b": 0, "o": 0, "khl": 0},
    "HH":   {"desc": "1 ngày đi học", "cong": 1.0, "truc": 0, "p": 0, "b": 0, "o": 0, "khl": 0},
    "CT":   {"desc": "½ ngày đi công tác", "cong": 0.5, "truc": 0, "p": 0, "b": 0, "o": 0, "khl": 0},
    "CTCT": {"desc": "1 ngày đi công tác", "cong": 1.0, "truc": 0, "p": 0, "b": 0, "o": 0, "khl": 0},
    "Ô":    {"desc": "½ ngày nghỉ ốm", "cong": 0.0, "truc": 0, "p": 0, "b": 0, "o": 0.5, "khl": 0},
    "O":    {"desc": "½ ngày nghỉ ốm (Không dấu)", "cong": 0.0, "truc": 0, "p": 0, "b": 0, "o": 0.5, "khl": 0},
    "ÔÔ":   {"desc": "1 ngày nghỉ ốm", "cong": 0.0, "truc": 0, "p": 0, "b": 0, "o": 1.0, "khl": 0},
    "OO":   {"desc": "1 ngày nghỉ ốm (Không dấu)", "cong": 0.0, "truc": 0, "p": 0, "b": 0, "o": 1.0, "khl": 0},
    "CO":   {"desc": "½ ngày nghỉ con ốm", "cong": 0.0, "truc": 0, "p": 0, "b": 0, "o": 0.5, "khl": 0},
    "COCO": {"desc": "1 ngày nghỉ con ốm", "cong": 0.0, "truc": 0, "p": 0, "b": 0, "o": 1.0, "khl": 0},
    "R":    {"desc": "½ ngày nghỉ việc riêng hưởng lương", "cong": 0.5, "truc": 0, "p": 0, "b": 0, "o": 0, "khl": 0},
    "RR":   {"desc": "1 ngày nghỉ việc riêng hưởng lương", "cong": 1.0, "truc": 0, "p": 0, "b": 0, "o": 0, "khl": 0},
    "KO":   {"desc": "1 ngày nghỉ không hưởng lương", "cong": 0.0, "truc": 0, "p": 0, "b": 0, "o": 0, "khl": 1.0},
    "TS":   {"desc": "1 ngày nghỉ thai sản", "cong": 0.0, "truc": 0, "p": 0, "b": 0, "o": 0, "khl": 0},
}

DEFAULT_DON_VI = [
    "Khoa Cấp cứu", "Khoa Khám bệnh", "Khoa Ngoại tổng hợp", "Khoa Dược", 
    "Khoa Hồi sức tích cực", "Phòng Tổ chức Cán bộ", "Phòng Tài chính Kế toán", "Phòng Kế hoạch Tổng hợp"
]

DEFAULT_CAN_BO = [
    {"Mã NV": "NV001", "Họ và tên": "Nguyễn Văn An", "Chức vụ": "Bác sĩ CKI", "Đơn vị": "Khoa Cấp cứu"},
    {"Mã NV": "NV002", "Họ và tên": "Trần Thị Bích", "Chức vụ": "Điều dưỡng trưởng", "Đơn vị": "Khoa Cấp cứu"},
    {"Mã NV": "NV003", "Họ và tên": "Lê Hoàng Cường", "Chức vụ": "Bác sĩ chính", "Đơn vị": "Khoa Ngoại tổng hợp"},
    {"Mã NV": "NV004", "Họ và tên": "Phạm Minh Đức", "Chức vụ": "Dược sĩ CKI", "Đơn vị": "Khoa Dược"},
    {"Mã NV": "NV005", "Họ và tên": "Vũ Thị Dung", "Chức vụ": "Chuyên viên TCCB", "Đơn vị": "Phòng Tổ chức Cán bộ"},
]

# ---------------------------------------------------------
# 3. TẢI VÀ LƯU DỮ LIỆU CSDL
# ---------------------------------------------------------
def load_employees():
    if not supabase:
        return pd.DataFrame(DEFAULT_CAN_BO)
    try:
        res = supabase.table("categories").select("content").eq("cat_key", "employees_profile").execute()
        if res.data and res.data[0]["content"]:
            df = pd.DataFrame(res.data[0]["content"])
            if "Mã CB" in df.columns and "Mã NV" not in df.columns:
                df.rename(columns={"Mã CB": "Mã NV"}, inplace=True)
            if "Khoa / Phòng" in df.columns and "Đơn vị" not in df.columns:
                df.rename(columns={"Khoa / Phòng": "Đơn vị"}, inplace=True)
            if "Chức vụ / Chức danh" in df.columns and "Chức vụ" not in df.columns:
                df.rename(columns={"Chức vụ / Chức danh": "Chức vụ"}, inplace=True)
            return df[["Mã NV", "Họ và tên", "Chức vụ", "Đơn vị"]]
        return pd.DataFrame(DEFAULT_CAN_BO)
    except Exception:
        return pd.DataFrame(DEFAULT_CAN_BO)

def load_timekeeping_db(month, year):
    key_db = f"tk_{year}_{month:02d}"
    if not supabase:
        return st.session_state.get(key_db, pd.DataFrame())
    try:
        res = supabase.table("categories").select("content").eq("cat_key", key_db).execute()
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
            "content": clean_df.to_dict(orient="records")
        }
        supabase.table("categories").upsert(payload).execute()
        return True
    except Exception as e:
        st.error(f"Lỗi lưu CSDL: {e}")
        return False

# ---------------------------------------------------------
# 4. TẠO FILE EXCEL MẪU CHẤM CÔNG THEO ĐƠN VỊ
# ---------------------------------------------------------
def generate_timekeeping_template(df_emp_unit, month, year, unit_name):
    num_days = calendar.monthrange(year, month)[1]
    day_cols = [f"Ngày {d:02d}" for d in range(1, num_days + 1)]
    
    data = []
    for _, row in df_emp_unit.iterrows():
        r_dict = {
            "Mã NV": row.get("Mã NV", ""),
            "Họ và tên": row.get("Họ và tên", ""),
            "Chức vụ": row.get("Chức vụ", ""),
            "Đơn vị": unit_name
        }
        for d_col in day_cols:
            r_dict[d_col] = "XX"  # Mặc định là làm việc hành chính
        data.append(r_dict)
        
    df_template = pd.DataFrame(data)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_template.to_excel(writer, index=False, sheet_name=f"Thang_{month}_{year}")
    output.seek(0)
    return output

# ---------------------------------------------------------
# 5. TÍNH TOÁN VÀ TỔNG HỢP CHẤM CÔNG
# ---------------------------------------------------------
def parse_and_summarize(df_tk):
    if df_tk.empty:
        return pd.DataFrame()
        
    day_cols = [c for c in df_tk.columns if str(c).startswith("Ngày ")]
    
    summary_list = []
    for idx, row in df_tk.iterrows():
        c_cong = 0.0
        c_truc = 0.0
        c_b = 0.0
        c_p = 0.0
        c_o = 0.0
        c_khl = 0.0
        
        for d in day_cols:
            val = str(row.get(d, "")).strip().upper()
            rule = TIMEKEEPING_RULES.get(val, None)
            if rule:
                c_cong += rule["cong"]
                c_truc += rule["truc"]
                c_b += rule["b"]
                c_p += rule["p"]
                c_o += rule["o"]
                c_khl += rule["khl"]
            elif val in ["XX", "X"]:
                c_cong += 1.0 if val == "XX" else 0.5
                
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
# 6. GIAO DIỆN CHÍNH MÔ ĐUN
# ---------------------------------------------------------
def render_timekeeping_management():
    st.subheader("⏰ Quản lý Chấm công - Ca trực - Phân lịch")

    tab1, tab2, tab3, tab4 = st.tabs([
        "📥 1. Tải Mẫu Chấm công",
        "📤 2. Upload Bảng Chấm công",
        "📊 3. Xem & Sửa Bảng Chấm công",
        "📈 4. Báo cáo Tổng hợp (Tháng/Quý/Năm)"
    ])

    df_emp_all = load_employees()
    unit_list = list(df_emp_all["Đơn vị"].unique()) if not df_emp_all.empty else DEFAULT_DON_VI

    # -----------------------------------------------------
    # TAB 1: TẢI FILE EXCEL MẪU
    # -----------------------------------------------------
    with tab1:
        st.markdown("##### 📥 Xuất mẫu Excel chấm công theo từng Khoa/Phòng/Trung tâm")
        c1, c2, c3 = st.columns(3)
        with c1:
            sel_unit = st.selectbox("Chọn Đơn vị / Khoa / Phòng:", options=["Tất cả đơn vị"] + unit_list, key="tk_sel_unit_dl")
        with c2:
            sel_month = st.selectbox("Chọn Tháng:", range(1, 13), index=date.today().month - 1, key="tk_sel_m_dl")
        with c3:
            sel_year = st.number_input("Chọn Năm:", min_value=2020, max_value=2030, value=date.today().year, key="tk_sel_y_dl")

        if sel_unit == "Tất cả đơn vị":
            df_target = df_emp_all
        else:
            df_target = df_emp_all[df_emp_all["Đơn vị"] == sel_unit]

        st.info(f"📋 Tìm thấy **{len(df_target)}** nhân viên thuộc danh sách xuất file mẫu.")
        
        excel_file = generate_timekeeping_template(df_target, sel_month, sel_year, sel_unit)
        st.download_button(
            label=f"📥 Tải File Excel Mẫu Chấm Công Tháng {sel_month}/{sel_year}",
            data=excel_file,
            file_name=f"Mau_Cham_Cong_{sel_unit.replace(' ', '_')}_T{sel_month}_{sel_year}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary"
        )

        with st.expander("📖 Xem Quy ước Ký hiệu Chấm công chuẩn Bộ Y tế & Bộ Nội vụ", expanded=False):
            rules_df = pd.DataFrame([
                {"Ký hiệu": k, "Tên ký hiệu / Diễn giải": v["desc"]} for k, v in TIMEKEEPING_RULES.items() if not k.endswith("O")
            ])
            st.dataframe(rules_df, use_container_width=True, hide_index=True)

    # -----------------------------------------------------
    # TAB 2: UPLOAD BẢNG CHẤM CÔNG
    # -----------------------------------------------------
    with tab2:
        st.markdown("##### 📤 Tải lên file Excel Bảng chấm công đã khai báo")
        up_c1, up_c2 = st.columns(2)
        with up_c1:
            up_m = st.selectbox("Chấm công cho Tháng:", range(1, 13), index=date.today().month - 1, key="up_m")
        with up_c2:
            up_y = st.number_input("Năm:", min_value=2020, max_value=2030, value=date.today().year, key="up_y")

        uploaded_tk_file = st.file_uploader("Chọn file Excel chấm công (.xlsx, .xls):", type=["xlsx", "xls"], key="up_tk_file")

        if uploaded_tk_file:
            try:
                df_up = pd.read_excel(uploaded_tk_file).fillna("")
                st.write("📌 **Dữ liệu đọc từ file mẫu:**")
                st.dataframe(df_up.head(10), use_container_width=True)

                if st.button("💾 Cập nhật dữ liệu vào Hệ thống CSDL", type="primary"):
                    existing_df = load_timekeeping_db(up_m, up_y)
                    if not existing_df.empty and "Mã NV" in existing_df.columns:
                        combined_df = pd.concat([existing_df, df_up], ignore_index=True).drop_duplicates(subset=["Mã NV"], keep="last")
                    else:
                        combined_df = df_up

                    if save_timekeeping_db(combined_df, up_m, up_y):
                        st.success(f"✅ Đã lưu dữ liệu chấm công Tháng {up_m}/{up_y} thành công!")
                        st.rerun()
            except Exception as e:
                st.error(f"Lỗi xử lý file Excel: {e}")

    # -----------------------------------------------------
    # TAB 3: XEM & SỬA BẢNG CHẤM CÔNG TƯƠNG TÁC
    # -----------------------------------------------------
    with tab3:
        v_c1, v_c2, v_c3 = st.columns(3)
        with v_c1:
            view_m = st.selectbox("Chọn Tháng xem:", range(1, 13), index=date.today().month - 1, key="view_m")
        with v_c2:
            view_y = st.number_input("Chọn Năm xem:", min_value=2020, max_value=2030, value=date.today().year, key="view_y")
        with v_c3:
            filter_unit = st.selectbox("Lọc theo Đơn vị:", ["Tất cả đơn vị"] + unit_list, key="view_unit")

        df_view = load_timekeeping_db(view_m, view_y)

        if not df_view.empty:
            if filter_unit != "Tất cả đơn vị" and "Đơn vị" in df_view.columns:
                df_view_filtered = df_view[df_view["Đơn vị"] == filter_unit]
            else:
                df_view_filtered = df_view

            df_calculated = parse_and_summarize(df_view_filtered)

            st.markdown(f"##### 📋 Bảng Chi tiết Chấm công Tháng {view_m}/{view_y}")
            edited_tk = st.data_editor(
                df_calculated,
                use_container_width=True,
                hide_index=True,
                key=f"editor_tk_{view_m}_{view_y}"
            )

            if st.button("💾 Lưu chỉnh sửa Bảng Chấm công", type="primary", key="btn_save_tk_edit"):
                if save_timekeeping_db(edited_tk, view_m, view_y):
                    st.success("✅ Đã cập nhật thành công CSDL Chấm công!")
                    st.rerun()
        else:
            st.warning(f"Chưa có dữ liệu chấm công cho Tháng {view_m}/{view_y}. Vui lòng upload file Excel ở Tab 2.")

    # -----------------------------------------------------
    # TAB 4: BÁO CÁO TỔNG HỢP TÙY CHỌN
    # ---------------------------------------------------------
    with tab4:
        st.markdown("##### 📈 Báo cáo Tổng hợp Chấm công - Trực - Nghỉ bù / Phép")
        
        rep_type = st.radio("Chọn loại báo cáo tổng hợp:", ["Theo Tháng", "Theo Quý", "Theo Năm", "Khoảng thời gian tùy chọn"], horizontal=True)

        selected_months = []
        rep_year = date.today().year

        if rep_type == "Theo Tháng":
            rc1, rc2 = st.columns(2)
            with rc1:
                rm = st.selectbox("Chọn Tháng báo cáo:", range(1, 13), index=date.today().month - 1, key="rm_single")
            with rc2:
                rep_year = st.number_input("Chọn Năm:", min_value=2020, max_value=2030, value=date.today().year, key="ry_single")
            selected_months = [rm]

        elif rep_type == "Theo Quý":
            rc1, rc2 = st.columns(2)
            with rc1:
                r_q = st.selectbox("Chọn Quý:", ["Quý I (Tháng 1-3)", "Quý II (Tháng 4-6)", "Quý III (Tháng 7-9)", "Quý IV (Tháng 10-12)"])
            with rc2:
                rep_year = st.number_input("Chọn Năm:", min_value=2020, max_value=2030, value=date.today().year, key="ry_q")
            
            if "Quý I" in r_q: selected_months = [1, 2, 3]
            elif "Quý II" in r_q: selected_months = [4, 5, 6]
            elif "Quý III" in r_q: selected_months = [7, 8, 9]
            else: selected_months = [10, 11, 12]

        elif rep_type == "Theo Năm":
            rep_year = st.number_input("Chọn Năm Báo cáo:", min_value=2020, max_value=2030, value=date.today().year, key="ry_year")
            selected_months = list(range(1, 13))

        else:
            rc1, rc2 = st.columns(2)
            with rc1:
                m_start = st.selectbox("Từ Tháng:", range(1, 13), index=0)
            with rc2:
                m_end = st.selectbox("Đến Tháng:", range(1, 13), index=date.today().month - 1)
            rep_year = st.number_input("Năm:", min_value=2020, max_value=2030, value=date.today().year, key="ry_range")
            selected_months = list(range(m_start, m_end + 1))

        # Tổng hợp dữ liệu các tháng đã chọn
        all_dfs = []
        for m in selected_months:
            df_m = load_timekeeping_db(m, rep_year)
            if not df_m.empty:
                df_parsed = parse_and_summarize(df_m)
                all_dfs.append(df_parsed)

        if all_dfs:
            combined_rep = pd.concat(all_dfs, ignore_index=True)
            
            # Groupby theo Mã NV và Họ tên
            group_cols = ["Mã NV", "Họ và tên", "Chức vụ", "Đơn vị"]
            sum_cols = ["Tổng ngày công", "Số ca trực", "Nghỉ bù trực", "Nghỉ phép", "Nghỉ ốm/con ốm", "Nghỉ không lương"]
            
            # Đảm bảo các cột số tồn tại
            for sc in sum_cols:
                if sc not in combined_rep.columns:
                    combined_rep[sc] = 0.0

            final_report = combined_rep.groupby(group_cols)[sum_cols].sum().reset_index()

            st.write(f"📊 **BẢO CÁO TỔNG HỢP CÔNG - TRỰC - NGHỈ ({rep_type.upper()} NĂM {rep_year})**")
            st.dataframe(final_report, use_container_width=True, hide_index=True)

            # Xuất Excel báo cáo tổng hợp
            out_rep = io.BytesIO()
            with pd.ExcelWriter(out_rep, engine="openpyxl") as writer:
                final_report.to_excel(writer, index=False, sheet_name="BaoCaoTongHop")
            out_rep.seek(0)

            st.download_button(
                label="📥 Tải xuống Báo cáo Tổng hợp Excel",
                data=out_rep,
                file_name=f"Bao_Cao_Tong_Hop_Cham_Cong_{rep_type}_{rep_year}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary"
            )
        else:
            st.warning("Không tìm thấy dữ liệu chấm công trong khoảng thời gian đã chọn.")


if __name__ == "__main__":
    render_timekeeping_management()
