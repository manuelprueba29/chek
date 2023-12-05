from flask import Flask, flash, render_template, request, redirect, url_for
import os
from mysql.connector import IntegrityError
import database as db

template_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
template_dir = os.path.join(template_dir, 'src', 'templates')

app = Flask(__name__, template_folder = template_dir)
app.secret_key = '123'

@app.route('/')
def home():
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
@app.route('/user', methods=['POST'])
def addUser():
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

    return redirect(url_for('home'))

    

@app.route('/delete/<string:Activo>')
def delete(Activo):
    cursor = db.database.cursor()
    sql = "DELETE FROM experiencias WHERE Activo=%s"
    data = (Activo,)
    cursor.execute(sql, data)
    db.database.commit()
    return redirect(url_for('home'))

@app.route('/edit/<string:Activo>', methods=['POST'])

def edit(Activo):
    Activo = request.form['Activo']
    NombreSala = request.form['NombreSala']
    NombreExperiencia = request.form['NombreExperiencia']

    if Activo and NombreSala and NombreExperiencia:

        cursor = db.database.cursor()
        sql = "UPDATE experiencias SET Activo = %s, NombreSala = %s, NombreExperiencia = %s WHERE Activo = %s"
        data = (Activo, NombreSala, NombreExperiencia, Activo)
        cursor.execute(sql, data)
        db.database.commit()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True, port=4000)