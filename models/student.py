class Student:
    def __init__(self, db):
        self.db = db

    def register(self, name, phone, regNo, gender):
        try:
            self.db.cursor.execute("""
            INSERT INTO students(name, phone, registrationNumber, gender)
            VALUES (?, ?, ?, ?)
            """, (name, phone, regNo, gender))
            self.db.conn.commit()
            return True
        except:
            return False

    def get_all(self):
        self.db.cursor.execute("SELECT * FROM students")
        return self.db.cursor.fetchall()

    def delete(self, studentId):
        self.db.cursor.execute("DELETE FROM students WHERE studentId=?", (studentId,))
        self.db.conn.commit()
