import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser, simpledialog
import json
import os
from tkinter import ttk, font
from datetime import datetime
import requests
from bs4 import BeautifulSoup


SETTINGS_FILE = "settings.json"
DEFAULT_FILE = "note.json"
default_settings = {
    "font_family": "Arial",
    "font_size": 12,
    "bg_color": "#FFFFFF",
    "fg_color": "#000000"
}

settings = None
current_note_index = None
list_window = None
note_listbox = None
notes_data = []
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
    global current_note_index
    current_note_index = None
    text_area.delete(1.0, tk.END)
    title_entry.delete(0, tk.END)
    date_create_entry.config(state="normal")
    date_create_entry.delete(0, tk.END)
    date_create_entry.config(state="readonly")
    root.title("Note - New Note")

def save_current_note():
    global current_note_index, notes_data, note_listbox
    title = title_entry.get().strip()
    content = text_area.get("1.0", tk.END).strip()
    created = date_create_entry.get()
    updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not title or not content:
        messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập cả tiêu đề và nội dung.")
        return
    file_path = DEFAULT_FILE
    
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                notes_data = json.load(f)
                if not isinstance(notes_data, list):
                    notes_data = [notes_data] if notes_data else []
                if current_note_index is None:
                    for note in notes_data:
                        if note.get("Title", "").lower() == title.lower():
                            messagebox.showwarning("Trùng tiêu đề", "Tiêu đề này đã tồn tại!!!!!!")
                            return
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể kiểm tra ghi chú: {e}")
            return
    
    if not created:
        created = updated
        date_create_entry.config(state="normal")
        date_create_entry.insert(0, created)
        date_create_entry.config(state="readonly")

    note = {
        "Title": title,
        "Content": content,
        "Created": created,
        "Updated": updated
    }

    file_path = DEFAULT_FILE
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump([], f)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            notes_data = json.load(f)
            if not isinstance(notes_data, list):
                notes_data = [notes_data] if notes_data else []

        if current_note_index is not None:
            notes_data[current_note_index] = note
        else:
            notes_data.append(note)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(notes_data, f, indent=4, ensure_ascii=False)

        if list_window and note_listbox:
            notes_data.sort(key=lambda x: x.get("Updated", ""), reverse=True)
            note_listbox.delete(0, tk.END)
            for note in notes_data:
                updated = note.get("Updated", "Unknown")
                title = note.get("Title", "Không tiêu đề")
                note_listbox.insert(tk.END, f"{updated} - {title}")

        messagebox.showinfo("Thành công", "Ghi chú đã được lưu.")
        root.title(f"Note - Updated: {updated}")
        current_note_index = None 
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể lưu ghi chú: {e}")
def del_current_note(selected_index):
    global notes_data, note_listbox
    if selected_index[0] is None:
        messagebox.showinfo("Thông báo", "Vui lòng chọn ghi chú để xóa.")
        return
    if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa ghi chú này?"):
        try:
            notes_data.pop(selected_index[0])
            with open(DEFAULT_FILE, "w", encoding="utf-8") as f:
                json.dump(notes_data, f, indent=4, ensure_ascii=False)
            if list_window and note_listbox and list_window.winfo_exists():
                notes_data.sort(key=lambda x: x.get("Updated", ""), reverse=True)
                note_listbox.delete(0, tk.END)
                for note in notes_data:
                    updated = note.get("Updated", "Unknown")
                    title = note.get("Title", "Không tiêu đề")
                    note_listbox.insert(tk.END, f"{updated} - {title}")

            messagebox.showinfo("Thành công", "Ghi chú đã được xóa.")
            selected_index[0] = None
        except Exception as e:
            os.remove(DEFAULT_FILE)
            messagebox.showinfo("Thành công", "Ghi chú đã được xóa.")
