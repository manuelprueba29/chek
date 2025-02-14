import base64
from flask import Flask, flash, render_template, request, redirect, url_for, send_file, jsonify
import os
from mysql.connector import IntegrityError
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Establecer el backend de Matplotlib
from io import BytesIO
import database as db
from collections import defaultdict
import numpy as np


template_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
template_dir = os.path.join(template_dir, 'src', 'templates')

app = Flask(__name__, template_folder = template_dir)
app.secret_key = 'Chek!Q988'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
# -------------------------------------------------------------------------------------------------------
# Rutas para la primera aplicación (home1)
#plotly
# -------------------------------------------------------------------------------------------------------
def obtener_conexion():
    return db.database

@app.route('/', methods=['GET', 'POST'])
def home(): 
     try:
        # Obtener una nueva conexión a la base de datos
        connection = obtener_conexion()

        # Verificar si la conexión está cerrada y, en ese caso, reconectar
        if not connection.is_connected():
            connection.reconnect()

        if request.method == 'POST':
            if 'opcion' in request.form:
                opcion_seleccionada = request.form['opcion']

                # Obtener la información de la tabla "experiencias" para la opción seleccionada
                with connection.cursor() as cursor:
                    sql = "SELECT Activo, NombreSala, NombreExperiencia FROM experiencias WHERE NombreSala = %s"
                    cursor.execute(sql, (opcion_seleccionada,))
                    experiencias_data = cursor.fetchall()

                # Renderizar el formulario con la información obtenida
                return render_template('guardardatos.html', data=experiencias_data, sala=opcion_seleccionada)
        

        # Si no es una solicitud POST, simplemente renderizar el formulario vacío
        return render_template('guardardatos.html', data=None)

     except Exception as e:
         print(f"Error al procesar la solicituddd: {e}")

     finally:
        # Asegurarse de cerrar la conexión incluso si hay un error
         if connection and connection.is_connected():
             
             connection.close()

     return "Error al procesar la solicitudd."


#Ruta para guardar experiencia en la bdd del crud
@app.route('/user1', methods=['POST'])
def addUser1():
    try:
        connection= obtener_conexion()

        # Verificar si la conexión está cerrada y, en ese caso, reconectar
        if not connection.is_connected():
            connection.reconnect()

        Activo = request.form['Activo']
        NombreSala = request.form['NombreSala']
        NombreExperiencia = request.form['NombreExperiencia']

        if Activo and NombreSala and NombreExperiencia:
            with connection.cursor() as cursor:

                sql = "INSERT INTO experiencias (Activo, NombreSala, NombreExperiencia) VALUES (%s, %s, %s)"
                data = (Activo, NombreSala, NombreExperiencia)
            
                try:
                    cursor.execute(sql, data)
                    db.database.commit()
                except IntegrityError as e:
                    db.database.rollback()  # Deshace la transacción
                    warning_message = f"Advertencia: El activo {Activo} ya está registrado. Ingrese un activo unico"
                    flash(warning_message, 'warning')  # Almacena el mensaje en la sesión con la categoría 'warning'

    except Exception as e:
        print(f"Error de conexión a la base de datos: {e}")
        return "Error de conexión a la base de datos. Consulta los registros del servidor para obtener más información."

    finally:
        # Asegurarse de cerrar la conexión al finalizar la operación
        if connection and connection.is_connected():
            connection.close()

    return redirect(url_for('home1'))

 #Ruta para eliminar datos guardados    
@app.route('/delete1/<string:Activo>')
def delete1(Activo):
    try:
        connection=obtener_conexion()

        # Verificar si la conexión está cerrada y, en ese caso, reconectar
        if not connection.is_connected():
            connection.reconnect()

        with connection.cursor() as cursor:

            sql = "DELETE FROM experiencias WHERE Activo=%s"
            data = (Activo,)
            cursor.execute(sql, data)
            connection.commit()
            
    except Exception as e:

        print(f"Error de conexión a la base de datos: {e}")
        return "Error de conexión a la base de datos. Consulta los registros del servidor para obtener más información."
    
    finally:

        # Asegurarse de cerrar la conexión al finalizar la operación
        if connection and connection.is_connected():
            connection.close()
    return redirect(url_for('home1'))

