import tkinter as tk
from tkinter import ttk, messagebox

from database import Database
from models.student import Student

SEMESTER_PRICE = 120000
YEAR_PRICE = 240000


class HMSApp:
    def __init__(self, root):
        self.root = root
        self.db = Database()
        self.student = Student(self.db)

        root.title("Hostel Management System")
        root.geometry("760x450")

        tk.Label(root, text="HOSTEL MANAGEMENT SYSTEM", font=("Arial", 18, "bold")).pack(pady=20)

        tk.Button(root, text="Manage Students", width=25, command=self.student_window).pack(pady=6)
        tk.Button(root, text="Manage Rooms", width=25, command=self.room_window).pack(pady=6)
        tk.Button(root, text="Make Payment & Allocate Room", width=30, command=self.payment_window).pack(pady=6)

        # optional: process expired allocations when app starts
        self.process_expired_allocations(silent=True)

    # ================= STUDENTS =================
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
            for row in self.student.get_all():
                tree.insert("", "end", values=row)

        def save_student():
            if name.get().strip() == "" or reg.get().strip() == "":
                messagebox.showerror("Error", "Name and Registration No are required")
                return

            ok = self.student.register(
                name.get().strip(),
                phone.get().strip(),
                reg.get().strip(),
                gender.get().strip()
            )

            if ok:
                messagebox.showinfo("Success", "Student Registered")
                name.delete(0, tk.END)
                phone.delete(0, tk.END)
                reg.delete(0, tk.END)
                gender.current(0)
                refresh_students()
            else:
                messagebox.showerror("Error", "Registration failed (maybe RegNo already exists)")

        tk.Button(form, text="Save Student", command=save_student).grid(row=4, column=0, columnspan=2, pady=10)
        refresh_students()

    # ================= EXPIRED ALLOCATIONS =================
    def process_expired_allocations(self, silent=False):
        """
        Deallocates students whose allocation endDate is past/current date.
        - Deletes allocation
        - Decreases room occupied
        - Updates room status
        """
        try:
            # get all expired allocations
            self.db.cursor.execute("""
                SELECT allocationId, roomId
                FROM allocations
                WHERE datetime(endDate) <= datetime('now')
            """)
            expired = self.db.cursor.fetchall()
            if not expired:
                if not silent:
                    messagebox.showinfo("Expired", "No expired allocations found.")
                return

            for allocationId, roomId in expired:
                # delete allocation
                self.db.cursor.execute("DELETE FROM allocations WHERE allocationId=?", (allocationId,))

                # decrease occupied
                self.db.cursor.execute("""
                    UPDATE rooms
                    SET occupied = CASE WHEN occupied > 0 THEN occupied - 1 ELSE 0 END
                    WHERE roomId=?
                """, (roomId,))

                # update status
                self.db.cursor.execute("SELECT occupied, capacity FROM rooms WHERE roomId=?", (roomId,))
                occ, cap = self.db.cursor.fetchone()
                status = "Full" if int(occ) >= int(cap) else "Available"
                self.db.cursor.execute("UPDATE rooms SET roomStatus=? WHERE roomId=?", (status, roomId))

            self.db.conn.commit()

            if not silent:
                messagebox.showinfo("Expired", f"Processed {len(expired)} expired allocations successfully.")

        except Exception as e:
            if not silent:
                messagebox.showerror("Error", f"Failed processing expired: {e}")

    # ================= ROOMS (TABS) =================
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

        ttk.Button(top, text="Process Expired Allocations", command=lambda: self._process_and_refresh(hostel_filter, totals_lbl)).pack(side="right", padx=10)

        notebook = ttk.Notebook(win)
        notebook.pack(fill="both", expand=True, padx=10, pady=8)

        tab_rooms = ttk.Frame(notebook)
        tab_students = ttk.Frame(notebook)
        tab_add = ttk.Frame(notebook)

        notebook.add(tab_rooms, text="Rooms")
        notebook.add(tab_students, text="Room Students")
        notebook.add(tab_add, text="Add Room")

        # ---------- Rooms table ----------
        rooms_container = ttk.Frame(tab_rooms)
        rooms_container.pack(fill="both", expand=True, padx=6, pady=6)

        roomsTree = ttk.Treeview(
            rooms_container,
            columns=("roomId", "roomNumber", "capacity", "occupied", "status"),
            show="headings",
            height=16
        )
        vsb = ttk.Scrollbar(rooms_container, orient="vertical", command=roomsTree.yview)
        roomsTree.configure(yscrollcommand=vsb.set)

        for col, text, w in [
            ("roomId", "Room ID", 80),
            ("roomNumber", "Room Number", 140),
            ("capacity", "Capacity", 120),
            ("occupied", "Occupied", 120),
            ("status", "Status", 140),
        ]:
            roomsTree.heading(col, text=text)
            roomsTree.column(col, width=w, anchor="center")

        roomsTree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # ---------- Students in selected room ----------
        stud_container = ttk.Frame(tab_students)
        stud_container.pack(fill="both", expand=True, padx=6, pady=6)

        info_lbl = tk.Label(tab_students, text="Select a room in Rooms tab to view students here.")
        info_lbl.pack(anchor="w", padx=6, pady=6)

        occTree = ttk.Treeview(
            stud_container,
            columns=("studentId", "name", "regNo", "period", "amount", "endDate", "daysLeft"),
            show="headings",
            height=14
        )
        occ_vsb = ttk.Scrollbar(stud_container, orient="vertical", command=occTree.yview)
        occTree.configure(yscrollcommand=occ_vsb.set)

        cols = [
            ("studentId", "Student ID", 90, "center"),
            ("name", "Name", 220, "w"),
            ("regNo", "Reg No", 140, "center"),
            ("period", "Period", 110, "center"),
            ("amount", "Amount", 110, "center"),
            ("endDate", "Expires", 160, "center"),
            ("daysLeft", "Days Left", 100, "center"),
        ]
        for c, t, w, a in cols:
            occTree.heading(c, text=t)
            occTree.column(c, width=w, anchor=a)

        occTree.pack(side="left", fill="both", expand=True)
        occ_vsb.pack(side="right", fill="y")

        def clear_rooms():
            for r in roomsTree.get_children():
                roomsTree.delete(r)

        def clear_students():
            for r in occTree.get_children():
                occTree.delete(r)

        def update_totals():
            ht = hostel_filter.get().strip()
            self.db.cursor.execute("""
                SELECT
                  SUM(CASE WHEN p.period='Semester' THEN p.amount ELSE 0 END) AS sem_total,
                  SUM(CASE WHEN p.period='Year' THEN p.amount ELSE 0 END) AS year_total
                FROM payments p
                JOIN allocations a ON a.studentId = p.studentId
                JOIN rooms r ON r.roomId = a.roomId
                WHERE LOWER(r.hostelType)=LOWER(?)
            """, (ht,))
            row = self.db.cursor.fetchone()
            sem_total = row[0] if row and row[0] is not None else 0
            year_total = row[1] if row and row[1] is not None else 0
            totals_lbl.config(text=f"Totals: Semester {int(sem_total)} | Year {int(year_total)}")

        def load_rooms():
            clear_rooms()
            ht = hostel_filter.get().strip()

            self.db.cursor.execute("""
                SELECT roomId, roomNumber, capacity, occupied, roomStatus
                FROM rooms
                WHERE LOWER(hostelType)=LOWER(?)
                ORDER BY roomNumber
            """, (ht,))
            for row in self.db.cursor.fetchall():
                roomsTree.insert("", "end", values=row)

            update_totals()
            clear_students()

        def load_room_students(roomId: int):
            clear_students()
            self.db.cursor.execute("""
                SELECT s.studentId, s.name, s.registrationNumber,
                       COALESCE(p.period, 'N/A') AS period,
                       COALESCE(p.amount, 0) AS amount,
                       a.endDate,
                       CAST((julianday(a.endDate) - julianday('now')) AS INTEGER) AS daysLeft
                FROM allocations a
                JOIN students s ON s.studentId = a.studentId
                LEFT JOIN payments p ON p.paymentId = (
                    SELECT paymentId FROM payments
                    WHERE studentId = s.studentId
                    ORDER BY paymentDate DESC
                    LIMIT 1
                )
                WHERE a.roomId=?
                ORDER BY s.studentId
            """, (roomId,))
            for row in self.db.cursor.fetchall():
                occTree.insert("", "end", values=row)

        def on_room_select(_=None):
            sel = roomsTree.selection()
            if not sel:
                return
            roomId = roomsTree.item(sel[0])["values"][0]
            load_room_students(roomId)
            notebook.select(tab_students)

        roomsTree.bind("<<TreeviewSelect>>", on_room_select)

        # Manual deallocate
        def deallocate_student():
            sel_room = roomsTree.selection()
            sel_student = occTree.selection()
            if not sel_room:
                messagebox.showerror("Error", "Select a room first (Rooms tab).")
                return
            if not sel_student:
                messagebox.showerror("Error", "Select a student from the list.")
                return

            roomId = roomsTree.item(sel_room[0])["values"][0]
            studentId = occTree.item(sel_student[0])["values"][0]

            try:
                self.db.cursor.execute("DELETE FROM allocations WHERE studentId=? AND roomId=?", (studentId, roomId))
                self.db.cursor.execute("""
                    UPDATE rooms
                    SET occupied = CASE WHEN occupied > 0 THEN occupied - 1 ELSE 0 END
                    WHERE roomId=?
                """, (roomId,))
                self.db.cursor.execute("SELECT occupied, capacity FROM rooms WHERE roomId=?", (roomId,))
                occ, cap = self.db.cursor.fetchone()
                status = "Full" if int(occ) >= int(cap) else "Available"
                self.db.cursor.execute("UPDATE rooms SET roomStatus=? WHERE roomId=?", (status, roomId))
                self.db.conn.commit()

                messagebox.showinfo("Success", "Student deallocated successfully.")
                load_rooms()
                load_room_students(roomId)
            except Exception as e:
                messagebox.showerror("Error", f"Failed: {e}")

        ttk.Button(tab_students, text="Deallocate Selected Student", command=deallocate_student).pack(pady=10, padx=6, anchor="w")

        # ---------- ADD ROOM TAB ----------
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

            if rn == "" or cap == "" or ht == "":
                messagebox.showerror("Error", "Room Number, Capacity and Hostel Type are required")
                return

            try:
                rn_i = int(rn)
                cap_i = int(cap)
                if rn_i <= 0 or cap_i <= 0:
                    messagebox.showerror("Error", "Room Number and Capacity must be positive")
                    return
            except ValueError:
                messagebox.showerror("Error", "Room Number and Capacity must be integers")
                return

            self.db.cursor.execute("""
                SELECT 1 FROM rooms
                WHERE roomNumber=? AND LOWER(hostelType)=LOWER(?)
                LIMIT 1
            """, (rn_i, ht))
            if self.db.cursor.fetchone():
                messagebox.showerror("Error", f"Room {rn_i} already exists in {ht} hostel.")
                return

            try:
                self.db.cursor.execute("""
                    INSERT INTO rooms (roomNumber, capacity, hostelType, occupied, roomStatus)
                    VALUES (?, ?, ?, 0, 'Available')
                """, (rn_i, cap_i, ht))
                self.db.conn.commit()

                messagebox.showinfo("Success", f"Room {rn_i} added to {ht} hostel.")
                new_room.delete(0, tk.END)
                new_cap.delete(0, tk.END)
                new_type.current(0)

                hostel_filter.set(ht)
                load_rooms()
                notebook.select(tab_rooms)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add room: {e}")

        ttk.Button(addf, text="Add Room", command=add_room).grid(row=2, column=0, columnspan=4, pady=12)

        hostel_filter.bind("<<ComboboxSelected>>", lambda e: load_rooms())
        load_rooms()

    def _process_and_refresh(self, hostel_filter, totals_lbl):
        self.process_expired_allocations(silent=False)
        # totals will update when rooms reload (user can press Manage Rooms again or switch hostel)
        # Not forcing reload here because we don't have access to the internal tree.
        # User can click hostel dropdown or reopen window.

    # ================= PAYMENT =================

    def payment_window(self):
        win = tk.Toplevel(self.root)
        win.title("Payment & Allocation")
        win.geometry("620x520")

        frm = ttk.LabelFrame(win, text="Payment & Allocation")
        frm.pack(fill="both", expand=True, padx=10, pady=10)

        # ✅ Search by Registration Number (NOT ID)
        tk.Label(frm, text="Registration Number").grid(row=0, column=0, padx=6, pady=8, sticky="w")
        reg_entry = tk.Entry(frm, width=30)
        reg_entry.grid(row=0, column=1, padx=6, pady=8)

        # This will hold the actual studentId after search
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

        payment_room_map = {}  # label -> roomId

        def update_price_and_expiry(*_):
            p = period_box.get().strip()
            amount = SEMESTER_PRICE if p == "Semester" else YEAR_PRICE
            price_lbl.config(text=f"Price ({p}) = {amount}")
            duration = "6 months" if p == "Semester" else "12 months"
            expiry_lbl.config(text=f"Duration: {duration} (auto deallocate after expiry)")

        period_box.bind("<<ComboboxSelected>>", update_price_and_expiry)
        update_price_and_expiry()

        def load_rooms_for_student(student_id, hostel_type, student_name, gender):
            # auto-remove expired before loading availability
            self.process_expired_allocations(silent=True)

            info_lbl.config(text=f"Student: {student_name} | Gender: {gender} | Hostel: {hostel_type}")

            self.db.cursor.execute("""
                SELECT roomId, roomNumber
                FROM rooms
                WHERE LOWER(hostelType)=LOWER(?)
                  AND occupied < capacity
                ORDER BY roomNumber
            """, (hostel_type,))
            rows = self.db.cursor.fetchall()

            payment_room_map.clear()
            labels = []
            for rid, rno in rows:
                label = f"{rno} (ID:{rid})"
                labels.append(label)
                payment_room_map[label] = rid

            room_box["values"] = labels
            if labels:
                room_box.current(0)
            else:
                room_box.set("")
                messagebox.showwarning("No Rooms", f"No available {hostel_type} rooms")

        def search_student():
            reg = reg_entry.get().strip()
            if reg == "":
                messagebox.showerror("Error", "Enter Registration Number first.")
                return

            self.db.cursor.execute("""
                SELECT studentId, name, gender
                FROM students
                WHERE registrationNumber=?
            """, (reg,))
            st = self.db.cursor.fetchone()

            if not st:
                student_id_var.set("")
                found_lbl.config(text="Student: (not found)")
                info_lbl.config(text="")
                room_box["values"] = []
                room_box.set("")
                payment_room_map.clear()
                messagebox.showerror("Error", "Student not found with that Registration Number.")
                return

            sid, name, gender = st
            gender = (gender or "").strip().upper()
            hostel_type = "Male" if gender == "M" else "Female"

            student_id_var.set(str(sid))
            found_lbl.config(text=f"Student: {name} (ID: {sid}) | RegNo: {reg}")

            # Load rooms for this student
            load_rooms_for_student(sid, hostel_type, name, gender)

        ttk.Button(frm, text="Search Student", command=search_student)\
            .grid(row=0, column=2, padx=10, pady=8)

        def submit_payment_allocate():
            sid = student_id_var.get().strip()
            room_label = room_box.get().strip()
            period = period_box.get().strip()
            method = method_box.get().strip()

            if sid == "":
                messagebox.showerror("Error", "Search student first using Registration Number.")
                return

            if room_label == "" or period == "" or method == "":
                messagebox.showerror("Error", "Select Room, Period and Payment Method.")
                return

            if room_label not in payment_room_map:
                messagebox.showerror("Error", "Invalid room selection. Click Search Student again.")
                return

            # Prevent duplicate allocation (active)
            self.db.cursor.execute("SELECT 1 FROM allocations WHERE studentId=? LIMIT 1", (sid,))
            if self.db.cursor.fetchone():
                messagebox.showerror("Error", "This student is already allocated to a room.")
                return

            roomId = payment_room_map[room_label]
            amount_required = SEMESTER_PRICE if period == "Semester" else YEAR_PRICE

            # Gender check
            self.db.cursor.execute("SELECT gender FROM students WHERE studentId=?", (sid,))
            st = self.db.cursor.fetchone()
            if not st:
                messagebox.showerror("Error", "Student not found")
                return

            studentGender = (st[0] or "").strip().upper()
            expected_hostel = "Male" if studentGender == "M" else "Female"

            # Room details
            self.db.cursor.execute("SELECT hostelType, occupied, capacity FROM rooms WHERE roomId=?", (roomId,))
            room = self.db.cursor.fetchone()
            if not room:
                messagebox.showerror("Error", "Room not found")
                return

            roomHostelType, occupied, capacity = room

            if str(roomHostelType).strip().lower() != expected_hostel.lower():
                messagebox.showerror("Error", "Gender mismatch! Student cannot be allocated to this hostel.")
                return

            if int(occupied) >= int(capacity):
                messagebox.showerror("Error", "Room is full!")
                return

            # expiry calc: semester = +6 months, year = +12 months
            end_expr = "datetime('now', '+6 months')" if period == "Semester" else "datetime('now', '+12 months')"

            try:
                # Payment
                self.db.cursor.execute("""
                    INSERT INTO payments(studentId, amount, period, paymentDate, paymentMethod, paymentStatus)
                    VALUES (?, ?, ?, datetime('now'), ?, 'Completed')
                """, (sid, amount_required, period, method))

                # Allocation with endDate
                self.db.cursor.execute(f"""
                    INSERT INTO allocations(studentId, roomId, allocationDate, endDate)
                    VALUES (?, ?, datetime('now'), {end_expr})
                """, (sid, roomId))

                # Update room occupancy + status
                self.db.cursor.execute("UPDATE rooms SET occupied = occupied + 1 WHERE roomId=?", (roomId,))
                new_occ = int(occupied) + 1
                status = "Full" if new_occ >= int(capacity) else "Available"
                self.db.cursor.execute("UPDATE rooms SET roomStatus=? WHERE roomId=?", (status, roomId))

                self.db.conn.commit()
                messagebox.showinfo("Success", f"Payment ({period}) recorded and room allocated successfully!")

                # Reset minimal fields
                room_box.set("")
                payment_room_map.clear()

            except Exception as e:
                messagebox.showerror("Error", f"Failed: {e}")

        ttk.Button(win, text="Submit Payment & Allocate", command=submit_payment_allocate).pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = HMSApp(root)
    root.mainloop()
