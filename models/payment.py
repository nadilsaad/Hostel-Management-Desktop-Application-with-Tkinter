class Payment:
    def __init__(self, db):
        self.db = db

    def pay_and_allocate(self, studentId, roomNumber, period, method):
        try:
            # Determine fee
            if period == "Semester":
                amount_required = 120000
                interval_value = "6 months"
            elif period == "Year":
                amount_required = 140000
                interval_value = "12 months"
            else:
                return "Invalid Period"

            # Get student gender
            self.db.cursor.execute("""
                SELECT gender
                FROM students
                WHERE studentId = %s
            """, (studentId,))
            student = self.db.cursor.fetchone()

            if not student:
                return "Student not found"

            student_gender = (student[0] or "").strip().upper()

            # Get room details using roomNumber
            self.db.cursor.execute("""
                SELECT roomId, capacity, occupied, hostelType
                FROM rooms
                WHERE roomNumber = %s
            """, (roomNumber,))
            room = self.db.cursor.fetchone()

            if not room:
                return "Room does not exist"

            roomId, capacity, occupied, hostelType = room

            # Gender validation
            if hostelType == "Male" and student_gender != "M":
                return "Female student cannot be allocated to Male hostel"

            if hostelType == "Female" and student_gender != "F":
                return "Male student cannot be allocated to Female hostel"

            if int(occupied) >= int(capacity):
                return "Room is Full"

            # Prevent duplicate allocation
            self.db.cursor.execute("""
                SELECT 1
                FROM allocations
                WHERE studentId = %s
                LIMIT 1
            """, (studentId,))
            if self.db.cursor.fetchone():
                return "Student is already allocated to a room"

            # Insert payment
            self.db.cursor.execute("""
                INSERT INTO payments(studentId, amount, period, paymentDate, paymentMethod, paymentStatus)
                VALUES (%s, %s, %s, NOW(), %s, %s)
            """, (studentId, amount_required, period, method, "Completed"))

            # Insert allocation with endDate
            self.db.cursor.execute(f"""
                INSERT INTO allocations(studentId, roomId, allocationDate, endDate)
                VALUES (%s, %s, NOW(), NOW() + INTERVAL '{interval_value}')
            """, (studentId, roomId))

            # Update room occupancy
            self.db.cursor.execute("""
                UPDATE rooms
                SET occupied = occupied + 1
                WHERE roomId = %s
            """, (roomId,))

            # Update room status
            new_status = "Full" if int(occupied) + 1 >= int(capacity) else "Available"
            self.db.cursor.execute("""
                UPDATE rooms
                SET roomStatus = %s
                WHERE roomId = %s
            """, (new_status, roomId))

            self.db.conn.commit()
            return "Payment Completed & Room Allocated"

        except Exception as e:
            self.db.conn.rollback()
            print("Payment error:", e)
            return f"Error: {e}"
