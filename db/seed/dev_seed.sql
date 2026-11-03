-- db/seed/dev_seed.sql
--
-- SOLO para desarrollo local. NO es una migración de Flyway (por eso no
-- vive en apps/api/src/main/resources/db/migration/ ni se ejecuta en
-- producción). Se corre manualmente cuando lo necesites:
--
--   docker compose exec postgres psql -U satori -d satoripms -f /seed/dev_seed.sql
--
-- Genera el hash real con bcrypt antes de usarlo, por ejemplo en Java:
--   new BCryptPasswordEncoder().encode("admin123")
-- El hash de ejemplo de abajo es solo un placeholder — reemplázalo por
-- uno generado de verdad antes de usarlo.

INSERT INTO system_user (username, password_hash, role, name) VALUES
('Admin', '$2a$12$Uy2lw7y1LED32eVFbbxvvO/96LQIj30HMF8LWpauAeqok7nrMaJS.', 'admin', 'Administrador de Torre Satori')
ON CONFLICT (username) DO NOTHING;
