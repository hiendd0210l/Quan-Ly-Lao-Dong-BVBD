import pandas as pd
import streamlit as st


def init_organization_data():
    """Khởi tạo dữ liệu cơ cấu tổ chức mặc định nếu chưa có trong session_state."""
    if "org_data" not in st.session_state:
        # Danh sách các cột chức danh mặc định
        st.session_state["org_job_titles"] = [
            "Bác sĩ",
            "Điều dưỡng",
            "Kỹ thuật viên",
            "Dược sĩ",
            "Hành chính / Khác",
        ]

        # Dữ liệu mẫu ban đầu
        st.session_state["org_data"] = pd.DataFrame([
            {
                "Tên Đơn vị / Khoa Phòng": "Phòng Khám Đa khoa",
                "Bác sĩ": 10,
                "Điều dưỡng": 15,
                "Kỹ thuật viên": 8,
                "Dược sĩ": 2,
                "Hành chính / Khác": 4,
            },
            {
                "Tên Đơn vị / Khoa Phòng": "Phòng Kinh doanh và Đầu tư",
                "Bác sĩ": 0,
                "Điều dưỡng": 0,
                "Kỹ thuật viên": 0,
                "Dược sĩ": 0,
                "Hành chính / Khác": 10,
            },
            {
                "Tên Đơn vị / Khoa Phòng": "Phòng Nhân sự - Tổng hợp",
                "Bác sĩ": 0,
                "Điều dưỡng": 0,
                "Kỹ thuật viên": 0,
                "Dược sĩ": 0,
                "Hành chính / Khác": 16,
            },
            {
                "Tên Đơn vị / Khoa Phòng": "Phòng Quản lý chất lượng - Công tác xã hội",
                "Bác sĩ": 1,
                "Điều dưỡng": 1,
                "Kỹ thuật viên": 0,
                "Dược sĩ": 0,
                "Hành chính / Khác": 2,
            },
            {
                "Tên Đơn vị / Khoa Phòng": "Phòng Tài chính - Kế toán",
                "Bác sĩ": 0,
                "Điều dưỡng": 0,
                "Kỹ thuật viên": 0,
                "Dược sĩ": 0,
                "Hành chính / Khác": 23,
            },
            {
                "Tên Đơn vị / Khoa Phòng": "Phòng Vật tư - TBYT",
                "Bác sĩ": 0,
                "Điều dưỡng": 0,
                "Kỹ thuật viên": 5,
                "Dược sĩ": 0,
                "Hành chính / Khác": 11,
            },
            {
                "Tên Đơn vị / Khoa Phòng": "Trung tâm Y tế Lao động Bưu điện",
                "Bác sĩ": 5,
                "Điều dưỡng": 8,
                "Kỹ thuật viên": 2,
                "Dược sĩ": 0,
                "Hành chính / Khác": 2,
            },
            {
                "Tên Đơn vị / Khoa Phòng": "Trung tâm Điều dưỡng và Chăm sóc sức khỏe Bưu điện",
                "Bác sĩ": 1,
                "Điều dưỡng": 1,
                "Kỹ thuật viên": 0,
                "Dược sĩ": 0,
                "Hành chính / Khác": 0,
            },
            {
                "Tên Đơn vị / Khoa Phòng": "Trung tâm Hỗ trợ Sinh sản",
                "Bác sĩ": 20,
                "Điều dưỡng": 30,
                "Kỹ thuật viên": 20,
                "Dược sĩ": 5,
                "Hành chính / Khác": 13,
            },
            {
                "Tên Đơn vị / Khoa Phòng": "Trung tâm Tế bào gốc và Di truyền",
                "Bác sĩ": 6,
                "Điều dưỡng": 5,
                "Kỹ thuật viên": 6,
                "Dược sĩ": 1,
                "Hành chính / Khác": 2,
            },
        ])


