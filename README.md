# NBA_predictions

### Descripción del proyecto

El proyecto está dividido en dos partes:

*ETL para obtener los datos del equipo Boston Celtics de una api

*Scrapping con selenium para obtener una prediccion


Antes de ejecutar nada, será necesario entrar al archivo config.txt, y rellenar la línea
Credenciales: XXXXXXXXXXXXXXX, con una clave de la api https://sportsdata.io que tenga acceso
a la sección de la nba.


Una vez hecho esto, se podrá continuar con la ejecución del proyecto


Para ello, se ha creado un Dockerfile para crear una imagen que contenga todo el proceso (eso si, una vez introducida la clave de la api).
Para ejecutarlo, vaya al archivo comandos_docker.txt para una información más detallada.


A modo de resumen, recomendamos los siguientes pasos:


    1. docker build -t nombre_imagen .


    2. docker run --name nombre_contenedor -v path_absoluto:/usr/src/app nombre_imagen

Si se quisiera ejecutar en local, sería necesario añadir un webdriver de chrome en el path (https://sites.google.com/chromium.org/driver/?pli=1)
