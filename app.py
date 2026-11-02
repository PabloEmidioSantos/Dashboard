from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse
import json
import mimetypes
import secrets
import threading

BASE = Path(__file__).resolve().parent
STATIC = BASE / "static"
DB = BASE / "database.json"
sessions = {}
session_lock = threading.Lock()

if not DB.exists():
    DB.write_text(json.dumps({"users": []}, ensure_ascii=False, indent=2), encoding="utf-8")


def read_db():
    with DB.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_db(data):
    temporary = DB.with_suffix(".tmp")
    with temporary.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    temporary.replace(DB)


def money(value):
    try:
        return max(0, round(float(value or 0), 2))
    except (TypeError, ValueError):
        return 0.0


class DashboardHandler(BaseHTTPRequestHandler):
    def send_json(self, status, payload):
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def body(self):
        length = int(self.headers.get("Content-Length", 0))
        try:
            return json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            return {}

    def current_user(self, data):
        token = self.headers.get("Authorization", "").replace("Bearer ", "")
        with session_lock:
            return sessions.get(token)

    def do_GET(self):
        path = urlparse(self.path).path
        if path.startswith("/api/"):
            self.api_get(path)
            return
        if path == "/":
            path = "/index.html"
        file_path = (STATIC / path.lstrip("/")).resolve()
        if STATIC not in file_path.parents and file_path != STATIC:
            self.send_error(403)
            return
        if not file_path.is_file():
            self.send_error(404)
            return
        content = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mimetypes.guess_type(file_path.name)[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def api_get(self, path):
        if path == "/api/dashboard":
            data = read_db()
            email = self.current_user(data)
            if not email:
                self.send_json(401, {"error": "Não autorizado"})
                return
            user = next((item for item in data["users"] if item["email"] == email), None)
            if not user:
                self.send_json(404, {"error": "Usuário não encontrado"})
                return
            income = money(user["finances"].get("income"))
            mandatory = {key: money(value) for key, value in user["finances"].get("mandatory", {}).items()}
            pending = [item | {"amount": money(item["amount"])} for item in user["finances"].get("pending", [])]
            expenses = sum(mandatory.values()) + sum(item["amount"] for item in pending)
            user_data = {
                "name": user["name"], "email": user["email"], "income": income,
                "mandatory": mandatory, "pending": pending,
                "expenses": expenses, "balance": income - expenses
            }
            self.send_json(200, user_data)
            return
        self.send_json(404, {"error": "Rota não encontrada"})

    def do_POST(self):
        path = urlparse(self.path).path
        payload = self.body()

        if path == "/api/register":
            name = str(payload.get("name", "")).strip()
            email = str(payload.get("email", "")).strip().lower()
            password = str(payload.get("password", ""))
            if not name or not email or not password:
                self.send_json(400, {"error": "Preencha todos os campos"})
                return
            data = read_db()
            if any(user["email"] == email for user in data["users"]):
                self.send_json(409, {"error": "Este e-mail já está cadastrado"})
                return
            data["users"].append({"name": name, "email": email, "password": password, "finances": {"income": 0, "mandatory": {"water": 0, "electricity": 0, "internet": 0}, "pending": []}})
            write_db(data)
            self.send_json(201, self.create_session(email))
            return

        if path == "/api/login":
            email = str(payload.get("email", "")).strip().lower()
            password = str(payload.get("password", ""))
            data = read_db()
            user = next((item for item in data["users"] if item["email"] == email and item["password"] == password), None)
            if not user:
                self.send_json(401, {"error": "E-mail ou senha inválidos"})
                return
            self.send_json(200, self.create_session(email))
            return

        if path == "/api/finances":
            data = read_db()
            email = self.current_user(data)
            if not email:
                self.send_json(401, {"error": "Não autorizado"})
                return
            user = next((item for item in data["users"] if item["email"] == email), None)
            if not user:
                self.send_json(404, {"error": "Usuário não encontrado"})
                return
            user["finances"] = {
                "income": money(payload.get("income")),
                "mandatory": {
                    "water": money(payload.get("water")),
                    "electricity": money(payload.get("electricity")),
                    "internet": money(payload.get("internet"))
                },
                "pending": payload.get("pending", [])
            }
            write_db(data)
            self.send_json(200, {"ok": True})
            return

        self.send_json(404, {"error": "Rota não encontrada"})

    def create_session(self, email):
        token = secrets.token_urlsafe(32)
        with session_lock:
            sessions[token] = email
        return {"token": token, "email": email}

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", 5469), DashboardHandler)
    print("Dashboard disponível em http://localhost:5469")
    server.serve_forever()
