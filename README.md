# Bot de Telegram para consultas de cajeros automáticos en CABA
* Dependencias:
  tinydb 
  schedule
  requests
  numpy
  pandas
 
* Ejecutar con: `python3 main.py`
* El nombre del usuario del bot es __py_atm_bot__
* El bot no acepta comandos inline (hay que crear una nueva conversación)



* Para obtener los 3 cajeros más cercanos a la ubicación actual en O(log(n)) en promedio, se preprocesan todos los cajeros y se arma un [kd-tree](https://en.wikipedia.org/wiki/K-d_tree) para cada red. Para calcular las distancias entre los puntos se hace una [proyección equirectangular](https://en.wikipedia.org/wiki/Equirectangular_projection) de (latitud, longitud), teniendo en cuenta que esto es posible sólo porque los puntos se encuentran todos dentro de una zona relativamente pequeña (sin embargo, hay que hacer un ajuste teniendo en cuenta la latitud media de los puntos).

* Por otro lado, se mantiene una pequeña base de datos ([tinydb](https://github.com/msiemens/tinydb) donde para cada cajero se tiene la cantidad de extracciones disponibles, con un máximo de 1000 extracciones por día, reiniciándose este número de lunes a viernes a las 08:00hs. Para esto último se usa [schedule](https://github.com/dbader/schedule).

* Cada vez que se hace una consulta se genera un número random entre 0 y 1 para simular la elección del usuario del cajero al que va a ir a realizar la extracción. Cuando hay 3 cajeros disponibles (es decir con al menos una extracción disponible, y dentro de los 500m de distancia), se elige el más cercano con 70% de probabilidad, el segundo más cercano con 20%, y el tercero con 10%. Cuando hay 2 cajeros disponibles, se elige el más cercano con 70% de probabilidad, y el segundo con 30%. Si hay un solo cajero disponible, se elige ese.

* Para la generación de las imágenes se utiliza la API de [MapQuest](https://developer.mapquest.com/) (la de Google Static Maps requiere registrarse con una tarjeta de crédito).

* Para comunicarse con la API de telegram se utiliza [requests](https://github.com/psf/requests). Al ser bloqueantes los requests, para hacer la comunicación más fluida, al enviar las respuestas a los usuarios se crea un nuevo thread para enviar el request.

* Para facilitar la lectura y el manejo de los datos del archivo csv se usan [numpy](https://numpy.org/) y [pandas](https://pandas.pydata.org/)
