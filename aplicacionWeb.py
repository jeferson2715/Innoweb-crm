from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
ListaPersonas = []

@app.route('/mensaje' ,methods=['GET'])
def mensaje():
    return 'Primera aplicacion web'

@app.route('/ListarPersonas' ,methods=['GET'])
def listar():
    return jsonify(ListaPersonas)

@app.route('/agregarPersona' ,methods=['POST'])
def agregar():
    nuevaPersona = request.json.get('persona')
    ListaPersonas.append(nuevaPersona)
    return 'Se agrego una nueva persona'


#proyecto


@app.route('/Cotizacion' ,methods=['GET'])
def Cotizacion():
    Cotizacion = ['Factura#1', {"Tipo de pagina": "LandingPage","Nit":1058960,"Ubicacion": "España-alicante","Costo Total": "5Usd"},
                     'Factura#2', {"Tipo de pagina": "Web 5 vistas","Nit":59824,"Ubicacion": "España-alicante","Costo Total": "1Usd"}, 
                     'Factura#3', {"Tipo de pagina": "Ecommerce","Nit":895441,"Ubicacion": "España-alicante","Costo Total": "100Usd"}]
    return jsonify(Cotizacion)


@app.route('/Proyectos' ,methods=['GET'])
def Proyectos():
    Proyectos = ['Status', {"Cliente": "Andres Rincon","Nit":1058960,"Pagina": "LandingPage", "Estado": "Entregado"},
                     {"Cliente": "Julian Castro","Nit":895644,"Pagina": "Pagina 5 vistas", "Estado": "Pendiente"}, 
                     {"Cliente": "Andrea Lopez","Nit":75632,"Pagina": "Ecommerce", "Estado": "Cancelado"}]
    return jsonify(Proyectos)







if __name__ == '__main__':
    app.run(debug=True)