def open_note():
    file_path = "note.json"
    if not file_path:
        return

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            notes = json.load(file)

        notes.sort(key=lambda x: x.get("Updated", ""), reverse=True)
        list_window = tk.Toplevel()
        list_window.title("Danh sách ghi chú")

        listbox = tk.Listbox(list_window, width=40, height=20)
        listbox.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        preview = tk.Text(list_window, wrap=tk.WORD, width=60, height=20)
        preview.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(list_window)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=listbox.yview)

        for note in notes:
            updated = note.get("Updated", "")
            title = note.get("Title", "Không tiêu đề")
            listbox.insert(tk.END, f"{updated} - {title}")

        selected_index = [None]

        def on_select(event):
            if listbox.curselection():
                index = listbox.curselection()[0]
                selected_index[0] = index
                note = notes[index]
                content = f"Tiêu đề: {note.get('Title', '')}\n"
                content += f"Ngày tạo: {note.get('Created', '')}\n"
                content += f"Cập nhật: {note.get('Updated', '')}\n\n"
                content += note.get("Content", "")
                preview.delete(1.0, tk.END)
                preview.insert(tk.END, content)

        listbox.bind('<<ListboxSelect>>', on_select)

        def edit_note():
            global current_note_index
            if selected_index[0] is None:
                messagebox.showinfo("Thông báo", "Vui lòng chọn ghi chú để chỉnh sửa.")
                return

            current_note_index = selected_index[0]
            note = notes[current_note_index]
            text_area.delete(1.0, tk.END)
            text_area.insert(tk.END, note.get("Content", ""))
            title_entry.delete(0, tk.END)
            title_entry.insert(0, note.get("Title", ""))
            date_create_entry.config(state="normal")
            date_create_entry.delete(0, tk.END)
            date_create_entry.insert(0, note.get("Created", ""))
            date_create_entry.config(state="readonly")
            root.title(f"Note - Updated: {note.get('Updated', '')}")
            list_window.destroy()

        tk.Button(list_window, text="Chỉnh sửa", command=edit_note).pack(side=tk.LEFT, pady=10, padx=10)
        tk.Button(list_window, text="Xóa", command=lambda: del_current_note(selected_index)).pack(side=tk.LEFT, pady=10, padx=10)

    except Exception as e:
        messagebox.showerror("Lỗi", f"Không có file ghi chú hãy tạo ghi chú mới!")
def save_note():
    file_path = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("JSON Files", "*.json")]
    )
    if not file_path:
        return
    try:
        current_time = datetime.now().strftime("%d-%m-%Y")
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        note_data = {
            "Created": data.get("Created", ""),
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
def crawl_web():
    url = simpledialog.askstring("Crawl Web", "Nhập URL để crawl:", parent=root)
    if not url:
        return
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        content = ""
        for element in soup.find_all(['p', 'h1', 'h2', 'h3']):
            text = element.get_text(strip=True)
            if text:
                content += text + "\n"
        if not content:
            messagebox.showwarning("Không có dữ liệu", "Không tìm thấy nội dung văn bản trên trang.")
            return
        new_note()
        title_entry.insert(0, soup.title.get_text(strip=True) if soup.title else "Web Content")
        text_area.insert(tk.END, content)
        root.title("Note - Crawled Web Content")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể láy dữ liệu từ trang web: {e}")
#--------------------------------------------------------------------------------------------------
# Khoi tao chuong trinh chinh
root = tk.Tk()
root.title("Note - New Note")
root.geometry("800x600")
menu_bar = tk.Menu(root)
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Ghi chú mới", command=new_note)
file_menu.add_command(label="Mở ghi chú", command=open_note)
file_menu.add_command(label="Crawl Web", command=crawl_web)
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
load_settings()
available_fonts = sorted(list(font.families()))

font_type_combobox = ttk.Combobox(top_frame, values=available_fonts, width=20)
font_type_combobox.pack(side=tk.LEFT)
font_type_combobox.set(settings.get("font_family", available_fonts[0]))

font_type_combobox.bind("<<ComboboxSelected>>", change_font_select)
text_frame = tk.Frame(root)
text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

scrollbar = tk.Scrollbar(text_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

text_area = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set)
text_area.pack(fill=tk.BOTH, expand=True)

scrollbar.config(command=text_area.yview)
save_button = tk.Button(top_frame,text="Lưu", command = save_current_note)
save_button.pack(side=tk.LEFT,padx=(5, 0))
# Luu cai dat
font_size_entry.insert(0, str(settings["font_size"]))
apply_settings()

root.mainloop()