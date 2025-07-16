# app_flask_inventario.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import mysql.connector
import os
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = 'clave_secreta_segura'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DB_CONFIG = {
    'host': 'localhost',
    'user': 'inventario_user',
    'password': 'Sk1llN3t.2025',
    'database': 'inventario_uniformes'
}

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            session['user'] = username
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        flash("Credenciales inválidas", "error")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    conn.close()
    return render_template('dashboard.html', productos=productos)

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        data = (
            request.form['nombre'],
            request.form['colegio'],
            request.form['genero'],
            request.form['talla'],
            int(request.form['cantidad']),
            float(request.form['precio']),
            id
        )
        cursor.execute(
            "UPDATE productos SET nombre=%s, colegio=%s, genero=%s, talla=%s, cantidad=%s, precio=%s WHERE id=%s",
            data,
        )
        conn.commit()
        conn.close()
        flash("Producto actualizado")
        return redirect(url_for('dashboard'))
    cursor.execute("SELECT * FROM productos WHERE id=%s", (id,))
    producto = cursor.fetchone()
    conn.close()
    return render_template('editar.html', producto=producto)

@app.route('/venta/<int:id>', methods=['POST'])
def venta(id):
    if 'user' not in session:
        return redirect(url_for('login'))
    cantidad = int(request.form['cantidad'])
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT cantidad FROM productos WHERE id=%s", (id,))
    stock = cursor.fetchone()[0]
    if stock >= cantidad:
        cursor.execute("UPDATE productos SET cantidad=cantidad-%s WHERE id=%s", (cantidad, id))
        cursor.execute("INSERT INTO ventas(producto_id, usuario, cantidad, fecha) VALUES (%s, %s, %s, %s)", 
                       (id, session['user'], cantidad, datetime.now()))
        conn.commit()
        flash("Venta registrada")
    else:
        flash("Stock insuficiente", "error")
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/usuarios')
def gestionar_usuarios():
    if session.get('role') != 'admin':
        flash("Acceso denegado", "error")
        return redirect(url_for('dashboard'))
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()
    conn.close()
    return render_template('usuarios.html', usuarios=usuarios)

@app.route('/usuarios/crear', methods=['POST'])
def crear_usuario():
    if session.get('role') != 'admin':
        return redirect(url_for('dashboard'))
    username = request.form['username']
    password = request.form['password']
    role = request.form['role']
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO usuarios(username, password, role) VALUES (%s, %s, %s)", (username, password, role))
    conn.commit()
    conn.close()
    flash("Usuario creado")
    return redirect(url_for('gestionar_usuarios'))

@app.route('/usuarios/borrar/<int:id>', methods=['POST'])
def eliminar_usuario(id):
    if session.get('role') != 'admin':
        return redirect(url_for('dashboard'))
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id=%s", (id,))
    conn.commit()
    conn.close()
    flash("Usuario eliminado")
    return redirect(url_for('gestionar_usuarios'))

@app.route('/eliminar/<int:id>', methods=['POST'])
def eliminar_producto(id):
    if session.get('role') != 'admin':
        return redirect(url_for('dashboard'))
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ventas WHERE producto_id=%s", (id,))
    cursor.execute("DELETE FROM productos WHERE id=%s", (id,))
    conn.commit()
    conn.close()
    flash("Producto eliminado")
    return redirect(url_for('dashboard'))

@app.route('/ventas')
def ver_ventas():
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT v.id, p.nombre, v.usuario, v.cantidad, v.fecha
        FROM ventas v
        JOIN productos p ON v.producto_id = p.id
        ORDER BY v.fecha DESC
    """)
    ventas = cursor.fetchall()
    conn.close()
    return render_template('ventas.html', ventas=ventas)

@app.route('/reportes')
def reporte_ventas():
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT DATE(fecha) AS dia, SUM(v.cantidad * p.precio) AS total
        FROM ventas v
        JOIN productos p ON v.producto_id = p.id
        GROUP BY dia ORDER BY dia DESC
    """)
    diarios = cursor.fetchall()
    cursor.execute("""
        SELECT YEAR(fecha) AS year, WEEK(fecha) AS semana, SUM(v.cantidad * p.precio) AS total
        FROM ventas v
        JOIN productos p ON v.producto_id = p.id
        GROUP BY year, semana ORDER BY year DESC, semana DESC
    """)
    semanal = cursor.fetchall()
    cursor.execute("""
        SELECT DATE_FORMAT(fecha, '%Y-%m') AS mes, SUM(v.cantidad * p.precio) AS total
        FROM ventas v
        JOIN productos p ON v.producto_id = p.id
        GROUP BY mes ORDER BY mes DESC
    """)
    mensual = cursor.fetchall()
    conn.close()
    return render_template('reportes.html', diarios=diarios, semanal=semanal, mensual=mensual)

@app.route('/agregar', methods=['GET', 'POST'])
def agregar_producto():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        nombre = request.form['nombre']
        colegio = request.form['colegio']
        genero = request.form['genero']
        talla = request.form['talla']
        cantidad = int(request.form['cantidad'])
        precio = float(request.form['precio'])

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO productos (nombre, colegio, genero, talla, cantidad, precio)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (nombre, colegio, genero, talla, cantidad, precio))
        conn.commit()
        conn.close()
        flash("Producto agregado correctamente")
        return redirect(url_for('dashboard'))

    return render_template("agregar_producto.html")

