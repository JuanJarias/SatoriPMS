-- V8: Eliminar las reseñas ficticias de semilla insertadas en V5.
-- Las reseñas reales se consultan directamente desde el perfil oficial de Google Reviews.

DELETE FROM review
WHERE author_name IN (
    'Carlos Mario Restrepo',
    'Valentina Gómez',
    'Andrés Felipe Morales'
);
