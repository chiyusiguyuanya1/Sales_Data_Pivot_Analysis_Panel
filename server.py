import json
import os
import sqlite3
from datetime import datetime
from decimal import Decimal, InvalidOperation
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


BASE_DIR = Path(__file__).resolve().parent
DB_DIR = BASE_DIR / "database"
DB_PATH = DB_DIR / "orders.db"
FRONTEND_DIST_DIR = BASE_DIR / "frontend" / "dist"
FRONTEND_DEV_DIR = BASE_DIR / "frontend"
HOST = "127.0.0.1"
PORT = 8000

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS orders (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  order_no TEXT NOT NULL,
  city TEXT NOT NULL,
  category TEXT NOT NULL,
  salesperson TEXT NOT NULL,
  amount REAL NOT NULL,
  refund_amount REAL NOT NULL DEFAULT 0,
  is_paid INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL
);
"""

SEED_DATA = [
    ("ORD-000001", "北京", "电子", "张伟", 3200, 0, 1, "2025-01-05 10:23:00"),
    ("ORD-000002", "上海", "服装", "李娜", 860, 0, 1, "2025-01-08 14:11:00"),
    ("ORD-000003", "广州", "食品", "王芳", 420, 20, 1, "2025-01-12 09:05:00"),
    ("ORD-000004", "杭州", "家居", "赵磊", 1580, 0, 0, "2025-01-15 16:40:00"),
    ("ORD-000005", "成都", "运动", "陈静", 990, 100, 1, "2025-01-18 11:22:00"),
    ("ORD-000006", "北京", "服装", "张伟", 2100, 0, 1, "2025-02-03 13:30:00"),
    ("ORD-000007", "上海", "电子", "刘洋", 4500, 500, 1, "2025-02-07 10:00:00"),
    ("ORD-000008", "广州", "家居", "王芳", 760, 0, 0, "2025-02-11 15:18:00"),
    ("ORD-000009", "杭州", "运动", "赵磊", 1200, 0, 1, "2025-02-14 09:45:00"),
    ("ORD-000010", "成都", "电子", "陈静", 2800, 0, 1, "2025-02-20 17:05:00"),
    ("ORD-000011", "北京", "食品", "李娜", 560, 0, 1, "2025-03-02 12:00:00"),
    ("ORD-000012", "上海", "家居", "刘洋", 1940, 120, 1, "2025-03-04 18:20:00"),
    ("ORD-000013", "广州", "电子", "王芳", 5200, 0, 1, "2025-03-06 11:35:00"),
    ("ORD-000014", "杭州", "服装", "赵磊", 730, 0, 0, "2025-03-09 09:15:00"),
    ("ORD-000015", "成都", "食品", "陈静", 410, 0, 1, "2025-03-12 14:00:00"),
    ("ORD-000016", "北京", "家居", "张伟", 1260, 60, 1, "2025-03-16 16:10:00"),
    ("ORD-000017", "上海", "运动", "李娜", 1580, 0, 1, "2025-03-20 10:28:00"),
    ("ORD-000018", "广州", "服装", "刘洋", 980, 0, 1, "2025-03-24 19:45:00"),
    ("ORD-000019", "杭州", "电子", "赵磊", 3680, 300, 1, "2025-04-01 08:55:00"),
    ("ORD-000020", "成都", "家居", "陈静", 890, 0, 0, "2025-04-03 13:12:00"),
    ("ORD-000021", "北京", "运动", "张伟", 1320, 0, 1, "2025-04-07 17:40:00"),
    ("ORD-000022", "上海", "食品", "李娜", 460, 0, 1, "2025-04-10 09:20:00"),
    ("ORD-000023", "广州", "运动", "王芳", 2050, 200, 1, "2025-04-14 12:46:00"),
    ("ORD-000024", "杭州", "家居", "刘洋", 1490, 0, 1, "2025-04-16 15:30:00"),
    ("ORD-000025", "成都", "服装", "陈静", 1180, 0, 1, "2025-04-19 11:08:00"),
    ("ORD-000026", "北京", "电子", "张伟", 4380, 0, 1, "2025-04-23 10:03:00"),
    ("ORD-000027", "上海", "家居", "刘洋", 2260, 260, 1, "2025-05-02 14:55:00"),
    ("ORD-000028", "广州", "食品", "王芳", 540, 0, 0, "2025-05-04 09:37:00"),
    ("ORD-000029", "杭州", "运动", "赵磊", 1750, 0, 1, "2025-05-08 18:12:00"),
    ("ORD-000030", "成都", "电子", "陈静", 3190, 90, 1, "2025-05-11 16:22:00"),
    ("ORD-000031", "北京", "服装", "李娜", 980, 0, 0, "2025-05-15 13:48:00"),
    ("ORD-000032", "上海", "运动", "张伟", 2640, 0, 1, "2025-05-18 11:33:00"),
    ("ORD-000033", "广州", "家居", "王芳", 1680, 80, 1, "2025-05-21 10:16:00"),
    ("ORD-000034", "杭州", "食品", "赵磊", 390, 0, 1, "2025-05-24 08:42:00"),
    ("ORD-000035", "成都", "家居", "刘洋", 1420, 0, 1, "2025-05-27 17:50:00"),
    ("ORD-000036", "北京", "食品", "张伟", 620, 0, 1, "2025-06-01 09:10:00"),
]


def get_static_dir():
    return FRONTEND_DIST_DIR if FRONTEND_DIST_DIR.exists() else FRONTEND_DEV_DIR


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    DB_DIR.mkdir(parents=True, exist_ok=True)
    with get_connection() as conn:
        conn.execute(SCHEMA_SQL)
        existing_count = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
        if existing_count == 0:
            conn.executemany(
                """
                INSERT INTO orders
                (order_no, city, category, salesperson, amount, refund_amount, is_paid, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                SEED_DATA,
            )
        conn.commit()


