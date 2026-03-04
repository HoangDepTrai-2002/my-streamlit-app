import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image
import os

# --- CẤU HÌNH THƯ MỤC LƯU ẢNH ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_FOLDER = os.path.join(BASE_DIR, "images_cum_thu")
if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)

COLUMNS = ["NGÀY LẮP", "TÊN XÃ", "TÊN CỤM THU (THÔN)", "SỐ LƯỢNG CỤM", 
           "TỌA ĐỘ GPS", "SERIAL SIM", "SỐ LOA", "GHI CHÚ", "ĐƯỜNG DẪN ẢNH"]

st.title("📻 PHẦN MỀM QUẢN LÝ CỤM THU TRUYỀN THANH")

# --- Form nhập liệu ---
st.header("Nhập thông tin cụm thu")

date = st.text_input("Ngày lắp đặt", datetime.now().strftime("%d/%m/%Y"))
ten_xa = st.text_input("Tên Xã (Tiêu đề file)")
ten_cum = st.text_input("Tên Cụm thu (Thôn)")
so_luong = st.number_input("Số lượng cụm", min_value=0)
gps = st.text_input("Tọa độ GPS")
sim = st.text_input("Serial Sim")
loa = st.number_input("Số loa trên cụm", min_value=0)
ghi_chu = st.text_area("Ghi chú")

uploaded_file = st.file_uploader("📸 Chọn ảnh vị trí", type=["jpg","png","jpeg"])

if st.button("💾 Lưu dữ liệu"):
    if not ten_xa or not ten_cum or not uploaded_file:
        st.error("Vui lòng nhập Tên Xã, Cụm và chọn ảnh!")
    else:
        # Lưu ảnh
        img_name = f"{ten_xa}_{ten_cum.replace(' ', '_')}_{sim}.jpg"
        img_dest = os.path.join(IMAGE_FOLDER, img_name)
        Image.open(uploaded_file).convert("RGB").save(img_dest)

        # Thu thập dữ liệu
        data = [
            date, ten_xa.upper(), ten_cum.upper(), so_luong, gps, sim, loa, ghi_chu, img_dest
        ]

        excel_file = os.path.join(BASE_DIR, f"{ten_xa}.xlsx")
        df_old = pd.read_excel(excel_file) if os.path.exists(excel_file) else pd.DataFrame(columns=COLUMNS)
        df_new = pd.concat([df_old, pd.DataFrame([data], columns=COLUMNS)], ignore_index=True)

        df_new.to_excel(excel_file, index=False)

        st.success(f"✅ Đã lưu cụm {ten_cum} vào file {ten_xa}.xlsx")

        st.subheader("📊 Dữ liệu hiện tại")
        st.dataframe(df_new)

        # Cho phép tải file Excel về
        with open(excel_file, "rb") as f:
            st.download_button("⬇️ Tải file Excel", f, file_name=f"{ten_xa}.xlsx")
