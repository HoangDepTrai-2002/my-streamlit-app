import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image
import os
import folium
from streamlit_folium import st_folium

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
gps_link = st.text_input("📍 Link Google Maps (dán link vào đây)")
sim = st.text_input("Serial Sim")
loa = st.number_input("Số loa trên cụm", min_value=0)
ghi_chu = st.text_area("Ghi chú")

uploaded_file = st.file_uploader("📸 Chọn ảnh vị trí", type=["jpg","png","jpeg"])

# --- Xử lý tọa độ từ link Google Maps ---
lat, lon = None, None
if gps_link:
    try:
        if "q=" in gps_link:
            coords = gps_link.split("q=")[1].split("&")[0]
            lat, lon = map(float, coords.split(","))
        elif "/@" in gps_link:
            coords = gps_link.split("/@")[1].split(",")[:2]
            lat, lon = map(float, coords)
    except:
        st.warning("⚠️ Không đọc được tọa độ từ link Google Maps")

# --- Nút lưu dữ liệu ---
if st.button("💾 Lưu dữ liệu"):
    if not ten_xa or not ten_cum or not uploaded_file:
        st.error("Vui lòng nhập Tên Xã, Cụm và chọn ảnh!")
    else:
        # Lưu ảnh
        img_name = f"{ten_xa}_{ten_cum.replace(' ', '_')}_{sim}.jpg"
        img_dest = os.path.join(IMAGE_FOLDER, img_name)
        Image.open(uploaded_file).convert("RGB").save(img_dest)

        # Thu thập dữ liệu
        gps_text = f"{lat},{lon}" if lat and lon else gps_link
        data = [
            date, ten_xa.upper(), ten_cum.upper(), so_luong,
            gps_text, sim, loa, ghi_chu, img_dest
        ]

        excel_file = os.path.join(BASE_DIR, f"{ten_xa}.xlsx")
        df_old = pd.read_excel(excel_file) if os.path.exists(excel_file) else pd.DataFrame(columns=COLUMNS)
        df_new = pd.concat([df_old, pd.DataFrame([data], columns=COLUMNS)], ignore_index=True)

        df_new.to_excel(excel_file, index=False)

        st.success(f"✅ Đã lưu cụm {ten_cum} vào file {ten_xa}.xlsx")

        # Hiển thị dữ liệu
        st.subheader("📊 Dữ liệu hiện tại")
        st.dataframe(df_new)

        # Hiển thị ảnh vừa lưu
        st.subheader("📸 Ảnh đã lưu")
        st.image(img_dest, caption=f"Ảnh của {ten_cum}", use_column_width=True)

        # Nút tải ảnh
        with open(img_dest, "rb") as f:
            st.download_button("⬇️ Tải ảnh về máy", f, file_name=os.path.basename(img_dest), mime="image/jpeg")

        # Nút tải Excel
        with open(excel_file, "rb") as f:
            st.download_button("⬇️ Tải file Excel", f, file_name=f"{ten_xa}.xlsx")

        # Hiển thị bản đồ nếu có tọa độ
        if lat and lon:
            st.subheader("🗺️ Vị trí trên bản đồ")
            m = folium.Map(location=[lat, lon], zoom_start=15)
            folium.Marker([lat, lon], popup=ten_cum).add_to(m)
            st_folium(m, width=700, height=500)
