oct 7, 2026

## **Reunión del 6 oct 2026 a las 20:18 GMT-05:00**

Registros de la reunión [Transcripción](https://docs.google.com/document/d/1OMb6EsyE-DFQnhAfpysILfDa3Y_5sR9avQHaSH6GfA0/edit?usp=drive_web&tab=t.l9hk073dz0ky) [Grabación](https://drive.google.com/file/d/1LS-Ridk82sdZ4f0stg0rprIordGTLaGp/view?usp=drive_web) 

### **Resumen**

Presentación y revisión del software para Torre Satori con integración de chatbot y gestión web.

**Presentación inicial del sistema**  
Esteban Guarin Valencia y Juan Felipe Garzon Trejos presentaron el chatbot y la aplicación web para Torre Satori.

**Módulos de reservas y finanzas**  
Se detallaron las funciones de reservas, gestión de inventario y el panel de finanzas con gráficos de ingresos.

**Arquitectura y próximos pasos**  
HAZ TOPE expuso la arquitectura tecnológica y se fijó el mes de noviembre para la entrega final.

### **Decisiones**

## **Requiere más debate**

* **Definición de políticas y penalizaciones por cancelación** La configuración de las penalizaciones y reglas por cancelación en el chatbot quedó pendiente de definir según la normativa y políticas del hotel.

## **Acordada**

* **Incorporación de pantallas para restaurante y experiencias** Se acordó agregar al sistema PMS nuevas pantallas para la gestión del restaurante y de experiencias de café.  
* **Sincronización automática de reseñas con Google** Se acordó añadir la funcionalidad para transferir automáticamente las reseñas de los clientes de WhatsApp a Google.

### **Próximos pasos**

- [ ] \[Frank Arias Salgado\] Entregar inventario de habitaciones: Proporcionar la base de datos detallada con la oferta de habitaciones del hotel.  
- [ ] \[Frank Arias Salgado\] Entregar lista de precios: Facilitar el documento con los precios actualizados de las habitaciones según las temporadas.  
- [ ] \[Frank Arias Salgado\] Entregar carta de desayunos: Enviar el listado del menú de desayunos para su integración en el sistema.  
- [ ] \[Frank Arias Salgado\] Definir políticas de cancelación: Establecer la normativa de penalizaciones por cancelaciones para configurar la lógica en el chatbot.  
- [ ] \[El grupo\] Crear pantalla de restaurante: Desarrollar e integrar una sección para la gestión de ventas de desayunos.  
- [ ] \[El grupo\] Crear pantalla de experiencias: Desarrollar e integrar una sección para la reserva de actividades como barismo y procesos de café.  
- [ ] \[El grupo\] Investigar integración de reseñas: Evaluar la viabilidad técnica para conectar las reseñas del chatbot con Google Reviews.  
- [ ] \[El grupo\] Configurar WhatsApp Business: Organizar la foto de perfil, nombre y catálogo en el perfil de WhatsApp del hotel.  
- [ ] \[Juan Felipe Garzon Trejos, Esteban Guarin Valencia\] Reservar alojamiento: Realizar la reserva del hotel en Sevilla para el viaje.  
- [ ] \[R\] Entregar video: Compartir el archivo de video con los interesados.

### **Detalles**

* **Introducción a la versión web y de chatbot para Torre Satori**: Esteban Guarin Valencia y Juan Felipe Garzon Trejos presentaron la versión preliminar del software para la Torre Satori, la cual se compone de un chatbot de WhatsApp y una aplicación web de gestión (PMS) ([00:02:05](#00:02:05)). Juan Felipe Garzon Trejos explicó que la pantalla inicial corresponde al inicio de sesión centralizado, donde únicamente el administrador tiene permisos para asignar credenciales a las recepcionistas ([00:03:48](#00:03:48)). Frank Arias Salgado evaluó la presentación y se acordó continuar con la revisión de las interfaces ([00:02:05](#00:02:05)).  
* **Dashboard principal y creación de reservas presenciales**: Juan Felipe Garzon Trejos mostró el panel principal (dashboard) que incluye métricas de habitaciones ocupadas (una de cinco), porcentaje de ocupación, llegadas, salidas, habitaciones en limpieza, ventas del día y accesos rápidos ([00:05:01](#00:05:01)). Frank Arias Salgado calificó la interfaz como completa ([00:06:06](#00:06:06)). Juan Felipe Garzon Trejos demostró el módulo de creación de reservas presenciales, ingresando fechas, cantidad de huéspedes, mascotas y seleccionando una habitación disponible por un costo de 180,000. Se estableció que al iniciar una reserva se activa un bloqueo temporal de 15 minutos en el chatbot para evitar dobles reservas, registrando datos de prueba como el nombre de Laura Gómez y un pago parcial en efectivo ([00:07:16](#00:07:16)).  
* **Pantalla de lista de reservas y calendario semanal**: Juan Felipe Garzon Trejos detalló la pantalla de lista de reservas, la cual muestra códigos identificadores, datos del huésped, teléfonos, habitaciones, fechas, canales, estados de pago y saldos pendientes con herramientas de filtrado ([00:09:44](#00:09:44)). Frank Arias Salgado validó que la información presentada es completa ([00:10:45](#00:10:45)). Adicionalmente, Juan Felipe Garzon Trejos expuso el calendario semanal con filtros por estado y habitación ([00:11:50](#00:11:50)). Ante la consulta de Frank Arias Salgado sobre la variación de precios por temporada, Juan Felipe Garzon Trejos aclaró que el administrador podrá configurar tarifas y fechas especiales desde su perfil, solicitando un documento con los precios base del hotel ([00:13:03](#00:13:03)).  
* **Módulos de llegadas, checkouts y gestión de inventario de tienda**: Juan Felipe Garzon Trejos presentó las pantallas de llegadas y checkouts, mostrando el registro de pagos de hospedaje y consumos de tienda (cerveza, papas, gaseosa) junto con la actualización automática de la habitación a estado de limpieza ([00:13:59](#00:13:59)). Se revisó el inventario de la tienda con productos de ejemplo, momento en el cual Frank Arias Salgado señaló un error al incluir una marca externa (Juan Valdés), acordando utilizar productos propios como "Salgados Café" y permitir la adición de nuevos productos desde la administración ([00:16:24](#00:16:24)). Juan Felipe Garzon Trejos indicó que los cobros pueden realizarse de forma inmediata mediante efectivo, datáfono, transferencia o cargarse directamente a la habitación ([00:18:21](#00:18:21)).  
* **Requerimientos adicionales de restaurante y experiencias de café**: Frank Arias Salgado solicitó incorporar a futuro la venta de desayunos, servicios en el mirador y experiencias de barismo o catas de café vinculadas a la maquila del hotel ([00:19:22](#00:19:22)). Juan Felipe Garzon Trejos y Esteban Guarin Valencia tomaron nota para desarrollar las pantallas de restaurante y experiencias, las cuales permitirán pagos directos o cargos a la habitación ([00:20:14](#00:20:14)). Juan Felipe Garzon Trejos solicitó que la carta de desayunos y el inventario respectivo se entreguen en un documento por parte del cliente ([00:21:03](#00:21:03)).  
* **Funcionalidad del chatbot de WhatsApp y opciones de reserva**: Esteban Guarin Valencia explicó que el chatbot automatiza la atención al cliente guiándole en la selección de fechas, cantidad de personas y mascotas, aplicando un bloqueo temporal de 15 minutos para prevenir reservas duplicadas ([00:21:03](#00:21:03)). Juan Felipe Garzon Trejos y Esteban Guarin Valencia añadieron que si la persona prefiere la atención humana, el chatbot escala la conversación al panel de recepcionistas a través de la API de WhatsApp ([00:23:29](#00:23:29)). HAZ TOPE y Esteban Guarin Valencia mencionaron el desarrollo futuro de reservas mediante lenguaje natural con inteligencia artificial y la integración de pasarelas de pago para enviar enlaces de pago directos ([00:25:49](#00:25:49)).  
* **Consulta y cancelación de reservas por parte del huésped**: Esteban Guarin Valencia explicó que los huéspedes pueden utilizar un código de reserva para consultar el estado de su habitación y proceder con la cancelación bajo un sistema de doble confirmación que desbloquea automáticamente la habitación. Ante la consulta de Frank Arias Salgado sobre posibles penalizaciones por cancelación tardía ([00:28:18](#00:28:18)), Juan Felipe Garzon Trejos y Esteban Guarin Valencia aclararon que las políticas de devolución dependen de la normativa del hotel y deben ser provistas por el cliente para su configuración en el chatbot ([00:29:30](#00:29:30)).  
* **Panel de administración, auditoría y finanzas**: HAZ TOPE y Juan Felipe Garzon Trejos presentaron el perfil de administración, destacando el módulo de auditoría que registra cada operación, inicios de sesión, acciones y accesos fallidos con fines de seguridad ([00:30:18](#00:30:18)). HAZ TOPE y Juan Felipe Garzon Trejos mostraron el panel de finanzas con gráficos de ingresos, egresos y balances filtrables por mes o año, la función de exportación a Excel y el registro manual de egresos (como servicios públicos o mantenimiento) con opción de adjuntar facturas ([00:33:19](#00:33:19)). HAZ TOPE agregó que el módulo de reportes incluye estadísticas de rotación de productos de tienda y porcentajes de ocupación ([00:34:50](#00:34:50)).  
* **Gestión de usuarios y análisis de automatización futura**: HAZ TOPE indicó que el administrador puede asociar o desasociar cuentas de recepcionistas y realizar funciones operativas. Frank Arias Salgado planteó la posibilidad de eliminar en el futuro el rol de recepcionista e implementar cerraduras electrónicas con códigos ([00:37:28](#00:37:28)). Juan Felipe Garzon Trejos y Esteban Guarin Valencia respondieron que, aunque técnicamente factible, requeriría una reestructuración completa del software y el chatbot hacia un modelo 100% automatizado, por lo que se mantendrá el esquema actual por ahora ([00:38:58](#00:38:58)). Frank Arias Salgado expresó conformidad con el diseño presentado ([00:39:48](#00:39:48)).  
* **Reseñas de clientes e integración con Google**: Juan Felipe Garzon Trejos señaló que el administrador podrá visualizar las reseñas enviadas por los clientes a través de WhatsApp. Frank Arias Salgado sugirió transferir dichas reseñas automáticamente a Google Reseñas para mayor impacto comercial. Esteban Guarin Valencia confirmó que la tecnología utilizada permite añadir dicha integración de manera automática. Juan Felipe Garzon Trejos y Frank Arias Salgado acordaron optimizar el perfil de WhatsApp Business, catálogos y accesos digitales ([00:40:41](#00:40:41)).  
* **Arquitectura de la solución y próximos pasos**: HAZ TOPE presentó la arquitectura tecnológica del sistema, la cual comprende canales de usuarios (huésped, administrador, recepcionista), base de datos de persistencia, backend y servicios externos como la API de WhatsApp, el motor de inteligencia artificial y la pasarela de pagos ([00:42:41](#00:42:41)). Frank Arias Salgado validó la estructura propuesta ([00:44:23](#00:44:23)). El equipo fijó como plazo el mes de noviembre para la entrega final del proyecto funcional ([00:45:51](#00:45:51)).

*Revisa las notas de Gemini para asegurarte de que sean precisas. [Obtén sugerencias y descubre cómo Gemini toma notas](https://support.google.com/meet/answer/14754931)*

*Cómo es la calidad de **estas notas específicas?** [Responde una breve encuesta](https://google.qualtrics.com/jfe/form/SV_5bXzKQfylMIhSXc?confid=pVquZC8nlLHymYPGe42jDxIYOBEQAjIGCIoCIAAYAQg&detailLevel=standard&hasImages=False&entryPoint=footerMain&isGoogler=False) para darnos tu opinión; por ejemplo, cuán útiles te resultaron las notas.*

oct 7, 2026

## **Reunión del 6 oct 2026 a las 20:18 GMT-05:00 \- Transcripción**

### **00:02:05** {#00:02:05}

**Santiago Gomez Robledo:** Ya. Ah, pena.

**Juan Felipe Garzon Trejos:** Faria, no.

**Esteban Guarin Valencia:** Listo.

**HAZ TOPE:** Creo que está grabando.

**Esteban Guarin Valencia:** Buenas noches. ¿Cómo están nosotros?

**Frank Arias Salgado:** Buenas noches. Bien, gracias.

**Esteban Guarin Valencia:** Pues aquí podemos pues queremos presentarle cómo va cómo se vería, digamos la web, lo de lo que vendría siendo eh la página de de la para la Torre Satori, digamos, como para presentarle cómo sería la pestaña de los financiamientos, digamos, cómo se sería reservar una habitación, cómo serían los horarios, cómo sería toda esta parte para ver si pues está

**Juan Felipe Garzon Trejos:** Ah.

**Esteban Guarin Valencia:** a gusto, como le gustaría a usted eh que viera la página o

**Juan Felipe Garzon Trejos:** Esta

**Esteban Guarin Valencia:** como usted quisiera, digamos, que sea fácil de hacer una cosa luego la otra, pues cualquier comentario pues que ustedes es cambiar o que vea que no le gusta o que quisiera añadir, pues se podría comentar.

**Frank Arias Salgado:** Listo.

**Juan Felipe Garzon Trejos:** es una versión eh pues va a tener dos dos partes. La primera es un chatbot de WhatsApp y el segundo es la aplicación web donde se va a llevar todo el tema de la gestión.

### **00:03:48** {#00:03:48}

**Juan Felipe Garzon Trejos:** de del PMS como tal. Entonces, por aquí te voy a mostrar. Este es el la pantalla de inicio. Eh, voy a probarlo aquí con un correo que, por ejemplo, no tenemos registrado en la base de datos, cualquier contraseña. Y si le damos, espérame que dame un segundo, espér un segundo que se me cayó acá. Tocar volver a empezar el a grabar. Espérame, espérame. Ah, no, ya.

**HAZ TOPE:** Igual la grabación la recortamos.

**Juan Felipe Garzon Trejos:** Okay. Okay. Listo. Bueno. Bueno, aquí tenemos la primera pantalla. Esta primera pantalla es la de login o inicio de sesión. Eh, pues como va a ser centralizado solamente el administrador va a ser quien pueda crear las el como tal el asignar un correo y una contraseña a las recepcionistas. Eh, no va a tener de registro, sino solamente de login.

### **00:05:01** {#00:05:01}

**Juan Felipe Garzon Trejos:** En este caso, si pruebo con un correo cualquiera que no tenemos registrado, él va a dar correo contra incorrectos. Sin embargo, eh al ingresar con un con el módulo de recepción, que es un correo ya asignado a la base de datos y una contraseña ya asignada a la base de datos, vamos a ingresar correctamente. Esto como tal es una demo, entonces tenemos también datos aleatorios para probar todos los requerimientos de del software. Entonces, bueno, en esta primera pantalla es como un dashboard principal donde tenemos las habitaciones ocupadas del hotel. En este caso, una de cinco nos muestra el porcentaje de ocupación del hotel. Eh, las llegadas de hoy, las que se han registrado, en este caso cero, las salidas de hoy, una, la marca como pendiente, eh las habitaciones que están en limpieza, las marca aquí, eh las ventas del día, eh, Tenemos un una pequeña pestaña de acciones rápidas como lo son para crear una reserva, para realizar un checking, para realizar un checkout o para realizar una venta.

### **00:06:06** {#00:06:06}

**Juan Felipe Garzon Trejos:** Eh, asimismo también tenemos eh una pequeña pestaña para las conversaciones de WhatsApp. Eh, tenemos los próximos checkins, un registro de los checkins que vienen, sería para mañana, este para el domingo de octubre, también una pestaña de próximos checkouts y eh una pequeña gráfica del estado de las habitaciones, de cuáles están libres, cuáles están ocupadas, cuáles están en limpieza y cuáles en mantenimiento. ¿Qué qué te parece esta primera pantalla?

**Frank Arias Salgado:** Muy chévere, pero o sea, está completa. Ah.

**Juan Felipe Garzon Trejos:** Okay, perfecto. Esta es una primera pantalla que muestra como un esquema de todo lo que está pasando en este momento en el hotel. Eh, si nos vamos a la segunda, eh, bueno, hagámoslo desde acá para vamos a crear una reserva. Entonces, le damos a nueva reserva. Acá nos permite acceder a esto es en este caso, si una persona llega al hotel y necesita hacer la la reserva y la recepcionista se la va a hacer, o sea, no lo estamos tomando como que la hizo por el chatbot, sino que lo está haciendo de forma presencial, que esa también fue uno de los requerimientos que vamos a cumplir.

### **00:07:16** {#00:07:16}

**Juan Felipe Garzon Trejos:** Entonces, la recepcionista lo que haría pues sería poner las fechas, digamos que la persona entra este sábado y eh pongamos la que sale el día lunes. cantidad de huésped, ponerle uno, una sola persona y que viaja con mascota. Entonces, acá nos va a aparecer las habitaciones disponibles que tenemos. Obviamente todo esto se va a hacer que te va a tener que meter a la base de datos previamente. Eh, vamos a elegir una habitación que esté libre. En este caso, digamos que la persona desea h esta de 180,000. Obviamente todo ese tema de de los precios de las habitaciones, de qué habitaciones tenemos y todo eso, tenemos que pues hablarlo contigo para que nos entregues como tal el la base de datos que tiene el hotel en cuanto a sus habitaciones, a sus habitaciones que ofrece. Entonces, todo esto es modificable en caso de cuando tengamos ya la información real del hotel. Esto es una un requerimiento también que estamos cumpliendo, que cada vez que se empieza una reserva se bloquea también en el chatbot.

### **00:08:23**

**Juan Felipe Garzon Trejos:** Entonces una persona que si está en caso de WhatsApp realizando otra reserva, la aplicación, la la habitación se le va a mostrar bloqueada. Entonces, mira, por ejemplo, acá ya va a activar un bloqueo de 15 minutos, que es más o menos un rango de tiempo para para realizar la reserva. Pongámosle Laura Gómez, un nombre ejemplo. Vámosle 310\. número, una cédula y que la reserva e pues se va a realizar por medio de recepción. Aquí nos muestra un resumen de la reserva como tal, el nombre del huésped, la habitación que seleccionó, las fechas, cuántas personas son, eh la la habitación, eh y acá ya ponemos el tipo de pago, si la persona va a pagar en efectivo, si va a pagar con datáfono, si va a pagar con transferencia o si va a dejar el pago pendiente eh hasta que la persona desee. Entonces, por ejemplo, pongámoslo que él está en efectivo y que lo paga la mitad de anticipo. En este caso, la reserva se crea, efectivamente se crea y si le damos a ver detalle no sale la reserva que realizó ella.

### **00:09:44** {#00:09:44}

**Juan Felipe Garzon Trejos:** Entonces, aquí ya nos envía la pestaña de reservas, donde está la lista de reservas. Aquí tenemos la que yo hice, donde podemos observar el nombre de la persona, su teléfono, su documento, el canal por el que realizó la reserva, los huéspes y se lleva mascota, el saldo que debe, lo que ha pagado y el historial como tal de de la reserva. Eh, bueno, les vamos a mostrar la pantalla de reservas. Esta es la pantalla de reservas donde vamos a tener todas las reservas que tiene el hotel. Eh, estas que puse acá pues son de demostración. Todo esto es para para ver más o menos. Entonces, ¿qué va a mostrar esta pantalla? Va a mostrar eh un código identificador de la reserva. va a mostrar a qué huésped se le hizo la reserva, su número de celular, qué habitación es, las fechas, el canal por el que realizó la reserva y en este caso el estado va a tener diferentes variaciones.

### **00:10:45** {#00:10:45}

**Juan Felipe Garzon Trejos:** Si está confirmada y pagó todo, si está confirmada pero pagó una parte y acá sale lo que debe. Si está pendiente de pago, en caso de que la reserva la haya realizado por pues por teléfono, eh, si está confirmada, pero tiene saldo. Si la reserva expiró, también nos va a marcar acá si está una reserva en curso, o sea, que en este momento está ya realizando la reserva y si finalizó también la marca. Asimismo también el estado de cancelado. ¿Qué tal está esta pantalla que también cuenta con con una pantalla para filtrar? Por ejemplo,

**Frank Arias Salgado:** Sí,

**Juan Felipe Garzon Trejos:** acá podemos filtrarlo por código,

**Frank Arias Salgado:** ahí están todos los datos.

**Juan Felipe Garzon Trejos:** hm, podemos filtrar acá por nombre. de la persona. Podemos filtrar por código 2058\. Esa sería donde va a tener va a llevar todos los los datos de de las reservas. Eh, bueno, también tenemos acá pues en casi todas es un acceso fácil para crear una reserva en caso de que llegue un cliente.

### **00:11:50** {#00:11:50}

**Juan Felipe Garzon Trejos:** Eh, bueno, este es una pantalla que va a ser el tema de del calendario, un calendario semanal para que sea de fácil acceso para para la recepcionista. Entonces, aquí lo podemos filtrar en tres semanas. Por ejemplo, esta fue la semana anterior. Eh, nos muestra las reservas que salieron, las que ya realizaron el checkout. esta que, por ejemplo, está en este momento, eh una habitación que está, por ejemplo, en mantenimiento o fuera de servicio. Todo esto lo filtra por habitación. Acá saldrían todas las habitaciones y saldría el estado en este momento de la habitación.

**Frank Arias Salgado:** Hm.

**Juan Felipe Garzon Trejos:** Y otra cosita importante es que si nos metemos acá al calendario y por ejemplo la recepcionista quiere eh agendar una reserva, ella puede agendarla ya sea por donde te mostré la de nueva reserva o aquí por el calendario si ella quiere ver la disponibilidad. Entonces, digamos que una persona desea reservar la la habitación jardín para el día miércoles, entonces ella directamente le da aquí y ya se le envía directamente la pastaña de reserva.

### **00:13:03** {#00:13:03}

**Juan Felipe Garzon Trejos:** Entonces,

**Frank Arias Salgado:** Mm.

**Juan Felipe Garzon Trejos:** también es un acceso fácil que que le hicimos a la a la aplicación. E, ¿qué más? Pues nada, esta es la pantalla de calendario. ¿Qué tal está?

**Frank Arias Salgado:** Sí. Una pregunta ahorita que está ahí el calendario, como de todas maneras eh los precios dependiendo de la temporada pues varían también van a cambiar los precios.

**Juan Felipe Garzon Trejos:** Mm.

**Frank Arias Salgado:** Entonces, eso también lo tuvieron en cuenta.

**Juan Felipe Garzon Trejos:** Esa esa parte se realizaría por medio de de la pantalla de administración, que él es quien puede evitar el precio de las habitaciones. Entonces, imagino que el administrador del hotel en ese caso lo que haría sería entrar en su perfil, que ahorita lo vamos a ver, entrar en su perfil y según la habitación cuadrarle los precios según la fecha, pero sí también va a tener esa disponibilidad.

**Frank Arias Salgado:** Y, por ejemplo, los puentes.

**Juan Felipe Garzon Trejos:** Mm. Sí, señor. Eso se puede poner.

### **00:13:59** {#00:13:59}

**Juan Felipe Garzon Trejos:** Igualmente también tenemos que que tú nos entregues eh más o menos una como un documento que tenga los precios de las habitaciones para nosotros adaptar todo el software que realizamos al al hotel ya como tal, a los datos del hotel reales.

**Frank Arias Salgado:** Mhm.

**Juan Felipe Garzon Trejos:** ¿Listo? Eh, bueno, acá tenemos una una pantalla de llegadas que en caso de que hay una llegada para el día de hoy, aquí le va a salir a la recepcionista las llegadas que tiene eh para que tenga pues un control y esté pendiente de las llegadas del día. En este caso, como no tenemos, pues no sale ninguna. También tenemos una pantalla que es la pantalla de los checkouts, que en este caso e va a salir la una tenemos una salida para hoy,

**Frank Arias Salgado:** Perfecto.

**Juan Felipe Garzon Trejos:** un ejemplo de las 11\. Entonces, le damos acá en hacer checkout y e la persona lo que va a hacer es registrar el pago. Entonces, en este caso, esta persona unos peajes de tres noches, consumió en la tienda una cerveza Club Colombia, unas papitas, una gaseosa y ya pagó el hospedaje, pero debe todo el tema de la tienda.

### **00:15:13**

**Juan Felipe Garzon Trejos:** Entonces, la recepcionista cuando ya vaya a hacer el el checkout en la al salir,

**Frank Arias Salgado:** Sí.

**Juan Felipe Garzon Trejos:** entonces le dice a la persona pues cuánto debe y acá marca el el en dónde va a pagar la persona sin efectivo, sin datáfono, sin transferencia y registra el pago. Entonces acá marca si marca el próximo estado, si la va a pasar a de una vez a limpieza o si la va a pasar de una vez a a lista. En este caso vamos a ponerla que que va a quedar en limpieza. registra el pago y posteriormente completa el checkout. Entonces acá realiza el checkout y ya la habitación ya pasaría estado a a en limpieza. Aquí como ya saldría en en limpieza. Bueno, esa es para la pantalla de checkouts, que aquí ya lo realizamos. Acá tenemos también se pidió un requerimiento de que ustedes manejan una tienda como tal de de snacks y todo eso. Entonces, también se va a llevar todo el tema de del inventario de la tienda y el registro de ventas.

### **00:16:24** {#00:16:24}

**Juan Felipe Garzon Trejos:** esto para todo el tema de las finanzas y para que se tenga como pues para que el dueño del hotel, en este caso usted eh tenga como un control de todos los ingresos y los egresos del hotel. Entonces, para también tener registradas las ventas. Entonces, claramente tenemos que agregar los productos como como usted no nos indique los que tienen, los que venden, los que los que tengan ustedes en el hotel. En este caso hicimos unos ejemplos, agua, gaseosa, cerveza, café, una chocolatina, papita margarita, protector solar y un cepillo de dientes.

**Frank Arias Salgado:** Uy, pero que cómo cabé Juan Valdés ahí si la embarraron

**Juan Felipe Garzon Trejos:** Sí, ahí fue. Ese fue un Sí,

**HAZ TOPE:** a

**Juan Felipe Garzon Trejos:** ese fue ese fue un ejemplo.

**Esteban Guarin Valencia:** o o bien

**Juan Felipe Garzon Trejos:** Voy a poner el de ustedes. Sí,

**Frank Arias Salgado:** Salgados Café.

**Juan Felipe Garzon Trejos:** claro.

**Esteban Guarin Valencia:** o también digamos que se podría añadir la función de agregar producto, digamos de que ustedes mismos en cualquier momento sin consultarnos ni nada, pues pueden agregar al producto y se añade mismo.

### **00:17:26**

**Frank Arias Salgado:** Ah,

**Juan Felipe Garzon Trejos:** Mm. Sí, en este caso lo haría en el administrador,

**HAZ TOPE:** M.

**Juan Felipe Garzon Trejos:** haría el la la la agregar el producto. Entonces, bueno, acá tenemos para filtrarlo por todas, por solamente bebidas. por solamente snacks, por solamente cuidado personal. En caso de tener más categorías, pues se agregarán acá sin ningún problema. Eh, vamos a hacer un ejemplo de que una persona pues desea comprar un una gaseosa, digamos, una apostón. Ah, bueno, aquí otra cosa importante es que siempre vamos a tener el inventario de cuántas hay disponibles. Eso también es muy importante para saber cuáles son los productos que más se venden y asimismo eh para que usted los pueda ordenar para no ordenar de más y todo eso.

**Frank Arias Salgado:** Mhm.

**Juan Felipe Garzon Trejos:** Es es un factor muy importante para el tema de gastos. Bueno, vamos a agregar, digamos, una gasosa postobón. Eh, le damos acá continuar al cobro y acá nos va a pasar eh dos opciones.

### **00:18:21** {#00:18:21}

**Juan Felipe Garzon Trejos:** La primera es si la persona la está comprando ahí mismo en en la en la recepción. Entonces, si ella la va a comprar de una vez y uno se la va a entregar de una, pues entonces selecciona el método de pago, si es efectivo, datáfono, transferencia y hace el tema de cobrar y ya lo cobra y ya queda el registro. O la segunda opción es si lo si una persona desde la habitación pide el el producto. Entonces, en este caso le daría cargo a habitación y ah, bueno, aquí no tenemos habitación con reserva activa, eh, pero en este caso si le da cargo a habitación acá va a aparecer la habitación y se lo las habitaciones que están y según la habitación le va a cargar el producto para que al final se cobre así como como mostré anteriormente. En este caso, pongámosle un ejemplo con esta gase que va a corar con datáformo. Entonces, ya la venta queda registrada. Eh, bueno, eso sería un poquito de las pantallas de la que va a ver la recepcionista.

### **00:19:22** {#00:19:22}

**Juan Felipe Garzon Trejos:** ¿Qué tal están o qué qué se puede cambiar?

**Frank Arias Salgado:** un pues mira que o sea no no sé si no mire,

**Juan Felipe Garzon Trejos:** Agregar.

**Frank Arias Salgado:** pero de pronto nosotros más adelante vamos a vender el desayuno.

**Juan Felipe Garzon Trejos:** Mm.

**Frank Arias Salgado:** No sé si eso se incluiría ahí o también uno lo puede.

**Juan Felipe Garzon Trejos:** Oh. Okay. Sí, sí, sí, claro. Podemos ponerlo. Sería una nueva una nueva pantalla que en este caso sería como restaurante. Puede ser.

**Frank Arias Salgado:** Sí. Y nosotros también digamos que tenemos proyectado con el tiempo tener algo en el mirador o no sé,

**Juan Felipe Garzon Trejos:** Okay.

**Frank Arias Salgado:** no sé si de pronto algunos servicios, por ejemplo, como una experiencia de de barismo, porque como nosotros también tenemos el café y la maquila en en un local del

**Juan Felipe Garzon Trejos:** Mhm.

**Frank Arias Salgado:** hotel,

**Juan Felipe Garzon Trejos:** Okay.

**Frank Arias Salgado:** entonces digamos que eso también acostura nosotros que, o sea, pueden reservar con una experiencia de una testión de café.

### **00:20:14** {#00:20:14}

**Frank Arias Salgado:** Bueno,

**Juan Felipe Garzon Trejos:** Perfecto.

**Frank Arias Salgado:** de varismo.

**Juan Felipe Garzon Trejos:** Listo. Entonces, aquí estoy anotando eh las pantallas que se agregarían. Entonces sería una pantalla de restaurante y una pantalla de como experiencias que también se le pueden agregar a

**Frank Arias Salgado:** Sí,

**Juan Felipe Garzon Trejos:** la Okay,

**Frank Arias Salgado:** experiencia de todo lo que tiene que ver con maquilar café, todo lo que es trilla,

**Juan Felipe Garzon Trejos:** listo.

**Frank Arias Salgado:** tosteón y que la gente pues al final se lleve una libra de café que él mismo no haya procesado.

**Juan Felipe Garzon Trejos:** Okay, listo, ya queda anotado. Listo. Entonces, estas serían unas nuevas pantallas y pues serían muy similares a estas. Se pueden cargar a la habitación o se pueden pagar directamente en la recepción. Pero entonces listo, ya quedaron anotadas acá,

**Esteban Guarin Valencia:** Ya.

**Juan Felipe Garzon Trejos:** ¿eh?

**Esteban Guarin Valencia:** Ya pues esas nuevas pantallas pues tocará que ir hablándolas con el transcurso de tiempo, digamos,

### **00:21:03** {#00:21:03}

**Juan Felipe Garzon Trejos:** Mm.

**Esteban Guarin Valencia:** como para añadir algunas cositas o algunas preguntas que tengamos pues estar en contacto.

**Frank Arias Salgado:** Ok.

**Esteban Guarin Valencia:** What?

**Juan Felipe Garzon Trejos:** Sí, sí, señor. Sí, sin problema. Las adicionamos ahí ya en el documento que usted nos entregaría con todo el tema del inventario, de las habitaciones, ahí también nos pondrías, por ejemplo, la carta de desayunos. para nosotros adicionar todo esto acá. Ahorita vamos a otra cosa también muy interesante que es el tema de el chatbot. Aquí si quiere Guarín ya puede entrar a explicarlo.

**Esteban Guarin Valencia:** Ya la parte de chatbot es donde digamos la recepcionista, digamos, el chatbot es para que la recepcionista no tenga que estar todo el tiempo pendiente del celular si llegaba una nueva reserva, digamos, eso lo maneja automáticamente el propio chat que te va mandando como unas preguntas digamos primero el menú, digamos, que quiere hacer, si reservar una habitación, si cancelarla, si agregar una reseña o exactamente

**Juan Felipe Garzon Trejos:** Les voy a mostrar acá.

### **00:22:07**

**Esteban Guarin Valencia:** así. Y ya luego digamos que elige eh digamos reservar una habitación, se le pregunta pues la fecha de llegada, la de salida, los adultos que tiene, los niños, si tiene mascota o no y pues le muestra las habitaciones que están disponibles en esa en esa fecha para él. Ya después de que se le muestre y pues la misma persona pues elija las habitaciones que quiere, digamos. puede ser una o varias, pues ya se le hace como un resumen de lo que vendría siendo todo lo que sería la conversación y ya solamente faltaría que la persona venga y diga, "Sí, yo quiero pagar de una vez o no quiero pagar y pues al final no hace el pago y no reserva nada." Claramente, pues para preservar de que digamos no sea el caso de que hayan doble reservas, se hace como el bloqueo temporal para evitar de que mientras que esta persona está haciendo la reserva con estas habitaciones, otra persona que esté haciendo la reserva en ese mismo instante no no se levean las habitaciones que están reservando la otra persona, digamos, para evitar de que se preserve doblemente.

### **00:23:29** {#00:23:29}

**Esteban Guarin Valencia:** Ahí se puede mostrar como que se avisa, digamos, el nombre completo, el documento, digamos, le piden los datos, pues si se necesita algún otro dato para pedir para una reserva se puede agregar. Y más o menos pues así se vería la el server, la reserva y como al final al final pues esto se agregaría a las reservas que tiene la aplicación y ahí aparecía inmediatamente. entre las otras funciones, pues se tiene la de reservar con la recepcionista, digamos, en esta pues simplemente la persona en cualquier momento la conversación o directamente dice, "No, yo quiero rececionar con la recepcionista, ya sea porque no le gusta, digamos, reservar con chatbots o con IA o simplemente no le funcionó, pues va a escala la recepcionista, le manda la identificación a la aplicación y ya La recepcionista toma el

**Frank Arias Salgado:** Ok.

**Esteban Guarin Valencia:** control.

**Juan Felipe Garzon Trejos:** Aquí esto es un ejemplo, digamos, la persona directamente dice hablar con recepción, entonces el chatbot lo que hace es pasar directamente acá. Entonces acá el ejemplo es Camilo Arias, t ta ta.

### **00:24:44**

**Juan Felipe Garzon Trejos:** Entonces, si nos vamos a conversaciones, a la al recepción a ah bueno, en este caso no lo tenemos conectado, pero ya acá lo que haría la recepcionista es que viene acá esto todo por una P de WhatsApp. Entonces acá lo que va a ver la persona, la recepcionista es el chat que tiene la persona. Entonces en caso tal acá están los datos, pues que envió Camilo Arias, la cédula, que autoriza la habitación, las reservas. Entonces, acá ya la persona, la recepcionista lo que hace es responderle.

**Frank Arias Salgado:** Sí, está

**Juan Felipe Garzon Trejos:** Ya la persona ya lo que hace es realizar la reserva por medio de del software en este caso porque pues obviamente hay muchas personas que aún no como que les gusta más a la antigua, pues entonces siempre va a haber un control humano,

**Frank Arias Salgado:** Bueno,

**Juan Felipe Garzon Trejos:** en este caso es la recepcionista que va a tener acá la pestañita de de conversaciones escaladas. Y acá otra cosa importante es que pues siempre le va a salir como en este caso

### **00:25:49** {#00:25:49}

**Frank Arias Salgado:** Ok.

**Juan Felipe Garzon Trejos:** la el número de de conversaciones y cuando lleggaue un mensaje entonces va a salir siempre acá que es muy importante pues para que ya esté pendiente si está en el dashboard acá y ve que le sube acá un numerito es porque tiene que venir acá a realizar una una reserva de forma manual.

**HAZ TOPE:** Eh, yo creo que también lo que queda pendiente es pues aún no lo tenemos en esta demo, pero es la funcionalidad de ella, poder reservar con forma de lenguaje natural eh con la inteligencia artificial. O sea, que el caso de que un huésped dese indicar, por ejemplo, necesito habitación para tres personas con mascota y todas las especificaciones en un solo mensaje, la IAintente hacer una reserva. eh y llegar pues digamos y darle una recomendación toda hecha con inteligencia artificial.

**Juan Felipe Garzon Trejos:** Mhm.

**Esteban Guarin Valencia:** La idea de opción es como simplemente facilitarle el proceso solamente un mensaje. Eh, se mandaría primero como un mensaje del propio salvo como indicándole tienes que mencionar tu nombre, tu cédula y todo eso como para que la persona no ande perdida sin saber qué es lo que tiene que mandar.

### **00:27:09**

**Esteban Guarin Valencia:** Es que le mandar tienes que indicar el nombre, la cédula y todas estas cosas. Al final de eso pues te manda el mensaje, estas son habitaciones que tenemos disponibles y ya se hace la el pago como corresponde.

**Juan Felipe Garzon Trejos:** Sí, igual la idea siempre es ofrecerle al Wespedo, en este caso tres formas de reserva. La primera sería por el formulario que sería reservar por medio del chatbot en formulario, la segunda sería hablando directamente con recepción o una tercera que es con el modelo de inteligencia artificial que sería enviando, como dijo mi compañero, en un solo mensaje todo lo de la reserva.

**Frank Arias Salgado:** Mhm. Okay.

**Juan Felipe Garzon Trejos:** Otra cosa que también tenemos pendiente es el tema de el link de pago. Entonces, eh el link que se escoja según el el beneficio para el hotel o no sé qué qué datfono manejen ustedes, que genera links de pagos y eso se manejan B o Credibo, todo eso. También se conectaría aquí pues con el con el WhatsApp para que le envíe directamente el link de pago a la persona, la persona realice el pago y se confirme la reserva.

### **00:28:18** {#00:28:18}

**Frank Arias Salgado:** Hm. Endi

**Esteban Guarin Valencia:** Y ya lo único que faltaría pues la parte de constelación y consulta. En esta parte,

**Juan Felipe Garzon Trejos:** He.

**Esteban Guarin Valencia:** pues con el código que se le entrega al hacer una reserva, simplemente escribe el código que se le entregó a la al hacerla y ya puede ver como la información del estado de la habitación, digamos, de la reserva que él tiene, ya sea digamos el nombre de los huéspedes, la habitación que reservó, las personas que estuvo, la fecha de entrada y salida, que tanto pagó y toda esta parte de la reserva en Sí. Y ya finalmente, pues si desea cancelar la reserva, simplemente le da encancelada esta reserva. La idea es que tenga doble confirmación como para evitar cancelaciones eh erróneas y finalmente la cancela y ya esto desbloquea la habitación en la aplicación y ya se puede y ya está disponible para que esta persona la reserve.

**Frank Arias Salgado:** Pero bueno, y eso es pues según es un ejemplo, pero pues no sé si eso tendrá una penalización por cancelarla pues después de un tiempo, no sé.

### **00:29:30** {#00:29:30}

**Juan Felipe Garzon Trejos:** Sí, sí, señor.

**Esteban Guarin Valencia:** Aleluya.

**Juan Felipe Garzon Trejos:** Ahí mismo se mostró la la Es que no se vio

**Frank Arias Salgado:** Sí, sí, sí, sí.

**Juan Felipe Garzon Trejos:** la Sí,

**Frank Arias Salgado:** Okay, ya estoy ciego.

**Juan Felipe Garzon Trejos:** ahí mismo se mostraba la la penalización. En este caso, digamos, si la reserva se cancelaba el mismo día, pues se volvía el Ajá.

**Frank Arias Salgado:** Como de tr a 5 días. Alcancé yo a ver algo ahí.

**Juan Felipe Garzon Trejos:** se volvía el dinero completo. Si se reserva ya después de tiempo se devuelve una parte. Si no, no se le devuelve nada. Eso. Obviamente también lo hablaríamos contigo, que nos dirías cómo son ustedes las políticas de cancelación en el hotel o si después de

**Frank Arias Salgado:** Eso debe era una normativa,

**Juan Felipe Garzon Trejos:** confirmar sí toca ver una normativa en cuanto a a los

**Frank Arias Salgado:** no sé. Tocas que mirar eso.

**Juan Felipe Garzon Trejos:** hoteles y eso para también confirmárnoslo para también ponerlo en el chatbot.

### **00:30:18** {#00:30:18}

**Juan Felipe Garzon Trejos:** Em, bueno, ya aquí sería el tema del chatbot y el de habitación. Está bien. Eh, ahorita vamos a irnos a la pantalla de administración que esta la va a

**Esteban Guarin Valencia:** administrad.

**Juan Felipe Garzon Trejos:** explicar Juan José. Acá vamos a tomar un ejemplo. En este caso, Marcela Torres, un ejemplo de que es la administradora. Entonces va a ingresar.

**HAZ TOPE:** Bueno, entonces, adicionalmente a la pantalla de la recepcionista,

**Juan Felipe Garzon Trejos:** ¿Cuál?

**HAZ TOPE:** el administrador tiene otro tipo de pantallas. Eh, como podemos ver en la columna izquierda, en la parte de operación, eh, digamos ahí y en la parte de administración está el añadido de la pantalla de auditoría en donde se pueden ver qué ventas ha realizado la recepcionista. Si quieres, Garson, vamos a esa pantalla de auditoría.

**Juan Felipe Garzon Trejos:** Auditoria. Ok.

**HAZ TOPE:** Ajá. Eh, ¿qué contiene la pantalla de auditoría? Contiene cada operación que se realizada en el sistema. Entonces, por ejemplo, si la una recepcionista inició sesión a cierta eh a cierta hora, el va a tener el registro aquí de fecha, hora, el tipo de usuario, el nombre del usuario, la acción que realizó, que por ejemplo puede ser iniciar sesión, eh, y el módulo que pues el módulo es de identidad porque se está autenticando.

### **00:31:50**

**HAZ TOPE:** ¿Qué más? Por ejemplo, incluye un log de auditoría cuando, por ejemplo, una persona realiza una cancelación en el chatbot o cuando la recepcionista, por ejemplo, hizo una venta. Digamos que el propósito de esta pantalla es llevar el registro de todo lo que hac en el sistema en caso de que haya un problema o o toque toque realizar algo al respecto. Entonces allí está todo el registro de de todo lo que se hace en el sistema.

**Esteban Guarin Valencia:** digamos como una ocasión que uno necesita, necesito que saber qué se hizo tal día, tal fecha o entonces ahí se ve como registro que se hizo tal cosa, tal otra o también Es como una parte de seguridad saber de quién hizo esta reserva, eh quién intentó hacer en esta sesión en tal tiempo, digamos, también sirve como una parte de la seguridad del propio de la propia obligación.

**HAZ TOPE:** Incluso si una persona intentó loguearse externa al hotel, que no sea ni recepcionista ni administrador, también lo registra. Entonces, por ejemplo, ahí dice intento fallido de tal persona con tal correo. Entonces, este módulo en general, el propósito es es buscar la seguridad del sistema, contribuirle a la seguridad al system.

### **00:33:19** {#00:33:19}

**HAZ TOPE:** Eh, si querés vamos a finanzas y en finanzas se encuentra un dashboard que contiene los ingresos. Eh, ahí se puede filtrar por mes, por año en el en la la barra principal. Eh, también el el valor de egresos y el balance. Además, también hay un componente visual que que da mostrar pues el rendimiento financiero que ha tenido el hotel. Y en la parte final de la pantalla están también un tipo de registros para poder hacer para poder calcular los ingresos e ingresos. Entonces, por ejemplo, si hay un gasto de operaciones, como puede ser un arreglo en el hotel,

**Juan Felipe Garzon Trejos:** mantenimiento

**HAZ TOPE:** eh mantenimiento, todo queda registrado en esta en este último componente de la pantalla.

**Juan Felipe Garzon Trejos:** Aquí podemos ver un ejemplo que este egreso fue el reembolso que realizamos por el chatbot. Entonces, todo queda registrado acá. Acá el ingreso sería la reserva que hizo por el chatbot, el hospedaje que realizamos de prueba, todo queda registrado. Eh, la venta de la Coca-Cola que vendim, de la apostojón que vendimos, está acá también registrada.

### **00:34:50** {#00:34:50}

**Juan Felipe Garzon Trejos:** Entonces es como también para llevar toda la auditoría de gastos y y los egresos y también va

**Frank Arias Salgado:** trae con balance. Ah.

**Juan Felipe Garzon Trejos:** a tener la funcionalidad de que si quiere usted exportarlo a Excel, pues dándole aquí le va a generar un Excel sin ningún problema y como tal el administrador va a tener la pantalla de registrar un egreso. Ya puede seguir con usted si quiere.

**HAZ TOPE:** sea. Listo. Entonces vamos a la parte de reporte y en la parte de reportes se tiene algo parecido, pero eh tenemos lo que ya habíamos mencionado y es una unas estadísticas o una un componente que nos indica qué productos son los que más se han vendido en la tienda y cuáles son los que menos se han vendido para poder hacer una rotación correcta. Y pues en base a eso eh pues dejar de vender lo que lo que no no se consume caso. También tenemos un porcentaje de ocupación. Esto es también se puede filtrar por los meses del año.

### **00:36:02**

**HAZ TOPE:** Los ingresos, gastos y el balance. También se puede exportar Excel

**Juan Felipe Garzon Trejos:** filtrar por meses.

**HAZ TOPE:** y yo sería esa pantalla.

**Juan Felipe Garzon Trejos:** Voy a mostrarle de cómo registrar un egreso también. y le aquí para registrar un egreso, le va a salir la fecha en la que en la que lo quiere registrar, cuánto fue, digamos, 180,000 la categoría, si es el tema de pagar servicios públicos, pago de nómina, pago de insumos, un pago de mantenimiento, una compra de tienda, internet y telefonía o de otros, digamos, servicios públicos. Entonces, acá vamos a poner e pago de agua del mes de octubre. Acá se se adjuntaría la factura caso de que se tenga y eh se guarda el egreso. Acá como ven, se actualizan todas las tablas, se actualiza la parte de egresos, se actualiza el balance y se marca acá el egreso. Realiza. Sigamos con usuarios.

**HAZ TOPE:** Y en la parte de usuarios, pues tendríamos la funcionalidad de poder eh asociar una nueva recepcionista al sistema.

### **00:37:28** {#00:37:28}

**HAZ TOPE:** Entonces, ajá, en el caso de hirle al botón de nuevo recepcionista, se indica el nombre completo, el correo, el teléfono y pues ya el rol está definido como recepcionista y también se pueden desasociar en caso de que ya no trabajen ciertos ciertas personas. Eh, y el resto, o sea, el apartado de operación es las mismas pantallas que mostramos para la recepcionista. O sea, el administrador también tiene acceso a realizar reservas, a chequear las habitaciones, hacer checkin, checkout y el resto de funcionalidades operativas del hotel. No sé si hay una duda,

**Esteban Guarin Valencia:** es

**HAZ TOPE:** una recomendación o o algo por mejorar.

**Frank Arias Salgado:** Eh, por ejemplo, si Yo de aquí a mañana yo digo, "No, yo no voy a tener más recepcionista y voy a montar unas chapas con código." Entonces, pues digamos que ese rol de de de hacerlo pues presencialmente con recesionista, eso ya no iría. Pero entonces tocaría que mirar como la forma de que yo pueda dar un código. Ah, bueno, eso me imagino que en los mismos datos de la red de, o sea, tuas que añadirle ahí como un código

### **00:38:58** {#00:38:58}

**Juan Felipe Garzon Trejos:** Mhm. Sería para que la que el hotel quede ya completamente como inteligente, o sea,

**Frank Arias Salgado:** Sí,

**Juan Felipe Garzon Trejos:** que ya no que solo se puede reservar por WhatsApp.

**Frank Arias Salgado:** sí. Mira que,

**Esteban Guarin Valencia:** Pues en el caso,

**Frank Arias Salgado:** o sea,

**Esteban Guarin Valencia:** digamos que como ya no estarían los restriccionistas, se tendría que ya cambiar bastante lo que sería la aplicación y el chatbamos como ya todo eso como buenoamos se

**Juan Felipe Garzon Trejos:** Hm.

**Esteban Guarin Valencia:** ha orientado, digamos como hacerlo en nada manejado por una persona, se tendría que cambiar y ya tocaría que adaptar todo eso como

**Frank Arias Salgado:** no, pero es simplemente una pregunta, o sea, No, no,

**Juan Felipe Garzon Trejos:** Ah, sí, sí es posible. Sí, es posible, la verdad.

**Frank Arias Salgado:** no, o sea,

**HAZ TOPE:** Amén.

**Frank Arias Salgado:** no, no es que vaya a suceder porque pues

**Esteban Guarin Valencia:** No se escucha. M.

**Juan Felipe Garzon Trejos:** Todavía todavía, porque eso es lo que hay que aspirarle.

### **00:39:48** {#00:39:48}

**Frank Arias Salgado:** sí, sí,

**Juan Felipe Garzon Trejos:** futuro,

**Frank Arias Salgado:** porque por ejemplo yo estuve por allá en otro país y yo nunca yo no no dice, no dar un código allá en la puerta y chao.

**Juan Felipe Garzon Trejos:** ¿no? Sí, eso eso también se puede realizar sin problema que se pero sería obviamente hay que adaptar completamente el el los dos software tanto del chatbot como el de el de administración, pero sí es posible.

**Frank Arias Salgado:** Pero eso de todas maneras no, o sea, ni ni en las grandes ciudades se ve todavía aquí en Colombia eso. No,

**Juan Felipe Garzon Trejos:** Mm.

**Frank Arias Salgado:** eso no.

**Juan Felipe Garzon Trejos:** Sí, todavía no que aspirar al futuro, mejor dicho. Pero por ahora,

**HAZ TOPE:** Pues

**Juan Felipe Garzon Trejos:** ¿qué tal está esta lo qué tal llevamos el tema de diseño?

**Frank Arias Salgado:** No, muy muy elegante. es completa porque lo importante es que entre más datos tenga uno mejor,

**Juan Felipe Garzon Trejos:** Mm.

**Frank Arias Salgado:** que quede todo registrado.

**Juan Felipe Garzon Trejos:** Sí, señor.

### **00:40:41** {#00:40:41}

**Juan Felipe Garzon Trejos:** También el administrador va a poder ver las reseñas que dejan los clientes. Eh, todas estas reseñas se realizarían por medio de WhatsApp.

**Frank Arias Salgado:** Ah,

**Juan Felipe Garzon Trejos:** Entonces, el administrador es quien las puede ver. Sin problema.

**Frank Arias Salgado:** eso no se puede transferir de una vez a Google reseñas.

**Juan Felipe Garzon Trejos:** E tocaría averiguarlo, pero también podríamos averiguarlo.

**Esteban Guarin Valencia:** Sí, esa digamos que se podría añadir como la función de que se añaden automáticamente en Google,

**Juan Felipe Garzon Trejos:** Okay.

**Esteban Guarin Valencia:** ya que la aplicación que estamos utilizando sí lo permite.

**Juan Felipe Garzon Trejos:** Okay. Listo.

**Frank Arias Salgado:** Sí,

**Juan Felipe Garzon Trejos:** También es importante.

**Frank Arias Salgado:** porque donde hay relevancia es más relevancia en Google.

**Juan Felipe Garzon Trejos:** Sí, en Google Maps, sí, que uno siempre busca ahí en Google Maps según las reseñas y es que se la reserva.

**Esteban Guarin Valencia:** Claro. No.

**Juan Felipe Garzon Trejos:** Sí, señor. Ahí la idea también sería eh cuando se entregue eh organizar bien el WhatsApp, el WhatsApp Business que va a tener el chatbot.

### **00:41:39**

**Juan Felipe Garzon Trejos:** Entonces, organizar bien la foto de perfil, el nombre, el catálogo, todo, organizarlo bien bacano para entregárselo a a usted, que en este caso el cliente es algo importante también.

**Frank Arias Salgado:** tocar Juan José dice este fin de semana trabajarle a eso.

**Juan Felipe Garzon Trejos:** Sí.

**Frank Arias Salgado:** No.

**Juan Felipe Garzon Trejos:** y y que que obviamente ente en la página de Instagram que quede en Google, o sea, que quede muy muy fácil acceso para las personas que quieran reservar,

**Frank Arias Salgado:** Mhm.

**HAZ TOPE:** Listo. Entonces,

**Juan Felipe Garzon Trejos:** pero no,

**HAZ TOPE:** yo creo que con falta algo más.

**Juan Felipe Garzon Trejos:** pues como tal este sería el entregable, eh, era para ver más o menos todo el tema de diseño. Obviamente aquí falta hacer todo que funcione perfectamente, pero aquí es es era más que todo un entregable diseño completo de que el cliente estuviera pues de acuerdo con nuestro diseño, de acuerdo con las pantallas. Se se van a adicionar las pantallas que que usted nos informó. Eh, también que todo el tema de colores estuviera bien.

### **00:42:41** {#00:42:41}

**Juan Felipe Garzon Trejos:** Eh, hay que agregar el logo, pero hasta ahora está conforme con con lo que llevamos, ¿verdad?

**Frank Arias Salgado:** Sí, sí. No está, o sea, está muy entendible.

**Juan Felipe Garzon Trejos:** Okay. Sí, eso se trata de hacer lo más intuitivo posible para el para el el recepcionista, el administrador y para el cliente también en el caso del chatbot.

**Frank Arias Salgado:** No, yo está muy bien. Pues yo lo veo

**Juan Felipe Garzon Trejos:** Sí, señor. No sé qué más vaya a decir algún compañero.

**HAZ TOPE:** Eh, no, pues yo creo que cerraríamos con con un breve resumen, pues voy a presentar pantalla de la arquitectura de la solución para hacer un breve resumen de cómo funciona el

**Juan Felipe Garzon Trejos:** Ok.

**HAZ TOPE:** sistema en general. Y yo creo que eso sería todo. Ahí se está viendo.

**Juan Felipe Garzon Trejos:** Sí.

**HAZ TOPE:** Entonces, bueno, los componentes de la solución que proponemos para todo el sistema tecnológico de la Torre Satori se tiene diferentes componentes. Entonces, en los canales de usuarios eh va a estar el huésped, el administrador y la recepcionista eh que van a poder realizar en el caso del de la recepcionista, va a poder realizar reservas manuales a través de la aplicación web, checkin, checkout, facturación de tienda, reportes y revisión de reseñas.

### **00:44:23** {#00:44:23}

**HAZ TOPE:** En el caso del cliente o del huésped que se quiere alojar en en el hotel, va a tener acceso al chatbot para realizar su reserva y también podrá físicamente ir a la al hotel y realizar la reserva con la recepcionista. Eh, en la parte de persistencia vamos a tener una base de datos que es donde se almacena toda la información eh del sistema. Eh, básicamente vamos a tener todo el inventario de de las de la tienda, el inventario de habitaciones, el inventario de pagos que se han realizado, logs y todas las funcionalidades que explicamos. Y el backend es el que dispondrá todas las funcionalidades del sistema general. En cuanto a servicios externos, tenemos la API de WhatsApp, vamos a tener un motor de ella y la pasarela de pagos que aún en esta demo no está implementada, pero en próximas reuniones sí la tendremos lista para mostrar. Entonces, eso sería todo.

**Frank Arias Salgado:** la estructura de lo que están haciendo. M.

**HAZ TOPE:** Mm. Eh, ¿qué más? ¿Alguien más? ¿Puedo decir algo?

### **00:45:51** {#00:45:51}

**Esteban Guarin Valencia:** Eso ya sería todo, digamos, por el momento. Ya luego próximo sería mostrar el chatbot ya e digamos el chatbo con un WhatsApp ya funcionando completamente. Por el momento pues se tiene funcionando es la parte de reservas, pero ya se mostrará más completo más adelante.

**Frank Arias Salgado:** Mhm.

**Esteban Guarin Valencia:** Y si no hay nada más que comentar, dudas, comentarios o digamos que le añademos un color en vez de otro o cositas así.

**Frank Arias Salgado:** No, que yo lo veo, o sea, muy muy entendible, o sea, no los colores también están bien porque no, o sea, no no están así como como extravagantes, ¿no? O sea, todo lo veo como bien

**HAZ TOPE:** No hay que coincid los colores también coincide con como con la coherencia de marca que se tiene en Satória. Es como rojo, eh, rojo, blanco.

**Frank Arias Salgado:** y ahí un color como doradito.

**HAZ TOPE:** Mm.

**Frank Arias Salgado:** Sí, está bien.

**HAZ TOPE:** Listo. Entonces, no pues muchas gracias por por darnos el tiempo para mostrarle pues lo que tenemos.

**Frank Arias Salgado:** No, a ustedes, pero o sea, lo llevan bien adelantado.

### **00:47:10**

**Frank Arias Salgado:** Y eso y eso es para cuándo, pues, o sea,

**HAZ TOPE:** Es es para es para noviembre,

**Frank Arias Salgado:** ¿cuándo tienen que terminar ustedes eles

**HAZ TOPE:** ¿no? Noviembre.

**Esteban Guarin Valencia:** Ya estaría como noviembre todo hecho.

**Frank Arias Salgado:** va a tocar ir a Sevilla, va a tocar que ir a Sevilla para que conozcan Sevill? ¿Sí conocen a Sevilla o no?

**Juan Felipe Garzon Trejos:** Mira que no tengo familias en Tuluá,

**HAZ TOPE:** M.

**Juan Felipe Garzon Trejos:** pero sí siempre me ha gustado Sevilla.

**Frank Arias Salgado:** no tienen que ir a chupar frío.

**Juan Felipe Garzon Trejos:** Mira, Satoria, conocerlo.

**Frank Arias Salgado:** En este momento estamos en todavía arreglándolo porque el terremoto siempre lo estaba

**Juan Felipe Garzon Trejos:** Ah, claro.

**Frank Arias Salgado:** averiando, pero no. Yo creo que en unas tres semanas ya está listo.

**Juan Felipe Garzon Trejos:** Ah, no toca ir cuando acabemos el el software para verlo allá.

**Frank Arias Salgado:** Hágale,

**Esteban Guarin Valencia:** Yo sí miraba,

**Juan Felipe Garzon Trejos:** Ok.

**Frank Arias Salgado:** hágale.

**Esteban Guarin Valencia:** yo sí miraba fotos del hotel ahí en el y se ve bien bonito.

### **00:47:57**

**Esteban Guarin Valencia:** todo el hotel con visas y todo.

**Juan Felipe Garzon Trejos:** Mm.

**Frank Arias Salgado:** Tienen una tiene una vista muy bonita, ¿no? Y el sitio es muy agradable. Por ahí no hay bulla, o sea, por no descansar.

**Juan Felipe Garzon Trejos:** Mm.

**Esteban Guarin Valencia:** Claro.

**Frank Arias Salgado:** Ahí está, pues, para que arranquen pues para Sevilla.

**Juan Felipe Garzon Trejos:** Sí, señor. Listo, ya vemos que tenemos donde quedarnosilla.

**Frank Arias Salgado:** Háganle, háganle,

**Esteban Guarin Valencia:** Muchas gracias.

**Frank Arias Salgado:** hagan la reserva. Listo. Bueno, hermano, que descansen.

**Juan Felipe Garzon Trejos:** Bueno, listo.

**Frank Arias Salgado:** Pues

**Juan Felipe Garzon Trejos:** El video,

**HAZ TOPE:** Bueno,

**Juan Felipe Garzon Trejos:** ¿cómo quedaría?

**HAZ TOPE:** el video lo tiene R.

**Juan Felipe Garzon Trejos:** Ah, okay.

**HAZ TOPE:** Ahorita no lo pasa.

**Juan Felipe Garzon Trejos:** Listo, listo, listo.

**Frank Arias Salgado:** listo. Chao.

**Juan Felipe Garzon Trejos:** Gracias. Que esté bien.

**Esteban Guarin Valencia:** que esté muy

**Juan Felipe Garzon Trejos:** Feliz noche.

**HAZ TOPE:** que descanse.

**Juan Felipe Garzon Trejos:** Hasta luego.

**Frank Arias Salgado:** Bueno, chao. Hasta luego.

### **La transcripción finalizó después de 00:48:52**

*Esta transcripción editable se generó por computadora y puede contener errores. Los usuarios también pueden cambiar el texto después de que se cree.*