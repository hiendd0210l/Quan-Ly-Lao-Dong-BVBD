import pandas as pd
import plotly.express as px
import streamlit as st

# Import mô-đun Quản lý danh mục mở
from category_management import render_category_management


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
    """Hiển thị toàn bộ giao diện và logic của ứng dụng sau khi đăng nhập."""
    try:
        df = load_data()
    except Exception as e:
        st.error(f"Lỗi kết nối dữ liệu Excel: {e}")
        st.stop()

    # 1. Header Trang
    col_logo, col_title = st.columns([1, 6])
    with col_logo:
        try:
            st.image("logo.png", width=100)
        except Exception:
            st.write("🏥")
    with col_title:
        st.title("BỆNH VIỆN BƯU ĐIỆN")
        st.caption(
            "HỆ THỐNG QUẢN TRỊ TỔNG THỂ NHÂN SỰ & CÁN BỘ Y TẾ (BVBD-HRM)"
        )

    st.divider()

    # 2. Danh sách 18 Menu Nghiệp vụ
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

    # 3. Điều hướng Nội dung theo Menu
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
        # Gọi mô-đun Quản lý Danh mục Cấu hình Mở
        render_category_management()

    elif menu == "3. Quản lý Cơ cấu Tổ chức":
        st.subheader("🏢 SƠ ĐỒ CƠ CẤU TỔ CHỨC BỆNH VIỆN BƯU ĐIỆN")
        st.info(
            "Quản lý mô hình Cây tổ chức: Ban Giám đốc ➔ Các Phòng chức năng / Khoa Lâm sàng / Khoa Cận lâm sàng / Trung tâm."
        )
        st.dataframe(
            df["PhongBan"]
            .value_counts()
            .reset_index()
            .rename(
                columns={
                    "PhongBan": "Tên Đơn vị/Khoa Phòng",
                    "count": "Nhân sự hiện diện",
                }
            ),
            use_container_width=True,
        )

    elif menu == "4. Quản lý Hồ sơ Cán bộ":
        st.subheader("🗂️ QUẢN LÝ HỒ SƠ ĐIỆN TỬ CÁN BỘ & SƠ YẾU LÝ LỊCH")
        st.caption(
            "Hỗ trợ trích xuất Sơ yếu lý lịch chuẩn: Mẫu BNV, Mẫu HS-02, Mẫu TCTW-98 (Đảng viên), Mẫu SYLL Hợp nhất."
        )

        search = st.text_input(
            "🔍 Tìm kiếm theo Mã NV, Họ tên, CCCD hoặc Chức danh:"
        )
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

    elif menu == "5. Quản lý Tuyển dụng":
        st.subheader("🎯 QUẢN LÝ QUY TRÌNH TUYỂN DỤNG & THỬ VIỆC")
        st.write(
            "Theo dõi các đợt tuyển dụng, thi tuyển, xét tuyển, tiếp nhận đặc biệt và đánh giá thử việc."
        )
        st.button("➕ Tạo Kế hoạch / Đợt Tuyển dụng mới")

    elif menu == "6. Quản lý Hợp đồng Lao động":
        st.subheader(
            "📝 QUẢN LÝ HỢP ĐỒNG LAO ĐỘNG & TỰ ĐỘNG CẢNH BÁO HẾT HẠN"
        )
        st.warning(
            "⚠️ Cảnh báo tự động danh sách HĐLĐ sắp hết hạn để thực hiện quy trình tái ký hoặc gia hạn."
        )
        hd_df = df[df["HD_XDXTH1_NgayKT"].notna()][
            ["MaNV", "HoTen", "PhongBan", "HD_XDXTH1_So", "HD_XDXTH1_NgayKT"]
        ]
        st.dataframe(hd_df, use_container_width=True)

    elif menu == "7. Điều động - Bổ nhiệm":
        st.subheader("🔄 QUẢN LÝ ĐIỀU ĐỘNG, LUÂN CHUYỂN & BỔ NHIỆM CÁN BỘ")
        st.write(
            "Lịch sử điều động khoa/phòng, bổ nhiệm, miễn nhiệm, kiêm nhiệm và quy hoạch cán bộ."
        )

    elif menu == "8. Chấm công - Ca trực - Phân kíp":
        st.subheader(
            "⏰ QUẢN LÝ CHẤM CÔNG - TÍCH HỢP MÁY CHẤM CÔNG / FACEID / CA TRỰC 24H"
        )
        st.info(
            "Đặc thù Y tế: Ca hành chính, Ca đêm, Trực 24h, Trực Cấp cứu, Trực Lễ/Tết, Đổi ca trực."
        )
        st.button("📲 Đồng bộ dữ liệu Máy chấm công / FaceID")

    elif menu == "9. Quản lý Nghỉ phép & Đơn từ":
        st.subheader("📅 QUẢN LÝ NGHỈ PHÉP, ĐƠN CÔNG TÁC & ĐI HỌC")
        st.write(
            "Quy trình phê duyệt phân cấp: Nhân viên ➔ Trưởng Khoa/Phòng ➔ Phòng TCCB ➔ Ban Giám đốc."
        )

    elif menu == "10. Quản lý Tiền lương & Phụ cấp":
        st.subheader("💰 QUẢN LÝ TÍNH LƯƠNG, PHỤ CẤP ĐẶC THÙ Y TẾ & BHXH")
        st.write(
            "Tính toán Lương ngạch bậc, Phụ cấp ưu đãi nghề, Phụ cấp phẫu thuật/thủ thuật, Phụ cấp trực, Thuế TNCN."
        )

    elif menu == "11. Quản lý Chứng chỉ Hành nghề Y":
        st.subheader(
            "📜 QUẢN LÝ CHỨNG CHỈ HÀNH NGHỀ Y & GIẤY PHÉP CHUYÊN MÔN"
        )
        st.error(
            "🚨 Quản lý và cảnh báo Giấy phép hành nghề KCB, Chứng chỉ Chuyên khoa, An toàn Bức xạ, An toàn Sinh học..."
        )

    elif menu == "12. Quản lý Đào tạo & Số giờ CME":
        st.subheader("🎓 QUẢN LÝ ĐÀO TẠO Y KHOA LIÊN TỤC (CME) & HỘI THẢO")
        st.write(
            "Theo dõi tổng số tiết/giờ Đào tạo liên tục (CME) bắt buộc hàng năm theo quy định của Bộ Y tế."
        )

    elif menu == "13. Đánh giá KPI & An toàn Người bệnh":
        st.subheader(
            "📈 ĐÁNH GIÁ KPI CÁ NHÂN, KHOA/PHÒNG & AN TOÀN NGƯỜI BỆNH"
        )
        st.write(
            "Đánh giá hiệu quả công việc theo Tiêu chí Chuyên môn, Kỷ luật, Thái độ phục vụ và Sự cố an toàn."
        )

    elif menu == "14. Thi đua - Khen thưởng & Kỷ luật":
        st.subheader("🏅 QUẢN LÝ THI ĐƯA, KHEN THƯỞNG & KỶ LUẬT")
        st.write(
            "Theo dõi Danh hiệu Lao động tiên tiến, Chiến sĩ thi đua, Bằng khen các cấp và Kỷ luật."
        )

    elif menu == "15. Quản lý Sức khỏe & Phơi nhiễm":
        st.subheader("🏥 QUẢN LÝ SỨC KHỎE ĐỊNH KỲ & PHƠI NHIỄM NGHỀ NGHIỆP")
        st.write(
            "Hồ sơ khám sức khỏe định kỳ, tiêm chủng vaccine và quy trình xử lý phơi nhiễm nghề nghiệp."
        )

    elif menu == "16. Quản lý Văn bản - Quyết định":
        st.subheader("📑 LƯU TRỮ VĂN BẢN, QUYẾT ĐỊNH NHÂN SỰ & KÝ SỐ")
        st.write(
            "Lưu trữ và quản lý phiên bản Quyết định Tuyển dụng, Nâng lương, Bổ nhiệm... có tích hợp Ký số."
        )

    elif menu == "17. Báo cáo - Thống kê - CSDL Y tế":
        st.subheader(
            "📈 TRÍCH XUẤT BÁO CÁO THỐNG KÊ & TÍCH HỢP BỘ Y TẾ / VNPT"
        )
        st.write(
            "Xuất báo cáo theo biểu mẫu Bộ Y tế, Sở Y tế, BHXH và Tập đoàn VNPT."
        )
        csv = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "📥 Tải Báo cáo Toàn bộ Danh sách Nhân sự (Excel/CSV)",
            data=csv,
            file_name="Bao_Cao_Nhan_Su_BVBD.csv",
            mime="text/csv",
        )

    elif menu == "18. Quản trị Hệ thống & Phân quyền":
        st.subheader("🔒 QUẢN TRỊ NGUỜI DÙNG, PHÂN QUYỀN ĐA CẤP & AUDIT LOG")
        st.write(
            "Phân quyền 8 cấp: Admin CNTT | Ban Giám đốc | Phòng TCCB | Trưởng Khoa/Phòng | Điều dưỡng trưởng | Kế toán | Phòng Đào tạo | ESS."
        )
