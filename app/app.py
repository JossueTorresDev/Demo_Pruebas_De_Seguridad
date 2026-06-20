"""
Mini aplicación web - Sistema de Maestro (Gestión de Estudiantes)
Backend: Python Flask
Propósito: Demo para pruebas funcionales y de seguridad
"""

from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
import sqlite3
import os
import secrets

app = Flask(__name__)
# Clave secreta segura para sesiones
app.secret_key = secrets.token_hex(32)

DB_PATH = os.path.join(os.path.dirname(__file__), "estudiantes.db")


# ─── Base de datos ────────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS estudiantes (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre  TEXT    NOT NULL,
                carnet  TEXT    NOT NULL UNIQUE,
                nota    REAL    NOT NULL DEFAULT 0
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT    NOT NULL UNIQUE,
                password TEXT    NOT NULL
            )
        """)
        # Usuario de demo: admin / admin123
        try:
            import hashlib
            pw_hash = hashlib.sha256("admin123".encode()).hexdigest()
            conn.execute(
                "INSERT INTO usuarios (username, password) VALUES (?, ?)",
                ("admin", pw_hash)
            )
        except sqlite3.IntegrityError:
            pass  # ya existe
        conn.commit()


# ─── Autenticación ────────────────────────────────────────────────────────────

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        import hashlib
        pw_hash = hashlib.sha256(password.encode()).hexdigest()

        # ✅ Consulta parametrizada — previene SQL Injection
        with get_db() as conn:
            user = conn.execute(
                "SELECT * FROM usuarios WHERE username = ? AND password = ?",
                (username, pw_hash)
            ).fetchone()

        if user:
            session["user"] = username
            return redirect(url_for("index"))
        else:
            error = "Credenciales incorrectas."
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ─── Vistas principales ───────────────────────────────────────────────────────

@app.route("/")
@login_required
def index():
    with get_db() as conn:
        estudiantes = conn.execute("SELECT * FROM estudiantes ORDER BY id DESC").fetchall()
    return render_template("index.html", estudiantes=estudiantes, user=session["user"])


@app.route("/agregar", methods=["GET", "POST"])
@login_required
def agregar():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        carnet = request.form.get("carnet", "").strip()
        nota   = request.form.get("nota", "0")

        # Validación básica
        if not nombre or not carnet:
            flash("Nombre y carnet son obligatorios.", "danger")
            return redirect(url_for("agregar"))

        try:
            nota = float(nota)
            if not (0 <= nota <= 10):
                raise ValueError
        except ValueError:
            flash("La nota debe ser un número entre 0 y 10.", "danger")
            return redirect(url_for("agregar"))

        try:
            with get_db() as conn:
                conn.execute(
                    "INSERT INTO estudiantes (nombre, carnet, nota) VALUES (?, ?, ?)",
                    (nombre, carnet, nota)
                )
                conn.commit()
            flash(f"Estudiante '{nombre}' agregado correctamente.", "success")
        except sqlite3.IntegrityError:
            flash("El carnet ya existe.", "danger")

        return redirect(url_for("index"))

    return render_template("agregar.html", user=session["user"])


@app.route("/eliminar/<int:id>", methods=["POST"])
@login_required
def eliminar(id):
    with get_db() as conn:
        conn.execute("DELETE FROM estudiantes WHERE id = ?", (id,))
        conn.commit()
    flash("Estudiante eliminado.", "info")
    return redirect(url_for("index"))


@app.route("/buscar")
@login_required
def buscar():
    q = request.args.get("q", "").strip()
    resultados = []
    if q:
        # ✅ Consulta parametrizada con LIKE — no concatenación directa
        with get_db() as conn:
            resultados = conn.execute(
                "SELECT * FROM estudiantes WHERE nombre LIKE ? OR carnet LIKE ?",
                (f"%{q}%", f"%{q}%")
            ).fetchall()
    return render_template("buscar.html", resultados=resultados, q=q, user=session["user"])


# ─── API JSON (para pruebas) ──────────────────────────────────────────────────

@app.route("/api/estudiantes")
@login_required
def api_estudiantes():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM estudiantes").fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/buscar")
@login_required
def api_buscar():
    q = request.args.get("q", "").strip()
    resultados = []
    if q:
        with get_db() as conn:
            resultados = conn.execute(
                "SELECT * FROM estudiantes WHERE nombre LIKE ? OR carnet LIKE ?",
                (f"%{q}%", f"%{q}%")
            ).fetchall()
    return jsonify([dict(r) for r in resultados])


# ─── Arranque ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    # debug=False en producción
    app.run(host="0.0.0.0", port=5000, debug=True)