def send_json(handler, payload, status=HTTPStatus.OK):
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(body)


def parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        return None


def parse_created_at(value):
    if not value:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def parse_decimal(value):
    if value in ("", None):
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def normalize_list_param(raw_value):
    if not raw_value:
        return []
    return [item.strip() for item in raw_value.split(",") if item.strip()]


def build_order_filters(params):
    where_clauses = []
    values = []
    errors = []

    start_date = params.get("startDate", [""])[0].strip()
    end_date = params.get("endDate", [""])[0].strip()
    category = params.get("category", [""])[0].strip()
    categories = normalize_list_param(params.get("categories", [""])[0].strip())
    cities = normalize_list_param(params.get("cities", [""])[0].strip())
    salespeople = normalize_list_param(params.get("salespeople", [""])[0].strip())
    paid_only = params.get("paidOnly", [""])[0].strip().lower()
    payment_status = params.get("paymentStatus", [""])[0].strip().lower()
    min_amount = params.get("minAmount", [""])[0].strip()
    max_amount = params.get("maxAmount", [""])[0].strip()

    parsed_start = parse_date(start_date)
    parsed_end = parse_date(end_date)
    parsed_min_amount = parse_decimal(min_amount)
    parsed_max_amount = parse_decimal(max_amount)

    if start_date and not parsed_start:
        errors.append("startDate 必须为 YYYY-MM-DD 格式")
    if end_date and not parsed_end:
        errors.append("endDate 必须为 YYYY-MM-DD 格式")
    if parsed_start and parsed_end and parsed_start > parsed_end:
        errors.append("startDate 不能晚于 endDate")

    if min_amount and parsed_min_amount is None:
        errors.append("minAmount 必须为数字")
    if max_amount and parsed_max_amount is None:
        errors.append("maxAmount 必须为数字")
    if (
        parsed_min_amount is not None
        and parsed_max_amount is not None
        and parsed_min_amount > parsed_max_amount
    ):
        errors.append("minAmount 不能大于 maxAmount")

    if parsed_start:
        where_clauses.append("date(created_at) >= date(?)")
        values.append(start_date)
    if parsed_end:
        where_clauses.append("date(created_at) <= date(?)")
        values.append(end_date)

    if cities:
        where_clauses.append(f"city IN ({','.join('?' for _ in cities)})")
        values.extend(cities)

    merged_categories = categories[:]
    if category:
        merged_categories.append(category)
    if merged_categories:
        deduped_categories = list(dict.fromkeys(merged_categories))
        where_clauses.append(f"category IN ({','.join('?' for _ in deduped_categories)})")
        values.extend(deduped_categories)

    if salespeople:
        where_clauses.append(f"salesperson IN ({','.join('?' for _ in salespeople)})")
        values.extend(salespeople)

    if parsed_min_amount is not None:
        where_clauses.append("amount >= ?")
        values.append(float(parsed_min_amount))
    if parsed_max_amount is not None:
        where_clauses.append("amount <= ?")
        values.append(float(parsed_max_amount))

    if paid_only in {"true", "1"}:
        where_clauses.append("is_paid = 1")
    elif paid_only not in {"", "false", "0"}:
        errors.append("paidOnly 只支持 true / 1 / false / 0")

    if payment_status == "paid":
        where_clauses.append("is_paid = 1")
    elif payment_status == "unpaid":
        where_clauses.append("is_paid = 0")
    elif payment_status not in {"", "all"}:
        errors.append("paymentStatus 只支持 paid / unpaid")

    return where_clauses, values, errors


def query_orders(params):
    where_clauses, values, errors = build_order_filters(params)
    if errors:
        return None, errors

    sql = """
    SELECT id, order_no, city, category, salesperson, amount, refund_amount, is_paid, created_at
    FROM orders
    """
    if where_clauses:
        sql += " WHERE " + " AND ".join(where_clauses)
    sql += " ORDER BY datetime(created_at) ASC, id ASC"

    with get_connection() as conn:
        rows = conn.execute(sql, values).fetchall()
        return [dict(row) for row in rows], None


