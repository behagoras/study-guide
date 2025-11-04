# Entrevista fullStack

- Teóric
    - Preguntas:
        - Sabes qué es un IDE
        - Con cuántas personas has trabajado en un equipo en el mismo proyecto y por cuánto tiempo?
        - 
    - Frontend
        - responsive metodologies
        - Qué tipo de selectores existen?
            - clase
            - universal
            - id
            - elemento
        - Cómo funciona la Especificidad en CSS
        - ¿Qué beneficios tiene la utilización de componentes en una aplicación Web?
            
            En general es que con componentes el código es más escalable, pero algunas de los beneficios específicos serían:
            
            1. Se genera código más legible que suele ser semántico, dividiendo el código en componentes que tienen funciones muy específicas, lo que hace que el código sea más mantenible (modularización del código)
            2. Reutilización de código: Al crear componentes, éstos son reutilizables gracias al poco acoplamiento que tienen
            3. Facilita el trabajo en equipo: al crear componentes pequeños y desacoplados hace más fácil que más de una persona esté trabajando en el mismo código sin pisar los trabajos de los demás.
            4. You can scope better your changes
        - ¿Qué característica de JavaScript permite que sea un lenguaje no bloqueante?
            
            Las promesas y los callbacks
            
        - ¿Qué es la programación reactiva?
            
            Declarativa
            
            Propagación del cambio
            
            Es un paradigma de programación orientado a flujos de datos (muy utilizado para lidiar con datos asíncronos) especializado en la propagación de datos mediante la generación de observables.
            
        - ¿̣Qué diferencias hay entre el Session Storage, Cookies y Local Storage?
            
            La Session Storage guarda data mientras la pestaña está abierta mientras que el local storage no expira y se mantiene en el browser (persiste) hasta que se borre por js o liberando el caché, las cookies sirven más para comunicación con el servidor donde con cada petición viaja la cookie por lo que no se recomienda hacerlas pesadas.
            
        - ¿Qué es un High Order Component?
            
            Los HOC son una técnica en la que una función regresa un componente, teniendo acceso a las variables de la función (suelen ser accedidos mediante el estado o las props), es muy utilizada esta técnica para hacer fetching de datos.
            
        - Qué es un Render Props?
            
            Cuando 
            
        - ¿Qué diferencias hay entre el DOM y el Virtual DOM?
            
            El DOM es lo que el árbol de elementos reales en el browser mientras que el DOM virtual es una copia en js del DOM que existe para facilitar las modificaciones del DOM al tener una referencia del arbol original.
            
            Si se desea modificar algo en el DOM, primero se modifica en el virtual dom, se comparan los cambios y en el DOM se modifican exactamente los nodos que cambiaron.
            
        - 10 formas de desaparecer un elemento del viewport
            - opacity: 0;
            - visibility: hidden;
            - display: none;
            - position: absolute; top: -9999px;
            - width: 0; height: 0; margin: 0; padding: 0; border: 0; line-height: 0; /* sólo en caso de elementos inline-block */ overflow: hidden;
            - z-index
            - transform: scale(0)
            - if en js
            - flag
        - Ciclo de vida
            - Class
            - functional
        - hooks
    - Javascript
        - Qué es un objeto en javascript
        - Qué es el prototype
        - Qué es un arrow function
        - Cómo funciona el hoisting
        - Cuáles son tus métodos de Array favoritos
        - Por qué es una mala práctica mutar un objeto?
        - Qué es un promesa
        - Qué son los 3 puntos en javascript?
        - ¿Qué es una expresión?
        - Cómo funcionan los operadores ternarios
        - ¿En cuántos hilos de ejecución corre JavaScript?
            
            1
            
        - ¿Qué diferencia hay entre Server Side Rendering y Client Side Rendering?
            
            El server SSR hace un prerenderizado del sitio web desde el servidor, mientras que el CSR renderiza en tiempo de ejecución.
            
        - Eventloop
    - Backend
        - ¿Cuál es la diferencia entre GET y POST?
        - Menciona los verbos disponibles en REST
            - get,
            - post,
            - delete,
            - put,
            - patch
        - ¿Cuál es la principal ventaja de GraphQL sobre una API REST?
            
            Hacer peticiones on demmand
            
        - ¿En qué casos se utiliza PUT y PATCH?
            
            ​ PUT para actualizar todo el recurso y PATCH para hacer una actualización parcial
            
            ​ PUT para hacer una actualización parcial y PATCH para actualizar todo el recurso
            
            ​ No hay diferencia, los dos se utilizan por igual
            
        - Son buenas prácticas para el despliegue en producción en seguridad
            
            ​ Agregar HTTP/2 y SOCKETS
            
            ​ Ofuscar los secrets y keys en el código
            
             Activar logs informativos en producción de errores posibles
            
             Agregar CORS
            
        - ¿Qué es un Middleware?
        - Qué es CORS
- Cultural English
    - Tell me about your hobbies?
    - What is your best success in your last project
    - How would you convince to use React to a client for your next project
    - Why do you like React
- Ejercicio
    - ToDo List backend / frontend
        
        Notas: Como es un proyecto de varias fases, se recomienda tener unas bases escalables, sobre todo en las partes que van a dejar de utilizarse, ejemplo localStorage
        
        - Fase 1: frontend
            - Debes de hacer un todo list que permita agregar, editar y eliminar
            - Estamos priorizando velocidad así que puedes hacer los atajos que gustes
            - Debe de ser completamente funcional
            - Calificar
                - Manejo de arrays
                - Ciclo de vida
                - velocidad
        - Fase 3: Guardar la data en local storage
        - Fase 2: Estilar el proyecto
            - Puedes utilizar una UI library tal como bootstrap o Material UI
            - No debe de verse completamente feo
            - Los estilos son libres, pero puntos extra si usas styled-components
            - Se sigue priorizando velocidad
        - Fase 4: backend
            - Conectar el todo list a un api REST, base de datos al gusto del programador
    - Hacer un buscador
- Algoritmos