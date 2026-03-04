import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from datetime import datetime
from PIL import Image

# --- CẤU HÌNH ĐƯỜNG DẪN TUYỆT ĐỐI (QUAN TRỌNG ĐỂ CHẠY .EXE) ---
if getattr(sys, 'frozen', False):
    # Nếu đang chạy từ file .exe
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Nếu đang chạy từ file .py
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

IMAGE_FOLDER = os.path.join(BASE_DIR, "images_cum_thu")
if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)

COLUMNS = ["NGÀY LẮP", "TÊN XÃ", "TÊN CỤM THU (THÔN)", "SỐ LƯỢNG CỤM", "TỌA ĐỘ GPS", "SERIAL SIM", "SỐ LOA", "GHI CHÚ", "ĐƯỜNG DẪN ẢNH"]

class RadioManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PHẦN MỀM QUẢN LÝ CỤM THU TRUYỀN THANH")
        self.root.geometry("1100x700")
        self.file_path = ""

        # Giao diện nhập liệu
        left_pnl = tk.LabelFrame(root, text=" THÔNG TIN CHI TIẾT ", padx=10, pady=10, fg="#1e3799", font=('Arial', 10, 'bold'))
        left_pnl.pack(side="left", fill="y", padx=10, pady=10)

        self.vars = {}
        fields = [
            ("Ngày lắp đặt:", "date"),
            ("Tên Xã (Tiêu đề file):", "xa"),
            ("Tên Cụm thu (Thôn):", "cum"),
            ("Số lượng cụm:", "sl"),
            ("Tọa độ GPS:", "gps"),
            ("Serial Sim:", "sim"),
            ("Số loa trên cụm:", "loa")
        ]

        for label, key in fields:
            tk.Label(left_pnl, text=label).pack(anchor="w")
            ent = tk.Entry(left_pnl, width=35)
            if key == "date": ent.insert(0, datetime.now().strftime("%d/%m/%Y"))
            ent.pack(pady=(0, 8))
            self.vars[key] = ent

        tk.Label(left_pnl, text="Ghi chú:").pack(anchor="w")
        self.txt_note = tk.Text(left_pnl, width=26, height=4)
        self.txt_note.pack(pady=(0, 8))

        tk.Button(left_pnl, text="📸 CHỌN ẢNH VỊ TRÍ", bg="#3498db", fg="white", command=self.select_image).pack(fill="x", pady=5)
        self.lbl_path = tk.Label(left_pnl, text="Chưa có ảnh", fg="gray", font=('Arial', 8))
        self.lbl_path.pack()

        tk.Button(left_pnl, text="💾 LƯU DỮ LIỆU", bg="#27ae60", fg="white", font=('Arial', 11, 'bold'), command=self.save_data).pack(fill="x", pady=20)

        # Giao diện hiển thị
        right_pnl = tk.LabelFrame(root, text=" DANH SÁCH DỮ LIỆU ", padx=10, pady=10, font=('Arial', 10, 'bold'))
        right_pnl.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        tk.Button(right_pnl, text="📂 Xem dữ liệu Xã khác", command=self.load_xa).pack(pady=5)
        
        self.tree = ttk.Treeview(right_pnl, columns=tuple(range(len(COLUMNS)-1)), show='headings')
        for i, col in enumerate(COLUMNS[:-1]):
            self.tree.heading(i, text=col)
            self.tree.column(i, width=80, anchor="center")
        self.tree.pack(fill="both", expand=True)

    def select_image(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.png *.jpeg")])
        if path:
            self.file_path = path
            self.lbl_path.config(text=os.path.basename(path), fg="black")

    def save_data(self):
        try:
            ten_xa = self.vars['xa'].get().strip()
            ten_cum = self.vars['cum'].get().strip()
            
            if not ten_xa or not ten_cum or not self.file_path:
                messagebox.showerror("Lỗi", "Vui lòng nhập Tên Xã, Cụm và Chọn ảnh!")
                return

            excel_file = os.path.join(BASE_DIR, f"{ten_xa}.xlsx")
            
            # Thu thập data
            data = [
                self.vars['date'].get(), ten_xa.upper(), ten_cum.upper(),
                self.vars['sl'].get(), self.vars['gps'].get(), self.vars['sim'].get(),
                self.vars['loa'].get(), self.txt_note.get("1.0", tk.END).strip(), ""
            ]

            # Lưu ảnh
            img_name = f"{ten_xa}_{ten_cum.replace(' ', '_')}_{data[5]}.jpg"
            img_dest = os.path.join(IMAGE_FOLDER, img_name)
            Image.open(self.file_path).convert("RGB").save(img_dest)
            data[-1] = img_dest

            # Lưu Excel
            df_old = pd.read_excel(excel_file) if os.path.exists(excel_file) else pd.DataFrame(columns=COLUMNS)
            df_new = pd.concat([df_old, pd.DataFrame([data], columns=COLUMNS)], ignore_index=True)

            with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
                df_new.to_excel(writer, index=False, sheet_name='Sheet1')
                workbook = writer.book
                worksheet = writer.sheets['Sheet1']
                fmt_hdr = workbook.add_format({'bold':True, 'border':1, 'align':'center', 'bg_color':'#C6E0B4'})
                fmt_cell = workbook.add_format({'border':1, 'align':'center'})

                for col_num, value in enumerate(df_new.columns.values):
                    worksheet.write(0, col_num, value, fmt_hdr)
                    worksheet.set_column(col_num, col_num, 20)
                for r_idx, row in enumerate(df_new.values):
                    for c_idx, val in enumerate(row):
                        worksheet.write(r_idx+1, c_idx, val, fmt_cell)

            messagebox.showinfo("Thành công", f"Đã lưu cụm {ten_cum} vào file {ten_xa}.xlsx")
            self.refresh_table(excel_file)
            
        except PermissionError:
            messagebox.showerror("Lỗi", "Vui lòng đóng file Excel trước khi lưu!")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def load_xa(self):
        f = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx")])
        if f: self.refresh_table(f)

    def refresh_table(self, file):
        for i in self.tree.get_children(): self.tree.delete(i)
        df = pd.read_excel(file)
        for r in df.values: self.tree.insert("", "end", values=list(r)[:-1])

if __name__ == "__main__":
    print("🚀 App đang chạy...")
    root = tk.Tk()
    app = RadioManagerApp(root)
    root.mainloop()