class RoomAllocation:
    def __init__(self, db):
        self.db = db

    def allocate_if_paid(self, studentId, roomId):
        try:
            # Check student exists
            self.db.cursor.execute("""
                SELECT gender
                FROM students
                WHERE studentId = %s
            """, (studentId,))
            student = self.db.cursor.fetchone()

            if not student:
                return "Student not found"

            student_gender = (student[0] or "").strip().upper()

            # Check latest payment
            self.db.cursor.execute("""
                SELECT amount, period
                FROM payments
                WHERE studentId = %s
                ORDER BY paymentDate DESC
                LIMIT 1
            """, (studentId,))
            payment = self.db.cursor.fetchone()

            if not payment:
                return "No payment found"

            amount, period = payment

            # Determine required fee
            if period == "Semester":
                required_fee = 120000
                interval_value = "6 months"
            elif period == "Year":
                required_fee = 140000
                interval_value = "12 months"
            else:
                return "Invalid payment period"

            if float(amount) < float(required_fee):
                return "Payment Not Enough"

            # Prevent duplicate allocation
            self.db.cursor.execute("""
                SELECT 1
                FROM allocations
                WHERE studentId = %s
                LIMIT 1
            """, (studentId,))
            if self.db.cursor.fetchone():
                return "Student already allocated"

            # Get room details
            self.db.cursor.execute("""
                SELECT roomId, hostelType, capacity, occupied
                FROM rooms
                WHERE roomId = %s
            """, (roomId,))
            room = self.db.cursor.fetchone()

            if not room:
                return "Room not found"

            room_id, hostel_type, capacity, occupied = room

            expected_hostel = "Male" if student_gender == "M" else "Female"
            if str(hostel_type).strip().lower() != expected_hostel.lower():
                return "Gender mismatch"

            if int(occupied) >= int(capacity):
                return "Room is Full"

            # Insert allocation
            self.db.cursor.execute(f"""
                INSERT INTO allocations(studentId, roomId, allocationDate, endDate)
                VALUES (%s, %s, NOW(), NOW() + INTERVAL '{interval_value}')
            """, (studentId, room_id))

            # Update room occupancy
            self.db.cursor.execute("""
                UPDATE rooms
                SET occupied = occupied + 1
                WHERE roomId = %s
            """, (room_id,))

            # Update room status
            new_status = "Full" if int(occupied) + 1 >= int(capacity) else "Available"
            self.db.cursor.execute("""
                UPDATE rooms
                SET roomStatus = %s
                WHERE roomId = %s
            """, (new_status, room_id))

            self.db.conn.commit()
            return "Student Fully Allocated"

        except Exception as e:
            self.db.conn.rollback()
            print("Allocation error:", e)
            return f"Error: {e}"

    def deallocate_student(self, studentId, roomId):
        try:
            self.db.cursor.execute("""
                DELETE FROM allocations
                WHERE studentId = %s AND roomId = %s
            """, (studentId, roomId))

            self.db.cursor.execute("""
                UPDATE rooms
                SET occupied = CASE
                    WHEN occupied > 0 THEN occupied - 1
                    ELSE 0
                END
                WHERE roomId = %s
            """, (roomId,))

            self.db.cursor.execute("""
                SELECT occupied, capacity
                FROM rooms
                WHERE roomId = %s
            """, (roomId,))
            room = self.db.cursor.fetchone()

            if room:
                occupied, capacity = room
                status = "Full" if int(occupied) >= int(capacity) else "Available"
                self.db.cursor.execute("""
                    UPDATE rooms
                    SET roomStatus = %s
                    WHERE roomId = %s
                """, (status, roomId))

            self.db.conn.commit()
            return "Student Deallocated Successfully"

        except Exception as e:
            self.db.conn.rollback()
            print("Deallocation error:", e)
            return f"Error: {e}"

    def get_all_allocations(self):
        try:
            self.db.cursor.execute("""
                SELECT
                    a.allocationId,
                    s.studentId,
                    s.name,
                    s.registrationNumber,
                    r.roomId,
                    r.roomNumber,
                    r.hostelType,
                    a.allocationDate,
                    a.endDate
                FROM allocations a
                JOIN students s ON a.studentId = s.studentId
                JOIN rooms r ON a.roomId = r.roomId
                ORDER BY a.allocationId
            """)
            return self.db.cursor.fetchall()
        except Exception as e:
            print("Get allocations error:", e)
            return []
