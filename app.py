from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import os
import hashlib
import uuid
from datetime import datetime
import requests
import json

app = Flask(__name__)
app.secret_key = 'happypet_secret_key_2024'

DB_PATH = 'petshop.db'

# ─── Transbank Webpay (Integración Mode - Credenciales de prueba) ───
TRANSBANK_API_URL = "https://webpay3gint.transbank.cl/rswebpaytransaction/api/webpay/v1.2/transactions"
TRANSBANK_COMMERCE_CODE = "597055555532"
TRANSBANK_API_KEY = "579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C"

# ─── Database Init ───────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        nombre TEXT,
        rol TEXT DEFAULT 'admin',
        creado_en TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        descripcion TEXT,
        precio REAL NOT NULL,
        stock INTEGER DEFAULT 0,
        categoria TEXT,
        tipo_mascota TEXT,
        imagen TEXT,
        activo INTEGER DEFAULT 1,
        creado_en TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS ventas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero_venta TEXT UNIQUE,
        cliente_nombre TEXT,
        cliente_email TEXT,
        total REAL,
        estado TEXT DEFAULT 'pendiente',
        metodo_pago TEXT DEFAULT 'webpay',
        token_transbank TEXT,
        creado_en TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS detalle_venta (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        venta_id INTEGER,
        producto_id INTEGER,
        cantidad INTEGER,
        precio_unitario REAL,
        subtotal REAL,
        FOREIGN KEY(venta_id) REFERENCES ventas(id),
        FOREIGN KEY(producto_id) REFERENCES productos(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        email TEXT UNIQUE,
        telefono TEXT,
        tipo_mascota TEXT,
        creado_en TEXT
    )''')

    # Default admin user
    pw = hashlib.sha256('admin123'.encode()).hexdigest()
    c.execute("INSERT OR IGNORE INTO usuarios (username, password, nombre, rol, creado_en) VALUES (?,?,?,?,?)",
              ('admin', pw, 'Administrador', 'admin', datetime.now().isoformat()))

    # Sample products
    productos_demo = [
        ('Alimento Premium Gato Adulto', 'Comida balanceada para gatos adultos 3kg', 18990, 50, 'Alimentos', 'Gato', '🐱'),
        ('Alimento Cachorro Royal', 'Croquetas para cachorros hasta 1 año 4kg', 22990, 35, 'Alimentos', 'Perro', '🐶'),
        ('Arena Sanitaria Premium', 'Arena aglomerante sin polvo 10kg', 9990, 80, 'Higiene', 'Gato', '🐱'),
        ('Collar Ajustable Perro', 'Collar de nylon reflectante talla M', 4990, 100, 'Accesorios', 'Perro', '🐶'),
        ('Rascador Torre Gato', 'Torre rascador con plataformas y juguetes', 34990, 15, 'Juguetes', 'Gato', '🐱'),
        ('Pelota Interactiva', 'Pelota con sonido y luz para perros', 7990, 60, 'Juguetes', 'Perro', '🐶'),
        ('Transportadora Plástica', 'Transportadora rígida para mascotas medianas', 29990, 20, 'Transporte', 'Ambos', '🐾'),
        ('Antipulgas Spot-On Gato', 'Tratamiento antipulgas mensual para gatos', 12990, 45, 'Salud', 'Gato', '🐱'),
        ('Shampoo Perro Neutro', 'Shampoo hipoalergénico para perros 500ml', 8990, 40, 'Higiene', 'Perro', '🐶'),
        ('Cama Redonda Mascotas', 'Cama suave antideslizante 60cm diámetro', 19990, 25, 'Descanso', 'Ambos', '🐾'),
    ]
    for p in productos_demo:
        c.execute("INSERT OR IGNORE INTO productos (nombre, descripcion, precio, stock, categoria, tipo_mascota, imagen, creado_en) VALUES (?,?,?,?,?,?,?,?)",
                  (*p, datetime.now().isoformat()))

    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ─── Auth helpers ────────────────────────────────────────────────────
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

# ─── Routes ──────────────────────────────────────────────────────────
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    if 'cliente_nombre' in session:
        return redirect(url_for('tienda'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = hashlib.sha256(request.form.get('password', '').encode()).hexdigest()
        conn = get_db()
        user = conn.execute("SELECT * FROM usuarios WHERE username=? AND password=?", (username, password)).fetchone()
        conn.close()
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['nombre'] = user['nombre']
            flash('Bienvenido al sistema!', 'success')
            return redirect(url_for('dashboard'))
        flash('Credenciales incorrectas. Intenta nuevamente.', 'error')
    return render_template('login.html')

@app.route('/cliente-login', methods=['POST'])
def cliente_login():
    nombre = request.form.get('cliente_nombre', '').strip()
    email = request.form.get('cliente_email', '').strip()
    if not nombre:
        flash('Ingresa tu nombre para continuar.', 'error')
        return redirect(url_for('login'))
    session['cliente_nombre'] = nombre
    session['cliente_email'] = email
    return redirect(url_for('tienda'))

@app.route('/tienda')
def tienda():
    conn = get_db()
    prods = conn.execute(
        "SELECT * FROM productos WHERE activo=1 AND stock>0 ORDER BY tipo_mascota, nombre"
    ).fetchall()
    conn.close()
    return render_template('tienda.html', productos=prods)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/logout-cliente')
def logout_cliente():
    session.pop('cliente_nombre', None)
    session.pop('cliente_email', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db()
    total_productos = conn.execute("SELECT COUNT(*) FROM productos WHERE activo=1").fetchone()[0]
    total_ventas = conn.execute("SELECT COUNT(*) FROM ventas WHERE estado='pagado'").fetchone()[0]
    ingresos = conn.execute("SELECT COALESCE(SUM(total),0) FROM ventas WHERE estado='pagado'").fetchone()[0]
    total_clientes = conn.execute("SELECT COUNT(*) FROM clientes").fetchone()[0]
    ventas_recientes = conn.execute("""
        SELECT v.*, COUNT(d.id) as items
        FROM ventas v LEFT JOIN detalle_venta d ON v.id=d.venta_id
        WHERE v.estado='pagado'
        GROUP BY v.id ORDER BY v.creado_en DESC LIMIT 5
    """).fetchall()
    low_stock = conn.execute("SELECT * FROM productos WHERE stock <= 10 AND activo=1").fetchall()
    conn.close()
    return render_template('dashboard.html', 
        total_productos=total_productos, total_ventas=total_ventas,
        ingresos=ingresos, total_clientes=total_clientes,
        ventas_recientes=ventas_recientes, low_stock=low_stock)

# ─── PRODUCTOS (CRUD) ─────────────────────────────────────────────────
@app.route('/productos')
@login_required
def productos():
    search = request.args.get('search', '')
    tipo = request.args.get('tipo', '')
    cat = request.args.get('categoria', '')
    conn = get_db()
    q = "SELECT * FROM productos WHERE activo=1"
    params = []
    if search:
        q += " AND (nombre LIKE ? OR descripcion LIKE ?)"
        params += [f'%{search}%', f'%{search}%']
    if tipo:
        q += " AND tipo_mascota=?"
        params.append(tipo)
    if cat:
        q += " AND categoria=?"
        params.append(cat)
    q += " ORDER BY nombre"
    prods = conn.execute(q, params).fetchall()
    categorias = conn.execute("SELECT DISTINCT categoria FROM productos WHERE activo=1").fetchall()
    conn.close()
    return render_template('productos.html', productos=prods, categorias=categorias,
                           search=search, tipo=tipo, cat=cat)

@app.route('/productos/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_producto():
    if request.method == 'POST':
        conn = get_db()
        conn.execute("""INSERT INTO productos (nombre, descripcion, precio, stock, categoria, tipo_mascota, imagen, creado_en)
                        VALUES (?,?,?,?,?,?,?,?)""",
            (request.form['nombre'], request.form['descripcion'], float(request.form['precio']),
             int(request.form['stock']), request.form['categoria'], request.form['tipo_mascota'],
             request.form.get('imagen','🐾'), datetime.now().isoformat()))
        conn.commit(); conn.close()
        flash('Producto creado exitosamente ✅', 'success')
        return redirect(url_for('productos'))
    return render_template('producto_form.html', producto=None, titulo='Nuevo Producto')

@app.route('/productos/editar/<int:pid>', methods=['GET', 'POST'])
@login_required
def editar_producto(pid):
    conn = get_db()
    if request.method == 'POST':
        conn.execute("""UPDATE productos SET nombre=?, descripcion=?, precio=?, stock=?,
                        categoria=?, tipo_mascota=?, imagen=? WHERE id=?""",
            (request.form['nombre'], request.form['descripcion'], float(request.form['precio']),
             int(request.form['stock']), request.form['categoria'], request.form['tipo_mascota'],
             request.form.get('imagen','🐾'), pid))
        conn.commit(); conn.close()
        flash('Producto actualizado ✅', 'success')
        return redirect(url_for('productos'))
    prod = conn.execute("SELECT * FROM productos WHERE id=?", (pid,)).fetchone()
    conn.close()
    return render_template('producto_form.html', producto=prod, titulo='Editar Producto')

@app.route('/productos/eliminar/<int:pid>', methods=['POST'])
@login_required
def eliminar_producto(pid):
    conn = get_db()
    conn.execute("UPDATE productos SET activo=0 WHERE id=?", (pid,))
    conn.commit(); conn.close()
    flash('Producto eliminado 🗑️', 'info')
    return redirect(url_for('productos'))

# ─── VENTAS ──────────────────────────────────────────────────────────
@app.route('/ventas')
@login_required
def ventas():
    conn = get_db()
    ventas_list = conn.execute("""
        SELECT v.*, COUNT(d.id) as items
        FROM ventas v LEFT JOIN detalle_venta d ON v.id=d.venta_id
        GROUP BY v.id ORDER BY v.creado_en DESC
    """).fetchall()
    conn.close()
    return render_template('ventas.html', ventas=ventas_list)

@app.route('/ventas/nueva', methods=['GET', 'POST'])
@login_required
def nueva_venta():
    conn = get_db()
    prods = conn.execute("SELECT * FROM productos WHERE activo=1 AND stock>0 ORDER BY nombre").fetchall()
    conn.close()
    return render_template('nueva_venta.html', productos=prods)

@app.route('/ventas/procesar', methods=['POST'])
def procesar_venta():
    data = request.get_json()
    cliente_nombre = data.get('cliente_nombre', 'Cliente')
    cliente_email = data.get('cliente_email', '')
    items = data.get('items', [])
    
    if not items:
        return jsonify({'error': 'Carrito vacío'}), 400
    
    conn = get_db()
    total = 0
    detalle = []
    for item in items:
        prod = conn.execute("SELECT * FROM productos WHERE id=?", (item['id'],)).fetchone()
        if not prod or prod['stock'] < item['cantidad']:
            conn.close()
            return jsonify({'error': f'Stock insuficiente para {prod["nombre"] if prod else "producto"}'}), 400
        subtotal = prod['precio'] * item['cantidad']
        total += subtotal
        detalle.append({'prod': prod, 'cantidad': item['cantidad'], 'subtotal': subtotal})
    
    numero_venta = f"VTA-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"
    venta_id = conn.execute("""INSERT INTO ventas (numero_venta, cliente_nombre, cliente_email, total, estado, creado_en)
                               VALUES (?,?,?,?,?,?)""",
        (numero_venta, cliente_nombre, cliente_email, total, 'pendiente', datetime.now().isoformat())).lastrowid
    
    for d in detalle:
        conn.execute("INSERT INTO detalle_venta (venta_id, producto_id, cantidad, precio_unitario, subtotal) VALUES (?,?,?,?,?)",
            (venta_id, d['prod']['id'], d['cantidad'], d['prod']['precio'], d['subtotal']))
        conn.execute("UPDATE productos SET stock = stock - ? WHERE id=?", (d['cantidad'], d['prod']['id']))
    
    conn.commit(); conn.close()
    
    # Iniciar pago Webpay
    buy_order = numero_venta[:26]
    session_id = f"SES-{venta_id}"
    amount = int(total)
    return_url = url_for('webpay_retorno', _external=True)
    
    try:
        headers = {
            "Tbk-Api-Key-Id": TRANSBANK_COMMERCE_CODE,
            "Tbk-Api-Key-Secret": TRANSBANK_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "buy_order": buy_order,
            "session_id": session_id,
            "amount": amount,
            "return_url": return_url
        }
        resp = requests.post(TRANSBANK_API_URL, headers=headers, json=payload, timeout=15)
        tb_data = resp.json()
        
        if 'token' in tb_data and 'url' in tb_data:
            conn2 = get_db()
            conn2.execute("UPDATE ventas SET token_transbank=? WHERE id=?", (tb_data['token'], venta_id))
            conn2.commit(); conn2.close()
            return jsonify({
                'success': True,
                'webpay_url': tb_data['url'],
                'token': tb_data['token'],
                'venta_id': venta_id
            })
        else:
            return jsonify({'error': 'Error al conectar con Transbank', 'detalle': str(tb_data)}), 500
    except Exception as e:
        return jsonify({'error': f'Error Transbank: {str(e)}', 'venta_id': venta_id, 'modo_demo': True}), 200

@app.route('/webpay/retorno', methods=['GET', 'POST'])
def webpay_retorno():
    token = request.form.get('token_ws') or request.args.get('token_ws', '')
    if not token:
        flash('Pago cancelado o token invalido.', 'error')
        if 'user_id' in session:
            return redirect(url_for('ventas'))
        return redirect(url_for('tienda'))
    
    try:
        headers = {
            "Tbk-Api-Key-Id": TRANSBANK_COMMERCE_CODE,
            "Tbk-Api-Key-Secret": TRANSBANK_API_KEY,
            "Content-Type": "application/json"
        }
        resp = requests.put(f"{TRANSBANK_API_URL}/{token}", headers=headers, timeout=15)
        result = resp.json()
        
        conn = get_db()
        if result.get('response_code') == 0:
            conn.execute("UPDATE ventas SET estado='pagado' WHERE token_transbank=?", (token,))
            conn.commit()
            venta = conn.execute("SELECT * FROM ventas WHERE token_transbank=?", (token,)).fetchone()
            conn.close()
            return render_template('pago_exitoso.html', venta=venta, resultado=result)
        else:
            conn.execute("UPDATE ventas SET estado='rechazado' WHERE token_transbank=?", (token,))
            conn.commit(); conn.close()
            flash('El pago fue rechazado. Intenta nuevamente.', 'error')
            return redirect(url_for('ventas'))
    except Exception as e:
        flash(f'Error al confirmar pago: {str(e)}', 'error')
        return redirect(url_for('ventas'))

@app.route('/venta/<int:vid>/detalle')
@login_required
def detalle_venta_view(vid):
    conn = get_db()
    venta = conn.execute("SELECT * FROM ventas WHERE id=?", (vid,)).fetchone()
    detalle = conn.execute("""
        SELECT d.*, p.nombre, p.imagen, p.categoria
        FROM detalle_venta d JOIN productos p ON d.producto_id=p.id
        WHERE d.venta_id=?
    """, (vid,)).fetchall()
    conn.close()
    return render_template('detalle_venta.html', venta=venta, detalle=detalle)

# ─── CLIENTES (CRUD) ──────────────────────────────────────────────────
@app.route('/clientes')
@login_required
def clientes():
    conn = get_db()
    cli = conn.execute("SELECT * FROM clientes ORDER BY nombre").fetchall()
    conn.close()
    return render_template('clientes.html', clientes=cli)

@app.route('/clientes/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_cliente():
    if request.method == 'POST':
        conn = get_db()
        try:
            conn.execute("INSERT INTO clientes (nombre, email, telefono, tipo_mascota, creado_en) VALUES (?,?,?,?,?)",
                (request.form['nombre'], request.form['email'], request.form['telefono'],
                 request.form['tipo_mascota'], datetime.now().isoformat()))
            conn.commit()
            flash('Cliente registrado ✅', 'success')
        except sqlite3.IntegrityError:
            flash('El email ya está registrado.', 'error')
        finally:
            conn.close()
        return redirect(url_for('clientes'))
    return render_template('cliente_form.html', cliente=None, titulo='Nuevo Cliente')

@app.route('/clientes/editar/<int:cid>', methods=['GET', 'POST'])
@login_required
def editar_cliente(cid):
    conn = get_db()
    if request.method == 'POST':
        conn.execute("UPDATE clientes SET nombre=?, email=?, telefono=?, tipo_mascota=? WHERE id=?",
            (request.form['nombre'], request.form['email'], request.form['telefono'],
             request.form['tipo_mascota'], cid))
        conn.commit(); conn.close()
        flash('Cliente actualizado ✅', 'success')
        return redirect(url_for('clientes'))
    cli = conn.execute("SELECT * FROM clientes WHERE id=?", (cid,)).fetchone()
    conn.close()
    return render_template('cliente_form.html', cliente=cli, titulo='Editar Cliente')

@app.route('/clientes/eliminar/<int:cid>', methods=['POST'])
@login_required
def eliminar_cliente(cid):
    conn = get_db()
    conn.execute("DELETE FROM clientes WHERE id=?", (cid,))
    conn.commit(); conn.close()
    flash('Cliente eliminado 🗑️', 'info')
    return redirect(url_for('clientes'))

# ─── REPORTES ─────────────────────────────────────────────────────────
@app.route('/reportes')
@login_required
def reportes():
    conn = get_db()
    ventas_mes = conn.execute("""
        SELECT strftime('%Y-%m', creado_en) as mes, COUNT(*) as total_ventas, SUM(total) as ingresos
        FROM ventas WHERE estado='pagado'
        GROUP BY mes ORDER BY mes DESC LIMIT 12
    """).fetchall()
    top_productos = conn.execute("""
        SELECT p.nombre, p.imagen, SUM(d.cantidad) as vendidos, SUM(d.subtotal) as total
        FROM detalle_venta d JOIN productos p ON d.producto_id=p.id
        JOIN ventas v ON d.venta_id=v.id WHERE v.estado='pagado'
        GROUP BY p.id ORDER BY vendidos DESC LIMIT 10
    """).fetchall()
    ventas_por_tipo = conn.execute("""
        SELECT p.tipo_mascota, COUNT(*) as items, SUM(d.subtotal) as total
        FROM detalle_venta d JOIN productos p ON d.producto_id=p.id
        JOIN ventas v ON d.venta_id=v.id WHERE v.estado='pagado'
        GROUP BY p.tipo_mascota
    """).fetchall()
    stock_bajo = conn.execute("SELECT * FROM productos WHERE stock<=10 AND activo=1 ORDER BY stock").fetchall()
    resumen = conn.execute("""
        SELECT COUNT(*) as total_ventas, COALESCE(SUM(total),0) as total_ingresos,
               COALESCE(AVG(total),0) as ticket_promedio
        FROM ventas WHERE estado='pagado'
    """).fetchone()
    conn.close()
    return render_template('reportes.html', ventas_mes=ventas_mes, top_productos=top_productos,
                           ventas_por_tipo=ventas_por_tipo, stock_bajo=stock_bajo, resumen=resumen)

# ─── USUARIOS ─────────────────────────────────────────────────────────
@app.route('/usuarios')
@login_required
def usuarios():
    conn = get_db()
    users = conn.execute("SELECT id, username, nombre, rol, creado_en FROM usuarios").fetchall()
    conn.close()
    return render_template('usuarios.html', usuarios=users)

@app.route('/usuarios/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_usuario():
    if request.method == 'POST':
        pw = hashlib.sha256(request.form['password'].encode()).hexdigest()
        conn = get_db()
        try:
            conn.execute("INSERT INTO usuarios (username, password, nombre, rol, creado_en) VALUES (?,?,?,?,?)",
                (request.form['username'], pw, request.form['nombre'], request.form['rol'], datetime.now().isoformat()))
            conn.commit()
            flash('Usuario creado ✅', 'success')
        except sqlite3.IntegrityError:
            flash('El usuario ya existe.', 'error')
        finally:
            conn.close()
        return redirect(url_for('usuarios'))
    return render_template('usuario_form.html', usuario=None, titulo='Nuevo Usuario')

@app.route('/usuarios/eliminar/<int:uid>', methods=['POST'])
@login_required
def eliminar_usuario(uid):
    if uid == session.get('user_id'):
        flash('No puedes eliminar tu propio usuario.', 'error')
        return redirect(url_for('usuarios'))
    conn = get_db()
    conn.execute("DELETE FROM usuarios WHERE id=?", (uid,))
    conn.commit(); conn.close()
    flash('Usuario eliminado 🗑️', 'info')
    return redirect(url_for('usuarios'))

# ─── DEMO Pago (sin Transbank real) ──────────────────────────────────
@app.route('/ventas/<int:vid>/pagar-demo', methods=['POST'])
def pagar_demo(vid):
    conn = get_db()
    conn.execute("UPDATE ventas SET estado='pagado', metodo_pago='demo' WHERE id=?", (vid,))
    conn.commit(); conn.close()
    # Si es admin redirige al historial, si es cliente devuelve OK
    if 'user_id' in session:
        flash('Venta marcada como pagada (modo demo)', 'success')
        return redirect(url_for('ventas'))
    return jsonify({'ok': True})

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