#Editar experiencia guardadas 
@app.route('/edit1/<string:Activo>', methods=['POST'])

def edit1(Activo):
    try:

        connection=obtener_conexion()
        if not connection.is_connected():
            connection.reconnect()



        Activo = request.form['Activo']
        NombreSala = request.form['NombreSala']
        NombreExperiencia = request.form['NombreExperiencia']

        if Activo and NombreSala and NombreExperiencia:

            with connection.cursor() as cursor:

                sql = "UPDATE experiencias SET Activo = %s, NombreSala = %s, NombreExperiencia = %s WHERE Activo = %s"
                data = (Activo, NombreSala, NombreExperiencia, Activo)
                cursor.execute(sql, data)
                db.database.commit()

    except Exception as e:
        print(f"Error de conexión a la base de datos: {e}")
        return "Error de conexión a la base de datos. Consulta los registros del servidor para obtener más información."
    
    finally:
        # Asegurarse de cerrar la conexión al finalizar la operación
        if connection and connection.is_connected():
            connection.close()

    return redirect(url_for('home1'))

#Funcion para mostrar informacion por sala 
@app.route('/mostrarchek', methods=['GET', 'POST'])
def mostrar1():

    try:

        connection=obtener_conexion()
        if not connection.is_connected():
            connection.reconnect()
    

        fecha_elegida=None
    
        if request.method=='POST':
            fecha_elegida=request.form['Fecha']

            if fecha_elegida:

                with connection.cursor() as cursor:


                    #Obtener la información de la tabla cheklist para la fecha y todas las salas
                
                    sql_cheklist="""
                        SELECT Activo, NombreSala, fecha, NombreExperiencia, Estado, Comentario
                        FROM cheklist
                        WHERE DATE(fecha) = %s AND NombreSala IN ('escena','tiempo', 'mente', 'musica', 'acuario', 'vivario', 'Sala 3D', 'Sala infantil','Taquilla Parque', 'Planetario 1 nivel', 'Planetario 2 nivel', 'Planetario 3 nivel', 'Taquilla Planetario', 'Correos')
                        ORDER BY FIELD(NombreSala, 'escena','tiempo', 'mente', 'musica', 'acuario', 'vivario', 'Sala 3D', 'Sala infantil','Taquilla Parque', 'Planetario 1 nivel','Planetario 2 nivel','Planetario 3 nivel','Taquilla Planetario', 'Correos')
                    """          
                    try:
                        cursor.execute(sql_cheklist,(fecha_elegida,))
                        cheklist_date=cursor.fetchall()
                        connection.commit()  # Hacer commit para guardar los cambios              
                    except Exception as e: 
                        print(f"Error al ejecutar la consulta: {e}")
                        cheklist_date = []
                        connection.rollback()  # Hacer rollback en caso de error
                  
                return render_template('mostrarchek.html', data=cheklist_date, sala='')
            
    except Exception as e:

        print(f"Error de conexión a la base de datos: {e}")
        return "Error de conexión a la base de datos. Consulta los registros del servidor para obtener más información."
    
    finally:
        # Asegurarse de cerrar la conexión al finalizar la operación
        if connection and connection.is_connected():
            connection.close()

    return render_template('mostrarchek.html', fecha_elegida=fecha_elegida)

#---------------------------------------------------------------------------------------------------------------------
# Función para actualizar el estado en la base de datos
@app.route('/actualizar_estado', methods=['POST'])
def actualizar_estado():
    try:
        connection = obtener_conexion()
        if not connection.is_connected():
            connection.reconnect()

        if request.method == 'POST':
            activo = request.form['activo']  # Obtener el identificador único del formulario
            nuevo_estado = request.form['estado']  # Obtener el nuevo estado del formulario
            fecha_actual = request.form['fecha']  # Obtener la fecha actual del formulario

            with connection.cursor() as cursor:
                # Actualizar el estado en la base de datos para la fila con el identificador único especificado
                sql_update_estado = """
                    UPDATE cheklist
                    SET Estado = %s
                    WHERE Activo = %s AND Fecha = %s
                """
                try:
                    cursor.execute(sql_update_estado, (nuevo_estado, activo, fecha_actual))
                    connection.commit()  # Hacer commit para guardar los cambios
                except Exception as e:
                    connection.rollback()  # Hacer rollback en caso de error
                    raise e  # Relanzar la excepción para identificar el error

    except Exception as e:
        print(f"Error de conexión a la base de datos: {e}")
        return "Error de conexión a la base de datos. Consulta los registros del servidor para obtener más información."

    finally:
        # Asegurarse de cerrar la conexión al finalizar la operación
        if connection and connection.is_connected():
            connection.close()

    # Redirigir a la página principal después de actualizar el estado
    return redirect(url_for('mostrar1'))



