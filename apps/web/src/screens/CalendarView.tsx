import React, { useState } from 'react';
import {
  Calendar as CalendarIcon,
  ChevronLeft,
  ChevronRight,
  Plus,
  BedDouble,
  Clock,
  Sparkles,
  Wrench,
  CheckCircle2,
  X,
  Phone,
  MessageSquare,
  Users,
  Tag
} from 'lucide-react';
import { useStore } from '../store';
import {
  PageHeader,
  Card,
  Button,
  BadgeStatus,
  Alert,
  formatCurrency,
  cn
} from '../ui';

interface CalendarEvent {
  id: string;
  roomNumber: string;
  guest: string;
  startDay: number; // 0..6
  endDay: number; // 1..7
  kind: 'enCasa' | 'confirmada' | 'bloqueo' | 'mantenimiento';
  code: string;
  guests: number;
  total: number;
  paid: number;
  phone: string;
  channel: string;
  note?: string;
}

const EVENT_STYLES = {
  enCasa: {
    label: 'En casa',
    icon: BedDouble,
    cls: 'bg-terra-500 text-white border-terra-600',
  },
  confirmada: {
    label: 'Confirmada',
    icon: CheckCircle2,
    cls: 'bg-forest-800 text-white border-forest-900',
  },
  bloqueo: {
    label: 'Bloqueo temporal',
    icon: Clock,
    cls: 'hatch-warn text-[#6e4700] border-dashed border-[#d99a1e]',
  },
  mantenimiento: {
    label: 'Mantenimiento',
    icon: Wrench,
    cls: 'hatch-maint text-maint border-dashed border-maint/60',
  },
};

