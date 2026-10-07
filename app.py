from datetime import datetime
import pandas as pd
import plotly.express as px
import streamlit as st
from category_management import render_category_management
from employee_management import render_employee_management
from organization_management import render_organization_management
from timekeeping_management import render_timekeeping_management

# ---------------------------------------------------------
# 1. CẤU HÌNH GIAO DIỆN & MÀU SẮC CHUẨN MẪU
# ---------------------------------------------------------
st.set_page_config(
    page_title="Hệ thống Quản lý Nhân sự - Bệnh viện Bưu điện",
    page_icon="🏥",
    layout="wide",
)

st.markdown(
    """
    <style>
        .stApp { background-color: #f8fafc; }
        [data-testid="stSidebar"] { background-color: #0f172a; color: #ffffff; }
        [data-testid="stSidebar"] .stRadio label { color: #cbd5e1 !important; font-size: 13px; }
        [data-testid="stSidebar"] .stRadio label:hover { color: #ffffff !important; background-color: #1e293b; border-radius: 4px; }
        .sidebar-section-title { font-size: 11px; text-transform: uppercase; color: #64748b; font-weight: bold; margin-top: 15px; margin-bottom: 5px; letter-spacing: 0.5px; }
    </style>
""",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# 2. HÀM XỬ LÝ NGÀY SINH VÀ QUẢN LÝ THÔNG MINH
# ---------------------------------------------------------
def extract_month_from_value(val):
    if pd.isna(val) or val is None:
        return None

    if isinstance(val, (pd.Timestamp, datetime)):
        return val.month

    s = str(val).strip()
    if not s or s.lower() in ["nan", "nat", "none", ""]:
        return None

    # Nếu là chuỗi số ngày Excel
    if s.replace(".", "", 1).isdigit():
        try:
            num = float(s)
            if num > 59:
                dt = pd.to_datetime("1899-12-30") + pd.Timedelta(days=num)
                return dt.month
        except Exception:
            pass

    # Quét các dấu phân cách ngày tháng
    for sep in ["/", "-", "."]:
        if sep in s:
            parts = s.split(sep)
            if len(parts) >= 3:
                for p in parts:
                    if p.isdigit():
                        val_int = int(p)
                        if 1 <= val_int <= 12 and len(p) <= 2:
                            return val_int
            elif len(parts) == 2:
                for p in parts:
                    if p.isdigit():
                        val_int = int(p)
                        if 1 <= val_int <= 12 and len(p) <= 2:
                            return val_int

    try:
        dt = pd.to_datetime(val, errors="coerce", dayfirst=True)
        if not pd.isna(dt):
            return dt.month
    except Exception:
        pass

    return None


def is_management_position(pos_str):
    if pd.isna(pos_str):
        return False
    p = str(pos_str).lower()
    keywords = [
        "trưởng",
        "phó",
        "giám đốc",
        "phụ trách",
        "tổ trưởng",
        "điều dưỡng trưởng",
        "kế toán trưởng",
    ]
    return any(kw in p for kw in keywords)


# ---------------------------------------------------------
# 3. HÀM HIỂN THỊ DASHBOARD
# ---------------------------------------------------------
def render_dashboard():
    df_emp = pd.DataFrame()
    if "employees_profile" in st.session_state:
        df_ses = st.session_state["employees_profile"]
        if isinstance(df_ses, pd.DataFrame) and not df_ses.empty:
            df_emp = df_ses.copy()

    total_emp = len(df_emp) if not df_emp.empty else 842

    # --- TIÊU ĐỀ & NÚT TÁC VỤ NHANH ---
    col_t1, col_t2 = st.columns([4, 1])
    with col_t1:
        st.markdown(
            "<span style='font-size: 11px; color: #64748b; letter-spacing: 1px;'>TRUNG"
            " TÂM ĐIỀU HÀNH • HÔM NAY</span>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<h2 style='color: #0f172a; margin-top: 0px; margin-bottom:"
            " 2px;'>Tổng quan nhân sự</h2>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<p style='color: #64748b; font-size: 13px;'>Một nhịp nhìn rõ ràng"
            " cho những việc cần xử lý đúng hạn[cite: 11].</p>",
            unsafe_allow_html=True,
        )
    with col_t2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Mở danh sách hồ sơ ➔", type="primary"):
            st.rerun()

    st.markdown("---")

    # --- 1. 5 THẺ CHỈ SỐ TỔNG QUAN (METRICS CARDS) ---
    m1, m2, m3, m4, m5 = st.columns(5)

    with m1:
        st.markdown(
            f"""
            <div style="background-color: white; padding: 16px; border-radius: 8px; border: 1px solid #e2e8f0; border-top: 3px solid #0f172a; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
                <span style="font-size: 11px; color: #94a3b8; font-family: monospace;">01-01</span>
                <h2 style="margin: 4px 0; color: #0f172a; font-size: 24px;">{total_emp}</h2>
                <p style="margin: 0; font-size: 13px; font-weight: 600; color: #1e293b;">Tổng số nhân sự</p>
                <p style="margin: 0; font-size: 11px; color: #64748b;">trong biên chế & hợp đồng[cite: 11]</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with m2:
        st.markdown(
            f"""
            <div style="background-color: white; padding: 16px; border-radius: 8px; border: 1px solid #e2e8f0; border-top: 3px solid #10b981; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
                <span style="font-size: 11px; color: #94a3b8; font-family: monospace;">01-02</span>
                <h2 style="margin: 4px 0; color: #10b981; font-size: 24px;">{total_emp}</h2>
                <p style="margin: 0; font-size: 13px; font-weight: 600; color: #1e293b;">Đang làm việc</p>
                <p style="margin: 0; font-size: 11px; color: #64748b;">100% tổng hồ sơ[cite: 11]</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with m3:
        st.markdown(
            """
            <div style="background-color: white; padding: 16px; border-radius: 8px; border: 1px solid #e2e8f0; border-top: 3px solid #f59e0b; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
                <span style="font-size: 11px; color: #94a3b8; font-family: monospace;">01-03</span>
                <h2 style="margin: 4px 0; color: #f59e0b; font-size: 24px;">0</h2>
                <p style="margin: 0; font-size: 13px; font-weight: 600; color: #1e293b;">Gia nhập tháng này</p>
                <p style="margin: 0; font-size: 11px; color: #64748b;">hồ sơ mới cập nhật[cite: 11]</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with m4:
        st.markdown(
            """
            <div style="background-color: white; padding: 16px; border-radius: 8px; border: 1px solid #e2e8f0; border-top: 3px solid #ef4444; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
                <span style="font-size: 11px; color: #94a3b8; font-family: monospace;">01-04</span>
                <h2 style="margin: 4px 0; color: #ef4444; font-size: 24px;">4</h2>
                <p style="margin: 0; font-size: 13px; font-weight: 600; color: #1e293b;">Hồ sơ sắp hết hạn</p>
                <p style="margin: 0; font-size: 11px; color: #64748b;">cần rà soát sớm[cite: 11]</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with m5:
        st.markdown(
            """
            <div style="background-color: white; padding: 16px; border-radius: 8px; border: 1px solid #e2e8f0; border-top: 3px solid #8b5cf6; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
                <span style="font-size: 11px; color: #94a3b8; font-family: monospace;">01-05</span>
                <h2 style="margin: 4px 0; color: #8b5cf6; font-size: 24px;">3</h2>
                <p style="margin: 0; font-size: 13px; font-weight: 600; color: #1e293b;">Cảnh báo chưa đọc</p>
                <p style="margin: 0; font-size: 11px; color: #64748b;">đang chờ xử lý[cite: 11]</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    # =========================================================
    # 2. THÔNG BÁO & DANH SÁCH SINH NHẬT NHÂN SỰ THEO THÁNG
    # =========================================================
    st.markdown("---")
    st.markdown(
        "🎂 **THỐNG KÊ NHÂN SỰ CÓ SINH NHẬT TRONG THÁNG**",
        unsafe_allow_html=True,
    )

    current_month = datetime.now().month
    col_s1, col_s2, col_s3, col_s4 = st.columns([2, 2, 2, 6])

    with col_s1:
        selected_birth_month = st.selectbox(
            "Chọn tháng sinh nhật:",
            list(range(1, 13)),
            index=current_month - 1,
            key="sb_birth_month",
        )

    birthday_count = 0
    df_birthday_filtered = pd.DataFrame()
    dob_col = None

    if not df_emp.empty:
        # Cho phép người dùng chọn trực tiếp cột Ngày sinh nếu hệ thống tự động quét không đúng
        with col_s2:
            cols_list = list(df_emp.columns)
            # Tự động gợi ý cột chứa từ khóa ngày sinh
            default_idx = 0
            for idx, c in enumerate(cols_list):
                if any(
                    k in str(c).lower()
                    for k in ["ngày sinh", "năm sinh", "dob", "ngay_sinh", "ns"]
                ):
                    default_idx = idx
                    break

            chosen_dob_col = st.selectbox(
                "Cột Ngày sinh trong Excel:",
                cols_list,
                index=default_idx,
                key="sb_dob_column",
            )
            dob_col = chosen_dob_col

        if dob_col:
            df_emp["_thang_sinh"] = df_emp[dob_col].apply(
                extract_month_from_value
            )
            df_birthday_filtered = df_emp[
                df_emp["_thang_sinh"] == selected_birth_month
            ].copy()
            birthday_count = len(df_birthday_filtered)

    with col_s3:
        st.write("")
        st.metric(
            label=f"Số lượng SN Tháng {selected_birth_month}",
            value=f"{birthday_count} cán bộ",
        )

    with col_s4:
        st.write("")
        show_birthday_list = st.checkbox(
            f"📋 Xem danh sách chi tiết cán bộ sinh nhật tháng"
            f" {selected_birth_month}"
        )

    if show_birthday_list:
        if birthday_count > 0:
            id_col, name_col, pos_col, title_col, unit_col = (
                None,
                None,
                None,
                None,
                None,
            )
            for col in df_birthday_filtered.columns:
                c_low = str(col).lower()
                if not id_col and any(
                    k in c_low for k in ["mã nv", "mã cb", "ma_nv", "id"]
                ):
                    id_col = col
                elif not name_col and any(
                    k in c_low for k in ["họ và tên", "họ tên", "tên", "name"]
                ):
                    name_col = col
                elif not pos_col and any(
                    k in c_low for k in ["chức vụ", "chuc_vu"]
                ):
                    pos_col = col
                elif not title_col and any(
                    k in c_low for k in ["chức danh", "chuc_danh", "vị trí"]
                ):
                    title_col = col
                elif not unit_col and any(
                    k in c_low
                    for k in ["đơn vị", "khoa", "phòng", "bộ phận", "don_vi"]
                ):
                    unit_col = col

            list_data = []
            for _, r in df_birthday_filtered.iterrows():
                cv = str(r.get(pos_col) or "").strip() if pos_col else ""
                list_data.append({
                    "Mã NV": str(r.get(id_col) or "").strip()
                    if id_col
                    else "",
                    "Họ và tên": str(r.get(name_col) or "").strip()
                    if name_col
                    else "",
                    "Chức vụ": cv,
                    "Chức danh": str(r.get(title_col) or "").strip()
                    if title_col
                    else "",
                    "Đơn vị công tác": str(r.get(unit_col) or "").strip()
                    if unit_col
                    else "",
                    "Ngày sinh": str(r.get(dob_col) or "").strip()
                    if dob_col
                    else "",
                    "_is_quan_ly": is_management_position(cv),
                })

            df_out = pd.DataFrame(list_data)
            df_out = df_out.sort_values(
                by="_is_quan_ly", ascending=False
            ).reset_index(drop=True)
            df_out.insert(0, "STT", range(1, len(df_out) + 1))
            df_out = df_out.drop(columns=["_is_quan_ly"])

            st.success(
                f"🎉 Đã tìm thấy {len(df_out)} cán bộ sinh nhật trong tháng"
                f" {selected_birth_month} (Đã ưu tiên xếp cán bộ quản lý lên"
                " đầu bảng):"
            )
            st.dataframe(df_out, use_container_width=True, hide_index=True)
        else:
            st.info(
                f"Không có cán bộ nào có ngày sinh trong tháng"
                f" {selected_birth_month} (hoặc định dạng cột Ngày sinh cần được"
                " chọn chính xác ở ô phía trên)."
            )

    st.markdown("---")

    # --- 3. BIỂU ĐỒ KHOA/PHÒNG & CẢNH BÁO CHƯA ĐỌC ---
    col_dept, col_alert = st.columns([7, 5])

    with col_dept:
        st.markdown(
            "<span style='font-size: 11px; color: #64748b; font-weight:"
            " bold;'>PHÂN BỐ LỰC LƯỢNG</span>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "**Nhân sự theo khoa / phòng**",
            unsafe_allow_html=True,
        )

        if not df_emp.empty:
            dept_col = None
            for col in df_emp.columns:
                if any(
                    k in str(col).lower()
                    for k in ["đơn vị", "khoa", "phòng", "bộ phận"]
                ):
                    dept_col = col
                    break
            if dept_col:
                dept_counts = (
                    df_emp[dept_col]
                    .astype(str)
                    .str.strip()
                    .value_counts()
                    .head(8)
                )
                df_dept = pd.DataFrame({
                    "Khoa / Phòng": dept_counts.index,
                    "Số lượng": dept_counts.values,
                })
            else:
                df_dept = pd.DataFrame({
                    "Khoa / Phòng": [
                        "Khoa Khám bệnh",
                        "Khoa Cấp cứu",
                        "Khoa Ngoại Tổng hợp",
                        "Khoa Xét nghiệm",
                        "Phòng Tổ chức Cán bộ",
                    ],
                    "Số lượng": [120, 85, 95, 60, 42],
                })
        else:
            df_dept = pd.DataFrame({
                "Khoa / Phòng": [
                    "Trung tâm Hỗ trợ Sinh sản",
                    "Khoa Sản",
                    "Khoa Ngoại Tổng hợp",
                    "Khoa Chẩn đoán hình ảnh",
                    "Khoa Gây mê hồi sức",
                    "Khoa Nội 1",
                    "Khoa Xét nghiệm 1",
                    "Khoa Hồi sức CC",
                ],
                "Số lượng": [88, 78, 46, 43, 41, 39, 27, 27],
            })

        fig_h = px.bar(
            df_dept,
            x="Số lượng",
            y="Khoa / Phòng",
            orientation="h",
            text="Số lượng",
            color="Số lượng",
            color_continuous_scale=["#0f766e", "#14b8a6", "#2dd4bf"],
        )
        fig_h.update_traces(
            textposition="outside", texttemplate="%{text}", cliponaxis=False
        )
        fig_h.update_layout(
            xaxis_title="",
            yaxis_title="",
            showlegend=False,
            height=320,
            yaxis=dict(autorange="reversed"),
            margin=dict(l=10, r=30, t=10, b=10),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_h, use_container_width=True)

    with col_alert:
        c_head1, c_head2 = st.columns([3, 1])
        with c_head1:
            st.markdown(
                "<span style='font-size: 11px; color: #64748b; font-weight:"
                " bold;'>CẦN CHÚ Ý</span>",
                unsafe_allow_html=True,
            )
            st.markdown(
                "**Cảnh báo chưa đọc**",
                unsafe_allow_html=True,
            )
        with c_head2:
            st.markdown(
                "<p style='text-align: right; font-size: 13px; color:"
                " #2563eb; cursor: pointer;'>Xem tất cả ➔</p>",
                unsafe_allow_html=True,
            )

        st.markdown(
            """
            <div style="background-color: white; padding: 12px; border-radius: 6px; border: 1px solid #e2e8f0; margin-bottom: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: bold; font-size: 13px; color: #b91c1c;">🔴 Chứng chỉ hành nghề cần gia hạn</span>
                    <span style="background-color: #fee2e2; color: #b91c1c; padding: 2px 8px; border-radius: 10px; font-size: 11px;">● Cao</span>
                </div>
                <p style="margin: 4px 0 0 0; font-size: 12px; color: #475569;">Trần Khánh Ngọc • Hạn 16/10/2026[cite: 11]</p>
            </div>
            <div style="background-color: white; padding: 12px; border-radius: 6px; border: 1px solid #e2e8f0; margin-bottom: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: bold; font-size: 13px; color: #c2410c;">🟠 Hợp đồng sắp hết hạn</span>
                    <span style="background-color: #ffedd5; color: #c2410c; padding: 2px 8px; border-radius: 10px; font-size: 11px;">● Vừa</span>
                </div>
                <p style="margin: 4px 0 0 0; font-size: 12px; color: #475569;">ĐD. Lê Quốc Bảo • Hạn 31/12/2026[cite: 11]</p>
            </div>
            <div style="background-color: white; padding: 12px; border-radius: 6px; border: 1px solid #e2e8f0;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: bold; font-size: 13px; color: #c2410c;">🟠 Hợp đồng sắp hết hạn</span>
                    <span style="background-color: #ffedd5; color: #c2410c; padding: 2px 8px; border-radius: 10px; font-size: 11px;">● Vừa</span>
                </div>
                <p style="margin: 4px 0 0 0; font-size: 12px; color: #475569;">Trần Hùng Mạnh • Hạn 31/12/2026[cite: 11]</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # --- 4. KHỐI HOẠT ĐỘNG GẦN ĐÂY ---
    c_act_head1, c_act_head2 = st.columns([4, 1])
    with c_act_head1:
        st.markdown(
            "<span style='font-size: 11px; color: #64748b; letter-spacing:"
            " 1px; font-weight: bold;'>DẤU VẾT VẬN HÀNH</span>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "##### Hoạt động gần đây",
            unsafe_allow_html=True,
        )
    with c_act_head2:
        st.markdown(
            "<p style='text-align: right; font-size: 12px; color:"
            " #64748b;'>Cập nhật tự động[cite: 11]</p>",
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div style="background-color: white; padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                <div>
                    <p style="margin: 0; font-size: 13px; font-weight: bold; color: #1e293b;">🟢 Đã lưu trữ hồ sơ BS. Nguyễn Minh Anh.</p>
                    <p style="margin: 0; font-size: 11px; color: #64748b;">Phòng Nhân sự • 10:07 23-09[cite: 11]</p>
                </div>
                <div>
                    <p style="margin: 0; font-size: 13px; font-weight: bold; color: #1e293b;">🟢 Đã lưu trữ hồ sơ BS. Vũ Hoàng Nam.</p>
                    <p style="margin: 0; font-size: 11px; color: #64748b;">Phòng Nhân sự • 10:07 23-09[cite: 11]</p>
                </div>
            </div>
            <hr style="margin: 8px 0; border: none; border-top: 1px solid #f1f5f9;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                <div>
                    <p style="margin: 0; font-size: 13px; font-weight: bold; color: #1e293b;">🔵 Hệ thống tạo cảnh báo gia hạn chứng chỉ cho BS. Vũ Hoàng Nam.</p>
                    <p style="margin: 0; font-size: 11px; color: #64748b;">Hệ thống • 09:34 23-09[cite: 11]</p>
                </div>
                <div>
                    <p style="margin: 0; font-size: 13px; font-weight: bold; color: #1e293b;">🔵 CN. Trần Thu Hà đã cập nhật thông tin đào tạo.</p>
                    <p style="margin: 0; font-size: 11px; color: #64748b;">Phòng Nhân sự • 09:34 23-09[cite: 11]</p>
                </div>
            </div>
            <hr style="margin: 8px 0; border: none; border-top: 1px solid #f1f5f9;">
            <div>
                <p style="margin: 0; font-size: 13px; font-weight: bold; color: #1e293b;">🔵 Báo cáo biến động nhân sự tháng 09/2026 đã được xuất.</p>
                <p style="margin: 0; font-size: 11px; color: #64748b;">CN. Trần Thu Hà • 09:34 23-09[cite: 11]</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------
# 4. THANH MENU BÊN TRÁI (SIDEBAR) ĐẦY ĐỦ
# ---------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px;">
            <div style="background-color: #2563eb; color: white; width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 16px;">BV</div>
            <div>
                <div style="font-weight: bold; font-size: 14px; color: white;">BỆNH VIỆN BƯU ĐIỆN</div>
                <div style="font-size: 11px; color: #94a3b8;">VNPT - HRM</div>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div class='sidebar-section-title'>Điều hành</div>",
        unsafe_allow_html=True,
    )
    menu_choice = st.radio(
        "Điều hành",
        ["🏠 Tổng quan", "👥 Hồ sơ nhân sự", "🏢 Sơ đồ tổ chức"],
        label_visibility="collapsed",
    )

    st.markdown(
        "<div class='sidebar-section-title'>Nghiệp vụ nhân sự</div>",
        unsafe_allow_html=True,
    )
    menu_nv = st.selectbox(
        "Nghiệp vụ nhân sự",
        [
            "Chọn nghiệp vụ...",
            "Tuyển dụng & tiếp nhận",
            "Hợp đồng & quyết định",
            "Lương & ngạch bậc",
            "Đào tạo & chứng chỉ",
            "Nghỉ phép & chấm công",
            "Đánh giá & khen thưởng",
            "Sức khỏe nghề nghiệp",
        ],
        label_visibility="collapsed",
    )

    st.markdown(
        "<div class='sidebar-section-title'>Dịch vụ nội bộ</div>",
        unsafe_allow_html=True,
    )
    menu_dv = st.selectbox(
        "Dịch vụ nội bộ",
        ["Chọn dịch vụ...", "Cổng nhân viên (ESS)", "Quản lý đơn vị (MSS)"],
        label_visibility="collapsed",
    )

    st.markdown(
        "<div class='sidebar-section-title'>Quản trị & Báo cáo</div>",
        unsafe_allow_html=True,
    )
    menu_qt = st.selectbox(
        "Quản trị & Báo cáo",
        [
            "Chọn chức năng...",
            "Cảnh báo hạn",
            "Chính sách & phúc lợi",
            "Báo cáo quản trị",
            "Phê duyệt & luân chuyển",
            "Kho văn bản nhân sự",
            "Phân quyền & tài khoản",
            "Thiết lập hệ thống",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown(
        """
        <div style="background-color: #1e293b; padding: 10px; border-radius: 6px; font-size: 11px; color: #94a3b8;">
            <div style="color: #38bdf8; font-weight: bold; margin-bottom: 4px;">TRẠNG THÁI HỆ THỐNG</div>
            <div>842 hồ sơ chính thức đã đồng bộ từ danh sách ngày 25/08/2026.</div>
            <hr style="border: none; border-top: 1px solid #334155; margin: 6px 0;">
            <div style="font-weight: bold; color: white;">Phòng Tổ chức</div>
            <div>Quản trị viên</div>
        </div>
    """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------
# 5. ĐIỀU HƯỚNG TRANG DỰA TRÊN MENU LỰA CHỌN
# ---------------------------------------------------------
if "Tổng quan" in menu_choice:
    render_dashboard()
elif "Hồ sơ nhân sự" in menu_choice:
    render_employee_management()
elif "Sơ đồ tổ chức" in menu_choice:
    render_organization_management()
elif menu_nv != "Chọn nghiệp vụ...":
    if "chấm công" in menu_nv.lower():
        render_timekeeping_management()
    else:
        st.title(f"Phân hệ: {menu_nv}")
        st.info("Chức năng đang được vận hành và đồng bộ dữ liệu.")
elif menu_qt != "Chọn chức năng...":
    if "danh mục" in menu_qt.lower() or "thiết lập" in menu_qt.lower():
        render_category_management()
    else:
        st.title(f"Quản trị: {menu_qt}")
        st.info("Chức năng đang được vận hành và đồng bộ dữ liệu.")
else:
    render_dashboard()