def obtener_cheklist_data(fecha_inicial, fecha_final):
    cheklist_date = []

    try:
        # Obtener una nueva conexión a la base de datos
        connection = obtener_conexion()
       
        if not  connection.is_connected():
            connection.reconnect()
            

        cursor = connection.cursor()
        #eliminar la busqueda por el nombre de sala ya que no se esta utilizando debido a que nos importa que jale todo lo que esta en ese rango de fecha
        # Modifica la consulta SQL según la estructura de tu base de datos
        sql_cheklist = """
            SELECT Activo, NombreSala, fecha, NombreExperiencia, Estado, Comentario
            FROM cheklist
            WHERE DATE(fecha) BETWEEN %s AND %s AND NombreSala IN ('escena','tiempo', 'mente', 'musica', 'acuario', 'vivario', 'Sala 3D', 'Sala infantil', 'Taquilla Parque', 'Planetario 1 nivel', 'Planetario 2 nivel', 'Planetario 3 nivel', 'Taquilla Planetario', 'Correos')
            ORDER BY FIELD(NombreSala, 'escena','tiempo', 'mente', 'musica', 'acuario', 'vivario', 'Sala 3D', 'Sala infantil', 'Taquilla Parque', 'Planetario 1 nivel', 'Planetario 2 nivel', 'Planetario 3 nivel', 'Taquilla Planetario', 'Correos')
        """

        try:
            cursor.execute(sql_cheklist, (fecha_inicial, fecha_final))
            cheklist_date = cursor.fetchall()
            connection.commit()
        except Exception as e:
            print(f"Error al ejecutar la consulta: {e}")
            connection.rollback()
        finally:
            # Asegúrate de cerrar la conexión incluso si hay un error
            if cursor:
                cursor.close()

    except Exception as e:
        print(f"Error al establecer la conexión a la base de datos: {e}")

    finally:

        if connection and connection.is_connected():
            connection.close()

    return cheklist_date

@app.route('/exportar', methods=['GET'])
def exportar():
    fecha_inicial = request.args.get('fecha_inicial')
    fecha_final = request.args.get('fecha_final')

    # Lógica para generar el informe PDF (sustituye esto con tu propia lógica)
    pdf_content = generar_pdf(fecha_inicial, fecha_final)

    # Crear un objeto BytesIO para almacenar el contenido del PDF
    buffer = BytesIO(pdf_content)

    # Imprime un mensaje para verificar que la ruta se está llamando correctamente

    # Enviar el archivo al navegador para su descarga
    return send_file(buffer, download_name='Informe_Checklist.pdf', as_attachment=True)

def generar_pdf(fecha_inicial, fecha_final):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    # Estilo para la tabla
    styles = getSampleStyleSheet()
    style = styles['BodyText']

    cheklist_data = obtener_cheklist_data(fecha_inicial, fecha_final)

    # Crear la tabla con los datos
    data = [["Activo", "NombreSala", "Fecha", "NombreExperiencia", "Estado", "Comentario"]]
    data.extend([list(map(str, row)) for row in cheklist_data])

    

    table = Table(data)
    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                               ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                               ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                               ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                               ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                               ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                               ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    
    
    # Añadir la tabla al documento
    doc.build([Paragraph('', style), Paragraph('', style), table])
    # Añadir la tabla al documento con un espacio adicional
    
    buffer.seek(0)
    pdf_content = buffer.getvalue()
    return pdf_content

