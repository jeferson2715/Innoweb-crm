from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
app = Flask(__name__)
CORS(app)
ListaProyectos = []
resultadosPersonas = []

db = mysql.connector.connect(
    host="localhost",
    user="root",           
    password="innoWeb2025*",     
    database="sabadoJulio" 
)
cursor = db.cursor(dictionary=True)
#pymysql.cursors.DictCursor

#query = "SELECT * FROM persona"

@app.route('/mensajes' ,methods=['GET'])
def mensaje():
    return 'Primera aplicacion Innoweb'

@app.route('/ListarProyectos' ,methods=['GET'])
def Proyectos():
    return jsonify(ListaProyectos)

@app.route('/agregarProyecto' ,methods=['POST'])
def agregar1():
    nuevoProyecto = request.json.get('proyecto')
    ListaProyectos.append(nuevoProyecto)
    return jsonify(resultadosPersonas)

# ruta de base

#Listar

@app.route('/datosDeLaBase' ,methods=['GET'])
def datosBase():
    cursor.execute("SELECT * FROM persona")
    resultadosPersonas = cursor.fetchall()
    return jsonify(resultadosPersonas)


#agregar

@app.route('/agregarPersonaBD' ,methods=['POST'])
def agregar():
    nuevaPersona = request.json.get('persona')
    resultadosPersonas.append(nuevaPersona)
    cursor.execute("INSERT INTO persona(identificacion, nombre, edad) VALUES (%s, %s, %s)",
            (nuevaPersona['identificacion'], nuevaPersona['nombre'], nuevaPersona['edad']))
    db.commit()
    return 'Se agrego una nueva persona'


# buscar

@app.route('/buscarPersona/<identificacion>' ,methods=['GET'])
def buscar(identificacion):
    cursor.execute("SELECT * FROM persona WHERE identificacion = %s",(identificacion,))
    resultadoPersona = cursor.fetchall()
    return jsonify(resultadoPersona)


# Actualizar

@app.route('/actualizarPersona/<identificacion>' ,methods=['PUT'])
def actualizar(identificacion):
    datos_nuevos = request.json
    cursor.execute("UPDATE persona SET nombre=%s,edad=%s WHERE identificacion=%s",
    (datos_nuevos['nombre'], datos_nuevos['edad'],datos_nuevos['identificacion']))
    db.commit()
    return "Persona actualizada"


#eliminar

@app.route('/eliminarPersona/<identificacion>' ,methods=['DELETE'])
def eliminar(identificacion):
    cursor.execute("DELETE  FROM persona WHERE identificacion = %s",(identificacion,))
    db.commit()
    return "Persona eliminada"


# @app.route('/eliminarPersona/<int:nit>', methods=['DELETE'])
# def eliminar(nit):
    # idx = numero - 1
    # if 0 <= idx < len(ListaProyectos):
        # eliminado = ListaProyectos.pop(idx)
        # return jsonify({
            # 'mensaje': f'usuario {nit} fuera de rango'
        # }), 200
        # else:
            # return jsonify({
                # 'error' f'Número {nit} fuera de rango' 
            # }), 404


if __name__ == '__main__':
    app.run(debug=True)






  