# Torre Satori PMS
Monolito modular (hotel, Sevilla, Valle del Cauca) + chatbot WhatsApp.
Stack único: Python 3.12 + FastAPI · PostgreSQL 16 (btree_gist) · SQLAlchemy + Alembic · React 18 (Vite, TS) · n8n + Gemini 2.0 Flash · Cloudflare R2.
Prohibido: Java, Spring, JPA/Hibernate, Maven, Flyway, Redis.
Épicas: Autenticación, Reservas, Calendario, Finanzas, Tienda, Reseñas.
RN-02 sin solapamiento (EXCLUDE USING gist) · RN-10 RBAC Recepcionista/Admin · RN-11 sueldo mensual (fijo/comisión/mixto) · RN-12 autorización datos Ley 1581 · RN-13 No-Show libera a las 12:00.
Reglas de trabajo: responder en español y conciso; cada afirmación con archivo:línea o comando; estados Funcional/Parcial/Roto/Ausente/No verificable; no inventar; detalle a docs/audit/, chat ≤10 líneas.
Reglas de cambios: nunca modificar sin aprobación de IDs; antes de cada cambio escribir POR QUÉ, QUÉ y ARCHIVOS; después de cada cambio correr su verificación y reportar PASS/FAIL; un commit por ID en rama propia.
