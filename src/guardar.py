from flask import Flask, flash, render_template, request, redirect, url_for
import os
from mysql.connector import IntegrityError
import database as db

template_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
template_dir = os.path.join(template_dir, 'src', 'templates')

app = Flask(__name__, template_folder = template_dir)
app.secret_key = 'Chek!Q988'

@app.route('/')
def home1():
    cursor = db.database.cursor()
    cursor.execute("SELECT * FROM experiencias")
    myresult = cursor.fetchall()
    #Convertir los datos a diccionario
    insertObject = []
    columnNames = [column[0] for column in cursor.description]
    for record in myresult:
        insertObject.append(dict(zip(columnNames, record)))
    cursor.close()
    return render_template('CRUD.html', data=insertObject)


#Ruta para guardar usuarios en la bdd
@app.route('/user1', methods=['POST'])
def addUser1():
    Activo = request.form['Activo']
    NombreSala = request.form['NombreSala']
    NombreExperiencia = request.form['NombreExperiencia']

    if Activo and NombreSala and NombreExperiencia:
        cursor = db.database.cursor()
        sql = "INSERT INTO experiencias (Activo, NombreSala, NombreExperiencia) VALUES (%s, %s, %s)"
        data = (Activo, NombreSala, NombreExperiencia)
        
        try:
            cursor.execute(sql, data)
            db.database.commit()
        except IntegrityError as e:
            db.database.rollback()  # Deshace la transacción
            warning_message = f"Advertencia: El activo {Activo} ya está registrado. Ingrese un activo unico"
            flash(warning_message, 'warning')  # Almacena el mensaje en la sesión con la categoría 'warning'

    return redirect(url_for('home1'))

    
@app.route('/delete1/<string:Activo>')
def delete1(Activo):
    cursor = db.database.cursor()
    sql = "DELETE FROM experiencias WHERE Activo=%s"
    data = (Activo,)
    cursor.execute(sql, data)
    db.database.commit()
    return redirect(url_for('home1'))

@app.route('/edit1/<string:Activo>', methods=['POST'])

def edit1(Activo):
    Activo = request.form['Activo']
    NombreSala = request.form['NombreSala']
    NombreExperiencia = request.form['NombreExperiencia']

    if Activo and NombreSala and NombreExperiencia:

        cursor = db.database.cursor()
        sql = "UPDATE experiencias SET Activo = %s, NombreSala = %s, NombreExperiencia = %s WHERE Activo = %s"
        data = (Activo, NombreSala, NombreExperiencia, Activo)
        cursor.execute(sql, data)
        db.database.commit()
    return redirect(url_for('home1'))


@app.route('/mostrarchek', methods=['GET', 'POST'])

def mostrar1():

    fecha_elegida=None
   
    if request.method=='POST':
        fecha_elegida=request.form['Fecha']

        if fecha_elegida:

            cursor=db.database.cursor()

            #Obtener la información de la tabla cheklist para la fecha y todas las salas
            print("probando1")
            sql_cheklist="""
                SELECT Activo, NombreSala, fecha, NombreExperiencia, Estado, Comentario
                FROM cheklist
                WHERE DATE(fecha) = %s AND NombreSala IN ('escena','tiempo', 'mente', 'musica', 'acuario', 'vivario', 'Sala 3D', 'Sala infantil','Taquilla parque', 'Planetario', 'Taquilla planetario', 'Correos experiencias')
                ORDER BY FIELD(NombreSala, 'escena','tiempo', 'mente', 'musica', 'acuario', 'vivario', 'Sala 3D', 'Sala infantil','Taquilla parque', 'Planetario', 'Taquilla planetario', 'Correos experiencias')
            """
            print("probando2")
            cursor.execute(sql_cheklist,(fecha_elegida,))
            print("probando3")
            cheklist_date=cursor.fetchall()
            print("probando4")

            cursor.close()
            return render_template('mostrarchek.html', data=cheklist_date, sala='')

    return render_template('mostrarchek.html', fecha_elegida=fecha_elegida)


if __name__ == '__main__':
    app.run(debug=True, port=5000)