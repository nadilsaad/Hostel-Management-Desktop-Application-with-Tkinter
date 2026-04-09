import os
import psycopg2


class Database:
    def __init__(self):
        self.conn = psycopg2.connect(
            os.getenv(
                "DATABASE_URL",
                "postgresql://neondb_owner:npg_GUeSt9TB7OKf@ep-cold-flower-alfabfxz-pooler.c-3.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
            )
        )
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS students(
            studentId SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT,
            registrationNumber TEXT UNIQUE,
            gender TEXT CHECK(gender IN ('M','F'))
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS rooms(
            roomId SERIAL PRIMARY KEY,
            roomNumber INTEGER NOT NULL,
            capacity INTEGER NOT NULL,
            hostelType TEXT NOT NULL CHECK(hostelType IN ('Male','Female')),
            occupied INTEGER DEFAULT 0,
            roomStatus TEXT DEFAULT 'Available',
            UNIQUE(roomNumber, hostelType)
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS allocations(
            allocationId SERIAL PRIMARY KEY,
            studentId INTEGER NOT NULL,
            roomId INTEGER NOT NULL,
            allocationDate TEXT NOT NULL,
            endDate TEXT NOT NULL,
            FOREIGN KEY(studentId) REFERENCES students(studentId) ON DELETE CASCADE,
            FOREIGN KEY(roomId) REFERENCES rooms(roomId) ON DELETE CASCADE
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments(
            paymentId SERIAL PRIMARY KEY,
            studentId INTEGER NOT NULL,
            amount REAL NOT NULL,
            period TEXT NOT NULL CHECK(period IN ('Semester','Year')),
            paymentDate TEXT NOT NULL,
            paymentMethod TEXT,
            paymentStatus TEXT DEFAULT 'Completed',
            FOREIGN KEY(studentId) REFERENCES students(studentId) ON DELETE CASCADE
        )
        """)

        self.conn.commit()

    def execute_query(self, query, params=None):
        try:
            self.cursor.execute(query, params or ())
            self.conn.commit()
            return True
        except Exception as e:
            print("Query Error:", e)
            self.conn.rollback()
            return False

    def fetch_all(self, query, params=None):
        try:
            self.cursor.execute(query, params or ())
            return self.cursor.fetchall()
        except Exception as e:
            print("Fetch Error:", e)
            return []

    def fetch_one(self, query, params=None):
        try:
            self.cursor.execute(query, params or ())
            return self.cursor.fetchone()
        except Exception as e:
            print("Fetch One Error:", e)
            return None

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
