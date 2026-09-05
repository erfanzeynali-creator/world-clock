import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import pytz
import threading
import time

class ReminderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🌐 ساعت جهانی هوشمند + یادآور")
        self.root.geometry("700x600")
        self.root.configure(bg="#1e1e1e")

        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TLabel", background="#1e1e1e", foreground="white", font=("Vazirmatn", 11))
        self.style.configure("TButton", background="#007acc", foreground="white", font=("Vazirmatn", 11, "bold"))
        self.style.map("TButton", background=[('active', '#005f99')])
        self.style.configure("TCombobox", fieldbackground="#2d2d30", background="#2d2d30", foreground="white", font=("Vazirmatn", 10))
        self.style.configure("TRadiobutton", background="#1e1e1e", foreground="white", font=("Vazirmatn", 10))
        self.style.configure("TLabelframe", background="#2d2d30", foreground="white", font=("Vazirmatn", 12, "bold"))
        self.style.configure("TLabelframe.Label", background="#2d2d30", foreground="white")

        self.running_reminders = []
        self.create_widgets()
        self.update_clocks()

    def create_widgets(self):
        header = ttk.Label(self.root, text="🕰️ ساعت جهانی و تنظیم یادآور پیشرفته", font=("Vazirmatn", 14, "bold"), background="#1e1e1e", foreground="white")
        header.pack(pady=10)

        frame1 = ttk.LabelFrame(self.root, text="🌍 ساعت جهانی")
        frame1.pack(padx=20, pady=5, fill="x")

        self.clock_zone = tk.StringVar()
        self.clock_combo = ttk.Combobox(frame1, values=pytz.all_timezones, textvariable=self.clock_zone)
        self.clock_combo.set("Asia/Tehran")
        self.clock_combo.pack(pady=5, padx=10)

        self.clock_label = ttk.Label(frame1, text="", font=("Courier", 13, "bold"))
        self.clock_label.pack(pady=5, padx=10)

        frame2 = ttk.LabelFrame(self.root, text="⏰ تنظیم یادآور")
        frame2.pack(padx=20, pady=5, fill="x")

        self.reminder_type = tk.StringVar(value="local")
        radio_frame = tk.Frame(frame2, bg="#2d2d30")
        radio_frame.pack(anchor="w", padx=10)
        ttk.Radiobutton(radio_frame, text="بر اساس کشور من", variable=self.reminder_type, value="local").pack(side="left")
        ttk.Radiobutton(radio_frame, text="بر اساس کشور دیگر", variable=self.reminder_type, value="world").pack(side="left")

        ttk.Label(frame2, text="کشور مقصد (اگر یادآور جهانی است):").pack(pady=2, anchor="w", padx=10)
        self.selected_country = tk.StringVar()
        self.country_combo = ttk.Combobox(frame2, values=pytz.all_timezones, textvariable=self.selected_country)
        self.country_combo.set("Asia/Tehran")
        self.country_combo.pack(pady=2, padx=10, fill="x")

        ttk.Label(frame2, text="کشور من:").pack(pady=2, anchor="w", padx=10)
        self.local_country = tk.StringVar()
        self.local_country_combo = ttk.Combobox(frame2, values=pytz.all_timezones, textvariable=self.local_country)
        self.local_country_combo.set("Asia/Tehran")
        self.local_country_combo.pack(pady=2, padx=10, fill="x")

        ttk.Label(frame2, text="تاریخ یادآور (yyyy-mm-dd):").pack(pady=2, anchor="w", padx=10)
        self.date_entry = ttk.Entry(frame2)
        self.date_entry.insert(0, datetime.now(pytz.utc).astimezone().strftime('%Y-%m-%d'))
        self.date_entry.pack(pady=2, padx=10, fill="x")

        ttk.Label(frame2, text="ساعت یادآور (hh:mm):").pack(pady=2, anchor="w", padx=10)
        self.time_entry = ttk.Entry(frame2)
        self.time_entry.pack(pady=2, padx=10, fill="x")

        ttk.Label(frame2, text="متن یادآور:").pack(pady=2, anchor="w", padx=10)
        self.msg_entry = ttk.Entry(frame2)
        self.msg_entry.pack(pady=2, padx=10, fill="x")

        btn_frame = tk.Frame(frame2, bg="#2d2d30")
        btn_frame.pack(pady=10, padx=10, fill="x")

        ttk.Button(btn_frame, text="تنظیم یادآور", command=self.set_reminder).pack(side="left", expand=True, fill="x", padx=(0, 5))
        ttk.Button(btn_frame, text="❌ حذف یادآور", command=self.delete_selected_reminder).pack(side="left", expand=True, fill="x", padx=(5, 0))

        frame3 = ttk.LabelFrame(self.root, text="📋 لیست یادآورها")
        frame3.pack(padx=20, pady=5, fill="both", expand=True)

        self.reminders_list = tk.Listbox(frame3, width=80, font=("Courier", 10), bg="#e0e0e0")
        self.reminders_list.pack(padx=10, pady=10, fill="both", expand=True)

        threading.Thread(target=self.check_reminders, daemon=True).start()

    def set_reminder(self):
        date_str = self.date_entry.get()
        time_str = self.time_entry.get()
        msg = self.msg_entry.get()
        reminder_type = self.reminder_type.get()

        if not date_str or not time_str or not msg:
            messagebox.showerror("خطا", "لطفاً تمام فیلدها را پر کنید.")
            return

        try:
            reminder_date = datetime.strptime(date_str, "%Y-%m-%d")
            hour, minute = map(int, time_str.split(":"))
            full_datetime = datetime(reminder_date.year, reminder_date.month, reminder_date.day, hour, minute)
        except:
            messagebox.showerror("خطا", "تاریخ یا زمان را به‌صورت صحیح وارد کنید (مثلاً 2025-06-29 و 14:30)")
            return

        try:
            user_timezone = pytz.timezone(self.local_country.get())
        except:
            messagebox.showerror("خطا", "لطفاً کشور خود را انتخاب کنید")
            return

        if reminder_type == "world":
            try:
                dest_timezone = pytz.timezone(self.selected_country.get())
                reminder_time = dest_timezone.localize(full_datetime)
                local_time = reminder_time.astimezone(user_timezone)
            except:
                messagebox.showerror("خطا", "مشکل در انتخاب منطقه زمانی")
                return
        else:
            local_time = user_timezone.localize(full_datetime)

        if local_time < datetime.now(pytz.utc).astimezone(user_timezone):
            messagebox.showerror("خطا", "زمان یادآور در گذشته است!")
            return

        self.running_reminders.append((local_time.astimezone(pytz.utc), msg, user_timezone))
        self.reminders_list.insert(tk.END, f"✅ {local_time.strftime('%Y-%m-%d %H:%M')} ({self.local_country.get()}) | {msg}")
        messagebox.showinfo("موفق", "یادآور با موفقیت تنظیم شد!")

    def delete_selected_reminder(self):
        selection = self.reminders_list.curselection()
        if not selection:
            messagebox.showwarning("هشدار", "هیچ یادآوری انتخاب نشده است!")
            return
        index = selection[0]
        self.reminders_list.delete(index)
        del self.running_reminders[index]

    def check_reminders(self):
        while True:
            now_utc = datetime.utcnow().replace(second=0, microsecond=0).replace(tzinfo=pytz.utc)
            for rem in self.running_reminders[:]:
                rem_time, msg, tz = rem
                if now_utc >= rem_time.replace(second=0, microsecond=0):
                    messagebox.showinfo("🔔 یادآور!", msg)
                    self.running_reminders.remove(rem)
            time.sleep(30)

    def update_clocks(self):
        try:
            tz = pytz.timezone(self.clock_zone.get())
            now = datetime.now(pytz.utc).astimezone(tz)
            self.clock_label.config(text=f"🕒 ساعت فعلی در {self.clock_zone.get()} : {now.strftime('%H:%M:%S')}")
        except:
            self.clock_label.config(text="")

        self.root.after(1000, self.update_clocks)

if __name__ == "__main__":
    root = tk.Tk()
    app = ReminderApp(root)
    root.mainloop()
    