def obtener_cheklist_dataG(fecha_inicial, fecha_final, tipo_sala):
    cheklist_dateG = []

    try:
        # Obtener una nueva conexión a la base de datos
        connection = obtener_conexion()
       
        if not connection.is_connected():
            connection.reconnect()

        cursor = connection.cursor()

        # Modificar la consulta SQL según el tipo de selección
        if len(fecha_inicial) == 4 and len(fecha_final) == 4:
            # Selección por año
            sql_cheklist = """
                SELECT Activo, NombreSala, fecha, NombreExperiencia, Estado, Comentario
                FROM cheklist
                WHERE DATE_FORMAT(fecha, '%Y') BETWEEN %s AND %s AND NombreSala = %s
                ORDER BY FIELD(NombreSala, 'escena', 'tiempo', 'mente', 'musica', 'acuario', 'vivario', 'Sala 3D', 'Sala infantil', 'Taquilla Parque', 'Planetario 1 nivel', 'Planetario 2 nivel', 'Planetario 3 nivel', 'Taquilla Planetario', 'Correos')
            """
        elif len(fecha_inicial) == 7 and len(fecha_final) == 7:
            # Selección por año-mes
            sql_cheklist = """
                SELECT Activo, NombreSala, fecha, NombreExperiencia, Estado, Comentario
                FROM cheklist
                WHERE DATE_FORMAT(fecha, '%Y-%m') BETWEEN %s AND %s AND NombreSala = %s
                ORDER BY FIELD(NombreSala, 'escena', 'tiempo', 'mente', 'musica', 'acuario', 'vivario', 'Sala 3D', 'Sala infantil', 'Taquilla Parque', 'Planetario 1 nivel', 'Planetario 2 nivel', 'Planetario 3 nivel', 'Taquilla Planetario', 'Correos')
            """
        else:
            # No es un formato válido, manejar error si es necesario
            pass

        try:
            #aquí se llama todos los datos y se extrae cada dato por filas si cumple el rango a continuacion
            cursor.execute(sql_cheklist, (fecha_inicial, fecha_final, tipo_sala,))        
            cheklist_dateG = cursor.fetchall()
          
            """""
            #df = pd.DataFrame(cheklist_dateG, columns=['Activo', 'sala', 'Fecha', 'Nombre', 'Estado', 'Observaciones'])
           # print(tabulate(df, headers='keys', tablefmt='grid'))   
            """"" 
                 
            connection.commit()
        except Exception as e:
            print(f"Error al ejecutar la consulta: {e}")
            connection.rollback()
        finally:
            # Asegurarse de cerrar la conexión incluso si hay un error
            if cursor:
                cursor.close()

    except Exception as e:
        print(f"Error al establecer la conexión a la base de datos: {e}")

    finally:
        if connection and connection.is_connected():
            connection.close()

    return cheklist_dateG 


def procesar_datos_cheklist(datos_cheklist):

    # Inicializar un diccionario para almacenar las cantidades por experiencia y estado
    cantidades_por_experiencia_estado = defaultdict(lambda: {'BUENA': 0, 'REPARADA': 0, 'DESHABILITADA': 0})
    total_por_experiencia = defaultdict(int)
   # datos = request.json
    #tipo_seleccion = datos['tipoSeleccion']

    # Iterar sobre los datos de la tabla checklist y cuenta las experiencias de cada tipo para la sala seleccionada
    for dato in datos_cheklist:
        #fecha=dato[2]#obtener fecha
        nombre = dato[3]  # Obtener nombre de la experiencia
        estado = dato[4]  # Obtener el estado
        
        # Obtener el año o el mes dependiendo del tipo de selección
        """""
        if tipo_seleccion == 'años':
            clave = fecha.year
        elif tipo_seleccion == 'meses':
            clave = fecha.strftime('%Y-%m')  # Formato: 'YYYY-MM'
        """""
            
        # Incrementar el contador correspondiente al estado para la experiencia actual
        #cantidades_por_experiencia_estado[(nombre, clave)][estado] += 1
        #guarda por experiencia el diccionario con la cantidad de veces que estuvo Buena, Reparada, deshabilitada
        cantidades_por_experiencia_estado[(nombre)][estado] += 1
        
        # Incrementar el contador total de experiencias para la experiencia actual
        #Me cuenta la cantidad de reporte por experiencia, independiente si es buena, reparada o mala
        #total_por_experiencia[(nombre, clave)] += 1
        total_por_experiencia[(nombre)] += 1
        

    # Calcular el porcentaje de veces que cada experiencia estuvo en cada estado
    porcentaje_por_experiencia = {}
    #for (nombre,clave), cantidades in cantidades_por_experiencia_estado.items():
    for (nombre), cantidades in cantidades_por_experiencia_estado.items():
        porcentaje_por_estado = {}
        #total_experiencias = total_por_experiencia[(nombre,clave)]
        total_experiencias = total_por_experiencia[(nombre)]
        
        for estado, cantidad in cantidades.items():
        # Calcular el porcentaje y redondearlo a un decimal
            porcentaje = cantidad / total_experiencias * 100
            porcentaje_redondeado = round(porcentaje, 1)
            porcentaje_por_estado[estado] = porcentaje_redondeado
        
        porcentaje_por_experiencia[nombre] = porcentaje_por_estado
        
    """""
    # Calcular el promedio del porcentaje de cada estado para todas las experiencias
    promedio_porcentaje_estado = {}
    total_experiencias = sum(total_por_experiencia.values())
    
    for estado in ('BUENA', 'REPARADA', 'DESHABILITADA'):
        total_estado = sum(cantidades[estado] for cantidades in cantidades_por_experiencia_estado.values())
        promedio = total_estado / total_experiencias * 100
        promedio_con_decimales = round(promedio, 1)  # Redondear a un decimal
        promedio_porcentaje_estado[estado] = promedio_con_decimales
    """""

    return porcentaje_por_experiencia

