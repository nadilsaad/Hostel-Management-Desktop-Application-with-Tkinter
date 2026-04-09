import sqlite3

class Database:
    def __init__(self):
        self.conn = sqlite3.connect("hms.db")
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS students(
            studentId INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            registrationNumber TEXT UNIQUE,
            gender TEXT CHECK(gender IN ('M','F'))
        )
        """)

        # roomId is PK; roomNumber can repeat across Male/Female
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS rooms(
            roomId INTEGER PRIMARY KEY AUTOINCREMENT,
            roomNumber INTEGER NOT NULL,
            capacity INTEGER NOT NULL,
            hostelType TEXT NOT NULL CHECK(hostelType IN ('Male','Female')),
            occupied INTEGER DEFAULT 0,
            roomStatus TEXT DEFAULT 'Available',
            UNIQUE(roomNumber, hostelType)
        )
        """)

        # ✅ endDate added (expiry date)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS allocations(
            allocationId INTEGER PRIMARY KEY AUTOINCREMENT,
            studentId INTEGER NOT NULL,
            roomId INTEGER NOT NULL,
            allocationDate TEXT NOT NULL,
            endDate TEXT NOT NULL,
            FOREIGN KEY(studentId) REFERENCES students(studentId),
            FOREIGN KEY(roomId) REFERENCES rooms(roomId)
        )
        """)

        # payments include period
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments(
            paymentId INTEGER PRIMARY KEY AUTOINCREMENT,
            studentId INTEGER NOT NULL,
            amount REAL NOT NULL,
            period TEXT NOT NULL CHECK(period IN ('Semester','Year')),
            paymentDate TEXT NOT NULL,
            paymentMethod TEXT,
            paymentStatus TEXT DEFAULT 'Completed',
            FOREIGN KEY(studentId) REFERENCES students(studentId)
        )
        """)

        self.conn.commit()
