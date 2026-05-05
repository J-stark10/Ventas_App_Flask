from flask import Flask, request, render_template, redirect
import sqlite3

app = Flask(__name__)

# ─────────────────────────────────────────
# CREACIÓN DE BASE DE DATOS Y TABLAS
# ─────────────────────────────────────────
def init_database():
    conn = sqlite3.connect("ventas.db")

    # Tabla clientes
    conn.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id      INTEGER PRIMARY KEY,
            nombre  TEXT NOT NULL
        )
    """)

    # Tabla productos
    conn.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id      INTEGER PRIMARY KEY,
            nombre  TEXT NOT NULL
        )
    """)

    # Tabla ventas — usa claves foráneas para relacionarse
    # con clientes y productos
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id          INTEGER PRIMARY KEY,
            cliente_id  INTEGER NOT NULL,
            producto_id INTEGER NOT NULL,
            cantidad    INTEGER NOT NULL,
            FOREIGN KEY (cliente_id)  REFERENCES clientes(id),
            FOREIGN KEY (producto_id) REFERENCES productos(id)
        )
    """)

    # Datos de ejemplo para probar la app desde el inicio
    conn.execute("INSERT OR IGNORE INTO clientes (id, nombre) VALUES (1, 'María García')")
    conn.execute("INSERT OR IGNORE INTO clientes (id, nombre) VALUES (2, 'Carlos López')")
    conn.execute("INSERT OR IGNORE INTO clientes (id, nombre) VALUES (3, 'Ana Martínez')")

    conn.execute("INSERT OR IGNORE INTO productos (id, nombre) VALUES (1, 'Laptop')")
    conn.execute("INSERT OR IGNORE INTO productos (id, nombre) VALUES (2, 'Mouse Inalámbrico')")
    conn.execute("INSERT OR IGNORE INTO productos (id, nombre) VALUES (3, 'Teclado Mecánico')")

    conn.execute("INSERT OR IGNORE INTO ventas (id, cliente_id, producto_id, cantidad) VALUES (1, 1, 1, 2)")
    conn.execute("INSERT OR IGNORE INTO ventas (id, cliente_id, producto_id, cantidad) VALUES (2, 2, 3, 1)")

    conn.commit()
    conn.close()

# Ejecutar al iniciar la aplicación
init_database()


# ─────────────────────────────────────────
# INDEX — Listar todas las ventas
# ─────────────────────────────────────────
@app.route("/")
def index():
    conn = sqlite3.connect("ventas.db")
    conn.row_factory = sqlite3.Row  # Permite acceder a columnas por nombre
    cursor = conn.cursor()

    # JOIN: combinamos las 3 tablas para mostrar nombres en vez de IDs
    # ventas.cliente_id  → busca en clientes  → trae clientes.nombre
    # ventas.producto_id → busca en productos → trae productos.nombre
    cursor.execute("""
        SELECT
            ventas.id,
            clientes.nombre  AS cliente,
            productos.nombre AS producto,
            ventas.cantidad
        FROM ventas
        JOIN clientes  ON ventas.cliente_id  = clientes.id
        JOIN productos ON ventas.producto_id = productos.id
        ORDER BY ventas.id DESC
    """)
    ventas = cursor.fetchall()
    conn.close()

    return render_template("index.html", ventas=ventas)


# ─────────────────────────────────────────
# CREATE — Mostrar formulario
# ─────────────────────────────────────────
@app.route("/create")
def create():
    conn = sqlite3.connect("ventas.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Cargamos clientes y productos para los <select>
    cursor.execute("SELECT * FROM clientes ORDER BY nombre")
    clientes = cursor.fetchall()

    cursor.execute("SELECT * FROM productos ORDER BY nombre")
    productos = cursor.fetchall()

    conn.close()
    return render_template("create.html", clientes=clientes, productos=productos)


# ─────────────────────────────────────────
# SAVE — Guardar nueva venta (POST)
# ─────────────────────────────────────────
@app.route("/save", methods=["POST"])
def save():
    cliente_id  = request.form["cliente_id"]
    producto_id = request.form["producto_id"]
    cantidad    = request.form["cantidad"]

    conn = sqlite3.connect("ventas.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO ventas (cliente_id, producto_id, cantidad)
        VALUES (?, ?, ?)
    """, (cliente_id, producto_id, cantidad))

    conn.commit()
    conn.close()
    return redirect("/")


# ─────────────────────────────────────────
# EDIT — Mostrar formulario con datos cargados
# ─────────────────────────────────────────
@app.route("/edit/<int:id>")
def edit(id):
    conn = sqlite3.connect("ventas.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Buscamos la venta a editar
    cursor.execute("SELECT * FROM ventas WHERE id = ?", (id,))
    venta = cursor.fetchone()

    # Cargamos las listas para los <select>
    cursor.execute("SELECT * FROM clientes ORDER BY nombre")
    clientes = cursor.fetchall()

    cursor.execute("SELECT * FROM productos ORDER BY nombre")
    productos = cursor.fetchall()

    conn.close()
    return render_template("edit.html", venta=venta, clientes=clientes, productos=productos)


# ─────────────────────────────────────────
# UPDATE — Actualizar venta (POST)
# ─────────────────────────────────────────
@app.route("/update", methods=["POST"])
def update():
    id          = request.form["id"]
    cliente_id  = request.form["cliente_id"]
    producto_id = request.form["producto_id"]
    cantidad    = request.form["cantidad"]

    conn = sqlite3.connect("ventas.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE ventas
        SET cliente_id = ?, producto_id = ?, cantidad = ?
        WHERE id = ?
    """, (cliente_id, producto_id, cantidad, id))

    conn.commit()
    conn.close()
    return redirect("/")


# ─────────────────────────────────────────
# DELETE — Eliminar venta
# ─────────────────────────────────────────
@app.route("/delete/<int:id>")
def delete(id):
    conn = sqlite3.connect("ventas.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM ventas WHERE id = ?", (id,))

    conn.commit()
    conn.close()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
