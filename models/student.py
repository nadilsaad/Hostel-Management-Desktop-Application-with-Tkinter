class Student:
    def __init__(self, db):
        self.db = db

    def register(self, name, phone, regNo, gender):
        try:
            self.db.cursor.execute("""
                INSERT INTO students(name, phone, registrationNumber, gender)
                VALUES (%s, %s, %s, %s)
            """, (name, phone, regNo, gender))
            self.db.conn.commit()
            return True
        except Exception as e:
            self.db.conn.rollback()
            print("Student register error:", e)
            return False

    def get_all(self):
        try:
            self.db.cursor.execute("""
                SELECT studentId, name, phone, registrationNumber, gender
                FROM students
                ORDER BY studentId
            """)
            return self.db.cursor.fetchall()
        except Exception as e:
            print("Get students error:", e)
            return []

    def delete(self, studentId):
        try:
            self.db.cursor.execute("""
                DELETE FROM students
                WHERE studentId = %s
            """, (studentId,))
            self.db.conn.commit()
            return True
        except Exception as e:
            self.db.conn.rollback()
            print("Delete student error:", e)
            return False
