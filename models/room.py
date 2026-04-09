class Room:
    def __init__(self, db):
        self.db = db

    def add_room(self, number, capacity, hostel_type):
        try:
            self.db.cursor.execute("""
                INSERT INTO rooms(roomNumber, capacity, hostelType, occupied, roomStatus)
                VALUES (%s, %s, %s, 0, 'Available')
            """, (number, capacity, hostel_type))
            self.db.conn.commit()
            return True
        except Exception as e:
            self.db.conn.rollback()
            print("Add room error:", e)
            return False

    def get_all(self):
        try:
            self.db.cursor.execute("""
                SELECT roomId, roomNumber, capacity, hostelType, occupied, roomStatus
                FROM rooms
                ORDER BY hostelType, roomNumber
            """)
            return self.db.cursor.fetchall()
        except Exception as e:
            print("Get rooms error:", e)
            return []

    def get_by_hostel_type(self, hostel_type):
        try:
            self.db.cursor.execute("""
                SELECT roomId, roomNumber, capacity, occupied, roomStatus
                FROM rooms
                WHERE hostelType = %s
                ORDER BY roomNumber
            """, (hostel_type,))
            return self.db.cursor.fetchall()
        except Exception as e:
            print("Get rooms by hostel type error:", e)
            return []

    def get_available_rooms(self, hostel_type):
        try:
            self.db.cursor.execute("""
                SELECT roomId, roomNumber, capacity, occupied, roomStatus
                FROM rooms
                WHERE hostelType = %s
                  AND occupied < capacity
                ORDER BY roomNumber
            """, (hostel_type,))
            return self.db.cursor.fetchall()
        except Exception as e:
            print("Get available rooms error:", e)
            return []

    def room_exists(self, room_number, hostel_type):
        try:
            self.db.cursor.execute("""
                SELECT 1
                FROM rooms
                WHERE roomNumber = %s AND hostelType = %s
                LIMIT 1
            """, (room_number, hostel_type))
            return self.db.cursor.fetchone() is not None
        except Exception as e:
            print("Room exists error:", e)
            return False

    def get_by_id(self, room_id):
        try:
            self.db.cursor.execute("""
                SELECT roomId, roomNumber, capacity, hostelType, occupied, roomStatus
                FROM rooms
                WHERE roomId = %s
            """, (room_id,))
            return self.db.cursor.fetchone()
        except Exception as e:
            print("Get room by id error:", e)
            return None

    def update_status(self, room_id):
        try:
            self.db.cursor.execute("""
                SELECT capacity, occupied
                FROM rooms
                WHERE roomId = %s
            """, (room_id,))
            room = self.db.cursor.fetchone()

            if not room:
                return None

            capacity, occupied = room
            status = "Full" if int(occupied) >= int(capacity) else "Available"

            self.db.cursor.execute("""
                UPDATE rooms
                SET roomStatus = %s
                WHERE roomId = %s
            """, (status, room_id))
            self.db.conn.commit()
            return status
        except Exception as e:
            self.db.conn.rollback()
            print("Update status error:", e)
            return None

    def increase_occupied(self, room_id):
        try:
            self.db.cursor.execute("""
                UPDATE rooms
                SET occupied = occupied + 1
                WHERE roomId = %s
            """, (room_id,))
            self.db.conn.commit()
            self.update_status(room_id)
            return True
        except Exception as e:
            self.db.conn.rollback()
            print("Increase occupied error:", e)
            return False

    def decrease_occupied(self, room_id):
        try:
            self.db.cursor.execute("""
                UPDATE rooms
                SET occupied = CASE
                    WHEN occupied > 0 THEN occupied - 1
                    ELSE 0
                END
                WHERE roomId = %s
            """, (room_id,))
            self.db.conn.commit()
            self.update_status(room_id)
            return True
        except Exception as e:
            self.db.conn.rollback()
            print("Decrease occupied error:", e)
            return False
