# Bot de Telegram para consultas de cajeros automáticos en CABA

Ejecutar `python3 main.py`

Usa [tinydb](https://github.com/msiemens/tinydb) para la persistencia de los datos sobre extracciones disponibles para los cajeros en caso de caídas o reinicios.

Se preprocesan todos los cajeros y se arma un [kd-tree](https://en.wikipedia.org/wiki/K-d_tree), que permite realizar las consultas sobre los 3 cajeros más cercanos a la ubicacin actual en O(log(n)) en promedio. Para calcular las distancias entre los puntos se hace una [proyección equirectangular](https://en.wikipedia.org/wiki/Equirectangular_projection) de (latitud, longitud), teniendo en cuenta que esto es posible sólo porque los puntos se encuentras todos dentro de una zona relativamente pequeña (sin embargo, hay que hacer un ajuste teniendo en cuenta la latitud media de los puntos).

Por otro lado, se mantiene una pequeña base de datos donde para cada cajero se tiene la cantidad de extracciones disponibles, con un máximo de 1000 extracciones por día, reiniciándose este número de lunes a viernes a las 08:00hs. Para lograr esto se crea un nuevo thread al iniciar el bot que periódicamente chequea si es hora de reiniciar la cantidad de extracciones disponibles. 

Cada vez que se hace una consulta se genera un número random entre 0 y 1 para simular la elección del usuario del cajero al que va a ir a realizar la extracción. Cuando hay 3 cajeros disponibles (es decir con al menos una extracción disponible, y dentro de los 500m de distancia), se elige el más cercano con 70% de probabilidad, el segundo más cercano con 20%, y el tercero con 10%. Cuando hay 2 cajeros disponibles, se elige el más cercano con 70% de probabilidad, y el segundo con 30%. Si hay un solo cajero disponible, se elige ese.

Para la generación de las imágenes se utiliza la API de [MapQuest](https://developer.mapquest.com/) (la de Google Static Maps requiere registrarse con una tarjeta de crédito).

NOTA: si se quisiera que el bot pueda responder a una gran cantidad de consultas en un tiempo muy corto, habría que considerar la utilización de threads para cada una de las consultas realizadas (por simplicidad, esto no fue tenido en cuenta).
