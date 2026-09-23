from datetime import datetime
import pandas as pd
import plotly.express as px
import streamlit as st

# 1. Cấu hình trang Streamlit
st.set_page_config(
    page_title="Quản lý Lao động - Bệnh viện Bưu điện",
    page_icon="🏥",
    layout="wide",
)


# 2. Đọc và xử lý dữ liệu từ file Excel
@st.cache_data
def load_data():
    excel_file = "Danh_sách_lao_động_25082026.xlsx"
    # Đọc từ dòng tiêu đề (Header row 8)
    df = pd.read_excel(excel_file, sheet_name=0, header=7)

    # Đặt lại tên các cột quan trọng
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
        cols[23]: "HD_XDXTH1_NgayKT",  # Ngày kết thúc HĐLĐ xác định thời hạn Lần 1
        cols[24]: "HD_XDXTH2_So",
        cols[27]: "HD_XDXTH2_NgayKT",  # Ngày kết thúc HĐLĐ xác định thời hạn Lần 2
        cols[42]: "IsDangVien",
    }
    df = df.rename(columns=rename_dict)

    # Lọc các dòng cán bộ hợp lệ
    df = df[
        df["MaNV"].notna() & df["MaNV"].astype(str).str.startswith("BVBD")
    ].copy()
    return df


try:
    df = load_data()
except Exception as e:
    st.error(f"Chưa đọc được file dữ liệu Excel. Lỗi: {e}")
    st.stop()

# 3. Giao diện Header & Logo
col_logo, col_title = st.columns([1, 5])
with col_logo:
    try:
        st.image("logo.png", width=110)
    except:
        st.write("🏥")
with col_title:
    st.title("BỆNH VIỆN BƯU ĐIỆN")
    st.subheader(
        "Hệ thống Quản lý Lao động & Hồ sơ Cán bộ (Phòng Nhân sự - Tổng hợp)"
    )

st.divider()

# 4. Sidebar Điều hướng
menu = st.sidebar.radio(
    "📌 MENU QUẢN TRỊ",
    [
        "1. Tổng quan Dashboard & Cảnh báo",
        "2. Danh sách Cán bộ Nhân viên",
        "3. Cảnh báo Hợp đồng sắp hết hạn",
        "4. Báo cáo Thống kê Nhân sự",
    ],
)

# 5. Xử lý các Menu
if menu == "1. Tổng quan Dashboard & Cảnh báo":
    st.subheader("📊 TỔNG QUAN NHÂN SỰ BỆNH VIỆN")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Tổng số Cán bộ / NV", f"{len(df):,} người")
    m2.metric(
        "Số lượng Khoa / Phòng", f"{df['PhongBan'].nunique():,} đơn vị"
    )
    m3.metric(
        "Số Đảng viên",
        f"{len(df[df['IsDangVien'].astype(str).str.contains('Có', na=False)]):,} đồng chí",
    )
    m4.metric(
        "HĐLĐ Không xác định TH",
        f"{len(df[df['LoaiLaoDong'].astype(str).str.contains('không xác định', case=False, na=False)]):,} người",
    )

    st.write("")
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
            df,
            names="TrinhDo",
            title="Cơ cấu Trình độ Cán bộ",
            hole=0.4,
        )
        st.plotly_chart(fig_td, use_container_width=True)

elif menu == "2. Danh sách Cán bộ Nhân viên":
    st.subheader("📋 TRA CỨU HỒ SƠ CÁN BỘ")
    search = st.text_input("🔍 Tìm theo Họ tên, Mã NV hoặc Chức danh:")

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

elif menu == "3. Cảnh báo Hợp đồng sắp hết hạn":
    st.subheader("⚠️ CẢNH BÁO TỰ ĐỘNG THỜI HẠN HỢP ĐỒNG LAO ĐỘNG")
    st.info(
        "Hệ thống tự động rà soát danh sách HĐLĐ Xác định thời hạn để nhắc gia hạn trước 30 - 60 - 90 ngày."
    )

    # Hiển thị các HĐLĐ có ngày kết thúc
    hd_df = df[df["HD_XDXTH1_NgayKT"].notna()][
        ["MaNV", "HoTen", "PhongBan", "HD_XDXTH1_So", "HD_XDXTH1_NgayKT"]
    ]
    st.write(
        f"Danh sách Cán bộ đang thuộc diện HĐLĐ xác định thời hạn ({len(hd_df)} nhân sự):"
    )
    st.dataframe(hd_df, use_container_width=True)

elif menu == "4. Báo cáo Thống kê Nhân sự":
    st.subheader("📈 TRÍCH XUẤT BÁO CÁO THỐNG KÊ")
    st.write("Thống kê theo Giới tính:")
    st.dataframe(df["GioiTinh"].value_counts())

    # Nút tải dữ liệu đã lọc về máy
    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 Tải Báo cáo Danh sách Nhân sự (File CSV/Excel)",
        data=csv,
        file_name="Bao_Cao_Nhan_Su_BVBD.csv",
        mime="text/csv",
    )
