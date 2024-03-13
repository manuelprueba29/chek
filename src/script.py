import subprocess

def abrir_terminal_y_ejecutar_comando(comando):
    try:
        # Ejecutar el comando en una nueva ventana de terminal
        subprocess.Popen(comando, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Terminal abierta y comando ejecutado correctamente.")
    except Exception as e:
        print(f"Error al abrir la terminal y ejecutar el comando: {e}")

# Comando que deseas ejecutar
comando = 'start cmd /c "cd C:\\cheklistexperiencia\\src && start waitress-serve --listen=10.1.4.49:5000 guardar:app"'

# Llamar a la función para abrir la terminal y ejecutar el comando
abrir_terminal_y_ejecutar_comando(comando)
