import sqlite3
import os
from config import MAX_DISPLAY_ROWS


def init_database(db_path: str) -> None:
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.executescript("""
        PRAGMA foreign_keys = ON;

        CREATE TABLE IF NOT EXISTS customers (
            customer_id  INTEGER PRIMARY KEY,
            name         TEXT    NOT NULL,
            email        TEXT    NOT NULL UNIQUE,
            city         TEXT    NOT NULL,
            signup_date  TEXT    NOT NULL
        );

        CREATE TABLE IF NOT EXISTS products (
            product_id  INTEGER PRIMARY KEY,
            name        TEXT    NOT NULL,
            category    TEXT    NOT NULL,
            price       REAL    NOT NULL,
            stock       INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS orders (
            order_id    INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
            order_date  TEXT    NOT NULL,
            status      TEXT    NOT NULL CHECK(status IN ('pending','paid','shipped','delivered','cancelled'))
        );

        CREATE TABLE IF NOT EXISTS order_items (
            item_id     INTEGER PRIMARY KEY,
            order_id    INTEGER NOT NULL REFERENCES orders(order_id),
            product_id  INTEGER NOT NULL REFERENCES products(product_id),
            quantity    INTEGER NOT NULL,
            unit_price  REAL    NOT NULL
        );
    """)

    customers = [
        (1, "Ana Silva",      "ana@email.com",     "São Paulo",       "2023-01-15"),
        (2, "Bruno Souza",    "bruno@email.com",   "Rio de Janeiro",  "2023-02-20"),
        (3, "Carla Mendes",   "carla@email.com",   "Belo Horizonte",  "2023-03-10"),
        (4, "Diego Rocha",    "diego@email.com",   "Curitiba",        "2023-04-05"),
        (5, "Elena Castro",   "elena@email.com",   "Porto Alegre",    "2023-05-18"),
        (6, "Felipe Lima",    "felipe@email.com",  "Recife",          "2023-06-22"),
        (7, "Gabi Ferreira",  "gabi@email.com",    "Salvador",        "2023-07-30"),
        (8, "Hugo Martins",   "hugo@email.com",    "Fortaleza",       "2023-08-12"),
        (9, "Isabela Nunes",  "isabela@email.com", "Manaus",          "2023-09-01"),
    ]
    cur.executemany(
        "INSERT OR IGNORE INTO customers VALUES (?,?,?,?,?)", customers
    )

    products = [
        (1,  "Notebook Gamer",    "Eletrônicos",   4500.00, 10),
        (2,  "Mouse Sem Fio",     "Eletrônicos",     89.90, 50),
        (3,  "Teclado Mecânico",  "Eletrônicos",    299.00, 30),
        (4,  "Monitor 27\"",      "Eletrônicos",   1200.00, 15),
        (5,  "Cadeira Gamer",     "Móveis",        1800.00,  8),
        (6,  "Mesa de Escritório","Móveis",         650.00, 12),
        (7,  "Headset USB",       "Eletrônicos",    199.00, 40),
        (8,  "Webcam Full HD",    "Eletrônicos",    249.00, 25),
        (9,  "Camisa Polo",       "Vestuário",       79.90, 100),
        (10, "Tênis Running",     "Vestuário",      349.00, 60),
        (11, "Mochila Executiva", "Acessórios",     189.00, 35),
        (12, "Garrafa Térmica",   "Acessórios",      59.90, 80),
    ]
    cur.executemany(
        "INSERT OR IGNORE INTO products VALUES (?,?,?,?,?)", products
    )

    orders = [
        (1,  1, "2024-01-10", "delivered"),
        (2,  2, "2024-01-15", "delivered"),
        (3,  3, "2024-02-01", "shipped"),
        (4,  4, "2024-02-14", "paid"),
        (5,  5, "2024-02-20", "cancelled"),
        (6,  1, "2024-03-05", "delivered"),
        (7,  6, "2024-03-10", "shipped"),
        (8,  7, "2024-03-22", "pending"),
        (9,  2, "2024-04-01", "paid"),
        (10, 8, "2024-04-15", "delivered"),
        (11, 3, "2024-04-20", "cancelled"),
        (12, 9, "2024-05-02", "pending"),
        (13, 4, "2024-05-10", "shipped"),
        (14, 5, "2024-05-18", "delivered"),
    ]
    cur.executemany(
        "INSERT OR IGNORE INTO orders VALUES (?,?,?,?)", orders
    )

    order_items = [
        (1,  1,  1, 1, 4500.00),
        (2,  1,  2, 2,   89.90),
        (3,  2,  3, 1,  299.00),
        (4,  2,  7, 1,  199.00),
        (5,  3,  4, 1, 1200.00),
        (6,  3,  8, 1,  249.00),
        (7,  4,  5, 1, 1800.00),
        (8,  5,  9, 3,   79.90),
        (9,  6,  2, 1,   89.90),
        (10, 6, 11, 1,  189.00),
        (11, 7, 10, 2,  349.00),
        (12, 8, 12, 4,   59.90),
        (13, 9,  6, 1,  650.00),
        (14, 9,  3, 1,  299.00),
        (15, 10, 1, 1, 4500.00),
        (16, 11, 4, 1, 1200.00),
        (17, 12, 9, 2,   79.90),
        (18, 12,10, 1,  349.00),
        (19, 13, 5, 1, 1800.00),
        (20, 14, 2, 3,   89.90),
        (21, 14,11, 2,  189.00),
    ]
    cur.executemany(
        "INSERT OR IGNORE INTO order_items VALUES (?,?,?,?,?)", order_items
    )

    conn.commit()
    conn.close()
    print(f"Banco criado/atualizado em: {db_path}")


def get_schema_description(db_path: str) -> str:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND sql IS NOT NULL ORDER BY name"
    )
    ddls = [row[0] for row in cur.fetchall()]
    conn.close()
    return "\n\n".join(ddls)


def execute_query(db_path: str, sql: str):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(sql)
    columns = [desc[0] for desc in cur.description] if cur.description else []
    rows = cur.fetchall()
    conn.close()
    return columns, rows


def print_table(columns: list, rows: list) -> None:
    if not rows:
        print("(nenhuma linha retornada)")
        return

    display_rows = rows[:MAX_DISPLAY_ROWS]
    hidden = len(rows) - len(display_rows)

    col_widths = [len(str(c)) for c in columns]
    for row in display_rows:
        for i, val in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(val)))

    sep = "+-" + "-+-".join("-" * w for w in col_widths) + "-+"
    header = "| " + " | ".join(str(c).ljust(col_widths[i]) for i, c in enumerate(columns)) + " |"

    print(sep)
    print(header)
    print(sep)
    for row in display_rows:
        line = "| " + " | ".join(str(v).ljust(col_widths[i]) for i, v in enumerate(row)) + " |"
        print(line)
    print(sep)
    print(f"  {len(display_rows)} linha(s) exibida(s)", end="")
    if hidden:
        print(f" — {hidden} linha(s) omitida(s) (limite: {MAX_DISPLAY_ROWS})")
    else:
        print()
