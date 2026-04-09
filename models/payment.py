class Payment:
    SEMESTER_PRICE = 120000
    YEAR_PRICE = 140000

    def __init__(self, db):
        self.db = db

    def pay_and_allocate(self, student_id, room_id, period, method):
        try:
            if period == "Semester":
                amount_required = self.SEMESTER_PRICE
                interval_value = "6 months"
            elif period == "Year":
                amount_required = self.YEAR_PRICE
                interval_value = "12 months"
            else:
                return False, "Invalid Period"

            self.db.cursor.execute("""
                SELECT gender
                FROM students
                WHERE studentId = %s
            """, (student_id,))
            student = self.db.cursor.fetchone()

            if not student:
                return False, "Student not found"

            student_gender = (student[0] or "").strip().upper()

            self.db.cursor.execute("""
                SELECT roomId, hostelType, capacity, occupied
                FROM rooms
                WHERE roomId = %s
            """, (room_id,))
            room = self.db.cursor.fetchone()

            if not room:
                return False, "Room not found"

            room_id_db, hostel_type, capacity, occupied = room
            expected_hostel = "Male" if student_gender == "M" else "Female"

            if hostel_type.lower() != expected_hostel.lower():
                return False, "Gender mismatch! Student cannot be allocated to this hostel."

            if int(occupied) >= int(capacity):
                return False, "Room is Full"

            self.db.cursor.execute("""
                SELECT 1
                FROM allocations
                WHERE studentId = %s
                LIMIT 1
            """, (student_id,))
            if self.db.cursor.fetchone():
                return False, "Student is already allocated to a room"

            self.db.cursor.execute("""
                INSERT INTO payments(studentId, amount, period, paymentDate, paymentMethod, paymentStatus)
                VALUES (%s, %s, %s, NOW(), %s, 'Completed')
            """, (student_id, amount_required, period, method))

            self.db.cursor.execute(f"""
                INSERT INTO allocations(studentId, roomId, allocationDate, endDate)
                VALUES (%s, %s, NOW(), NOW() + INTERVAL '{interval_value}')
            """, (student_id, room_id_db))

            self.db.cursor.execute("""
                UPDATE rooms
                SET occupied = occupied + 1
                WHERE roomId = %s
            """, (room_id_db,))

            new_status = "Full" if int(occupied) + 1 >= int(capacity) else "Available"
            self.db.cursor.execute("""
                UPDATE rooms
                SET roomStatus = %s
                WHERE roomId = %s
            """, (new_status, room_id_db))

            self.db.conn.commit()
            return True, f"Payment ({period}) completed and room allocated successfully"

        except Exception as e:
            self.db.conn.rollback()
            print("Payment error:", e)
            return False, f"Error: {e}"

    def get_totals_by_hostel(self, hostel_type):
        try:
            self.db.cursor.execute("""
                SELECT
                    COALESCE(SUM(CASE WHEN p.period = 'Semester' THEN p.amount ELSE 0 END), 0) AS sem_total,
                    COALESCE(SUM(CASE WHEN p.period = 'Year' THEN p.amount ELSE 0 END), 0) AS year_total
                FROM payments p
                JOIN allocations a ON a.studentId = p.studentId
                JOIN rooms r ON r.roomId = a.roomId
                WHERE r.hostelType = %s
            """, (hostel_type,))
            row = self.db.cursor.fetchone()
            return row if row else (0, 0)
        except Exception as e:
            print("Get totals error:", e)
            return (0, 0)
