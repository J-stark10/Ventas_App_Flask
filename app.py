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
            nombre  TEXT NOT NULL,
            precio  REAL NOT NULL DEFAULT 0.0
        )
    """)

    # 🔥 Tabla ventas ahora con PRECIO
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id          INTEGER PRIMARY KEY,
            cliente_id  INTEGER NOT NULL,
            producto_id INTEGER NOT NULL,
            cantidad    INTEGER NOT NULL,
            precio      REAL NOT NULL,
            FOREIGN KEY (cliente_id)  REFERENCES clientes(id),
            FOREIGN KEY (producto_id) REFERENCES productos(id)
        )
    """)

    # Datos de ejemplo
    conn.execute("INSERT OR IGNORE INTO clientes (id, nombre) VALUES (1, 'María García')")
    conn.execute("INSERT OR IGNORE INTO clientes (id, nombre) VALUES (2, 'Carlos López')")
    conn.execute("INSERT OR IGNORE INTO clientes (id, nombre) VALUES (3, 'Ana Martínez')")

    conn.execute("INSERT OR IGNORE INTO productos (id, nombre, precio) VALUES (1, 'Laptop', 1200)")
    conn.execute("INSERT OR IGNORE INTO productos (id, nombre, precio) VALUES (2, 'Mouse Inalámbrico', 25)")
    conn.execute("INSERT OR IGNORE INTO productos (id, nombre, precio) VALUES (3, 'Teclado Mecánico', 80)")

    conn.commit()
    conn.close()

init_database()

# ─────────────────────────────────────────
# INDEX
# ─────────────────────────────────────────
@app.route("/")
def index():
    conn = sqlite3.connect("ventas.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            ventas.id,
            clientes.nombre  AS cliente,
            productos.nombre AS producto,
            ventas.precio,
            ventas.cantidad,
            (ventas.cantidad * ventas.precio) AS total
        FROM ventas
        JOIN clientes  ON ventas.cliente_id  = clientes.id
        JOIN productos ON ventas.producto_id = productos.id
        ORDER BY ventas.id DESC
    """)

    ventas = cursor.fetchall()
    conn.close()

    return render_template("index.html", ventas=ventas)

# ─────────────────────────────────────────
# CREATE
# ─────────────────────────────────────────
@app.route("/create")
def create():
    conn = sqlite3.connect("ventas.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM clientes ORDER BY nombre")
    clientes = cursor.fetchall()

    cursor.execute("SELECT * FROM productos ORDER BY nombre")
    productos = cursor.fetchall()

    conn.close()
    return render_template("create.html", clientes=clientes, productos=productos)

# ─────────────────────────────────────────
# SAVE
# ─────────────────────────────────────────
@app.route("/save", methods=["POST"])
def save():
    cliente_id  = request.form["cliente_id"]
    producto_id = request.form["producto_id"]
    cantidad    = request.form["cantidad"]

    conn = sqlite3.connect("ventas.db")
    cursor = conn.cursor()

    # 🔥 Obtener precio del producto
    cursor.execute("SELECT precio FROM productos WHERE id = ?", (producto_id,))
    precio = cursor.fetchone()[0]

    # 🔥 Guardar precio en la venta
    cursor.execute("""
        INSERT INTO ventas (cliente_id, producto_id, cantidad, precio)
        VALUES (?, ?, ?, ?)
    """, (cliente_id, producto_id, cantidad, precio))

    conn.commit()
    conn.close()
    return redirect("/")

# ─────────────────────────────────────────
# EDIT
# ─────────────────────────────────────────
@app.route("/edit/<int:id>")
def edit(id):
    conn = sqlite3.connect("ventas.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM ventas WHERE id = ?", (id,))
    venta = cursor.fetchone()

    cursor.execute("SELECT * FROM clientes ORDER BY nombre")
    clientes = cursor.fetchall()

    cursor.execute("SELECT * FROM productos ORDER BY nombre")
    productos = cursor.fetchall()

    conn.close()
    return render_template("edit.html", venta=venta, clientes=clientes, productos=productos)

# ─────────────────────────────────────────
# UPDATE
# ─────────────────────────────────────────
@app.route("/update", methods=["POST"])
def update():
    id          = request.form["id"]
    cliente_id  = request.form["cliente_id"]
    producto_id = request.form["producto_id"]
    cantidad    = request.form["cantidad"]

    conn = sqlite3.connect("ventas.db")
    cursor = conn.cursor()

    # 🔥 Obtener precio actualizado
    cursor.execute("SELECT precio FROM productos WHERE id = ?", (producto_id,))
    precio = cursor.fetchone()[0]

    cursor.execute("""
        UPDATE ventas
        SET cliente_id = ?, producto_id = ?, cantidad = ?, precio = ?
        WHERE id = ?
    """, (cliente_id, producto_id, cantidad, precio, id))

    conn.commit()
    conn.close()
    return redirect("/")

# ─────────────────────────────────────────
# DELETE
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