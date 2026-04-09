class Room:
    def __init__(self, db):
        self.db = db

    def add_room(self, number, capacity, fee, hostelType):
        try:
            self.db.cursor.execute(
                """
                INSERT INTO rooms(roomNumber, capacity, fee, hostelType)
                VALUES (?, ?, ?, ?)
                """,
                (number, capacity, fee, hostelType),
            )
            self.db.conn.commit()
            return True
        except Exception:
            return False

    def get_all(self):
        self.db.cursor.execute("SELECT * FROM rooms")
        return self.db.cursor.fetchall()

    def update_status(self, roomNumber):
        self.db.cursor.execute(
            """
            SELECT capacity, occupied FROM rooms WHERE roomNumber=?
            """,
            (roomNumber,),
        )
        room = self.db.cursor.fetchone()
        if room:
            capacity, occupied = room
            status = "Full" if occupied >= capacity else "Available"
            self.db.cursor.execute(
                """
                UPDATE rooms SET roomStatus=? WHERE roomNumber=?
                """,
                (status, roomNumber),
            )
            self.db.conn.commit()
            return status
        return None

    def get_by_hostel_type(self, hostelType):
        self.db.cursor.execute(
            """
            SELECT * FROM rooms WHERE hostelType=?
            """,
            (hostelType,),
        )
        return self.db.cursor.fetchall()

    def update_room(self, roomNumber, capacity, fee):
        self.db.cursor.execute(
            """
            UPDATE rooms
            SET capacity=?, fee=?
            WHERE roomNumber=?
            """,
            (capacity, fee, roomNumber),
        )
        self.db.conn.commit()
        # Recalculate and update status after changing capacity/fee
        self.update_status(roomNumber)
        return True
