import tkinter as tk
from tkinter import ttk, messagebox

from database import Database
from models.student import Student
from models.room import Room
from models.payment import Payment
from models.allocation import RoomAllocation


class HMSApp:
    def __init__(self, root):
        self.root = root
        self.db = Database()

        self.student_model = Student(self.db)
        self.room_model = Room(self.db)
        self.payment_model = Payment(self.db)
        self.allocation_model = RoomAllocation(self.db)

        self.root.title("Hostel Management System")
        self.root.geometry("760x450")

        tk.Label(
            root,
            text="HOSTEL MANAGEMENT SYSTEM",
            font=("Arial", 18, "bold")
        ).pack(pady=20)

        tk.Button(root, text="Manage Students", width=25, command=self.student_window).pack(pady=6)
        tk.Button(root, text="Manage Rooms", width=25, command=self.room_window).pack(pady=6)
        tk.Button(root, text="Make Payment & Allocate Room", width=30, command=self.payment_window).pack(pady=6)

        self.allocation_model.process_expired_allocations()

    # ================= STUDENT WINDOW =================
    def student_window(self):
        win = tk.Toplevel(self.root)
        win.title("Manage Students")
        win.geometry("900x520")

        form = ttk.LabelFrame(win, text="Register Student")
        form.pack(fill="x", padx=10, pady=10)

        tk.Label(form, text="Name").grid(row=0, column=0, padx=6, pady=6, sticky="w")
        name = tk.Entry(form, width=32)
        name.grid(row=0, column=1, padx=6, pady=6)

        tk.Label(form, text="Phone").grid(row=1, column=0, padx=6, pady=6, sticky="w")
        phone = tk.Entry(form, width=32)
        phone.grid(row=1, column=1, padx=6, pady=6)

        tk.Label(form, text="Registration No").grid(row=2, column=0, padx=6, pady=6, sticky="w")
        reg = tk.Entry(form, width=32)
        reg.grid(row=2, column=1, padx=6, pady=6)

        tk.Label(form, text="Gender").grid(row=3, column=0, padx=6, pady=6, sticky="w")
        gender = ttk.Combobox(form, values=["M", "F"], state="readonly", width=29)
        gender.grid(row=3, column=1, padx=6, pady=6)
        gender.current(0)

        tree = ttk.Treeview(win, columns=(1, 2, 3, 4, 5), show="headings")
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        for col, text in zip((1, 2, 3, 4, 5), ("Student ID", "Name", "Phone", "RegNo", "Gender")):
            tree.heading(col, text=text)

        def refresh_students():
            for r in tree.get_children():
                tree.delete(r)
            for row in self.student_model.get_all():
                tree.insert("", "end", values=row)

        def save_student():
            if name.get().strip() == "" or reg.get().strip() == "":
                messagebox.showerror("Error", "Name and Registration No are required")
                return

            ok = self.student_model.register(
                name.get().strip(),
                phone.get().strip(),
                reg.get().strip(),
                gender.get().strip()
            )

            if ok:
                messagebox.showinfo("Success", "Student registered successfully")
                name.delete(0, tk.END)
                phone.delete(0, tk.END)
                reg.delete(0, tk.END)
                gender.current(0)
                refresh_students()
            else:
                messagebox.showerror("Error", "Registration failed. Registration number may already exist.")

        tk.Button(form, text="Save Student", command=save_student).grid(row=4, column=0, columnspan=2, pady=10)
        refresh_students()

    # ================= ROOM WINDOW =================
    def room_window(self):
        win = tk.Toplevel(self.root)
        win.title("Manage Rooms")
        win.geometry("1000x650")
        win.minsize(980, 620)

        top = ttk.Frame(win)
        top.pack(fill="x", padx=10, pady=8)

        tk.Label(top, text="Hostel Type:").pack(side="left")
        hostel_filter = ttk.Combobox(top, values=["Male", "Female"], state="readonly", width=12)
        hostel_filter.pack(side="left", padx=6)
        hostel_filter.current(0)

        totals_lbl = tk.Label(top, text="", font=("Arial", 10, "bold"))
        totals_lbl.pack(side="right")

        notebook = ttk.Notebook(win)
        notebook.pack(fill="both", expand=True, padx=10, pady=8)

        tab_rooms = ttk.Frame(notebook)
        tab_students = ttk.Frame(notebook)
        tab_add = ttk.Frame(notebook)

        notebook.add(tab_rooms, text="Rooms")
        notebook.add(tab_students, text="Room Students")
        notebook.add(tab_add, text="Add Room")

        rooms_container = ttk.Frame(tab_rooms)
        rooms_container.pack(fill="both", expand=True, padx=6, pady=6)

        rooms_tree = ttk.Treeview(
            rooms_container,
            columns=("roomId", "roomNumber", "capacity", "occupied", "status"),
            show="headings",
            height=16
        )
        vsb = ttk.Scrollbar(rooms_container, orient="vertical", command=rooms_tree.yview)
        rooms_tree.configure(yscrollcommand=vsb.set)

        for col, text, width in [
            ("roomId", "Room ID", 80),
            ("roomNumber", "Room Number", 140),
            ("capacity", "Capacity", 120),
            ("occupied", "Occupied", 120),
            ("status", "Status", 140),
        ]:
            rooms_tree.heading(col, text=text)
            rooms_tree.column(col, width=width, anchor="center")

        rooms_tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        info_lbl = tk.Label(tab_students, text="Select a room in Rooms tab to view students here.")
        info_lbl.pack(anchor="w", padx=6, pady=6)

        stud_container = ttk.Frame(tab_students)
        stud_container.pack(fill="both", expand=True, padx=6, pady=6)

        occ_tree = ttk.Treeview(
            stud_container,
            columns=("studentId", "name", "regNo", "period", "amount", "endDate", "daysLeft"),
            show="headings",
            height=14
        )
        occ_vsb = ttk.Scrollbar(stud_container, orient="vertical", command=occ_tree.yview)
        occ_tree.configure(yscrollcommand=occ_vsb.set)

        for c, t, w, a in [
            ("studentId", "Student ID", 90, "center"),
            ("name", "Name", 220, "w"),
            ("regNo", "Reg No", 140, "center"),
            ("period", "Period", 110, "center"),
            ("amount", "Amount", 110, "center"),
            ("endDate", "Expires", 160, "center"),
            ("daysLeft", "Days Left", 100, "center"),
        ]:
            occ_tree.heading(c, text=t)
            occ_tree.column(c, width=w, anchor=a)

        occ_tree.pack(side="left", fill="both", expand=True)
        occ_vsb.pack(side="right", fill="y")

        def clear_rooms():
            for r in rooms_tree.get_children():
                rooms_tree.delete(r)

        def clear_students():
            for r in occ_tree.get_children():
                occ_tree.delete(r)

        def update_totals():
            sem_total, year_total = self.payment_model.get_totals_by_hostel(hostel_filter.get().strip())
            totals_lbl.config(text=f"Totals: Semester {int(sem_total)} | Year {int(year_total)}")

        def load_rooms():
            clear_rooms()
            clear_students()
            rooms = self.room_model.get_by_hostel_type(hostel_filter.get().strip())
            for row in rooms:
                rooms_tree.insert("", "end", values=row)
            update_totals()

        def load_room_students(room_id):
            clear_students()
            students = self.allocation_model.get_students_in_room(room_id)
            for row in students:
                occ_tree.insert("", "end", values=row)

        def on_room_select(_=None):
            selected = rooms_tree.selection()
            if not selected:
                return
            room_id = rooms_tree.item(selected[0])["values"][0]
            load_room_students(room_id)
            notebook.select(tab_students)

        rooms_tree.bind("<<TreeviewSelect>>", on_room_select)

        def process_expired_and_refresh():
            success, count = self.allocation_model.process_expired_allocations()
            if success:
                messagebox.showinfo("Expired Allocations", f"Processed {count} expired allocation(s).")
                load_rooms()
            else:
                messagebox.showerror("Error", "Failed to process expired allocations.")

        ttk.Button(top, text="Process Expired Allocations", command=process_expired_and_refresh).pack(side="right", padx=10)

        def deallocate_student():
            selected_room = rooms_tree.selection()
            selected_student = occ_tree.selection()

            if not selected_room:
                messagebox.showerror("Error", "Select a room first.")
                return

            if not selected_student:
                messagebox.showerror("Error", "Select a student first.")
                return

            room_id = rooms_tree.item(selected_room[0])["values"][0]
            student_id = occ_tree.item(selected_student[0])["values"][0]

            ok, msg = self.allocation_model.deallocate_student(student_id, room_id)
            if ok:
                messagebox.showinfo("Success", msg)
                load_rooms()
                load_room_students(room_id)
            else:
                messagebox.showerror("Error", msg)

        ttk.Button(tab_students, text="Deallocate Selected Student", command=deallocate_student).pack(pady=10, padx=6, anchor="w")

        addf = ttk.LabelFrame(tab_add, text="Add New Room")
        addf.pack(fill="x", padx=10, pady=14)

        tk.Label(addf, text="Room Number").grid(row=0, column=0, padx=6, pady=6, sticky="w")
        new_room = tk.Entry(addf, width=22)
        new_room.grid(row=0, column=1, padx=6, pady=6)

        tk.Label(addf, text="Capacity").grid(row=0, column=2, padx=6, pady=6, sticky="w")
        new_cap = tk.Entry(addf, width=22)
        new_cap.grid(row=0, column=3, padx=6, pady=6)

        tk.Label(addf, text="Hostel Type").grid(row=1, column=0, padx=6, pady=6, sticky="w")
        new_type = ttk.Combobox(addf, values=["Male", "Female"], state="readonly", width=19)
        new_type.grid(row=1, column=1, padx=6, pady=6)
        new_type.current(0)

        def add_room():
            rn = new_room.get().strip()
            cap = new_cap.get().strip()
            ht = new_type.get().strip()

            if rn == "" or cap == "":
                messagebox.showerror("Error", "Room Number and Capacity are required")
                return

            try:
                rn = int(rn)
                cap = int(cap)
                if rn <= 0 or cap <= 0:
                    messagebox.showerror("Error", "Values must be positive")
                    return
            except ValueError:
                messagebox.showerror("Error", "Room Number and Capacity must be integers")
                return

            if self.room_model.room_exists(rn, ht):
                messagebox.showerror("Error", f"Room {rn} already exists in {ht} hostel")
                return

            ok = self.room_model.add_room(rn, cap, ht)
            if ok:
                messagebox.showinfo("Success", "Room added successfully")
                new_room.delete(0, tk.END)
                new_cap.delete(0, tk.END)
                new_type.current(0)
                hostel_filter.set(ht)
                load_rooms()
                notebook.select(tab_rooms)
            else:
                messagebox.showerror("Error", "Failed to add room")

        ttk.Button(addf, text="Add Room", command=add_room).grid(row=2, column=0, columnspan=4, pady=12)

        hostel_filter.bind("<<ComboboxSelected>>", lambda e: load_rooms())
        load_rooms()

    # ================= PAYMENT WINDOW =================
    def payment_window(self):
        win = tk.Toplevel(self.root)
        win.title("Payment & Allocation")
        win.geometry("620x520")

        frm = ttk.LabelFrame(win, text="Payment & Allocation")
        frm.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Label(frm, text="Registration Number").grid(row=0, column=0, padx=6, pady=8, sticky="w")
        reg_entry = tk.Entry(frm, width=30)
        reg_entry.grid(row=0, column=1, padx=6, pady=8)

        student_id_var = tk.StringVar(value="")

        found_lbl = tk.Label(frm, text="Student: (not selected)", font=("Arial", 10, "bold"))
        found_lbl.grid(row=1, column=0, columnspan=2, padx=6, pady=6, sticky="w")

        tk.Label(frm, text="Period").grid(row=2, column=0, padx=6, pady=8, sticky="w")
        period_box = ttk.Combobox(frm, values=["Semester", "Year"], state="readonly", width=27)
        period_box.grid(row=2, column=1, padx=6, pady=8)
        period_box.current(0)

        tk.Label(frm, text="Payment Method").grid(row=3, column=0, padx=6, pady=8, sticky="w")
        method_box = ttk.Combobox(frm, values=["Cash", "Bank", "Mobile Money"], state="readonly", width=27)
        method_box.grid(row=3, column=1, padx=6, pady=8)
        method_box.current(0)

        tk.Label(frm, text="Select Room").grid(row=4, column=0, padx=6, pady=8, sticky="w")
        room_box = ttk.Combobox(frm, values=[], state="readonly", width=27)
        room_box.grid(row=4, column=1, padx=6, pady=8)

        price_lbl = tk.Label(frm, text="", font=("Arial", 11, "bold"))
        price_lbl.grid(row=5, column=0, columnspan=2, pady=8)

        info_lbl = tk.Label(frm, text="", font=("Arial", 10))
        info_lbl.grid(row=6, column=0, columnspan=2, pady=6)

        expiry_lbl = tk.Label(frm, text="", font=("Arial", 10, "bold"))
        expiry_lbl.grid(row=7, column=0, columnspan=2, pady=6)

        room_map = {}

        def update_price_and_expiry(*_):
            if period_box.get() == "Semester":
                price_lbl.config(text="Price (Semester) = 120000")
                expiry_lbl.config(text="Duration: 6 months")
            else:
                price_lbl.config(text="Price (Year) = 140000")
                expiry_lbl.config(text="Duration: 12 months")

        def load_rooms_for_student(student_name, gender):
            hostel_type = "Male" if gender == "M" else "Female"
            info_lbl.config(text=f"Student: {student_name} | Gender: {gender} | Hostel: {hostel_type}")

            rooms = self.room_model.get_available_rooms(hostel_type)
            room_map.clear()

            labels = []
            for room_id, room_number, capacity, occupied, status in rooms:
                label = f"{room_number} (ID:{room_id})"
                labels.append(label)
                room_map[label] = room_id

            room_box["values"] = labels
            if labels:
                room_box.current(0)
            else:
                room_box.set("")
                messagebox.showwarning("No Rooms", f"No available {hostel_type} rooms")

        def search_student():
            reg_no = reg_entry.get().strip()
            if reg_no == "":
                messagebox.showerror("Error", "Enter registration number first")
                return

            student = self.student_model.find_by_regno(reg_no)
            if not student:
                student_id_var.set("")
                found_lbl.config(text="Student: (not found)")
                room_box["values"] = []
                room_box.set("")
                room_map.clear()
                info_lbl.config(text="")
                messagebox.showerror("Error", "Student not found")
                return

            student_id, name, gender, regno = student
            student_id_var.set(str(student_id))
            found_lbl.config(text=f"Student: {name} (ID: {student_id}) | RegNo: {regno}")
            load_rooms_for_student(name, gender)

        def submit_payment_allocate():
            student_id = student_id_var.get().strip()
            room_label = room_box.get().strip()
            period = period_box.get().strip()
            method = method_box.get().strip()

            if student_id == "":
                messagebox.showerror("Error", "Search student first")
                return

            if room_label == "" or period == "" or method == "":
                messagebox.showerror("Error", "Complete all fields")
                return

            if room_label not in room_map:
                messagebox.showerror("Error", "Invalid room selected")
                return

            room_id = room_map[room_label]
            ok, msg = self.payment_model.pay_and_allocate(int(student_id), room_id, period, method)

            if ok:
                messagebox.showinfo("Success", msg)
                room_box.set("")
                room_map.clear()
            else:
                messagebox.showerror("Error", msg)

        ttk.Button(frm, text="Search Student", command=search_student).grid(row=0, column=2, padx=10, pady=8)
        ttk.Button(win, text="Submit Payment & Allocate", command=submit_payment_allocate).pack(pady=10)

        period_box.bind("<<ComboboxSelected>>", update_price_and_expiry)
        update_price_and_expiry()


if __name__ == "__main__":
    root = tk.Tk()
    app = HMSApp(root)
    root.mainloop()
