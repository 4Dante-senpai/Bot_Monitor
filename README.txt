Bot twitter monitorea las gpu en Windows.

Este script hace de monitor de las placas de video a nivel sistema, en caso de que claymore o
cualquier otro miner falle al momento de hacer un reset o controlar las temperaturas.

Este script NO controla las temperaturas ni los ventiladores, solamente los monitorea para luego
notificar segun las especificaciones del usuario via Twitter.

Debido a que se requieren librerias de windows el mismo no se puede ejecutar en maquina virtual
por lo que el usuario tendra que instalar las librerias requeridas para el correcto funcionamiento.

Requerimientos:

++Python 3.6 o superior
++OpenHardwareMonitor ejecutandose
++Librerias:
-----Twython
-----Wmi
-----Pillow

...::::INSTALACION::::...

1-Instalar la versión de Python (3.6 en adelante) ---¡¡MUY IMPORTANTE!!: Al final de la instalacion hacer clic en el checkbox para agregar a Python al PATH de windows.

2-"Crear" una app de twitter para obtener los tokens del login --- Guia: https://developer.twitter.com/en/docs/basics/authentication/guides/access-tokens.html

3-Ejecutar el "install_requeriments.py" mediante python. --- Ejemplo: Crear un archivo de texto, con en la primeria linea la lugar donde esta el archivo y en la segunda linea "python install_requeriments.py" y cambiarle la extension a .BAT EJEMPLO: cd C:\Users##TU_USUARIO##\Desktop\bot_monitor python install_requeriments.py

4-Configurar el config.txt (usar la misma metodologia que la del ejemplo (los espacios y los 2 puntos) --- Más abajo se explica el config.txt

5-crear un RUN.bat que tenga openhardwaremonitor y al monitor_bot.py --- Ejemplo: cd C:\Users##TU_USUARIO##\Desktop\bot_monitor run
