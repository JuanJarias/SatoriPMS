import React from 'react';
import {
  BedDouble,
  Clock,
  Sparkles,
  ShoppingBag,
  Plus,
  ArrowRight,
  Info
} from 'lucide-react';
import { useStore } from '../store';
import {
  PageHeader,
  Card,
  CardHeader,
  Button,
  BadgeStatus,
  Alert,
  formatCurrency,
  RoomStatusKey,
  useRealtimeClock,
} from '../ui';

export function Dashboard({ go }: { go: (view: string, param?: string) => void }) {
  const { rooms, bookings, orders, charges, currentUser } = useStore();
  const { formattedDate, formattedTime, greeting } = useRealtimeClock();

  const firstName = currentUser?.name ? currentUser.name.split(' ')[0] : 'Equipo';
  const todayIso = new Date().toISOString().slice(0, 10);

  const totalRooms = rooms.length;
  const occupiedRooms = rooms.filter((r) => r.status === 'ocupada').length;
  const cleaningRooms = rooms.filter((r) => r.status === 'limpieza').length;
  const maintenanceRooms = rooms.filter((r) => r.status === 'mantenimiento').length;
  const blockedRooms = rooms.filter((r) => r.status === 'bloqueada').length;
  const freeRooms = rooms.filter((r) => r.status === 'libre').length;
  const occupancyPct = Math.round((occupiedRooms / (totalRooms || 1)) * 100);

  const upcomingCheckins = bookings.filter((b) => b.status === 'confirmada');
  const activeInHouse = bookings.filter((b) => b.status === 'enCurso');
  const activeLocks = bookings.filter((b) => b.status === 'bloqueada');
  const todayArrivalsCount = upcomingCheckins.filter((b) => b.checkIn === todayIso).length;
  const todayDeparturesCount = activeInHouse.filter((b) => b.checkOut === todayIso).length;

  const pendingChargesTotal = Object.values(charges)
    .flat()
    .reduce((acc, c) => acc + c.amount, 0);
  const cafeOrdersTotal = orders.reduce((acc, o) => acc + (o.total || 0), 0);

  const kpis = [
    {
      label: 'Habitaciones ocupadas',
      value: `${occupiedRooms} de ${totalRooms}`,
      sub: `${occupancyPct}% de ocupación`,
      icon: BedDouble,
    },
    {
      label: 'Llegadas de hoy',
      value: `${todayArrivalsCount}`,
      sub: `${upcomingCheckins.length} reservas confirmadas`,
      icon: Clock,
    },
    {
      label: 'Salidas de hoy',
      value: `${todayDeparturesCount}`,
      sub: `${activeInHouse.length} huéspedes en casa`,
      icon: ArrowRight,
    },
    {
      label: 'En limpieza',
      value: `${cleaningRooms}`,
      sub: `${freeRooms} listas para ingreso`,
      icon: Sparkles,
    },
    {
      label: 'Consumos & Café',
      value: formatCurrency(pendingChargesTotal + cafeOrdersTotal),
      sub: `${orders.length} comandas registradas`,
      icon: ShoppingBag,
    },
  ];

  const statusCounts: { s: RoomStatusKey; n: number }[] = [
    { s: 'libre', n: freeRooms },
    { s: 'ocupada', n: occupiedRooms },
    { s: 'limpieza', n: cleaningRooms },
    { s: 'mantenimiento', n: maintenanceRooms },
    { s: 'bloqueada', n: blockedRooms },
  ];

  return (
    <div>
      <PageHeader
        eyebrow={`${formattedDate} · ${formattedTime}`}
        title={`${greeting}, ${firstName}`}
        desc="Panel central de control conectado en tiempo real con PostgreSQL 16."
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

      {/* KPI Cards */}
      <div className="grid grid-cols-2 gap-4 min-[1100px]:grid-cols-5">
        {kpis.map((kpi) => {
          const Icon = kpi.icon;
          return (
            <Card key={kpi.label} className="p-4">
              <div className="flex items-center justify-between text-ink-soft">
                <span className="text-[13px] font-medium">{kpi.label}</span>
                <Icon size={16} />
              </div>
              <p className="mt-2 font-display text-[28px] font-semibold leading-none text-forest-900">
                {kpi.value}
              </p>
              <p className="mt-2 text-xs text-ink-soft">{kpi.sub}</p>
            </Card>
          );
        })}
      </div>

      {/* Main Layout Grid */}
      <div className="mt-6 grid gap-6 min-[1100px]:grid-cols-[1.6fr_1fr]">
        <div className="space-y-6">
          {/* Quick Actions */}
          <Card className="p-5">
            <CardHeader title="Acciones rápidas de recepción" />
            <div className="grid grid-cols-2 gap-3 min-[1100px]:grid-cols-4">
              <button
                onClick={() => go('calendario')}
                className="flex cursor-pointer flex-col items-start gap-3 rounded-xl border border-forest-800 bg-forest-800 p-4 text-left text-white transition-colors hover:bg-forest-700 shadow-sm"
              >
                <Plus size={20} className="text-terra-100" />
                <span>
                  <span className="block text-sm font-semibold">Calendario</span>
                  <span className="text-xs text-sand-200">Ocupación semanal</span>
                </span>
              </button>

              <button
                onClick={() => go('llegadas')}
                className="flex cursor-pointer flex-col items-start gap-3 rounded-xl border border-sand-200 bg-sand-50 p-4 text-left transition-colors hover:border-forest-700"
              >
                <Clock size={20} className="text-terra-600" />
                <span>
                  <span className="block text-sm font-semibold text-ink">Check-in</span>
                  <span className="text-xs text-ink-soft">{upcomingCheckins.length} pendientes</span>
                </span>
              </button>

              <button
                onClick={() => go('salidas')}
                className="flex cursor-pointer flex-col items-start gap-3 rounded-xl border border-sand-200 bg-sand-50 p-4 text-left transition-colors hover:border-forest-700"
              >
                <ArrowRight size={20} className="text-terra-600" />
                <span>
                  <span className="block text-sm font-semibold text-ink">Check-out</span>
                  <span className="text-xs text-ink-soft">{activeInHouse.length} en casa</span>
                </span>
              </button>

              <button
                onClick={() => go('restaurante')}
                className="flex cursor-pointer flex-col items-start gap-3 rounded-xl border border-sand-200 bg-sand-50 p-4 text-left transition-colors hover:border-forest-700"
              >
                <ShoppingBag size={20} className="text-terra-600" />
                <span>
                  <span className="block text-sm font-semibold text-ink">Salgados Café</span>
                  <span className="text-xs text-ink-soft">Comandas y Tienda</span>
                </span>
              </button>
            </div>
          </Card>

          {/* Check-ins & Check-outs Lists */}
          <div className="grid gap-6 min-[1100px]:grid-cols-2">
            <Card className="p-5">
              <CardHeader title="Próximos check-ins" />
              {upcomingCheckins.length === 0 ? (
                <p className="text-xs text-ink-soft py-2">No hay llegadas confirmadas pendientes.</p>
              ) : (
                <div className="divide-y divide-sand-200">
                  {upcomingCheckins.slice(0, 4).map((b) => {
                    const roomObj = rooms.find((r) => r.id === b.roomId || r.number === b.room);
                    const pending = Math.max(0, b.total - b.paid);
                    return (
                      <div key={b.code} className="py-3 first:pt-0 last:pb-0">
                        <div className="flex items-start justify-between gap-3">
                          <div>
                            <p className="text-sm font-semibold text-ink">{b.guest}</p>
                            <p className="text-[13px] text-ink-soft">
                              Hab. {b.room} {roomObj?.name} · {b.guests} huéspedes
                            </p>
                          </div>
                          <span className="flex items-center gap-1 rounded-md bg-sand-100 px-2 py-1 text-xs font-semibold text-forest-800">
                            <Clock size={12} />
                            {b.checkIn}
                          </span>
                        </div>
                        <p className={`mt-1.5 text-xs font-medium ${pending > 0 ? 'text-warn' : 'text-ok'}`}>
                          {pending > 0
                            ? `▲ Saldo pendiente ${formatCurrency(pending)}`
                            : '✓ 100% Pagado'}
                        </p>
                      </div>
                    );
                  })}
                </div>
              )}
            </Card>

            <Card className="p-5">
              <CardHeader title="Huéspedes en casa (Check-outs)" />
              {activeInHouse.length === 0 ? (
                <p className="text-xs text-ink-soft py-2">No hay huéspedes con estadía EN_CURSO.</p>
              ) : (
                <div className="divide-y divide-sand-200">
                  {activeInHouse.slice(0, 4).map((b) => {
                    const roomObj = rooms.find((r) => r.id === b.roomId || r.number === b.room);
                    const pending = Math.max(0, b.total - b.paid);
                    return (
                      <div key={b.code} className="py-3 first:pt-0 last:pb-0">
                        <div className="flex items-start justify-between gap-3">
                          <div>
                            <p className="text-sm font-semibold text-ink">{b.guest}</p>
                            <p className="text-[13px] text-ink-soft">
                              Hab. {b.room} {roomObj?.name} · {b.guests} huéspedes
                            </p>
                          </div>
                          <Button
                            variant="secondary"
                            className="h-7 px-2.5 text-xs"
                            onClick={() => go('checkout', b.code)}
                          >
                            Check-out
                          </Button>
                        </div>
                        <p className={`mt-1.5 text-xs font-medium ${pending > 0 ? 'text-warn' : 'text-ok'}`}>
                          {pending > 0 ? `Saldo por liquidar: ${formatCurrency(pending)}` : '✓ Cuenta saldada'}
                        </p>
                      </div>
                    );
                  })}
                </div>
              )}
            </Card>
          </div>
        </div>

        {/* Right Sidebar: Alerts & Room Distribution */}
        <div className="space-y-6">
          <Card className="p-5">
            <CardHeader
              title="Bloqueos temporales activos"
              hint="Reservas en espera de confirmación de pago (15 min)"
            />
            {activeLocks.length === 0 ? (
              <p className="text-xs text-ink-soft">No hay bloqueos temporales pendientes en este momento.</p>
            ) : (
              <div className="space-y-2">
                {activeLocks.map((b) => (
                  <Alert
                    key={b.code}
                    tone="warn"
                    title={`Hab. ${b.room} · ${b.guest}`}
                    action={
                      <Button
                        variant="secondary"
                        className="h-8 px-3 text-xs"
                        onClick={() => go('reservas', b.code)}
                      >
                        Ver
                      </Button>
                    }
                  >
                    {b.checkIn} → {b.checkOut} · {formatCurrency(b.total)}
                  </Alert>
                ))}
              </div>
            )}
            <p className="mt-3 flex items-center gap-1.5 text-xs text-ink-soft">
              <Info size={14} /> Los bloqueos temporales expiran automáticamente a los 15 minutos sin pago.
            </p>
          </Card>

          <Card className="p-5">
            <CardHeader
              title="Estado de las habitaciones"
              hint={`Total: ${totalRooms} habitaciones en el hotel`}
            />
            <div className="space-y-3">
              {statusCounts.map((item) => (
                <div
                  key={item.s}
                  className="flex items-center justify-between border-b border-sand-200 pb-2 text-sm last:border-b-0"
                >
                  <BadgeStatus status={item.s} size="sm" />
                  <span className="font-semibold tabular-nums text-forest-900">
                    {item.n} hab.
                  </span>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
