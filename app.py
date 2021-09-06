from flask import Flask, jsonify, request, make_response
import mysql.connector
from mysql.connector import errorcode
from flask_httpauth import HTTPBasicAuth
import MySQLdb
from flask_sqlalchemy import SQLAlchemy
import re
import collections
import json

USER_DATA ={
    "admin":"root"
}

app = Flask(__name__)
db = SQLAlchemy(app)
auth = HTTPBasicAuth()


@auth.verify_password
def verify(username, password):
    if not(username and password):
        return False
    return USER_DATA.get(username) == password    


@app.route('/sortlist/<int_list>', methods=['GET'])
@auth.login_required
def sortArray(int_list):
    if not re.match(r'^\d+(?:,\d+)*,?$', int_list):
        return "Por favor colocar una serie de números únicamente", 400
    requestList = sum(int(i) for i in int_list.split(','))
    sortedListFromRequest = list(int(d) for d in str(requestList))
    duplicatedElements = [item for item, count in collections.Counter(sortedListFromRequest).items() if count > 1]
    sortedListFromRequest.sort()
    
    sortedListFromRequest = list(dict.fromkeys(sortedListFromRequest))
    return jsonify({"sin clasificar": list(int(d) for d in str(requestList)) }
                  ,{"clasificado": sortedListFromRequest + duplicatedElements })   


@app.route('/getbalances', methods=['POST']) 
def balancePerMonth():
    if not request.is_json:
        return jsonify({"errorMessage": "No se encontró objeto JSON en la solicitud"}), 400
    jsonRequest =  json.loads(request.data)
    months = jsonRequest['mes']
    sales = jsonRequest['ventas']
    expenses = jsonRequest['gastos']
    response = []
    if len(sales) != len(months) or  len(expenses) != len(months) :
        return jsonify({"errorMessage": "Error en la estructura del JSON, por favor verificar"}), 400
    for i in range(len(months)):
        if not isinstance(sales[i], int) or not isinstance(expenses[i], int) :
            return jsonify({"errorMessage": "Error en la estructura del JSON, por favor verificar"}), 400 
        response.append({"mes": months[i],"ventas":sales[i],"gastos":expenses[i], "balance": sales[i] -expenses[i] })

    return jsonify(response)    

                 
@app.route('/database', methods=['GET','POST'])
@auth.login_required
def handleDatabase():

    try:

        db_connection = mysql.connector.connect(
        host= "localhost",
        user= "root",
        passwd= "",
        database="db_finkargo_daag"
        )
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            return "Usuario o clave incorrectos", 405
        else:
            return "No se pudo conectar al servidor", 500
    else:
            cursor = db_connection.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS `usuarios` (`id` INT AUTO_INCREMENT PRIMARY KEY,`Nombres` VARCHAR(20), `Apellidos` VARCHAR(20),"
                "`Edad` int(3), `Nacionalidad` VARCHAR(20))")

            if request.method == 'GET':
                cursor.execute("SELECT * FROM usuarios")
                row_headers=[x[0] for x in cursor.description]
                myresult = cursor.fetchall()
                response = []
                for x in myresult:
                    response.append(dict(zip(row_headers,x)))
                return jsonify(response)
            if request.method == 'POST':   
                if not request.is_json:
                    return jsonify({"errorMessage": "No se encontró objeto JSON en la solicitud"}), 400
                data =  request.data
                r_nombres = request.json['Nombres']
                r_apellidos = request.json['Apellidos']
                r_edad = request.json['Edad']
                r_nacionalidad = request.json['Nacionalidad']
                
                sql = "insert into usuarios (Nombres, Apellidos, Edad, Nacionalidad) values ('%s', '%s','%d','%s')" %(r_nombres, r_apellidos, r_edad, r_nacionalidad)

                try:

                        cursor.execute(sql)
                        db_connection.commit()
                    
                except (MySQLdb.Error, MySQLdb.Warning) as e:
                    db_connection.rollback()
                    return e,400  
                return "Proceso realizado con exito" 
           
            
@app.route('/database/<id>', methods=['PUT','DELETE'])
@auth.login_required
def handleDatabaseUpdateDelete(id):

    try:

        db_connection = mysql.connector.connect(
        host= "localhost",
        user= "root",
        passwd= "",
        database="db_finkargo_daag"
        )
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            return "Usuario o clave incorrectos", 405
        else:
            return "No se pudo conectar al servidor", 500
    else:
            cursor = db_connection.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS `usuarios` (`id` INT AUTO_INCREMENT PRIMARY KEY,`Nombres` VARCHAR(20), `Apellidos` VARCHAR(20),"
                "`Edad` int(3), `Nacionalidad` VARCHAR(20))")

            if request.method == 'PUT':
                if not request.is_json:
                    return jsonify({"errorMessage": "No se encontró objeto JSON en la solicitud"}), 400
                r_nombres = request.json['Nombres']
                r_apellidos = request.json['Apellidos']
                r_edad = request.json['Edad']
                r_nacionalidad = request.json['Nacionalidad']

                try:
                    cursor.execute("UPDATE usuarios SET Nombres=%s,Apellidos=%s,Edad=%s,Nacionalidad=%s WHERE id=%s",(r_nombres,r_apellidos,r_edad,r_nacionalidad,id))
                    db_connection.commit()
                except:
                    db_connection.rollback()
                    return "error en la solicitud",400  
                return "Proceso realizado con exito" 
            if request.method == 'DELETE':   
                try:
                    cursor.execute("DELETE FROM usuarios WHERE id = '"+id+"'")
                    db_connection.commit()
                    
                except (MySQLdb.Error, MySQLdb.Warning) as e:
                    db_connection.rollback()
                    return e,400  
                return "Proceso realizado con exito"         





if __name__ == '__main__':
    app.run(debug=True, port=4000)