def query_filter_options():
    with get_connection() as conn:
        cities = [row[0] for row in conn.execute("SELECT DISTINCT city FROM orders ORDER BY city ASC")]
        categories = [
            row[0]
            for row in conn.execute("SELECT DISTINCT category FROM orders ORDER BY category ASC")
        ]
        salespeople = [
            row[0]
            for row in conn.execute("SELECT DISTINCT salesperson FROM orders ORDER BY salesperson ASC")
        ]
        return {
            "cities": cities,
            "categories": categories,
            "salespeople": salespeople,
        }


def validate_order_payload(payload):
    errors = []

    if not isinstance(payload, dict):
        return None, ["请求体必须为 JSON 对象"]

    normalized = {}
    for field in ["order_no", "city", "category", "salesperson", "created_at"]:
        value = str(payload.get(field, "")).strip()
        if not value:
            errors.append(f"{field} 不能为空")
        normalized[field] = value

    amount = parse_decimal(payload.get("amount"))
    refund_amount = parse_decimal(payload.get("refund_amount", 0))
    is_paid = payload.get("is_paid", 0)
    parsed_created_at = parse_created_at(normalized["created_at"])

    if amount is None or amount < 0:
        errors.append("amount 必须为大于等于 0 的数字")
    if refund_amount is None or refund_amount < 0:
        errors.append("refund_amount 必须为大于等于 0 的数字")
    if amount is not None and refund_amount is not None and refund_amount > amount:
        errors.append("refund_amount 不能大于 amount")

    if str(is_paid) not in {"0", "1"}:
        errors.append("is_paid 只支持 0 或 1")
    if normalized["created_at"] and not parsed_created_at:
        errors.append("created_at 必须为 YYYY-MM-DD 或 YYYY-MM-DD HH:mm:ss 格式")

    normalized["amount"] = float(amount) if amount is not None else 0
    normalized["refund_amount"] = float(refund_amount) if refund_amount is not None else 0
    normalized["is_paid"] = int(is_paid) if str(is_paid) in {"0", "1"} else 0
    normalized["created_at"] = (
        parsed_created_at.strftime("%Y-%m-%d %H:%M:%S")
        if parsed_created_at
        else normalized["created_at"]
    )

    if errors:
        return None, errors
    return normalized, None


def insert_order(payload):
    normalized, errors = validate_order_payload(payload)
    if errors:
        return None, errors

    with get_connection() as conn:
        existing = conn.execute(
            "SELECT id FROM orders WHERE order_no = ?",
            (normalized["order_no"],),
        ).fetchone()
        if existing:
            return None, ["order_no 已存在"]

        cursor = conn.execute(
            """
            INSERT INTO orders
            (order_no, city, category, salesperson, amount, refund_amount, is_paid, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                normalized["order_no"],
                normalized["city"],
                normalized["category"],
                normalized["salesperson"],
                normalized["amount"],
                normalized["refund_amount"],
                normalized["is_paid"],
                normalized["created_at"],
            ),
        )
        conn.commit()

        created = conn.execute(
            """
            SELECT id, order_no, city, category, salesperson, amount, refund_amount, is_paid, created_at
            FROM orders
            WHERE id = ?
            """,
            (cursor.lastrowid,),
        ).fetchone()

        return dict(created), None


class SalesDashboardHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(get_static_dir()), **kwargs)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/api/orders":
            params = parse_qs(parsed.query, keep_blank_values=True)
            data, errors = query_orders(params)
            if errors:
                send_json(
                    self,
                    {"code": 1, "message": "；".join(errors), "data": [], "total": 0},
                    HTTPStatus.BAD_REQUEST,
                )
                return

            send_json(self, {"code": 0, "data": data, "total": len(data)})
            return

        if parsed.path == "/api/meta":
            send_json(self, {"code": 0, "data": query_filter_options()})
            return

        if parsed.path == "/" or not Path(parsed.path.lstrip("/")).suffix:
            self.path = "/index.html"

        super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)

        if parsed.path != "/api/orders":
            send_json(self, {"code": 1, "message": "接口不存在"}, HTTPStatus.NOT_FOUND)
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            send_json(self, {"code": 1, "message": "Content-Length 非法"}, HTTPStatus.BAD_REQUEST)
            return

        try:
            raw_body = self.rfile.read(content_length) if content_length else b"{}"
            payload = json.loads(raw_body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            send_json(self, {"code": 1, "message": "请求体必须为合法 JSON"}, HTTPStatus.BAD_REQUEST)
            return

        created, errors = insert_order(payload)
        if errors:
            send_json(self, {"code": 1, "message": "；".join(errors)}, HTTPStatus.BAD_REQUEST)
            return

        send_json(self, {"code": 0, "data": created}, HTTPStatus.CREATED)

    def log_message(self, format, *args):
        return


def main():
    initialize_database()
    port = int(os.environ.get("PORT", PORT))
    server = ThreadingHTTPServer((HOST, port), SalesDashboardHandler)
    print(f"Server running at http://{HOST}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
