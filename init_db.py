import sqlite3
import os

def init_db():
    db_path = 'gym.db'
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create USERS table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    ''')
    cursor.execute("INSERT INTO users (username, password) VALUES ('admin', 'admin123')")
    cursor.execute("INSERT INTO users (username, password) VALUES ('staff', 'staff123')")

    # Create TRAINER table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS trainer (
        trainer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        trainer_name TEXT,
        specialization TEXT,
        phone TEXT,
        email TEXT
    )
    ''')
    trainers = [
        ('Trainer1','Cardio','900000001','t1@gym.com'),
        ('Trainer2','Weights','900000002','t2@gym.com'),
        ('Trainer3','Yoga','900000003','t3@gym.com'),
        ('Trainer4','CrossFit','900000004','t4@gym.com'),
        ('Trainer5','Zumba','900000005','t5@gym.com')
    ]
    cursor.executemany("INSERT INTO trainer (trainer_name, specialization, phone, email) VALUES (?,?,?,?)", trainers)

    # Create MEMBER table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS member (
        member_id INTEGER PRIMARY KEY AUTOINCREMENT,
        member_name TEXT,
        age INTEGER,
        gender TEXT,
        phone TEXT,
        email TEXT,
        join_date TEXT,
        expiry_date TEXT,
        status TEXT,
        trainer_id INTEGER,
        FOREIGN KEY (trainer_id) REFERENCES trainer(trainer_id)
    )
    ''')
    members = [
        ('Member1',21,'Male','800000001','m1@gym.com','2024-01-01','2024-12-31','Active', 1),
        ('Member2',22,'Female','800000002','m2@gym.com','2024-01-02','2024-06-30','Active', 2),
        ('Member3',23,'Male','800000003','m3@gym.com','2024-01-03','2023-12-31','Expired', 1)
    ]
    cursor.executemany("INSERT INTO member (member_name, age, gender, phone, email, join_date, expiry_date, status, trainer_id) VALUES (?,?,?,?,?,?,?,?,?)", members)

    # Create PLAN table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS plan (
        plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
        plan_name TEXT,
        duration TEXT,
        fee REAL
    )
    ''')
    plans = [
        ('Monthly','1 Month', 1500),
        ('Quarterly','3 Months', 4000),
        ('Yearly','12 Months', 12000)
    ]
    cursor.executemany("INSERT INTO plan (plan_name, duration, fee) VALUES (?,?,?)", plans)

    # Create BILLING table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS billing (
        billing_id INTEGER PRIMARY KEY AUTOINCREMENT,
        member_id INTEGER,
        trainer_id INTEGER,
        amount REAL,
        bill_date TEXT,
        FOREIGN KEY (member_id) REFERENCES member(member_id),
        FOREIGN KEY (trainer_id) REFERENCES trainer(trainer_id)
    )
    ''')
    billing_data = [
        (1,1,1500,'2024-01-01'),
        (2,2,1600,'2024-01-02'),
        (3,3,1700,'2024-01-03')
    ]
    cursor.executemany("INSERT INTO billing (member_id, trainer_id, amount, bill_date) VALUES (?,?,?,?)", billing_data)

    conn.commit()
    conn.close()
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()
