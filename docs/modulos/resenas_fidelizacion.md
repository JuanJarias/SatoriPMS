# Módulo — Reseñas y Fidelización

### 1. Requerimientos y Casos de Uso

* **HU-02 (Consultar reseñas):** Visualización de comentarios de huéspedes anteriores desde el chatbot y la web pública.
* **HU-04 (Dejar reseña):** Formulario conversacional o web que solicita calificación numérica (1 a 5) y comentario al finalizar el check-out.
* **HU-10 (Panel de reseñas):** Vista para el administrador y recepcionista para moderar y responder a las opiniones recibidas.
* **HU-12 (Huéspedes recurrentes):** Identificación automática de clientes que superen el umbral de visitas para aplicar beneficios de fidelización.

---

### 2. Reglas de Integridad

* **Unicidad de reseña:** Una reserva finalizada solo puede tener asociada un único registro de reseña (`booking_id` único en tabla `review`), evitando calificaciones duplicadas.
