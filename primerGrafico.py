import matplotlib.pyplot as plt
import mysql.connector
import pandas as pd
db = mysql.connector.connect(
    host="localhost",
    user="root",           
    password="innoWeb2025*",     
    database="sabadoJulio" 
)
cursor = db.cursor(dictionary=True)
resultadosPersonas = []
cursor.execute("SELECT * FROM persona")
resultadosPersonas = cursor.fetchall() 
print(resultadosPersonas)
personas = pd.DataFrame(resultadosPersonas)
print(personas)

nombre = ["Jorge","Ana","Luis"]
edad = [31,26,37]

plt.plot(personas['nombre'],personas['edad'])
plt.title("Grafico de edad por persona")
plt.show()

plt.bar(nombre,edad)
plt.title("Grafico de barras edad por persona")
plt.xlabel("Nombre")
plt.ylabel("Edad")
plt.show()

plt.scatter(nombre,edad)
plt.title("Grafico de dispersion edad por persona")
plt.xlabel("Nombre")
plt.ylabel("Edad")
plt.show()



#ventas por mes 

labels = ["Marzo","Abril","Mayo","Junio"]
sizes = [23,56,12,32]
#Que no se nos olvide el formato es decir la f%%
plt.pie(sizes,labels = labels, autopct='%1.1f%%',startangle=90)
plt.title("Grafico de torta de ventas por mes")
plt.axis('equal')
plt.show()