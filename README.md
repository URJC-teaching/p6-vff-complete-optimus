# p6_vff_complete

En esta práctica el robot tendrá que evitar obstáculos mientras busca y sigue a una persona. Para ello, se seguirá la misma estructura que en la práctica anterior, utilizando un nodo encargado de generar el vector atractivo y una máquina de estados para gestionar el comportamiento de búsqueda y seguimiento. En la fase de seguimiento, el robot utilizará un controlador basado en VFF, que combina vectores atractivos y repulsivos. Por lo tanto, nuestro sistema estará compuesto de 3 nodos:

- Un nodo que calcula y publica el vector atractivo a partir de las detecciones 3D de personas.
- Un nodo que procesa los datos del láser para detectar obstáculos y publica el vector repulsivo, con una dirección opuesta a los obstáculos detectados.
- Un nodo controlador que implementa la máquina de estados (buscar/seguir) y, en el estado de seguimiento, combina ambos vectores mediante suma vectorial para calcular la velocidad de salida del robot (velocidad lineal y angular).

Utiliza el código de la práctica 5 así como los nodos vff_control/vff_controller_node y vff_control/obstacle_detector_node del repositorio [asr-clase](https://github.com/URJC-teaching/asr-clase/tree/py).

Escribe un launch para lanzar todos los nodos necesarios con el comando ros2 launch.