@app.route('/mostrar_grafico', methods=['GET', 'POST'])
def mostrarGrafico():
    try:
        if request.method != 'POST':
            # Si la solicitud no es POST, renderiza la página HTML
            return render_template('InfGrafico.html')

        datos = request.json  # Obtener los datos enviados desde la página HTML
        tipo_seleccion = datos['tipoSeleccion']
        rango_fechas = datos['rangoFechas']
        fecha_inicial = rango_fechas['fechaInicial']
        fecha_final = rango_fechas['fechaFinal']
        tipo_sala = datos['tipoSala']

        if tipo_seleccion == 'años':
            datos_cheklist = obtener_cheklist_dataG(fecha_inicial, fecha_final, tipo_sala)
        elif tipo_seleccion == 'meses':
            datos_cheklist = obtener_cheklist_dataG(fecha_inicial, fecha_final, tipo_sala)
        else:
            return jsonify({'error': 'Tipo de selección no válido'})

        # Procesar los datos para obtener las cantidades de experiencias por sala y estado
        cantidades_por_sala_estado = procesar_datos_cheklist(datos_cheklist)

        claves = list(cantidades_por_sala_estado.keys())

        # Obtener las cantidades de experiencias buenas, reparadas y deshabilitadas por experiencia
        estados = {
            'BUENA': [cantidades_por_sala_estado[nombre]['BUENA'] for nombre in cantidades_por_sala_estado],
            'REPARADA': [cantidades_por_sala_estado[nombre]['REPARADA'] for nombre in cantidades_por_sala_estado], 
            'DESHABILITADA': [cantidades_por_sala_estado[nombre]['DESHABILITADA'] for nombre in cantidades_por_sala_estado]
        }

        x = np.arange(len(claves))
        width = 0.20 # Ancho de cada barra

        fig, ax = plt.subplots(figsize=(30, 5))  # Tamaño ampliado del gráfico

        for i, (attribute, measurement) in enumerate(estados.items()):
            color = 'green' if attribute == 'BUENA' else ('orange' if attribute == 'REPARADA' else 'red')
            offset = width * i
            rects = ax.bar(x + offset, measurement, width, label=attribute, color=color)
            ax.bar_label(rects, padding=3)

        # Configuraciones adicionales del gráfico
        ax.set_ylabel('Cantidad')
        ax.set_title('Cantidad de Experiencias por Estado')
        ax.set_xticks(x + width / 2)
        ax.set_xticklabels(claves, rotation=35, ha='right')
        ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
        ax.set_ylim(0, max([max(vals) for vals in estados.values()]) + 10)

        # Convertir el gráfico a imagen base64
        buffer = BytesIO()
        plt.tight_layout()  # Ajusta el diseño del gráfico
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        img_str = base64.b64encode(buffer.getvalue()).decode()

        # Devolver la imagen base64 al cliente
        return jsonify({'imagen': img_str})

    except Exception as e:
        print(f"Error al mostrar el gráfico: {e}")
        return jsonify({'error': 'Error al procesar los datos para el gráfico: ' + str(e)})

