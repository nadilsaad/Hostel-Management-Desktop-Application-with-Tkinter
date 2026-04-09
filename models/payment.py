from datetime import datetime

class Payment:
    def __init__(self, db):
        self.db = db

    def pay_and_allocate(self, studentId, roomNumber, period, method):

        # Determine fee
        if period == "Semester":
            amount_required = 120000
        elif period == "Year":
            amount_required = 140000
        else:
            return "Invalid Period"

        # Get student gender
        self.db.cursor.execute("""
        SELECT gender FROM students WHERE studentId=?
        """, (studentId,))
        student = self.db.cursor.fetchone()

        if not student:
            return "Student not found"

        student_gender = student[0]

        # Get room details
        self.db.cursor.execute("""
        SELECT capacity, occupied, hostelType FROM rooms WHERE roomNumber=?
        """, (roomNumber,))
        room = self.db.cursor.fetchone()

        if not room:
            return "Room does not exist"

        capacity, occupied, hostelType = room

        # Gender validation
        if hostelType == "Male" and student_gender != "M":
            return "Female student cannot be allocated to Male hostel"

        if hostelType == "Female" and student_gender != "F":
            return "Male student cannot be allocated to Female hostel"

        if occupied >= capacity:
            return "Room is Full"

        # Insert payment
        self.db.cursor.execute("""
        INSERT INTO payments(studentId, amount, paymentDate, paymentMethod, paymentStatus)
        VALUES (?, ?, ?, ?, ?)
        """, (studentId, amount_required, datetime.now(), method, "Completed"))

        # Allocate
        self.db.cursor.execute("""
        INSERT INTO allocations(studentId, roomNumber, allocationDate)
        VALUES (?, ?, ?)
        """, (studentId, roomNumber, datetime.now()))

        self.db.cursor.execute("""
        UPDATE rooms SET occupied = occupied + 1 WHERE roomNumber=?
        """, (roomNumber,))

        # Update room status
        new_status = "Full" if occupied + 1 >= capacity else "Available"

        self.db.cursor.execute("""
        UPDATE rooms SET roomStatus=? WHERE roomNumber=?
        """, (new_status, roomNumber))

        self.db.conn.commit()

        return "Payment Completed & Room Allocated"
