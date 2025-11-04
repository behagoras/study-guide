# Preguntas técnicas de entrevista

https://roadmap.sh/

[https://github.com/leonardomso/33-js-concepts](https://github.com/leonardomso/33-js-concepts)

## html

- Qué es html semántico
- Para qué sirve el html semántico
    - Accesibilidad
    - Developer Experience (DX)
    - SEO
- section vs article
- etiquetas meta
- atributos aria
- importar css en html
    - link
- Cómo podemos importar estilos según el dispositivo que estamos manejando (impresión, teléfono, tablet, computadora)
- Cuál es la estructura básica de un documento html? (modelo de arbol)
- Por qué se pone hasta el final la etiqueta de script?
- DOM

## CSS

- Cómo seleccionar un elemento html en css
- Qué tipo de selectores existen?
    - clase
    - id
    - universal
    - etiqueta
- Cómo funciona la Especificidad en CSS
- para qué sirve display
    
    Para especificar el comportamiento del elemento
    
- Qué define la altura en un inline
    
    line-height
    
- Qué define la altura de un bloque?
    - Modelo de caja
    - height, padding
- Qué es `flexbox`
- Qué es `grid`
- Cuál es la diferencias principales entre grid y flex?
- Lazy loading CSS
- 10 formas de `desaparecer` un elemento del `viewport`
    - opacity: 0;
    - visibility: hidden;
    - display: none;
    - position: absolute; top: -9999px;
    - width: 0; height: 0; margin: 0; padding: 0; border: 0; line-height: 0; /* sólo en caso de elementos inline-block */ overflow: hidden;
    - z-index
    - transform: scale(0) ## JavaScript
    - background del mismo color del contenido
    - alpha 0

## Javascript

- Qué es un `objeto` en javascript
- Qué no es un objeto?
- Qué es el `prototype`
- Qué es una clase en javascript
- Qué es un arrow function
- Qué diferencia una arrow function de una función normal
- Qué es el objeto this
- Scope del this
- scope
    - function scope
    - global scope
    - block scope
- Cuál es la diferencia de var y let
- Cómo funciona el hoisting desde la perspectiva del eventloop
- event loop
- Qué es una promesa?
- Qué son los 3 puntos en javascript?
- Qué es el lazy loading
- Existe alguna manera de cargar estilos de manera lazy con async await?
- Cómo podemos agregar o quitar una clase de un elemento en javascript
- Qué son las high order functions
- [**Expression vs Statement**](https://github.com/leonardomso/33-js-concepts#7-expression-vs-statement)

## React

- Qué es jsx
- Qué es React y qué no es React en las aplicaciones de React?
- Qué es un componente de clase
- Diferencias entre un componente de clase y function
- Cómo puedo pasar información de un componente padre a un componente hijo
- Cómo puedo pasar información de un componente hijo a un padre
- Cuál es el ciclo de vida de un componente
- Cómo puedo acceder al estado en un componente funcional
- Qué son los render props, High order components
- 

## English

- What is your best success in your last project
- How would you convince to use React to a client for your next project
- Why do you like React
- Tell me about yourself

## Bonus deseable

- Leer un libro de estructuras de datos e implementarlo en un lenguaje desconocido

# Frontend

- ¿Qué diferencia hay entre Server Side Rendering y Client Side Rendering?
    
    El server SSR hace un prerenderizado del sitio web desde el servidor, mientras que el CSR renderiza en tiempo de ejecución.
    
- ¿Qué beneficios tiene la utilización de componentes en una aplicación Web?
    
    En general es que con componentes el código es más escalable, pero algunas de los beneficios específicos serían:
    
    1. Se genera código más legible que suele ser semántico, dividiendo el código en componentes que tienen funciones muy específicas, lo que hace que el código sea más mantenible (modularización del código)
    2. Reutilización de código: Al crear componentes, éstos son reutilizables gracias al poco acoplamiento que tienen
    3. Facilita el trabajo en equipo: al crear componentes pequeños y desacoplados hace más fácil que más de una persona esté trabajando en el mismo código sin pisar los trabajos de los demás.
- ¿Qué es CSS Grid?
    
    Es un sistema de retículas de CSS en 2 dimensiones dónde se define el tamaño de la rejilla desde el padre, mismo que tiene cierto control sobre los hijos.
    
- ¿Qué es un Closure?
    
    Es una función que guarda referencia de su contexto (puede acceder a variables externas a la función) donde las variables del padre del closure siguen existiendo después del llamado de la función.
    
- ¿Qué característica de JavaScript permite que sea un lenguaje no bloqueante?
    
    Las promesas y los callbacks
    
- ¿Qué es la programación reactiva?
    
    Es un paradigma de programación orientado a flujos de datos (muy utilizado para lidiar con datos asíncronos) especializado en la propagación de datos mediante la generación de observables.
    
- ¿Qué diferencia hay entre instalar una dependencia de desarrollo y una de producción en JavaScript?
    
    Las dependencias de desarrollo (dev dependencies) son dependencias (librerías) que utilizarás en tu aplicación sólamente a la hora de desarrollar, como librerías de testing, transpiladores, servidores de desarrollo, etc, mientras que las dependencias de producción son dependencias que se utilizan tanto para desarrollo como producción.
    
    Las diferencias son casi meramente de organización, a miprograma le da igual si la dependencia es de producción o de desarrollo, lo que le interesa es que se encuentre el paquete en mi node_modules en la mayoría de casos.
    
    Aunque existe un caso en el que sí podría tener una diferencia real, en el que en un servidor tenga poco espacio podría instalar sólo las dependencias de producción con el comando npm -i —only=prod
    
- ¿Por qué utilizar Webpack o un enpaquetador de código?
    
    Para mantener una buena developer experience, mientras webpack empaqueta tu código optimizándolo para que corra de manera optimizada.
    
    Además existen funcionalidades que los lenguajes no pueden hacer, por ejemplo, javascript no entiende lo que es un archivo css, así que webpack te puede permitir importar un archivo en javascript y que en la versión de producción éste se importe de manera correcta (en el html).
    
    De esta manera programas como gustes y webpack te convierte a los formatos correctos
    
- ¿̣Qué diferencias hay entre el Session Storage, Cookies y Local Storage?
    
    La Session Storage guarda data mientras la pestaña está abierta mientras que el local storage no expira y se mantiene en el browser (persiste) hasta que se borre por js o liberando el caché, las cookies sirven más para comunicación con el servidor donde con cada petición viaja la cookie por lo que no se recomienda hacerlas pesadas.
    
- ¿Por qué se dice que las **SPA** usualmente no tienen un buen SEO?
    
    Porque las Single Page Applications renderizan la información en tiempo de ejecución lo que hace que los robots no puedan acceder al contenido de manera sencilla (ya que Google no es tan bueno leyendo javascript)
    
- ¿Qué función cumplen los preprocesadores?
    
    Ayudar al programador a facilitar su escritura de código, traspilando de un lenguaje con más funcionalidades (como variables, mixins y funciones) a un lenguaje más limitado (como html o css)
    
- ¿Qué es el Hoisting?
    
    Es la elevación de la declaración de variables o funciones, las variables declaradas con var y las funciones con sintaxis previa a ES7 ( function(){} ) elevan su declaración al principio de la función en la que fueron definidas, cabe destacar que sólo elevan su declaración por lo que si haces uso de una variable antes de que le asignes valor, no lo va a tener en ese momento y las funciones al ser declaradas ya pueden ser usadas.
    
- ¿Qué es un High Order Component en React?
    
    Los HOC son una técnica en la que una función regresa un componente, teniendo acceso a las variables de la función (suelen ser accedidos mediante el estado o las props), es muy utilizada esta técnica para hacer fetching de datos.
    
- ¿Tailwind CSS, Materialize, Bootstrap y Foundation son?
    
    Frameworks CSS
    
- ¿Por qué no es buena práctica usar jQuery en 2022?
    
    Lo principal es porque jQuery es una librería muy pesada que no es necesaria en nuestros flujos porque el lenguaje hace la mayoría de las cosas importantes como seleccionar elementos, hacer fetching de data o agregar eventos, jQuery nació en momentos en los que estas cosas eran difíciles, pero el lenguaje evolucionó, en parte gracias a los avances que generó jQuery en su momento.
    
- Patrones de diseño en el frontend
- ¿Cómo funciona el patrón de diseño Singleton?
    
    Se refiere a que sólo debería poder existir una instancia de una clase particular, por lo tanto se debe de tener una función que revise si existe una instancia de la clase, si no existe la debería crear y si existe, puede utilizarse.
    
    Un buen ejemplo de esta implementación sería en Redux donde se genera una store que es única (única fuente de la verdad) por lo tanto siempre que se quiera acceder a la data de la store, se sabrá que sólo hay un lugar de donde sacarla y no hay diferencias entre la data (porque es la misma)
    
- ¿Qué diferencias hay entre el DOM y el Virtual DOM?
    
    El DOM es lo que el árbol de elementos reales en el browser mientras que el DOM virtual es una copia en js del DOM que existe para facilitar las modificaciones del DOM al tener una referencia del arbol original.
    
    Si se desea modificar algo en el DOM, primero se modifica en el virtual dom, se comparan los cambios y en el DOM se modifican exactamente los nodos que cambiaron.
    
- ¿Qué diferencia a una PWA de una aplicación Bridge?
    
    Una progressive web app es una aplicación web instalable en el dispositivo, pero sigue siendo una aplicación web, por lo tanto puedes acceder a ella mediante el navegador y funciona en tiempo de ejecución.
    
    Mientras que una aplicación bridge son programadas en un lenguaje bridge (como React Native) y se compila a código máquina, por lo tanto en las aplcaciones bridge tienes acceso al hardware y hay una compilación previa a la instalación de la apl
    
- ¿Qué diferencia una Single Page Application de una Multi Page Application?
- ¿En cuántos hilos de ejecución corre JavaScript y por qué es importante?
    
    1
    

# Backend

- ¿Cuál es la diferencia entre GET y POST?
- Menciona los verbos disponibles en REST
    - get,
    - post,
    - delete,
    - put,
    - patch
- ¿Cuáles son los flujos de datos estándar en cualquier comando que ejecutemos en una terminal Linux?
- Un Stream es un trozo de memoria temporal que almacena información hasta que es consumido por medio de un Buffer.
- ¿Para qué sirven las variables de entorno de un sistema operativo?
- ¿Qué caso de uso es el más común para una base de datos basada en documentos como MongoDB?
    
    ​ En aplicaciones que requieren mucha analítica
    
    ​ En aplicaciones real time que hacen uso de machine learning
    
    ​ En aplicaciones muy rápidas con estructuras en sus datos de tipo JSON
    
    ​ En aplicaciones real time donde necesitamos saber el estado actual de una aplicación rápidamente
    
    ​ En aplicaciones real time donde necesitamos una estructura rígida a base de esquemas
    
- ¿Cuál es la principal ventaja de GraphQL sobre una API REST?
    
    Hacer peticiones on demmand
    
    frontend based application
    
- ¿En qué casos se utiliza PUT y PATCH?
    
    ​ PUT para actualizar todo el recurso y PATCH para hacer una actualización parcial
    
    ​ PUT para hacer una actualización parcial y PATCH para actualizar todo el recurso
    
     No hay diferencia real, los dos son estándares
    
- ¿MongoDB es Schema Less (sin esquema)?
    
    Sí, pero puedes trabajar con schemas utilizando librerías como mongoose
    
- ¿Qué es el contenido estático en un servidor web?
- Son buenas prácticas para el despliegue en producción
    
    ​ Agregar HTTP/2 y SOCKETS
    
    ​ Ofuscar los secrets y keys en el código
    
    ​ Deshabilitar el soporte de cache
    
    ​ Activar todos los tipos de logs de errores posibles
    
    ​ Agregar HTTPS y CORS
    
- ¿MongoDB es una base de datos distribuida?
- Menciona al menos dos tipos de bases de datos no relacionales (NoSQL)
    
    mongoDB, firestore
    
- Una aplicación Express es fundamentalmente una serie de llamadas a funciones de middleware.
    
    Verdadero
    
- ¿Cómo funciona el Layer Chche o las capas de una imagen de Docker?
    
    
- ¿Qué es un Middleware?
- ¿Cómo debe informar el servidor acerca de errores ocurridos durante el procesamiento de un pedido?
- Los métodos más usados de un Readable Stream son: *
    
    ​ data(), pipe(), error(), push()
    
    ​ pipe(), unpipe(), read(), push()
    
    ​ pipe(), end(), push()
    
    ​ data(), end(), error(), read()
    
- Diferencia entre una imagen y un contenedor en Docker
- Qué es CORS
- Programación reactiva
    
    > Es un paradigma de programación que se utiliza para trabajar con datos asíncronos donde se propagan cambios entre las variables de manera sencilla y automágica mediante la generación de observables.flujos de datos finitos o infinitos de manera asíncronaPor ejemplo, si tengo una operación a=b+c el valor de a automaticamente es actualizada cuando los valores de b o c cambian, sin tener que volver a ejecutar la sentencia.Una variación sería la programación funcional reactiva dónde se filtran, transforman o resumen los flujos de datos que se reciben de manera asíncrona y se transforman en datos que sean más útiles para la lógica de la aplicaciónPropagar cambios entre las variables y trabajar con flujos asíncronos de datosEs un paradigma de programación donde al actualizar un valor que reciba una operación, el resultado se actualiza de manera automática sin tener que volver a llamar la operación.Patrón de ObservadorFrogramación funcional reactiva nos permite filtrar, transformar y resumir los flujos de datos asíncronos para transformarlos en tipos que funcionen mejor para el flujo de nuestra aplicaciónObservables y observadoresDatos en tiempo real o interfaces gráficas
    > 

- ¿Qué es un Closure?
- Patrones de diseño que suelo utilizar
    
    Singleton: 1 instance per Object definition, never more than 1
    Global state
    Database
    
    State pattern: Object will behave different deppending what state It is
    
    PubSub
    
    Observer pattern:
    suscribe
    unsuscribe
    message
    
    ```
      eventListeners
      sockets
    
    ```
    
    Decorator pattern
    
    Dependency injection pattern
    
- Strict mode:
    
    Is for telling the browser or context to avoid the use of undeclared variables
    
- Set:
    
    IS a collection of values, there can only be an instance of the containing objects once
    
    ```
    Can know If It has a key
    It's perfect to avoid duplicity of values (which can let to not knowing If the value is deleted or not deleted)
    
    ```
    
- Types in js:
    
    primitive:
    number
    string
    boolean
    undefined
    null
    
- Virtual DOM
    
    Is a javascript copy of the actual DOM which is easier to work within javascript.
    
- High Order Component
    
    It's a function that returns a Component, the particularity of this is tha has a context in which can return different types of components depending of certain logic
    
- The component lifecycle
    
    A lifecycle
    
    custom code called at given times
    
    componentDidMount
    componentDidUpdate
    render
    componentWillUnmount
    
- State vs props
    
    A component manage his own state and the props are the tool that comunicate between components
    
    In terms of code, a parent component can send props as a message to their childrens, and the state is managed within the components via events and logic.
    
    The state of a component is where we store property values that belongs to the component
    
    The state is a design pattern in which we can do things deppending on the state of the component, In general terms the component will render differently or do different things depending of his state or states.