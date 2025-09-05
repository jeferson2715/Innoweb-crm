import re
from io import BytesIO
from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
import mysql.connector
from mysql.connector import errors as mysql_errors
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ---- App: usa FRONTED para templates y estáticos ----
app = Flask(
    __name__,
    template_folder='FRONTED',  # .html
    static_folder='FRONTED',    # estilos.css y app.js
    static_url_path=''          # se sirven en /estilos.css y /app.js
)
CORS(app)

# ----------------- VALIDACIONES -----------------
PHONE_RE = re.compile(r'^\+?\d{7,15}$')
ESTADOS = {'Nuevo', 'Antiguo'}
TIPOS_PROYECTO = {'Pagina web', 'LandinPage', 'Marketing', 'Programación'}
ESTADOS_PROYECTO = {'Pendiente', 'En proceso', 'Entregado', 'Cancelado'}

def validar_persona(p, parcial=False):
    errores = []
    def presente(c): return c in p and p.get(c) is not None
    if not parcial or presente('nombre'):
        if not (p.get('nombre') or '').strip():
            errores.append('El nombre es obligatorio.')
    if not parcial or presente('telefono'):
        tel = (p.get('telefono') or '').strip()
        if not tel:
            errores.append('El teléfono es obligatorio.')
        elif not PHONE_RE.fullmatch(tel):
            errores.append('El teléfono debe tener solo dígitos (7–15) y opcionalmente un + inicial.')
    if presente('estado') and (p.get('estado') or '').strip() not in ESTADOS:
        errores.append(f"Estado inválido. Valores permitidos: {', '.join(ESTADOS)}.")
    if presente('tipo_proyecto') and (p.get('tipo_proyecto') or '').strip() not in TIPOS_PROYECTO:
        errores.append(f"Tipo de proyecto inválido. Valores: {', '.join(TIPOS_PROYECTO)}.")
    if presente('estado_proyecto') and (p.get('estado_proyecto') or '').strip() not in ESTADOS_PROYECTO:
        errores.append(f"Estado de proyecto inválido. Valores: {', '.join(ESTADOS_PROYECTO)}.")
    return errores

def error_json(msgs, status=400):
    if isinstance(msgs, str): msgs = [msgs]
    return jsonify({'ok': False, 'errores': msgs}), status

def ok_json(msg, status=200, **extra):
    payload = {'ok': True, 'mensaje': msg}
    payload.update(extra)
    return jsonify(payload), status

# ----------------- BD -----------------
ListaProyectos = []
resultadosPersonas = []

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="innoWeb2025*",
    database="sabadoJulio"
)
cursor = db.cursor(dictionary=True)

# ----------------- PÁGINAS -----------------
@app.route('/')
def home():
    return render_template('Innoweb.html')   # formulario

@app.route('/datos')
def pagina_datos():
    return render_template('datos.html')     # tabla

# ----------------- APIs -----------------
@app.route('/datosDeLaBase', methods=['GET'])
def datosBase():
    cursor.execute("SELECT * FROM persona")
    resultadosPersonas = cursor.fetchall()
    return jsonify(resultadosPersonas)




# --------------- Agregar personas ----------

@app.route('/agregarPersonaBD', methods=['POST'])
def agregar():
    body = request.get_json(silent=True) or {}
    nuevaPersona = body.get('persona') or {}
    errores = validar_persona(nuevaPersona, parcial=False)
    if errores: return error_json(errores, 400)
    try:
        cursor.execute("""
            INSERT INTO persona
                (id, estado, empresa, nombre, email, telefono, ciudad_pais,
                 tipo_proyecto, estado_proyecto, responsable)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            nuevaPersona['id'],
            (nuevaPersona.get('estado') or 'Nuevo'),
            nuevaPersona.get('empresa'),
            nuevaPersona['nombre'],
            nuevaPersona.get('email'),
            nuevaPersona.get('telefono'),
            nuevaPersona.get('ciudad_pais'),
            (nuevaPersona.get('tipo_proyecto') or 'Pagina web'),
            (nuevaPersona.get('estado_proyecto') or 'Pendiente'),
            nuevaPersona.get('responsable')
        ))
        db.commit()
        return ok_json('Persona agregada correctamente.', status=201)
    except mysql.connector.Error as e:
        if getattr(e, 'errno', None) == 3819 or 'chk_telefono_formato' in str(e).lower():
            return error_json('El teléfono no cumple el formato (7–15 dígitos, + opcional).', 400)
        if getattr(e, 'errno', None) == 1062:
            return error_json('El ID ya existe.', 400)
        db.rollback()
        return error_json('Error de integridad de datos.', 400)
    except Exception:
        db.rollback()
        return error_json('Error al guardar en la base de datos.', 500)

@app.route('/buscarPersona/<id>', methods=['GET'])
def buscar(id):
    cursor.execute("SELECT * FROM persona WHERE id = %s", (id,))
    return jsonify(cursor.fetchall())


# ----- Actualizar personas --------

@app.route('/actualizarPersona/<id>', methods=['PUT'])
def actualizar(id):
    datos = request.get_json(silent=True) or {}
    errores = validar_persona(datos, parcial=True)
    if errores: return error_json(errores, 400)
    try:
        cursor.execute("""
            UPDATE persona
               SET estado=%s, empresa=%s, nombre=%s, email=%s, telefono=%s,
                   ciudad_pais=%s, tipo_proyecto=%s, estado_proyecto=%s, responsable=%s
             WHERE id=%s
        """, (
            datos.get('estado', 'Nuevo'),
            datos.get('empresa'),
            datos.get('nombre'),
            datos.get('email'),
            datos.get('telefono'),
            datos.get('ciudad_pais'),
            datos.get('tipo_proyecto', 'Pagina web'),
            datos.get('estado_proyecto', 'Pendiente'),
            datos.get('responsable'),
            id
        ))
        db.commit()
        
        if cursor.rowcount == 0:
            return error_json('Ya existe un cliente con ese ID.', 404)

        return ok_json('Persona actualizada', id=id)

    except mysql.connector.Error as e:
        if getattr(e, 'errno', None) == 3819 or 'chk_telefono_formato' in str(e).lower():
            return error_json('El teléfono no cumple el formato (7–15 dígitos, + opcional).', 400)
        db.rollback()
        return error_json('Error de integridad de datos.', 400)
    except Exception:
        db.rollback()
        return error_json('Error al actualizar en la base de datos.', 500)


# ------------------- eliminar personas -------
@app.route('/eliminarPersona/<id>', methods=['DELETE'])
def eliminar(id):
    cursor.execute("DELETE FROM persona WHERE id = %s", (id,))
    db.commit()
    return "Persona eliminada"

@app.route('/graficoPersona', methods=['GET'])
def graficoLineal():
    nombres = ["Jorge", "Alejandra", "Luis", "Ana"]
    edades = [31, 27, 28, 45]
    plt.figure(figsize=(10, 6))
    plt.plot(nombres, edades)
    plt.title("Grafico de edad por persona")
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)
    plt.close()
    return send_file(img_buffer, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)  