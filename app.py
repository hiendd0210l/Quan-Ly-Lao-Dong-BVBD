import pandas as pd
import plotly.express as px
import streamlit as st
from category_management import render_category_management
from employee_management import render_employee_management
from organization_management import render_organization_management
from timekeeping_management import render_timekeeping_management

# ---------------------------------------------------------
# 1. CẤU HÌNH TRANG STREAMLIT
# ---------------------------------------------------------
st.set_page_config(
    page_title="Hệ thống Quản lý Nhân sự - Bệnh viện Bưu điện",
    page_icon="🏥",
    layout="wide",
)


# ---------------------------------------------------------
# 2. HÀM HIỂN THỊ DASHBOARD THEO MẪU CHUẨN
# ---------------------------------------------------------
def render_dashboard():
    # Lấy dữ liệu thực tế từ Session State (Menu Quản lý Hồ sơ Cán bộ)
    df_emp = pd.DataFrame()
    if "employees_profile" in st.session_state:
        df_ses = st.session_state["employees_profile"]
        if isinstance(df_ses, pd.DataFrame) and not df_ses.empty:
            df_emp = df_ses.copy()

    total_emp = len(df_emp) if not df_emp.empty else 842  # Lấy 842 làm mặc định hoặc số thực tế

    # --- TIÊU ĐỀ VÀ NÚT TÁC VỤ NHANH ---
    col_t1, col_t2 = st.columns([4, 1])
    with col_t1:
        st.markdown(
            "<h2 style='color: #002060; margin-bottom: 0px;'>Tổng quan hệ"
            " thống nhân sự</h2>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<p style='color: #555; font-size: 14px;'>Một nhịp nhìn rõ ràng"
            " cho những việc cần xử lý đúng hạn[cite: 11].</p>",
            unsafe_allow_html=True,
        )
    with col_t2:
        if st.button("Mở danh sách hồ sơ ➔", type="primary"):
            st.rerun()

    st.markdown("---")

    # --- 1. 5 THẺ CHỈ SỐ TỔNG QUAN (METRICS CARDS MẪU) ---
    m1, m2, m3, m4, m5 = st.columns(5)
    
    with m1:
        st.markdown(
            """
            <div style="background-color: white; padding: 15px; border-radius: 8px; border-left: 4px solid #1F497D; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <span style="font-size: 12px; color: gray;">01-01</span>
                <h2 style="margin: 5px 0; color: #1F497D;">{}</h2>
                <p style="margin: 0; font-size: 13px; font-weight: bold;">Tổng số nhân sự</p>
                <p style="margin: 0; font-size: 11px; color: gray;">trong biên chế & hợp đồng[cite: 11]</p>
            </div>
            """.format(total_emp),
            unsafe_allow_html=True,
        )

    with m2:
        st.markdown(
            """
            <div style="background-color: white; padding: 15px; border-radius: 8px; border-left: 4px solid #274E13; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <span style="font-size: 12px; color: gray;">01-02</span>
                <h2 style="margin: 5px 0; color: #274E13;">{}</h2>
                <p style="margin: 0; font-size: 13px; font-weight: bold;">Đang làm việc</p>
                <p style="margin: 0; font-size: 11px; color: gray;">100% tổng hồ sơ[cite: 11]</p>
            </div>
            """.format(total_emp),
            unsafe_allow_html=True,
        )

    with m3:
        st.markdown(
            """
            <div style="background-color: white; padding: 15px; border-radius: 8px; border-left: 4px solid #E37D00; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <span style="font-size: 12px; color: gray;">01-03</span>
                <h2 style="margin: 5px 0; color: #E37D00;">0</h2>
                <p style="margin: 0; font-size: 13px; font-weight: bold;">Gia nhập tháng này</p>
                <p style="margin: 0; font-size: 11px; color: gray;">hồ sơ mới cập nhật[cite: 11]</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with m4:
        st.markdown(
            """
            <div style="background-color: white; padding: 15px; border-radius: 8px; border-left: 4px solid #C00000; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <span style="font-size: 12px; color: gray;">01-04</span>
                <h2 style="margin: 5px 0; color: #C00000;">4</h2>
                <p style="margin: 0; font-size: 13px; font-weight: bold;">Hồ sơ sắp hết hạn</p>
                <p style="margin: 0; font-size: 11px; color: gray;">cần rà soát sớm[cite: 11]</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with m5:
        st.markdown(
            """
            <div style="background-color: white; padding: 15px; border-radius: 8px; border-left: 4px solid #7030A0; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <span style="font-size: 12px; color: gray;">01-05</span>
                <h2 style="margin: 5px 0; color: #7030A0;">3</h2>
                <p style="margin: 0; font-size: 13px; font-weight: bold;">Cảnh báo chưa đọc</p>
                <p style="margin: 0; font-size: 11px; color: gray;">đang chờ xử lý[cite: 11]</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    st.write("")

    # --- 2. KHU VỰC BIỂU ĐỒ KHOA/PHÒNG & CẢNH BÁO ---
    col_dept, col_alert = st.columns([7, 5])

    with col_dept:
        st.markdown("##### PHÂN BỐ LỰC LƯỢNG")
        st.markdown(
            "**Nhân sự theo khoa / phòng** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
            " <span style='font-size: 12px; color: gray; border: 1px solid"
            " #ccc; padding: 2px 6px; border-radius: 4px;'>Đơn vị[cite: 11]</span>",
            unsafe_allow_html=True,
        )

        # Xử lý dữ liệu khoa phòng thực tế từ file
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

        # Biểu đồ thanh ngang (Horizontal Bar Chart) chuẩn mẫu giao diện
        fig_h = px.bar(
            df_dept,
            x="Số lượng",
            y="Khoa / Phòng",
            orientation="h",
            text="Số lượng",
            color="Số lượng",
            color_continuous_scale=["#1B4D3E", "#2E8B57", "#3CB371"],
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
        )
        st.plotly_chart(fig_h, use_container_width=True)

    with col_alert:
        c_head1, c_head2 = st.columns([3, 1])
        with c_head1:
            st.markdown("##### CẦN CHÚ Ý")
            st.markdown(
                "**Cảnh báo chưa đọc**",
                unsafe_allow_html=True,
            )
        with c_head2:
            st.markdown(
                "<p style='text-align: right; font-size: 13px; color:"
                " #0056b3; cursor: pointer;'>Xem tất cả ➔</p>",
                unsafe_allow_html=True,
            )

        # Danh sách cảnh báo mô phỏng theo mẫu
        st.markdown(
            """
            <div style="background-color: white; padding: 12px; border-radius: 6px; border: 1px solid #e0e0e0; margin-bottom: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: bold; font-size: 13px; color: #b71c1c;">🔴 Chứng chỉ hành nghề cần gia hạn</span>
                    <span style="background-color: #ffebee; color: #c62828; padding: 2px 8px; border-radius: 10px; font-size: 11px;">● Cao</span>
                </div>
                <p style="margin: 4px 0 0 0; font-size: 12px; color: #555;">Trần Khánh Ngọc • Hạn 16/10/2026[cite: 11]</p>
            </div>
            <div style="background-color: white; padding: 12px; border-radius: 6px; border: 1px solid #e0e0e0; margin-bottom: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: bold; font-size: 13px; color: #e65100;">🟠 Hợp đồng sắp hết hạn</span>
                    <span style="background-color: #fff3e0; color: #ef6c00; padding: 2px 8px; border-radius: 10px; font-size: 11px;">● Vừa</span>
                </div>
                <p style="margin: 4px 0 0 0; font-size: 12px; color: #555;">ĐD. Lê Quốc Bảo • Hạn 31/12/2026[cite: 11]</p>
            </div>
            <div style="background-color: white; padding: 12px; border-radius: 6px; border: 1px solid #e0e0e0;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: bold; font-size: 13px; color: #e65100;">🟠 Hợp đồng sắp hết hạn</span>
                    <span style="background-color: #fff3e0; color: #ef6c00; padding: 2px 8px; border-radius: 10px; font-size: 11px;">● Vừa</span>
                </div>
                <p style="margin: 4px 0 0 0; font-size: 12px; color: #555;">Trần Hùng Mạnh • Hạn 31/12/2026[cite: 11]</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # --- 3. KHỐI HOẠT ĐỘNG GẦN ĐÂY (DẤU VẾT VẬN HÀNH) ---
    c_act_head1, c_act_head2 = st.columns([4, 1])
    with c_act_head1:
        st.markdown(
            "<span style='font-size: 11px; color: gray; letter-spacing:"
            " 1px;'>DẤU VẾT VẬN HÀNH</span>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "##### Hoạt động gần đây",
            unsafe_allow_html=True,
        )
    with c_act_head2:
        st.markdown(
            "<p style='text-align: right; font-size: 12px; color:"
            " gray;'>Cập nhật tự động[cite: 11]</p>",
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div style="background-color: white; padding: 15px; border-radius: 8px; border: 1px solid #e0e0e0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                <div>
                    <p style="margin: 0; font-size: 13px; font-weight: bold;">🟢 Đã lưu trữ hồ sơ BS. Nguyễn Minh Anh.</p>
                    <p style="margin: 0; font-size: 11px; color: gray;">Phòng Nhân sự • 10:07 23-09[cite: 11]</p>
                </div>
                <div>
                    <p style="margin: 0; font-size: 13px; font-weight: bold;">🟢 Đã lưu trữ hồ sơ BS. Vũ Hoàng Nam.</p>
                    <p style="margin: 0; font-size: 11px; color: gray;">Phòng Nhân sự • 10:07 23-09[cite: 11]</p>
                </div>
            </div>
            <hr style="margin: 8px 0; border: none; border-top: 1px solid #eee;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                <div>
                    <p style="margin: 0; font-size: 13px; font-weight: bold;">🔵 Hệ thống tạo cảnh báo gia hạn chứng chỉ cho BS. Vũ Hoàng Nam.</p>
                    <p style="margin: 0; font-size: 11px; color: gray;">Hệ thống • 09:34 23-09[cite: 11]</p>
                </div>
                <div>
                    <p style="margin: 0; font-size: 13px; font-weight: bold;">🔵 CN. Trần Thu Hà đã cập nhật thông tin đào tạo.</p>
                    <p style="margin: 0; font-size: 11px; color: gray;">Phòng Nhân sự • 09:34 23-09[cite: 11]</p>
                </div>
            </div>
            <hr style="margin: 8px 0; border: none; border-top: 1px solid #eee;">
            <div>
                <p style="margin: 0; font-size: 13px; font-weight: bold;">🔵 Báo cáo biến động nhân sự tháng 09/2026 đã được xuất.</p>
                <p style="margin: 0; font-size: 11px; color: gray;">CN. Trần Thu Hà • 09:34 23-09[cite: 11]</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------
# 3. THANH MENU BÊN TRÁI (SIDEBAR)
# ---------------------------------------------------------
st.sidebar.title("MENU QUẢN TRỊ CÁN BỘ")
st.sidebar.markdown("---")
menu_choice = st.sidebar.radio(
    "Chọn chức năng:",
    [
        "1. 📊 Dashboard Tổng quan",
        "2. 📁 Danh mục Hệ thống",
        "3. 🏢 Quản lý Cơ cấu Tổ chức",
        "4. 👨‍⚕️ Quản lý Hồ sơ Cán bộ",
        "5. 📑 Quản lý Tuyển dụng",
        "6. 📝 Quản lý Hợp đồng Lao động",
        "7. 🔄 Điều động - Điều chuyển",
        "8. ⏰ Chấm công - Ca trực - Phân lịch",
        "9. 🏖️ Quản lý Nghỉ phép & Miễn trực",
        "10. 💰 Quản lý Tiền lương & Phụ cấp",
        "11. 🩺 Quản lý Chứng chỉ Hành nghề Y",
        "12. 🎓 Quản lý Đào tạo & Bồi dưỡng CML",
        "13. 🏆 Đánh giá & Đánh giá An toàn Bệnh viện",
        "14. 🎖️ Thi đua - Khen thưởng & Kỷ luật",
        "15. 🏥 Quản lý Sức khỏe & Bảo hiểm",
        "16. 📋 Quản lý Tài sản - Quy trình",
        "17. 📈 Báo cáo - Thống kê - CSDL Y tế",
        "18. ⚙️ Quản lý Hệ thống & Phân quyền",
    ],
)

# ---------------------------------------------------------
# 4. ĐIỀU HƯỚNG MÀN HÌNH THEO MENU AN TOÀN
# ---------------------------------------------------------
if "Dashboard Tổng quan" in menu_choice:
    render_dashboard()
elif "Danh mục Hệ thống" in menu_choice:
    render_category_management()
elif "Quản lý Cơ cấu Tổ chức" in menu_choice:
    render_organization_management()
elif "Quản lý Hồ sơ Cán bộ" in menu_choice:
    render_employee_management()
elif "Chấm công" in menu_choice:
    render_timekeeping_management()
else:
    st.title(menu_choice)
    st.info("Chức năng đang được nâng cấp và phát triển.")
