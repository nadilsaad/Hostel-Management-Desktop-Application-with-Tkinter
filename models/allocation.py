from datetime import datetime

class RoomAllocation:
    def __init__(self, db):
        self.db = db

    def allocate_if_paid(self, studentId):

        # Check payment
        self.db.cursor.execute("""
        SELECT p.amount, r.roomNumber, r.capacity, r.occupied, r.fee
        FROM payments p
        JOIN allocations a ON p.studentId = a.studentId
        JOIN rooms r ON a.roomNumber = r.roomNumber
        WHERE p.studentId = ?
        ORDER BY p.paymentDate DESC
        """, (studentId,))

        data = self.db.cursor.fetchone()

        if not data:
            return "No payment found"

        amount, roomNumber, capacity, occupied, fee = data

        if amount >= fee:

            if occupied < capacity:

                self.db.cursor.execute("""
                UPDATE rooms SET occupied = occupied + 1 WHERE roomNumber=?
                """, (roomNumber,))

                self.db.conn.commit()

                return "Student Fully Allocated"

            else:
                return "Room is Full"

        else:
            return "Payment Not Enough"
