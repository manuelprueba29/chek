
"""
from flask import Flask, flash, render_template, request, redirect, url_for
from mysql.connector import IntegrityError
import database as db

app = Flask(__name__)
app.secret_key = 'Chek!Q987'  # Agrega tu clave secreta aquí
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0 

# Función para obtener datos de la base de datos
def obtener_datos():
    cursor = db.database.cursor()
    cursor.execute("SELECT * FROM experiencias")
    myresult = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    data = [dict(zip(column_names, record)) for record in myresult]
    cursor.close()
    return data

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if 'opcion' in request.form:
            opcion_seleccionada = request.form['opcion']
            # Obtener la información de la tabla "experiencias" para la opción seleccionada
            with db.database.cursor() as cursor:
                sql = "SELECT Activo, NombreSala, NombreExperiencia FROM experiencias WHERE NombreSala = %s"
                cursor.execute(sql, (opcion_seleccionada,))
                experiencias_data = cursor.fetchall()

            # Renderizar el formulario con la información obtenida
            return render_template('guardardatos.html', data=experiencias_data, sala=opcion_seleccionada)

    # Si no es una solicitud POST, simplemente renderizar el formulario vacío
    return render_template('guardardatos.html', data=None)

# Ruta para guardar formulario  en la  base de datos
@app.route('/submit', methods=['POST'])
def addUser():
    Activos = request.form.getlist('Activo[]')
    NombreSalas = request.form.getlist('NombreSala[]')
    Fechas = request.form.getlist('Fecha[]')
    NombreExperiencias = request.form.getlist('NombreExperiencia[]')
    Estados = request.form.getlist('Estado[]')
    Comentarios = request.form.getlist('Comentario[]')

    for Activo, NombreSala, NombreExperiencia, Fecha, Estado, Comentario in zip(Activos, NombreSalas, NombreExperiencias, Fechas, Estados, Comentarios):
        # Utilizar el cursor dentro del bloque 'with' para garantizar el cierre adecuado
        with db.database.cursor() as cursor:
            # Verificar si el activo ya realizó un checklist para la misma fecha y sala
            sql_verificacion_activo = "SELECT * FROM cheklist WHERE Activo = %s AND Fecha = %s AND NombreSala = %s"
            data_verificacion_activo = (Activo, Fecha, NombreSala)
            cursor.execute(sql_verificacion_activo, data_verificacion_activo)
            resultado_verificacion_activo = cursor.fetchone()

            if resultado_verificacion_activo:
                # El activo ya realizó un checklist para la misma fecha y sala
                flash(f"Advertencia: El activo {Activo} ya realizó un checklist para la sala {NombreSala} en la fecha {Fecha}.", 'warning')
            else:
                # Insertar datos en la tabla cheklist
                sql_cheklist = "INSERT INTO cheklist (Activo, NombreSala, Fecha, NombreExperiencia, Estado, Comentario) VALUES (%s, %s, %s, %s, %s, %s)"
                data_cheklist = (Activo, NombreSala, Fecha, NombreExperiencia, Estado, Comentario)

                try:
                    cursor.execute(sql_cheklist, data_cheklist)
                    db.database.commit()
                except IntegrityError as e:
                    db.database.rollback()
                    warning_message = f"Advertencia: El activo {Activo} ya está registrado. Ingrese un activo único."
                    flash(warning_message, 'warning')

    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True, port=4000)


    
"""