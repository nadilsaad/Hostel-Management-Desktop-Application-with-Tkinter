class Room:
    def __init__(self, db):
        self.db = db

    def add_room(self, number, capacity, hostelType):
        try:
            self.db.cursor.execute("""
                INSERT INTO rooms(roomNumber, capacity, hostelType, occupied, roomStatus)
                VALUES (%s, %s, %s, 0, 'Available')
            """, (number, capacity, hostelType))
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
                ORDER BY roomNumber
            """)
            return self.db.cursor.fetchall()
        except Exception as e:
            print("Get rooms error:", e)
            return []

    def update_status(self, roomId):
        try:
            self.db.cursor.execute("""
                SELECT capacity, occupied
                FROM rooms
                WHERE roomId = %s
            """, (roomId,))
            room = self.db.cursor.fetchone()

            if room:
                capacity, occupied = room
                status = "Full" if int(occupied) >= int(capacity) else "Available"

                self.db.cursor.execute("""
                    UPDATE rooms
                    SET roomStatus = %s
                    WHERE roomId = %s
                """, (status, roomId))
                self.db.conn.commit()
                return status

            return None
        except Exception as e:
            self.db.conn.rollback()
            print("Update room status error:", e)
            return None

    def get_by_hostel_type(self, hostelType):
        try:
            self.db.cursor.execute("""
                SELECT roomId, roomNumber, capacity, hostelType, occupied, roomStatus
                FROM rooms
                WHERE hostelType = %s
                ORDER BY roomNumber
            """, (hostelType,))
            return self.db.cursor.fetchall()
        except Exception as e:
            print("Get rooms by hostel type error:", e)
            return []

    def update_room(self, roomId, capacity, hostelType):
        try:
            self.db.cursor.execute("""
                UPDATE rooms
                SET capacity = %s,
                    hostelType = %s
                WHERE roomId = %s
            """, (capacity, hostelType, roomId))
            self.db.conn.commit()

            self.update_status(roomId)
            return True
        except Exception as e:
            self.db.conn.rollback()
            print("Update room error:", e)
            return False

    def delete_room(self, roomId):
        try:
            self.db.cursor.execute("""
                DELETE FROM rooms
                WHERE roomId = %s
            """, (roomId,))
            self.db.conn.commit()
            return True
        except Exception as e:
            self.db.conn.rollback()
            print("Delete room error:", e)
            return False

    def get_available_rooms(self, hostelType):
        try:
            self.db.cursor.execute("""
                SELECT roomId, roomNumber, capacity, occupied, roomStatus
                FROM rooms
                WHERE hostelType = %s
                  AND occupied < capacity
                ORDER BY roomNumber
            """, (hostelType,))
            return self.db.cursor.fetchall()
        except Exception as e:
            print("Get available rooms error:", e)
            return []
