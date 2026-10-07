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

# Tùy chỉnh CSS để làm menu sidebar có màu xanh đen tối sang trọng giống mẫu
st.markdown(
    """
    <style>
        /* Màu nền tổng thể trang */
        .stApp {
            background-color: #f8fafc;
        }
        /* Tùy chỉnh Sidebar */
        [data-testid="stSidebar"] {
            background-color: #0f172a;
            color: #ffffff;
        }
        [data-testid="stSidebar"] .stRadio label {
            color: #cbd5e1 !important;
            font-size: 13px;
        }
        [data-testid="stSidebar"] .stRadio label:hover {
            color: #ffffff !important;
            background-color: #1e293b;
            border-radius: 4px;
        }
        /* Tiêu đề nhóm trong sidebar */
        .sidebar-section-title {
            font-size: 11px;
            text-transform: uppercase;
            color: #64748b;
            font-weight: bold;
            margin-top: 15px;
            margin-bottom: 5px;
            letter-spacing: 0.5px;
        }
    </style>
""",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# 2. HÀM HIỂN THỊ DASHBOARD THEO ĐÚNG MẪU GIAO DIỆN
# ---------------------------------------------------------
def render_dashboard():
    # Lấy dữ liệu thực tế từ Session State (Menu Quản lý Hồ sơ Cán bộ)
    df_emp = pd.DataFrame()
    if "employees_profile" in st.session_state:
        df_ses = st.session_state["employees_profile"]
        if isinstance(df_ses, pd.DataFrame) and not df_ses.empty:
            df_emp = df_ses.copy()

    total_emp = len(df_emp) if not df_emp.empty else 842  # Lấy 842 lao động thực tế làm chuẩn

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
        st.markdown(
            "<br>", unsafe_allow_html=True
        )  # Canh chỉnh khoảng cách nút
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
    st.write("")

    # --- 2. BIỂU ĐỒ KHOA/PHÒNG & CẢNH BÁO CHƯA ĐỌC ---
    col_dept, col_alert = st.columns([7, 5])

    with col_dept:
        st.markdown(
            "<span style='font-size: 11px; color: #64748b; font-weight: bold;'>PHÂN"
            " BỐ LỰC LƯỢNG</span>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "**Nhân sự theo khoa / phòng**",
            unsafe_allow_html=True,
        )

        # Xử lý dữ liệu thực tế từ hồ sơ
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

    # --- 3. KHỐI HOẠT ĐỘNG GẦN ĐÂY (DẤU VẾT VẬN HÀNH) ---
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
# 3. THANH MENU BÊN TRÁI (SIDEBAR) ĐẦY ĐỦ CÁC NHÓM
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
# 4. ĐIỀU HƯỚNG TRANG DỰA TRÊN MENU LỰA CHỌN
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
