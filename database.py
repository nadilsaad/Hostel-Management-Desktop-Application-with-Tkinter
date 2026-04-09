import os
from dotenv import load_dotenv
import psycopg2


load_dotenv()


class Database:
    def __init__(self):
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise ValueError("DATABASE_URL not found in environment variables.")

        self.conn = psycopg2.connect(db_url)
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
                allocationDate TIMESTAMP NOT NULL,
                endDate TIMESTAMP NOT NULL,
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
                paymentDate TIMESTAMP NOT NULL,
                paymentMethod TEXT,
                paymentStatus TEXT DEFAULT 'Completed',
                FOREIGN KEY(studentId) REFERENCES students(studentId) ON DELETE CASCADE
            )
        """)

        self.conn.commit()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
