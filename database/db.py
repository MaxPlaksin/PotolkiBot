import aiosqlite
from bot.config import DB_PATH

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                address TEXT NOT NULL,
                wishes TEXT,
                area REAL,
                material TEXT,
                price INTEGER,
                photo_file_id TEXT,
                status TEXT DEFAULT 'new',
                manager_comment TEXT,
                desired_date TEXT,
                measure_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP
            );
        ''')
        await db.commit()

async def save_user(name: str, phone: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        await db.execute('INSERT INTO users (name, phone) VALUES (?, ?)', (name, phone))
        await db.commit()

async def get_all_users():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT id, name, phone, created_at FROM users ORDER BY created_at DESC') as cursor:
            return await cursor.fetchall()

async def save_order(name: str, phone: str, address: str, desired_date: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT INTO orders (name, phone, address, desired_date)
            VALUES (?, ?, ?, ?)
        ''', (name, phone, address, desired_date))
        await db.commit()

async def get_all_orders():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT id, name, phone, address, desired_date, created_at FROM orders ORDER BY created_at DESC') as cursor:
            return await cursor.fetchall()

async def update_measure_date(order_id: int, measure_date: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('UPDATE orders SET measure_date = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?', (measure_date, order_id))
        await db.commit()