@app.route('/entrada', methods=['GET', 'POST'])
def entrada_producto():
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()

    if request.method == 'POST':
        producto_id = int(request.form['producto_id'])
        cantidad = int(request.form['cantidad'])
        cursor.execute("UPDATE productos SET cantidad = cantidad + %s WHERE id = %s", (cantidad, producto_id))
        conn.commit()
        conn.close()
        flash("Entrada registrada")
        return redirect(url_for('dashboard'))

    conn.close()
    return render_template("entrada_producto.html", productos=productos)

@app.route('/venta', methods=['GET', 'POST'])
def nueva_venta():
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    cursor.execute("SELECT DISTINCT colegio FROM productos")
    colegios = [row['colegio'] for row in cursor.fetchall()]

    if request.method == 'POST':
        items = json.loads(request.form['items']) if request.form.get('items') else []
        ventas_detalle = []
        total = 0
        for item in items:
            producto_id = int(item['id'])
            cantidad = int(item['cantidad'])
            cursor.execute(
                "SELECT nombre, colegio, cantidad, precio FROM productos WHERE id=%s",
                (producto_id,))
            prod = cursor.fetchone()
            if not prod or prod['cantidad'] < cantidad:
                flash("Stock insuficiente o producto no encontrado", "error")
                conn.close()
                return redirect(url_for('nueva_venta'))

            subtotal = prod['precio'] * cantidad
            ventas_detalle.append({
                'nombre': prod['nombre'],
                'colegio': prod['colegio'],
                'cantidad': cantidad,
                'precio': prod['precio'],
                'subtotal': subtotal
            })
            total += subtotal

            cursor.execute(
                "UPDATE productos SET cantidad = cantidad - %s WHERE id = %s",
                (cantidad, producto_id))
            cursor.execute(
                "INSERT INTO ventas(producto_id, usuario, cantidad, fecha) VALUES (%s, %s, %s, %s)",
                (producto_id, session['user'], cantidad, datetime.now()))

        conn.commit()
        conn.close()
        return render_template("recibo_venta.html", ventas=ventas_detalle, total=total)

    conn.close()
    return render_template("nueva_venta.html", productos=productos, colegios=colegios)

# --- CRUD Colegios ---

@app.route('/colegios')
def listar_colegios():
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM colegios")
    colegios = cursor.fetchall()
    conn.close()
    return render_template('colegios.html', colegios=colegios)


@app.route('/colegios/crear', methods=['POST'])
def crear_colegio():
    if 'user' not in session:
        return redirect(url_for('login'))
    nombre = request.form['nombre']
    direccion = request.form['direccion']
    telefono = request.form['telefono']
    contacto = request.form['contacto']
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO colegios(nombre, direccion, telefono, contacto) VALUES (%s, %s, %s, %s)",
        (nombre, direccion, telefono, contacto))
    conn.commit()
    conn.close()
    flash('Colegio creado correctamente')
    return redirect(url_for('listar_colegios'))


@app.route('/colegios/editar/<int:id>', methods=['GET', 'POST'])
def editar_colegio(id):
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        nombre = request.form['nombre']
        direccion = request.form['direccion']
        telefono = request.form['telefono']
        contacto = request.form['contacto']
        cursor.execute(
            "UPDATE colegios SET nombre=%s, direccion=%s, telefono=%s, contacto=%s WHERE id=%s",
            (nombre, direccion, telefono, contacto, id))
        conn.commit()
        conn.close()
        flash('Colegio actualizado')
        return redirect(url_for('listar_colegios'))
    cursor.execute("SELECT * FROM colegios WHERE id=%s", (id,))
    colegio = cursor.fetchone()
    conn.close()
    return render_template('editar_colegio.html', colegio=colegio)


@app.route('/colegios/borrar/<int:id>', methods=['POST'])
def eliminar_colegio(id):
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM colegios WHERE id=%s", (id,))
    conn.commit()
    conn.close()
    flash('Colegio eliminado')
    return redirect(url_for('listar_colegios'))


# --- CRUD Clientes ---

@app.route('/clientes')
def listar_clientes():
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM clientes")
    clientes = cursor.fetchall()
    conn.close()
    return render_template('clientes.html', clientes=clientes)


@app.route('/clientes/crear', methods=['POST'])
def crear_cliente():
    if 'user' not in session:
        return redirect(url_for('login'))
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    cedula = request.form['cedula']
    telefono = request.form.get('telefono')
    email = request.form.get('email')
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO clientes(nombre, apellido, cedula, telefono, email) VALUES (%s, %s, %s, %s, %s)",
        (nombre, apellido, cedula, telefono, email))
    conn.commit()
    conn.close()
    flash('Cliente creado correctamente')
    return redirect(url_for('listar_clientes'))


@app.route('/clientes/editar/<int:id>', methods=['GET', 'POST'])
def editar_cliente(id):
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        cedula = request.form['cedula']
        telefono = request.form.get('telefono')
        email = request.form.get('email')
        cursor.execute(
            """UPDATE clientes SET nombre=%s, apellido=%s, cedula=%s, telefono=%s, email=%s WHERE id=%s""",
            (nombre, apellido, cedula, telefono, email, id))
        conn.commit()
        conn.close()
        flash('Cliente actualizado')
        return redirect(url_for('listar_clientes'))
    cursor.execute("SELECT * FROM clientes WHERE id=%s", (id,))
    cliente = cursor.fetchone()
    conn.close()
    return render_template('editar_cliente.html', cliente=cliente)


@app.route('/clientes/borrar/<int:id>', methods=['POST'])
def eliminar_cliente(id):
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clientes WHERE id=%s", (id,))
    conn.commit()
    conn.close()
    flash('Cliente eliminado')
    return redirect(url_for('listar_clientes'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
