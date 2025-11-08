# ---------------------------------------------------------------
# Aplicación Flask conectada a PostgreSQL
# Guarda los datos de un formulario (nombre, apellido, dirección, etc.)
# ---------------------------------------------------------------

from flask import Flask, request, jsonify, render_template
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

# ---------------------------------------------------------------
# CONFIGURACIÓN DE LA APLICACIÓN
# ---------------------------------------------------------------

app = Flask(__name__)

# Datos de conexión a PostgreSQL
DB_CONFIG = {
    'host': 'localhost',
    'database': 'FORMULARIO',
    'user': 'postgres',
    'password': '123456',  
    'port': 5432
}

# ---------------------------------------------------------------
# FUNCIÓN PARA CONECTAR A LA BASE DE DATOS
# ---------------------------------------------------------------
def conectar_bd():
    try:
        conexion = psycopg2.connect(**DB_CONFIG)
        return conexion
    except psycopg2.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

# ---------------------------------------------------------------
# FUNCIÓN: CREAR TABLA SI NO EXISTE
# ---------------------------------------------------------------
def crear_tabla():
    conexion = conectar_bd()
    if conexion:
        cursor = conexion.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS mensajes (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(50),
            apellido VARCHAR(50),
            direccion VARCHAR(100),
            telefono VARCHAR(20),
            correo VARCHAR(100),
            mensaje TEXT,
            creado TIMESTAMP DEFAULT NOW()
        );
        """)
        conexion.commit()
        cursor.close()
        conexion.close()
        print("Tabla 'mensajes' verificada o creada correctamente")

# ---------------------------------------------------------------
# RUTA PRINCIPAL
# Muestra el formulario HTML
# ---------------------------------------------------------------
@app.route('/')
def inicio():
    return render_template("index.html")

# ---------------------------------------------------------------
# RUTA PARA GUARDAR DATOS DEL FORMULARIO
# ---------------------------------------------------------------
@app.route('/guardar', methods=['POST'])
def guardar_datos():
    try:
        conexion = conectar_bd()
        if conexion is None:
            return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

        # Recibimos los datos del formulario
        datos = request.get_json()

        nombre = datos.get('nombre', '').strip()
        apellido = datos.get('apellido', '').strip()
        direccion = datos.get('direccion', '').strip()
        telefono = datos.get('telefono', '').strip()
        correo = datos.get('correo', '').strip()
        mensaje = datos.get('mensaje', '').strip()

        # Validar campos obligatorios
        if not nombre or not correo:
            return jsonify({'error': 'El nombre y el correo son obligatorios'}), 400

        # Insertar datos en la tabla
        cursor = conexion.cursor()
        sql = """
        INSERT INTO mensajes (nombre, apellido, direccion, telefono, correo, mensaje)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id;
        """
        cursor.execute(sql, (nombre, apellido, direccion, telefono, correo, mensaje))
        nuevo_id = cursor.fetchone()[0]

        conexion.commit()
        cursor.close()
        conexion.close()

        return jsonify({
            'mensaje': 'Datos guardados correctamente',
            'id': nuevo_id
        }), 201

    except Exception as e:
        print(f"Error al guardar los datos: {e}")
        return jsonify({'error': 'Error interno al guardar los datos'}), 500

# ---------------------------------------------------------------
# RUTA PARA VER TODOS LOS REGISTROS GUARDADOS
# ---------------------------------------------------------------
@app.route('/mensajes', methods=['GET'])
def ver_mensajes():
    try:
        conexion = conectar_bd()
        if conexion is None:
            return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

        cursor = conexion.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM mensajes ORDER BY creado DESC;")
        registros = cursor.fetchall()
        cursor.close()
        conexion.close()

        for fila in registros:
            if fila['creado']:
                fila['creado'] = fila['creado'].strftime('%Y-%m-%d %H:%M:%S')

        return jsonify(registros), 200

    except Exception as e:
        print(f"Error al obtener los registros: {e}")
        return jsonify({'error': 'Error interno al obtener los datos'}), 500

# ---------------------------------------------------------------
# INICIO DEL SERVIDOR
# ---------------------------------------------------------------
if __name__ == '__main__':
    print("Iniciando el servidor Flask...")
    crear_tabla()
    app.run(debug=True, host='0.0.0.0', port=5000)