export function CalendarView({ go }: { go: (view: string, param?: string) => void }) {
  const { rooms, bookings, events } = useStore();
  const [selectedEvent, setSelectedEvent] = useState<CalendarEvent | null>(null);
  const [weekOffset, setWeekOffset] = useState(0);

  // Construir ventana de 7 días desde hoy + desplazamiento semanal
  const todayMidnight = new Date();
  todayMidnight.setHours(0, 0, 0, 0);
  const startOfWindow = new Date(todayMidnight);
  startOfWindow.setDate(todayMidnight.getDate() + weekOffset * 7);

  const dayNames = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'];
  const monthNames = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'];

  const weekDays = Array.from({ length: 7 }, (_, i) => {
    const d = new Date(startOfWindow);
    d.setDate(startOfWindow.getDate() + i);
    const iso = d.toISOString().slice(0, 10);
    return {
      key: iso,
      iso,
      label: dayNames[d.getDay()],
      n: d.getDate(),
      m: monthNames[d.getMonth()],
      today: d.getTime() === todayMidnight.getTime(),
    };
  });

  const rangeLabel = `${weekDays[0].n} ${weekDays[0].m} – ${weekDays[6].n} ${weekDays[6].m} ${startOfWindow.getFullYear()}`;
  const windowStartIso = weekDays[0].iso;
  const windowEndIso = new Date(startOfWindow.getTime() + 7 * 86400000).toISOString().slice(0, 10);

  const dayDiff = (isoA: string, isoB: string) =>
    Math.round((new Date(isoA + 'T00:00:00').getTime() - new Date(isoB + 'T00:00:00').getTime()) / 86400000);

  const calendarEvents: CalendarEvent[] = bookings
    .filter((b) => b.status !== 'cancelada' && b.checkOut > windowStartIso && b.checkIn < windowEndIso)
    .map((b) => {
      const startDay = Math.max(0, dayDiff(b.checkIn, windowStartIso));
      const endDay = Math.min(7, Math.max(startDay + 1, dayDiff(b.checkOut, windowStartIso)));
      const kind: CalendarEvent['kind'] =
        b.status === 'enCurso' ? 'enCasa' : b.status === 'bloqueada' || b.status === 'pendiente' ? 'bloqueo' : 'confirmada';
      return {
        id: b.code,
        roomNumber: b.room,
        guest: b.guest,
        startDay,
        endDay,
        kind,
        code: b.code,
        guests: b.guests,
        total: b.total,
        paid: b.paid,
        phone: b.phone || '—',
        channel: b.channel,
        note: b.note,
      };
    });

  const activeLocks = calendarEvents.filter((ev) => ev.kind === 'bloqueo');
  const colWidth = '160px';

  return (
    <div className="flex gap-5">
      <div className="min-w-0 flex-1">
        <PageHeader
          eyebrow="Ocupación & Planificación"
          title="Calendario Semanal"
          desc="Grilla de reservas por habitación en tiempo real desde PostgreSQL 16 (GiST RN-02)."
          actions={
            <Button
              variant="primary"
              icon={<Plus size={16} />}
              onClick={() => go('reservas')}
            >
              Nueva reserva
            </Button>
          }
        />

        {/* Temporadas Especiales Activas Banner */}
        {events.filter((e) => e.active).length > 0 && (
          <div className="mb-4 flex flex-wrap items-center gap-2 rounded-lg bg-sand-50 p-2.5 border border-sand-200 text-xs">
            <Tag size={14} className="text-terra-600 shrink-0" />
            <span className="font-semibold text-forest-900">Eventos activos:</span>
            {events.filter((e) => e.active).map((ev) => (
              <span key={ev.id} className="rounded bg-sand-200 px-2 py-0.5 text-[11px] font-medium text-ink">
                {ev.name} ({ev.discountPercentage > 0 ? `-${ev.discountPercentage}%` : `+${Math.abs(ev.discountPercentage)}%`} en tarifa)
              </span>
            ))}
          </div>
        )}

        {/* Date Selector & Legend */}
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <Button variant="secondary" className="w-10 px-0" aria-label="Semana anterior" onClick={() => setWeekOffset((w) => w - 1)}>
              <ChevronLeft size={16} />
            </Button>
            <Button variant="secondary" className="w-10 px-0" aria-label="Semana siguiente" onClick={() => setWeekOffset((w) => w + 1)}>
              <ChevronRight size={16} />
            </Button>
            <span className="ml-2 font-display text-lg font-semibold text-forest-900">
              {rangeLabel}
            </span>
            <Button variant="ghost" className="ml-1 h-8 px-3" onClick={() => setWeekOffset(0)}>
              Hoy
            </Button>
          </div>

          <div className="flex flex-wrap gap-2 text-xs">
            {Object.keys(EVENT_STYLES).map((k) => {
              const conf = EVENT_STYLES[k as keyof typeof EVENT_STYLES];
              const Icon = conf.icon;
              return (
                <span
                  key={k}
                  className={cn(
                    'flex items-center gap-1.5 rounded-md border px-2 py-1 font-semibold',
                    conf.cls
                  )}
                >
                  <Icon size={12} />
                  {conf.label}
                </span>
              );
            })}
          </div>
        </div>

        {/* Calendar Grid Table */}
        <Card className="overflow-x-auto">
          <div style={{ minWidth: 920 }}>
            {/* Header row */}
            <div
              className="grid border-b border-sand-200 bg-sand-50"
              style={{ gridTemplateColumns: `${colWidth} repeat(7, minmax(0, 1fr))` }}
            >
              <div className="p-3 text-xs font-semibold uppercase tracking-wider text-ink-soft">
                Habitación
              </div>
              {weekDays.map((d) => (
                <div
                  key={d.key}
                  className={cn(
                    'border-l border-sand-200 p-3 text-center',
                    d.today && 'bg-forest-100'
                  )}
                >
                  <p className="text-xs font-semibold uppercase tracking-wider text-ink-soft">
                    {d.label}
                  </p>
                  <p
                    className={cn(
                      'font-display text-xl font-semibold',
                      d.today ? 'text-forest-800' : 'text-ink'
                    )}
                  >
                    {d.n}
                    {d.today && (
                      <span className="ml-1 text-[10px] font-semibold uppercase tracking-wider text-terra-600 align-middle">
                        hoy
                      </span>
                    )}
                  </p>
                </div>
              ))}
            </div>

            {/* Room Rows */}
            {rooms.map((room) => {
              const roomEvents = calendarEvents.filter((e) => e.roomNumber === room.number);
              return (
                <div
                  key={room.id}
                  className="relative grid border-b border-sand-200 last:border-b-0"
                  style={{
                    gridTemplateColumns: `${colWidth} repeat(7, minmax(0, 1fr))`,
                    gridTemplateRows: '76px',
                  }}
                >
                  {/* Left Label */}
                  <div className="flex flex-col justify-center gap-1.5 px-3">
                    <p className="text-sm font-semibold">
                      <span className="font-display text-base text-forest-900">{room.number}</span>{' '}
                      {room.name}
                    </p>
                    <div>
                      <BadgeStatus status={room.status} size="sm" />
                    </div>
                  </div>

                  {/* Day background columns */}
                  {weekDays.map((d, idx) => (
                    <div
                      key={d.key}
                      style={{ gridColumn: idx + 2, gridRow: 1 }}
                      className={cn('border-l border-sand-200', d.today && 'bg-forest-50')}
                    />
                  ))}

                  {/* Event Bars */}
                  {roomEvents.map((ev) => {
                    const conf = EVENT_STYLES[ev.kind];
                    const Icon = conf.icon;
                    const isSelected = selectedEvent?.id === ev.id;
                    const colStart = ev.startDay + 2;
                    const colEnd = Math.min(ev.endDay, 7) + 2;

                    return (
                      <button
                        key={ev.id}
                        onClick={() => setSelectedEvent(ev)}
                        aria-label={`${ev.guest}, ${conf.label}`}
                        style={{
                          gridColumn: `${colStart} / ${colEnd}`,
                          gridRow: 1,
                        }}
                        className={cn(
                          'relative z-10 m-1.5 mt-3 flex min-w-0 cursor-pointer flex-col justify-center overflow-hidden rounded-lg border px-2.5 py-1 text-left transition-shadow hover:shadow-md',
                          conf.cls,
                          isSelected && 'ring-2 ring-offset-1 ring-terra-500'
                        )}
                      >
                        <span className="flex items-center gap-1.5 text-[13px] font-semibold">
                          <Icon size={12} className="shrink-0" />
                          <span className="truncate">{ev.guest}</span>
                        </span>
                        <span className="truncate text-[11px] opacity-85">
                          {ev.kind === 'bloqueo'
                            ? 'Bloqueo 15 min'
                            : `${ev.guests} huésp. · ${ev.code}`}
                        </span>
                      </button>
                    );
                  })}
                </div>
              );
            })}
          </div>
        </Card>

        {activeLocks.length > 0 && (
          <div className="mt-4">
            <Alert
              tone="warn"
              title={`${activeLocks.length} bloqueo(s) temporal(es) activo(s) en esta semana`}
            >
              Los bloqueos temporales de 15 minutos sin pago confirmado se liberan automáticamente por APScheduler (RN-02).
            </Alert>
          </div>
        )}
      </div>

      {/* Slide-in Sidebar for Event Details */}
      {selectedEvent && (
        <aside
          aria-label="Detalle de reserva en calendario"
          className="slide-in sticky top-6 h-fit w-[340px] shrink-0 self-start rounded-xl border border-sand-200 bg-white shadow-md max-[1100px]:fixed max-[1100px]:right-0 max-[1100px]:top-0 max-[1100px]:z-40 max-[1100px]:h-full max-[1100px]:rounded-none"
        >
          <div className="flex items-start justify-between border-b border-sand-200 p-5">
            <div>
              <span
                className={cn(
                  'mb-2 inline-flex items-center gap-1.5 rounded-md border px-2 py-1 text-xs font-semibold',
                  EVENT_STYLES[selectedEvent.kind].cls
                )}
              >
                {React.createElement(EVENT_STYLES[selectedEvent.kind].icon, { size: 12 })}
                {EVENT_STYLES[selectedEvent.kind].label}
              </span>
              <h3 className="font-display text-xl font-semibold text-forest-900">
                {selectedEvent.guest}
              </h3>
              <p className="text-sm text-ink-soft">Código {selectedEvent.code}</p>
            </div>
            <button
              aria-label="Cerrar panel"
              onClick={() => setSelectedEvent(null)}
              className="cursor-pointer rounded-md p-1 text-ink-soft hover:bg-sand-100"
            >
              <X size={18} />
            </button>
          </div>

          <div className="space-y-3.5 p-5 text-sm">
            <div className="flex justify-between">
              <span className="text-ink-soft">Habitación:</span>
              <span className="font-semibold text-ink">Hab. {selectedEvent.roomNumber}</span>
            </div>
            {selectedEvent.guests > 0 && (
              <div className="flex justify-between">
                <span className="text-ink-soft">Ocupación:</span>
                <span className="font-medium text-ink">{selectedEvent.guests} personas</span>
              </div>
            )}
            <div className="flex justify-between">
              <span className="text-ink-soft">Canal:</span>
              <span className="font-medium text-ink">{selectedEvent.channel}</span>
            </div>
            {selectedEvent.total > 0 && (
              <div className="rounded-lg bg-sand-50 p-3 ring-1 ring-sand-200 text-xs space-y-1">
                <div className="flex justify-between">
                  <span className="text-ink-soft">Total:</span>
                  <span className="font-bold">{formatCurrency(selectedEvent.total)}</span>
                </div>
                <div className="flex justify-between text-ok font-semibold">
                  <span>Abono pagado:</span>
                  <span>{formatCurrency(selectedEvent.paid)}</span>
                </div>
                <div className="flex justify-between text-warn font-semibold pt-1 border-t border-sand-200">
                  <span>Saldo pendiente:</span>
                  <span>{formatCurrency(selectedEvent.total - selectedEvent.paid)}</span>
                </div>
              </div>
            )}
            {selectedEvent.note && (
              <p className="text-xs italic bg-sand-50 p-2.5 rounded text-ink-soft">
                {selectedEvent.note}
              </p>
            )}
          </div>

          <div className="flex gap-2 border-t border-sand-200 p-5">
            <Button
              variant="primary"
              className="flex-1 text-xs"
              onClick={() => {
                go('reservas', selectedEvent.code);
              }}
            >
              Ver reserva completa
            </Button>
            <Button
              variant="secondary"
              onClick={() => setSelectedEvent(null)}
            >
              Cerrar
            </Button>
          </div>
        </aside>
      )}
    </div>
  );
}
