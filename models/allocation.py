class RoomAllocation:
    def __init__(self, db):
        self.db = db

    def process_expired_allocations(self):
        try:
            self.db.cursor.execute("""
                SELECT allocationId, roomId
                FROM allocations
                WHERE endDate <= NOW()
            """)
            expired = self.db.cursor.fetchall()

            count = 0
            for allocation_id, room_id in expired:
                self.db.cursor.execute("""
                    DELETE FROM allocations
                    WHERE allocationId = %s
                """, (allocation_id,))

                self.db.cursor.execute("""
                    UPDATE rooms
                    SET occupied = CASE
                        WHEN occupied > 0 THEN occupied - 1
                        ELSE 0
                    END
                    WHERE roomId = %s
                """, (room_id,))

                self.db.cursor.execute("""
                    SELECT occupied, capacity
                    FROM rooms
                    WHERE roomId = %s
                """, (room_id,))
                room = self.db.cursor.fetchone()

                if room:
                    occupied, capacity = room
                    status = "Full" if int(occupied) >= int(capacity) else "Available"
                    self.db.cursor.execute("""
                        UPDATE rooms
                        SET roomStatus = %s
                        WHERE roomId = %s
                    """, (status, room_id))

                count += 1

            self.db.conn.commit()
            return True, count
        except Exception as e:
            self.db.conn.rollback()
            print("Process expired allocations error:", e)
            return False, 0

    def deallocate_student(self, student_id, room_id):
        try:
            self.db.cursor.execute("""
                DELETE FROM allocations
                WHERE studentId = %s AND roomId = %s
            """, (student_id, room_id))

            self.db.cursor.execute("""
                UPDATE rooms
                SET occupied = CASE
                    WHEN occupied > 0 THEN occupied - 1
                    ELSE 0
                END
                WHERE roomId = %s
            """, (room_id,))

            self.db.cursor.execute("""
                SELECT occupied, capacity
                FROM rooms
                WHERE roomId = %s
            """, (room_id,))
            room = self.db.cursor.fetchone()

            if room:
                occupied, capacity = room
                status = "Full" if int(occupied) >= int(capacity) else "Available"
                self.db.cursor.execute("""
                    UPDATE rooms
                    SET roomStatus = %s
                    WHERE roomId = %s
                """, (status, room_id))

            self.db.conn.commit()
            return True, "Student deallocated successfully"
        except Exception as e:
            self.db.conn.rollback()
            print("Deallocate student error:", e)
            return False, f"Error: {e}"

    def get_students_in_room(self, room_id):
        try:
            self.db.cursor.execute("""
                SELECT
                    s.studentId,
                    s.name,
                    s.registrationNumber,
                    COALESCE(p.period, 'N/A') AS period,
                    COALESCE(p.amount, 0) AS amount,
                    a.endDate,
                    GREATEST(0, DATE_PART('day', a.endDate - NOW()))::int AS daysLeft
                FROM allocations a
                JOIN students s ON s.studentId = a.studentId
                LEFT JOIN LATERAL (
                    SELECT period, amount
                    FROM payments
                    WHERE studentId = s.studentId
                    ORDER BY paymentDate DESC
                    LIMIT 1
                ) p ON TRUE
                WHERE a.roomId = %s
                ORDER BY s.studentId
            """, (room_id,))
            return self.db.cursor.fetchall()
        except Exception as e:
            print("Get students in room error:", e)
            return []
