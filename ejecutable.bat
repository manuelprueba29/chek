start cmd /c "cd C:\cheklistexperiencia\src && start waitress-serve --listen=10.1.4.49:5000 guardar:app"

sc create FlaskApp binPath= "C:\cheklistexperiencia\nssm-2.24\nssm-2.24\win64\nssm.exe" start= auto DisplayName= "Flask App" depend= Tcpip obj= SYSTEM


sc create FlaskApp binPath= "C:\cheklistexperiencia\nssm-2.24\nssm-2.24\win64\nssm.exe" start= auto DisplayName= "Flask App" depend= Tcpip obj= "PARQUE-EXPLORA.LOCAL\manuel.moreno" password= "D.....odema18*****"


nssm.exe install FlaskApp C:\cheklistexperiencia\src\flask_app.xml



sc create "miapp1" binPatch= "C:\Users\manuel.moreno\Desktop\output\script.exe"

