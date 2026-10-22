# Módulo — Diseño UX/UI

## 1. Fuente de Diseño

Los mockups de la aplicación web y del chatbot se mantienen en Figma, bajo el nombre "SatoriPMS, Bloque C, Mockups app web y chatbot". Este módulo recoge los principios que esos diseños deben cumplir.

## 2. Canal Conversacional (WhatsApp)

La experiencia en WhatsApp prioriza los componentes interactivos nativos, listas y botones de respuesta rápida, para minimizar los errores de digitación. Los mensajes son claros y concisos, con negritas y emojis moderados que faciliten la lectura rápida en el teléfono. Cuando el huésped escribe algo que el bot no entiende, la respuesta es amable, indica el formato esperado con un ejemplo y recuerda que puede reiniciar escribiendo "menú".

El diseño respeta los límites de la API de WhatsApp: las listas admiten hasta 10 filas y los títulos de fila se recortan a 24 caracteres; los mensajes con botones admiten hasta 3 botones con títulos cortos. Las listas se usan para menús y selección de habitaciones, y los botones para decisiones de dos o tres opciones como Sí o No, Continuar o Cancelar.

Cada paso de un flujo pide un solo dato y muestra el avance de forma implícita. Los resúmenes previos a una confirmación incluyen siempre fechas, habitaciones, ocupación, valores y código de reserva cuando exista. Las acciones irreversibles, como la cancelación, piden doble confirmación.

## 3. Aplicación Web (Administración y Recepción)

El diseño es responsivo: se adapta a las pantallas de escritorio de recepción y a dispositivos móviles para la administración remota. Se construye con Tailwind CSS.

Los estados de habitación usan códigos de color semánticos: verde para Disponible, rojo para Ocupada, amarillo para En limpieza y gris para Mantenimiento. El bloqueo temporal se distingue visualmente de los anteriores, ya que es un estado transitorio.

Las operaciones críticas dan retroalimentación visual inmediata: notificaciones tipo toast para éxito y error, y diálogos modales de confirmación para cancelaciones y acciones destructivas. Los cambios de estado enviados por el backend actualizan la pantalla sin recargar la página.

La navegación se organiza por las áreas funcionales del sistema (habitaciones y calendario, reservas, conversaciones, tienda, finanzas, reseñas y administración), y cada usuario ve solo las áreas permitidas por su rol.
