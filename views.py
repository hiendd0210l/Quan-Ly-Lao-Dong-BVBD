import pandas as pd
import plotly.express as px
import streamlit as st


@st.cache_data
def load_data():
    excel_file = "Danh_sách_lao_động_25082026.xlsx"
    df = pd.read_excel(excel_file, sheet_name=0, header=7)

    cols = list(df.columns)
    rename_dict = {
        cols[1]: "MaNV",
        cols[2]: "DonVi",
        cols[3]: "PhongBan",
        cols[5]: "HoTen",
        cols[6]: "GioiTinh",
        cols[7]: "NgaySinh",
        cols[9]: "TrinhDo",
        cols[10]: "ChucDanh",
        cols[12]: "LoaiLaoDong",
        cols[20]: "HD_XDXTH1_So",
        cols[23]: "HD_XDXTH1_NgayKT",
        cols[24]: "HD_XDXTH2_So",
        cols[27]: "HD_XDXTH2_NgayKT",
        cols[42]: "IsDangVien",
    }
    df = df.rename(columns=rename_dict)
    df = df[
        df["MaNV"].notna() & df["MaNV"].astype(str).str.startswith("BVBD")
    ].copy()
    return df


def render_main_app():
    """Hiển thị toàn bộ ứng dụng chính sau khi đăng nhập."""
    try:
        df = load_data()
    except Exception as e:
        st.error(f"Lỗi kết nối dữ liệu Excel: {e}")
        st.stop()

    # Header
    col_logo, col_title = st.columns([1, 6])
    with col_logo:
        try:
            st.image("logo.png", width=100)
        except:
            st.write("🏥")
    with col_title:
        st.title("BỆNH VIỆN BƯU ĐIỆN")
        st.caption(
            "HỆ THỐNG QUẢN TRỊ TỔNG THỂ NHÂN SỰ & CÁN BỘ Y TẾ (BVBD-HRM)"
        )

    st.divider()

    # Sidebar Menu
    list_menu = [
        "1. Dashboard Tổng quan",
        "2. Danh mục Hệ thống",
        "3. Quản lý Cơ cấu Tổ chức",
        "4. Quản lý Hồ sơ Cán bộ",
        "5. Quản lý Tuyển dụng",
        "6. Quản lý Hợp đồng Lao động",
        "7. Điều động - Bổ nhiệm",
        "8. Chấm công - Ca trực - Phân kíp",
        "9. Quản lý Nghỉ phép & Đơn từ",
        "10. Quản lý Tiền lương & Phụ cấp",
        "11. Quản lý Chứng chỉ Hành nghề Y",
        "12. Quản lý Đào tạo & Số giờ CME",
        "13. Đánh giá KPI & An toàn Người bệnh",
        "14. Thi đua - Khen thưởng & Kỷ luật",
        "15. Quản lý Sức khỏe & Phơi nhiễm",
        "16. Quản lý Văn bản - Quyết định",
        "17. Báo cáo - Thống kê - CSDL Y tế",
        "18. Quản trị Hệ thống & Phân quyền",
    ]

    menu = st.sidebar.radio("📌 MENU QUẢN TRỊ CÁN BỘ", list_menu)

    # Hiển thị nội dung theo Menu chọn
    if menu == "1. Dashboard Tổng quan":
        st.subheader("📊 DASHBOARD TỔNG QUAN NHÂN SỰ BỆNH VIỆN")
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Tổng cán bộ/NV", f"{len(df):,} người")
        m2.metric(
            "Khoa/Phòng/Trung tâm", f"{df['PhongBan'].nunique():,} đơn vị"
        )
        m3.metric(
            "Đảng viên",
            f"{len(df[df['IsDangVien'].astype(str).str.contains('Có', na=False)]):,} đồng chí",
        )
        m4.metric(
            "HĐ Không xác định TH",
            f"{len(df[df['LoaiLaoDong'].astype(str).str.contains('không xác định', case=False, na=False)]):,} người",
        )
        m5.metric(
            "Cảnh báo HĐLĐ hết hạn",
            "12 trường hợp",
            delta="-3",
            delta_color="inverse",
        )

        c1, c2 = st.columns(2)
        with c1:
            fig_pb = px.bar(
                df["PhongBan"].value_counts().reset_index().head(10),
                x="count",
                y="PhongBan",
                orientation="h",
                title="Top 10 Khoa/Phòng đông nhân sự nhất",
                labels={"count": "Số lượng", "PhongBan": "Khoa/Phòng"},
            )
            st.plotly_chart(fig_pb, use_container_width=True)
        with c2:
            fig_td = px.pie(
                df, names="TrinhDo", title="Cơ cấu Trình độ Cán bộ", hole=0.4
            )
            st.plotly_chart(fig_td, use_container_width=True)

    elif menu == "2. Danh mục Hệ thống":
        st.subheader("⚙️ QUẢN LÝ DANH MỤC HỆ THỐNG DÙNG CHUNG")
        tab1, tab2 = st.tabs(
            ["Chức danh & Mạch ngạch", "Trình độ / Chuyên môn"]
        )
        with tab1:
            st.dataframe(
                pd.DataFrame({
                    "Mã CD": ["BS", "BSCK1", "BSCK2", "DD", "KTV", "DS"],
                    "Tên Chức Danh": [
                        "Bác sĩ",
                        "Bác sĩ CKI",
                        "Bác sĩ CKII",
                        "Điều dưỡng",
                        "Kỹ thuật viên",
                        "Dược sĩ",
                    ],
                    "Mạch Ngạch": [
                        "V.08.01.03",
                        "V.08.01.02",
                        "V.08.01.01",
                        "V.08.05.12",
                        "V.08.07.23",
                        "V.08.08.26",
                    ],
                }),
                use_container_width=True,
            )

    elif menu == "4. Quản lý Hồ sơ Cán bộ":
        st.subheader("🗂️ QUẢN LÝ HỒ SƠ ĐIỆN TỬ CÁN BỘ & SƠ YẾU LÝ LỊCH")
        search = st.text_input("🔍 Tìm kiếm theo Mã NV, Họ tên hoặc Chức danh:")
        df_show = df.copy()
        if search:
            df_show = df_show[
                df_show["HoTen"].str.contains(search, case=False, na=False)
                | df_show["MaNV"].str.contains(search, case=False, na=False)
                | df_show["ChucDanh"].str.contains(search, case=False, na=False)
            ]
        st.dataframe(
            df_show[
                [
                    "MaNV",
                    "HoTen",
                    "GioiTinh",
                    "PhongBan",
                    "ChucDanh",
                    "TrinhDo",
                    "LoaiLaoDong",
                ]
            ],
            use_container_width=True,
        )

    elif menu == "6. Quản lý Hợp đồng Lao động":
        st.subheader(
            "📝 QUẢN LÝ HỢP ĐỒNG LAO ĐỘNG & TỰ ĐỘNG CẢNH BÁO HẾT HẠN"
        )
        hd_df = df[df["HD_XDXTH1_NgayKT"].notna()][
            ["MaNV", "HoTen", "PhongBan", "HD_XDXTH1_So", "HD_XDXTH1_NgayKT"]
        ]
        st.dataframe(hd_df, use_container_width=True)

    elif menu == "17. Báo cáo - Thống kê - CSDL Y tế":
        st.subheader(
            "📈 TRÍCH XUẤT BÁO CÁO THỐNG KÊ & TÍCH HỢP BỘ Y TẾ / VNPT"
        )
        csv = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "📥 Tải Báo cáo Toàn bộ Danh sách Nhân sự (Excel/CSV)",
            data=csv,
            file_name="Bao_Cao_Nhan_Su_BVBD.csv",
            mime="text/csv",
        )

    else:
        st.subheader(f"📌 {menu}")
        st.info("Tính năng đang được kết nối dữ liệu chi tiết.")
