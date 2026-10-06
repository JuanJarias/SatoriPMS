# Módulo 14 — Decisiones Pendientes

*(Por discutir con Juan José Arias Gallego y el stakeholder)*

1. **Regla de capacidad combinada (RN-01):** ¿adultos y niños se validan y se cobran juntos contra un único tope, o cada uno por separado?
2. ~~**Mecanismo del bloqueo temporal (RN-02):** ¿se implementa con Redis, con las columnas de `conversation`, o con ambos?~~ **DECIDIDO:** Se implementa con Redis (Lua scripts en `RedisLockService`) con TTL de 900 segundos (15 minutos). Las columnas de `conversation` existen pero no se usan activamente para el bloqueo.
3. **Datos obligatorios de registro del huésped** y tiempo de conservación de esos datos, conforme a la Ley 1581 de 2012.
4. **Reglas exactas de descuentos y fidelización** (Épica 5) y cómo se aplican en el modelo de datos.
5. **Cálculo del sueldo del recepcionista:** ¿fijo, por comisión o mixto?, ¿dónde se configura?
6. **Umbral de estadías que define a un huésped como "recurrente"** y quién lo configura.
7. **Duración mínima y máxima de una reserva** (en noches): valores exactos a definir.
8. **Horario real de atención de la recepcionista** (hoy se usa 7:00 a.m.–11:00 p.m. como valor provisional).
