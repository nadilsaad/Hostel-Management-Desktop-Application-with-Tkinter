class Student:
    def __init__(self, db):
        self.db = db

    def register(self, name, phone, reg_no, gender):
        try:
            self.db.cursor.execute("""
                INSERT INTO students(name, phone, registrationNumber, gender)
                VALUES (%s, %s, %s, %s)
            """, (name, phone, reg_no, gender))
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

    def find_by_regno(self, reg_no):
        try:
            self.db.cursor.execute("""
                SELECT studentId, name, gender, registrationNumber
                FROM students
                WHERE registrationNumber = %s
            """, (reg_no,))
            return self.db.cursor.fetchone()
        except Exception as e:
            print("Find student by reg no error:", e)
            return None

    def delete(self, student_id):
        try:
            self.db.cursor.execute("""
                DELETE FROM students
                WHERE studentId = %s
            """, (student_id,))
            self.db.conn.commit()
            return True
        except Exception as e:
            self.db.conn.rollback()
            print("Delete student error:", e)
            return False