"""""
# --------------------------------------------------------------------------------------------
# Rutas para la segunda aplicación (home)
# --------------------------------------------------------------------------------------------
"""""
#ruta para guardar informacion en la tabla experiencia
@app.route('/CRUD', methods=['GET', 'POST'])
def home1():
    try:
        connection=obtener_conexion()

        # Verificar si la conexión está cerrada y, en ese caso, reconectar
        if not connection.is_connected():
            connection.reconnect()

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM experiencias")
            myresult = cursor.fetchall()  

        # Convertir los datos a diccionario
            insertObject = []
            columnNames = [column[0] for column in cursor.description]
            for record in myresult:
                insertObject.append(dict(zip(columnNames, record)))

        return render_template('CRUD.html', data=insertObject)

    except Exception as e:
        print(f"Error de conexión a la base de datos: {e}")
        return "Error de conexión a la base de datos. Consulta los registros del servidor para obtener más información."



# Ruta para guardar formulario  en la  base de datos
@app.route('/submit', methods=['POST'])
def addUser():

        Activos = request.form.getlist('Activo[]')
        NombreSalas = request.form.getlist('NombreSala[]')
        Fechas = request.form.getlist('Fecha[]')
        NombreExperiencias = request.form.getlist('NombreExperiencia[]')
        Estados = request.form.getlist('Estado[]')
        Comentarios = request.form.getlist('Comentario[]')

        #Variable para controlar si ya mostró el mensaje de advertencia
        advertencia_mostrada=False

        try:
            # Obtener una nueva conexión a la base de datos
            connection = obtener_conexion()

            # Verificar si la conexión está cerrada y, en ese caso, reconectar
            if not connection.is_connected():
                connection.reconnect()
            for Activo, NombreSala, NombreExperiencia, Fecha, Estado, Comentario in zip(Activos, NombreSalas, NombreExperiencias, Fechas, Estados, Comentarios):
                # Utilizar el cursor dentro del bloque 'with' para garantizar el cierre adecuado
                with connection.cursor() as cursor:
                    # Verificar si el activo ya realizó un checklist para la misma fecha y sala
                    sql_verificacion_activo = "SELECT * FROM cheklist WHERE Activo = %s AND Fecha = %s AND NombreSala = %s"
                    data_verificacion_activo = (Activo, Fecha, NombreSala)
                    cursor.execute(sql_verificacion_activo, data_verificacion_activo)
                    resultado_verificacion_activo = cursor.fetchone()

                    if resultado_verificacion_activo and not advertencia_mostrada:
                        # El activo ya realizó un checklist para la misma fecha y sala
                        flash(f"Advertencia: El checklist para la sala {NombreSala} en la fecha {Fecha} ya fue realizado", 'warning')
                        advertencia_mostrada=True
                    elif not resultado_verificacion_activo:
                        # Insertar datos en la tabla cheklist
                        sql_cheklist = "INSERT INTO cheklist (Activo, NombreSala, Fecha, NombreExperiencia, Estado, Comentario) VALUES (%s, %s, %s, %s, %s, %s)"
                        data_cheklist = (Activo, NombreSala, Fecha, NombreExperiencia, Estado, Comentario)

                        try:
                            cursor.execute(sql_cheklist, data_cheklist)
                            connection.commit()
                        except IntegrityError as e:
                            connection.rollback()
                            warning_message = f"Advertencia: El activo {Activo} ya está registrado. Ingrese un activo único."
                            flash(warning_message, 'warning')
        except Exception as e:
            print(f"Error al procesar la solicitud: {e}")

        finally:
            # Asegurarse de cerrar la conexión incluso si hay un error
            if connection and connection.is_connected():
                connection.close()

        return redirect(url_for('home'))
        
    
if __name__ == '__main__':
    app.run(host='10.1.4.42', port=5000)