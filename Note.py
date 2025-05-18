import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser
import json
import os
from tkinter import ttk, font
from datetime import datetime

SETTINGS_FILE = "settings.json"

default_settings = {
    "font_family": "Arial",
    "font_size": 12,
    "bg_color": "#FFFFFF",
    "fg_color": "#000000"
}

# khoi tao cai dat
settings = None
# defs
def load_settings():
    global settings
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                settings = json.load(f)
        except Exception as e:
            messagebox.showerror("Erorr", f"Không thể tải cài đặt: {e}")
            settings = default_settings
    else:
        settings = default_settings
    return settings

def save_settings():
    global settings
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        messagebox.showerror("Error", f"Không thể lưu cài đặt: {e}")

def apply_settings():
    text_area.config(
        font=(settings["font_family"], settings["font_size"]),
        bg=settings["bg_color"],
        fg=settings["fg_color"],
        insertbackground=settings["fg_color"]
    )

def new_note():
    text_area.delete(1.0, tk.END)
    title_entry.delete(0, tk.END)
    date_create_entry.config(state="normal")
    date_create_entry.delete(0, tk.END)
    date_create_entry.config(state="readonly")

def open_note():
    file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
    if not file_path:
        return
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            text_area.delete(1.0, tk.END)
            text_area.insert(tk.END, data.get("Content", ""))
            title_entry.delete(0, tk.END)
            title_entry.insert(0, data.get("Title", ""))
            date_create_entry.config(state="normal")
            date_create_entry.delete(0, tk.END)
            date_create_entry.insert(0, data.get("Created", ""))
            date_create_entry.config(state="readonly")
            root.title(f"DeathNote - Updated: {data.get('Updated', '')}")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể mở file: {e}")

def save_note():
    file_path = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("JSON Files", "*.json")]
    )
    if not file_path:
        return
    try:
        current_time = datetime.now().strftime("%d-%m-%Y")
        note_data = {
            "Created": current_time,
            "Updated": current_time,
            "Title": title_entry.get() or "Untitled",
            "Content": text_area.get(1.0, tk.END).rstrip()
        }
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(note_data, file, indent=4)
        messagebox.showinfo("Thành công", "Đã lưu ghi chú thành công!")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể lưu file: {e}")

def change_font_size():
    try:
        new_size = int(font_size_entry.get())
        if new_size <= 0:
            raise ValueError("Kích thước phông chữ phải lớn hơn 0")
        settings["font_size"] = new_size
        apply_settings()
        save_settings()
    except ValueError as e:
        messagebox.showerror("Lỗi", str(e) or "Vui lòng nhập một số hợp lệ")

def change_theme():
    bg_color = colorchooser.askcolor(title="Chọn màu nền")[1]
    fg_color = colorchooser.askcolor(title="Chọn màu chữ")[1]
    if bg_color and fg_color:
        settings["bg_color"] = bg_color
        settings["fg_color"] = fg_color
        apply_settings()
        save_settings()

def change_font_select(event):
    try:
        new_font = font_type_combobox.get()
        settings["font_family"] = new_font
        apply_settings()
        save_settings()
    except:
        messagebox.showerror("Lỗi", "Lỗi Font hãy thử lại")
#--------------------------------------------------------------------------------------------------
# Khoi tao chuong trinh chinh
root = tk.Tk()
root.title("DeathNote")
root.geometry("1280x1024")

menu_bar = tk.Menu(root)
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Ghi chú mới", command=new_note)
file_menu.add_command(label="Mở ghi chú", command=open_note)
file_menu.add_command(label="Lưu", command=save_note)
file_menu.add_separator()
file_menu.add_command(label="Thoát", command=root.quit)
menu_bar.add_cascade(label="Tệp", menu=file_menu)

settings_menu = tk.Menu(menu_bar, tearoff=0)
settings_menu.add_command(label="Đổi màu nền & chữ", command=change_theme)
menu_bar.add_cascade(label="Cài đặt", menu=settings_menu)

root.config(menu=menu_bar)

top_frame = tk.Frame(root)
top_frame.pack(pady=5, fill=tk.X)

title_label = tk.Label(top_frame, text="Tiêu đề:")
title_label.pack(side=tk.LEFT, padx=(0, 5))

title_entry = tk.Entry(top_frame, width=30)
title_entry.pack(side=tk.LEFT, padx=(0, 10))

date_create_label = tk.Label(top_frame, text="Ngày tạo:")
date_create_label.pack(side=tk.LEFT, padx=(0, 5))

date_create_entry = tk.Entry(top_frame, width=15, state="readonly")
date_create_entry.pack(side=tk.LEFT, padx=(0, 10))

font_size_label = tk.Label(top_frame, text="Cỡ chữ:")
font_size_label.pack(side=tk.LEFT, padx=(0, 5))

font_size_entry = tk.Entry(top_frame, width=5)
font_size_entry.pack(side=tk.LEFT)

font_size_button = tk.Button(top_frame, text="Đổi", command=change_font_size)
font_size_button.pack(side=tk.LEFT, padx=(5, 0))

font_type_label = tk.Label(top_frame, text="Font:")
font_type_label.pack(side=tk.LEFT,padx=(0,5))

available_fonts = sorted(list(font.families()))

font_type_combobox = ttk.Combobox(top_frame, values=available_fonts, width=20)
font_type_combobox.pack(side=tk.LEFT)
font_type_combobox.set(available_fonts[0])

font_type_combobox.bind("<<ComboboxSelected>>", change_font_select)

text_frame = tk.Frame(root)
text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

scrollbar = tk.Scrollbar(text_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

text_area = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set)
text_area.pack(fill=tk.BOTH, expand=True)

scrollbar.config(command=text_area.yview)

# Luu cai dat
load_settings()
font_size_entry.insert(0, str(settings["font_size"]))
apply_settings()

# loop
root.mainloop()