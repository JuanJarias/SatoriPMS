import React, { useState, useEffect } from 'react';
import {
  Star,
  CheckCircle2,
  ShieldCheck,
  MessageSquare,
  RefreshCw,
  Award,
  TrendingUp,
  AlertCircle
} from 'lucide-react';
import { apiClient } from '../api/client';
import {
  PageHeader,
  Card,
  SearchBar,
  FilterChip,
  EmptyState,
  Alert,
  Button,
  cn
} from '../ui';

export interface ReviewItem {
  id: number;
  authorName: string;
  authorPhotoUrl?: string | null;
  rating: number;
  comment: string;
  relativeTime?: string;
  source: string;
  createdAt: string;
}

export interface ReviewSummaryResponse {
  placeName: string;
  placeId: string;
  average: number | null;
  total: number;
  distribution: Record<number, number>;
  reviews: ReviewItem[];
  source: string;
  placesApiConfigured: boolean;
  fetchedAt: string;
  error?: string;
}

export function Resenas() {
  const [loading, setLoading] = useState<boolean>(true);
  const [refreshing, setRefreshing] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [summary, setSummary] = useState<ReviewSummaryResponse | null>(null);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [selectedStar, setSelectedStar] = useState<number | 'all'>('all');

  const fetchReviews = async (forceRefresh = false) => {
    if (forceRefresh) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }
    setError(null);

    try {
      const path = forceRefresh ? '/api/reviews/summary?refresh=true' : '/api/reviews/summary';
      const response = await apiClient.get<ReviewSummaryResponse>(path);
      if (response?.data) {
        setSummary(response.data);
        if (response.data.error) {
          setError(response.data.error);
        }
      } else {
        setError('No se recibió respuesta válida del servidor de reseñas.');
      }
    } catch {
      setError(
        'No fue posible conectar con el servidor central para consultar las reseñas en vivo de Google Reviews.'
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchReviews(false);
  }, []);

  const reviewsList = summary?.reviews ?? [];
  const totalCount = summary?.total ?? 0;
  const averageRating = summary?.average ?? null;
  const distribution = summary?.distribution ?? { 5: 0, 4: 0, 3: 0, 2: 0, 1: 0 };

  const filteredReviews = reviewsList.filter((item) => {
    const matchesSearch =
      (item.authorName || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (item.comment || '').toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStar = selectedStar === 'all' || item.rating === selectedStar;
    return matchesSearch && matchesStar;
  });

  const positiveCount = (distribution[5] || 0) + (distribution[4] || 0);
  const positiveRatePct = totalCount > 0 ? Math.round((positiveCount / totalCount) * 100) : 0;

  const formatDate = (isoString: string) => {
    if (!isoString) return '';
    try {
      const date = new Date(isoString);
      return date.toLocaleDateString('es-CO', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    } catch {
      return isoString;
    }
  };

  const formatFetchedAt = (isoString?: string) => {
    if (!isoString) return '';
    try {
      return new Date(isoString).toLocaleString('es-CO', {
        dateStyle: 'medium',
        timeStyle: 'short'
      });
    } catch {
      return isoString;
    }
  };

  return (
    <div className="space-y-6">
      {/* Encabezado */}
      <PageHeader
        eyebrow="Reputación & Calidad"
        title="Reseñas Oficiales de Google Reviews"
        desc={`Visualización en tiempo real de las valoraciones publicadas en Google Reviews para ${
          summary?.placeName || 'Hotel Satori - Sevilla Valle del Cauca'
        }. Modo estricto de solo lectura.`}
        actions={
          <Button
            variant="secondary"
            onClick={() => fetchReviews(true)}
            disabled={loading || refreshing}
            icon={<RefreshCw size={15} className={cn(refreshing && 'animate-spin')} />}
          >
            {refreshing ? 'Actualizando…' : 'Actualizar desde Google'}
          </Button>
        }
      />

      {/* Nota de integridad y fuente real */}
      <Alert tone="info" title="Fuente Directa de Google Reviews (Solo Lectura)">
        Las métricas y opiniones provienen directamente del perfil oficial del hotel en Google
        Reviews sin datos simulados ni modificaciones locales. En la aplicación web no se redactan
        reseñas ni se realizan redirecciones externas.
        {summary?.fetchedAt ? ` Última sincronización: ${formatFetchedAt(summary.fetchedAt)}.` : ''}
      </Alert>

      {error && (
        <Alert tone="warn" title="Aviso de sincronización con Google Reviews">
          {error}
        </Alert>
      )}

      {loading ? (
        <Card className="p-12 text-center text-ink-soft">
          <RefreshCw size={24} className="mx-auto mb-2 animate-spin text-forest-700" />
          <p className="text-sm">Consultando datos reales en vivo desde Google Reviews…</p>
        </Card>
      ) : (
        <>
          {/* Bloque de Métricas Principales */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* KPI 1: Calificación Promedio */}
            <Card className="p-5 flex flex-col justify-between">
              <div className="flex items-center justify-between text-ink-soft">
                <span className="text-xs font-semibold uppercase tracking-wider">
                  Calificación Promedio
                </span>
                <Award size={18} className="text-terra-600" />
              </div>
              <div className="my-3 flex items-baseline gap-3">
                <span className="font-display text-4xl font-bold text-forest-900">
                  {averageRating !== null ? averageRating.toFixed(1) : '—'}
                </span>
                {averageRating !== null && (
                  <div className="flex items-center gap-1">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <Star
                        key={star}
                        size={18}
                        className={cn(
                          'transition-colors',
                          star <= Math.round(averageRating)
                            ? 'fill-amber-400 text-amber-500'
                            : 'text-sand-300'
                        )}
                      />
                    ))}
                  </div>
                )}
              </div>
              <p className="text-xs text-ink-soft">Escala sobre 5.0 estrellas en Google Reviews</p>
            </Card>

            {/* KPI 2: Total de Opiniones Verificadas */}
            <Card className="p-5 flex flex-col justify-between">
              <div className="flex items-center justify-between text-ink-soft">
                <span className="text-xs font-semibold uppercase tracking-wider">
                  Opiniones en Google
                </span>
                <MessageSquare size={18} className="text-forest-700" />
              </div>
              <div className="my-3">
                <span className="font-display text-4xl font-bold text-forest-900">
                  {totalCount}
                </span>
                <span className="ml-2 text-sm text-ink-soft font-medium">
                  opiniones publicadas
                </span>
              </div>
              <p className="text-xs text-ink-soft">
                Conteo oficial en vivo de Google Reviews
              </p>
            </Card>

            {/* KPI 3: Tasa de Satisfacción */}
            <Card className="p-5 flex flex-col justify-between">
              <div className="flex items-center justify-between text-ink-soft">
                <span className="text-xs font-semibold uppercase tracking-wider">
                  Satisfacción Alta
                </span>
                <TrendingUp size={18} className="text-ok" />
              </div>
              <div className="my-3">
                <span className="font-display text-4xl font-bold text-ok">
                  {totalCount > 0 ? `${positiveRatePct}%` : '—'}
                </span>
                <span className="ml-2 text-sm text-ink-soft font-medium">
                  calificaciones de 4 y 5 estrellas
                </span>
              </div>
              <p className="text-xs text-ink-soft">
                Calculado sobre las {totalCount} opiniones reales de Google
              </p>
            </Card>
          </div>

          {/* Desglose Real de Calificaciones por Estrellas */}
          <Card className="p-6">
            <h2 className="font-display text-base font-semibold text-forest-900 mb-4">
              Resumen de Opiniones de Google por Estrellas
            </h2>
            <div className="space-y-2.5">
              {[5, 4, 3, 2, 1].map((star) => {
                const count = distribution[star] || 0;
                const pct = totalCount > 0 ? Math.round((count / totalCount) * 100) : 0;
                return (
                  <div key={star} className="flex items-center gap-4 text-sm">
                    <div className="flex items-center gap-1 w-24 shrink-0 text-ink">
                      <span className="font-semibold">{star}</span>
                      <Star size={14} className="fill-amber-400 text-amber-500" />
                    </div>
                    <div className="flex-1 h-3 rounded-full bg-sand-200 overflow-hidden">
                      <div
                        className="h-full bg-amber-400 rounded-full transition-all duration-300"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                    <span className="w-12 text-right text-xs font-semibold text-ink-soft">
                      {count}
                    </span>
                    <span className="w-12 text-right text-xs text-ink-soft/70">({pct}%)</span>
                  </div>
                );
              })}
            </div>
          </Card>

          {/* Listado de Comentarios Individuales Reales */}
          {reviewsList.length > 0 ? (
            <>
              <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
                <div className="w-full sm:w-80">
                  <SearchBar
                    value={searchTerm}
                    onChange={setSearchTerm}
                    placeholder="Buscar por huésped o comentario…"
                  />
                </div>
                <div className="flex flex-wrap items-center gap-2">
                  <FilterChip
                    active={selectedStar === 'all'}
                    onClick={() => setSelectedStar('all')}
                  >
                    Todas ({reviewsList.length})
                  </FilterChip>
                  {[5, 4, 3, 2, 1].map((star) => {
                    const countInList = reviewsList.filter((r) => r.rating === star).length;
                    return (
                      <FilterChip
                        key={star}
                        active={selectedStar === star}
                        onClick={() => setSelectedStar(star)}
                      >
                        {star} ★ ({countInList})
                      </FilterChip>
                    );
                  })}
                </div>
              </div>

              {filteredReviews.length === 0 ? (
                <Card className="p-10">
                  <EmptyState
                    icon={<MessageSquare size={36} className="text-ink-soft/60" />}
                    title="No se encontraron reseñas con los criterios seleccionados"
                  >
                    Intente con otros términos de búsqueda o limpie el filtro de estrellas.
                  </EmptyState>
                </Card>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {filteredReviews.map((rev) => (
                    <Card
                      key={rev.id}
                      className="p-5 flex flex-col justify-between hover:border-forest-700/40 transition"
                    >
                      <div>
                        <div className="flex items-start justify-between gap-3 mb-3">
                          <div className="flex items-center gap-3">
                            {rev.authorPhotoUrl ? (
                              <img
                                src={rev.authorPhotoUrl}
                                alt={rev.authorName}
                                className="h-10 w-10 rounded-full object-cover border border-sand-300"
                              />
                            ) : (
                              <div className="grid h-10 w-10 place-items-center rounded-full bg-forest-800 text-sm font-bold text-sand-50">
                                {(rev.authorName || 'G')
                                  .split(' ')
                                  .map((n) => n[0])
                                  .slice(0, 2)
                                  .join('')}
                              </div>
                            )}
                            <div>
                              <h3 className="font-semibold text-sm text-forest-900 leading-tight">
                                {rev.authorName}
                              </h3>
                              <p className="text-xs text-ink-soft">
                                {rev.relativeTime || formatDate(rev.createdAt)}
                              </p>
                            </div>
                          </div>

                          <span className="inline-flex items-center gap-1 rounded-full bg-sand-200/80 px-2.5 py-0.5 text-[11px] font-semibold text-forest-900">
                            <CheckCircle2 size={12} className="text-ok" />
                            Google Reviews
                          </span>
                        </div>

                        <div className="flex items-center gap-1 mb-3">
                          {[1, 2, 3, 4, 5].map((star) => (
                            <Star
                              key={star}
                              size={15}
                              className={cn(
                                star <= rev.rating
                                  ? 'fill-amber-400 text-amber-500'
                                  : 'text-sand-300'
                              )}
                            />
                          ))}
                          <span className="ml-1.5 text-xs font-semibold text-ink">
                            {rev.rating}.0 de 5.0
                          </span>
                        </div>

                        {rev.comment ? (
                          <p className="text-sm text-ink leading-relaxed font-normal">
                            &ldquo;{rev.comment}&rdquo;
                          </p>
                        ) : (
                          <p className="text-xs italic text-ink-soft">
                            Calificación publicada sin comentario escrito.
                          </p>
                        )}
                      </div>

                      <div className="mt-4 pt-3 border-t border-sand-200 flex items-center justify-between text-xs text-ink-soft">
                        <span className="flex items-center gap-1">
                          <ShieldCheck size={13} className="text-forest-700" />
                          Opinión verificada de Google
                        </span>
                        <span>{formatDate(rev.createdAt)}</span>
                      </div>
                    </Card>
                  ))}
                </div>
              )}
            </>
          ) : (
            <Card className="p-8">
              <EmptyState
                icon={<AlertCircle size={32} className="text-terra-600" />}
                title="Comentarios individuales pendientes de llave de Google Places API"
              >
                {summary?.placesApiConfigured
                  ? 'No se recibieron comentarios individuales desde Google Places API en este momento.'
                  : `El resumen oficial (${averageRating ?? '—'} estrellas y ${totalCount} opiniones con su distribución exacta) se extrajo en tiempo real desde Google Reviews. Para visualizar también los textos individuales de cada reseña dentro de esta aplicación, configure la variable GOOGLE_PLACES_API_KEY en el archivo .env (Place ID: ${
                      summary?.placeId || 'ChIJQRr4FV2zOY4RvqM_8_EfzsY'
                    }).`}
              </EmptyState>
            </Card>
          )}
        </>
      )}
    </div>
  );
}