def render_organization_management():
    """Giao diện chính Quản lý Cơ cấu Tổ chức."""
    init_organization_data()

    st.subheader("🏢 SƠ ĐỒ CƠ CẤU TỔ CHỨC VÀ NHÂN SỰ CHI TIẾT")
    st.caption(
        "Thống kê số lượng nhân sự theo từng chức danh cụ thể ở mỗi đơn vị / khoa phòng."
    )

    df_org = st.session_state["org_data"].copy()
    job_titles = st.session_state["org_job_titles"]

    # -------------------------------------------------------------------------
    # 1. QUẢN LÝ CỘT CHỨC DANH (THÊM / XÓA CỘT CHỨC DANH)
    # -------------------------------------------------------------------------
    with st.expander("📐 **QUẢN LÝ TÙY CHỈNH CỘT CHỨC DANH (THÊM / XÓA CỘT)**"):
        col_a1, col_a2 = st.columns(2)

        with col_a1:
            new_title = st.text_input("➕ Nhập tên Chức danh mới muốn thêm:")
            if st.button("Thêm Chức danh"):
                if not new_title.strip():
                    st.warning("Vui lòng nhập tên chức danh!")
                elif new_title in job_titles:
                    st.warning("Chức danh này đã tồn tại!")
                else:
                    st.session_state["org_job_titles"].append(new_title)
                    st.session_state["org_data"][new_title] = 0
                    st.success(f"Đã thêm chức danh '{new_title}'!")
                    st.rerun()

        with col_a2:
            del_title = st.selectbox(
                "🗑️ Chọn Chức danh muốn xóa:",
                options=job_titles,
            )
            if st.button("Xóa Chức danh chọn", type="primary"):
                if len(job_titles) <= 1:
                    st.error("Bảng phải giữ lại ít nhất 01 chức danh!")
                else:
                    st.session_state["org_job_titles"].remove(del_title)
                    st.session_state["org_data"] = st.session_state[
                        "org_data"
                    ].drop(columns=[del_title])
                    st.success(f"Đã xóa chức danh '{del_title}'!")
                    st.rerun()

    st.divider()

    # -------------------------------------------------------------------------
    # 2. CHỈNH SỬA VÀ THÔNG THỐNG KÊ BẢNG DỮ LIỆU CƠ CẤU
    # -------------------------------------------------------------------------
    st.markdown("### 📋 **Chi tiết Cơ cấu & Định biên Nhân sự**")
    st.caption(
        "💡 *Bạn có thể chỉnh sửa số lượng trực tiếp trên bảng bên dưới, hoặc thêm đơn vị mới ở dòng cuối của bảng:*"
    )

    # Đảm bảo các cột chức danh là kiểu số nguyên
    for title in job_titles:
        df_org[title] = pd.to_numeric(df_org[title], errors="coerce").fillna(0).astype(int)

    # Cho phép người dùng trực tiếp sửa số lượng từng chức danh
    edited_df = st.data_editor(
        df_org,
        num_rows="dynamic",
        use_container_width=True,
        key="org_data_editor",
    )

    # Tính toán cột "TỔNG SỐ" cho từng dòng (Đơn vị)
    edited_df["TỔNG SỐ"] = edited_df[job_titles].sum(axis=1)

    # -------------------------------------------------------------------------
    # 3. TÍNH HÀNG TỔNG CỘNG CỦA MỖI CỘT Ở DƯỚI CÙNG BẢNG
    # -------------------------------------------------------------------------
    total_row = {"Tên Đơn vị / Khoa Phòng": "🔴 TỔNG CỘNG THÀNH TIỀN / TOÀN BỆNH VIỆN"}
    for title in job_titles:
        total_row[title] = edited_df[title].sum()
    total_row["TỔNG SỐ"] = edited_df["TỔNG SỐ"].sum()

    df_total = pd.DataFrame([total_row])

    # Hiển thị bảng tổng cộng bằng st.dataframe với giao diện làm nổi bật
    st.markdown("#### 📊 **HÀNG TỔNG CỘNG TOÀN BỆNH VIỆN**")
    st.dataframe(
        df_total,
        use_container_width=True,
        hide_index=True,
    )

    # -------------------------------------------------------------------------
    # 4. NÚT LƯU THAY ĐỔI DỮ LIỆU
    # -------------------------------------------------------------------------
    col_save, _ = st.columns([1, 4])
    with col_save:
        if st.button("💾 Lưu Cơ cấu Tổ chức", type="primary"):
            # Lược bỏ cột TỔNG SỐ trước khi lưu lại vào session_state (vì TỔNG SỐ tự động tính)
            save_df = edited_df.drop(columns=["TỔNG SỐ"], errors="ignore")
            st.session_state["org_data"] = save_df
            st.success("Đã cập nhật dữ liệu cơ cấu tổ chức thành công!")
            st.rerun()
