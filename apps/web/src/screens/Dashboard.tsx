import React, { useState } from 'react';
import {
  BedDouble,
  Clock,
  Sparkles,
  ShoppingBag,
  Plus,
  ArrowRight,
  AlertTriangle,
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
  ConfirmModal,
  useToast,
  formatCurrency,
  RoomStatusKey,
  ROOM_STATUS_META,
  useRealtimeClock,
} from '../ui';

export function Dashboard({ go }: { go: (view: string) => void }) {
  const { rooms, bookings, currentUser, setRoomStatus, log } = useStore();
  const [checkoutModalOpen, setCheckoutModalOpen] = useState(false);
  const { show, node } = useToast();
  const { formattedDate, formattedTime, greeting } = useRealtimeClock();

  const firstName = currentUser?.name ? currentUser.name.split(' ')[0] : 'Sofía';

  const totalRooms = rooms.length;
  const occupiedRooms = rooms.filter((r) => r.status === 'ocupada').length;
  const cleaningRooms = rooms.filter((r) => r.status === 'limpieza').length;
  const maintenanceRooms = rooms.filter((r) => r.status === 'mantenimiento').length;
  const blockedRooms = rooms.filter((r) => r.status === 'bloqueada').length;
  const freeRooms = rooms.filter((r) => r.status === 'libre').length;
  const occupancyPct = Math.round((occupiedRooms / (totalRooms || 1)) * 100);

  const kpis = [
    {
      label: 'Habitaciones ocupadas',
      value: `${occupiedRooms} de ${totalRooms}`,
      sub: `${occupancyPct}% de ocupación`,
      icon: BedDouble,
    },
    {
      label: 'Llegadas de hoy',
      value: '1',
      sub: 'Andrés Martínez · 3:00 pm',
      icon: Clock,
    },
    {
      label: 'Salidas de hoy',
      value: '1',
      sub: 'Laura Gómez · Salida lista',
      icon: ArrowRight,
    },
    {
      label: 'En limpieza',
      value: `${cleaningRooms}`,
      sub: 'Hab. 201 Balcón',
      icon: Sparkles,
    },
    {
      label: 'Ventas del día',
      value: formatCurrency(186500),
      sub: 'Tienda & Salgados Café',
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
        desc="Panel central de control y atención prioritaria para la recepción."
        actions={
          <Button
            variant="primary"
            icon={<Plus size={16} />}
            onClick={() => go('calendario')}
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
                  <span className="block text-sm font-semibold">Nueva reserva</span>
                  <span className="text-xs text-sand-200">Verificar fechas</span>
                </span>
              </button>

              <button
                onClick={() => go('llegadas')}
                className="flex cursor-pointer flex-col items-start gap-3 rounded-xl border border-sand-200 bg-sand-50 p-4 text-left transition-colors hover:border-forest-700"
              >
                <Clock size={20} className="text-terra-600" />
                <span>
                  <span className="block text-sm font-semibold text-ink">Check-in</span>
                  <span className="text-xs text-ink-soft">1 llegada hoy</span>
                </span>
              </button>

              <button
                onClick={() => setCheckoutModalOpen(true)}
                className="flex cursor-pointer flex-col items-start gap-3 rounded-xl border border-sand-200 bg-sand-50 p-4 text-left transition-colors hover:border-forest-700"
              >
                <ArrowRight size={20} className="text-terra-600" />
                <span>
                  <span className="block text-sm font-semibold text-ink">Check-out</span>
                  <span className="text-xs text-ink-soft">Laura Gómez (Hab. 101)</span>
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
              <div className="divide-y divide-sand-200">
                <div className="py-3 first:pt-0">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-sm font-semibold text-ink">Andrés Martínez</p>
                      <p className="text-[13px] text-ink-soft">Hab. 102 Familiar · 4 huéspedes</p>
                    </div>
                    <span className="flex items-center gap-1 rounded-md bg-sand-100 px-2 py-1 text-xs font-semibold text-forest-800">
                      <Clock size={12} />
                      Hoy 3:00 pm
                    </span>
                  </div>
                  <p className="mt-1.5 text-xs font-medium text-ok">✓ Anticipo del 50% confirmado ($435.000)</p>
                </div>

                <div className="py-3 last:pb-0">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-sm font-semibold text-ink">Camilo Herrera</p>
                      <p className="text-[13px] text-ink-soft">Hab. 201 Balcón · 3 huéspedes</p>
                    </div>
                    <span className="flex items-center gap-1 rounded-md bg-sand-100 px-2 py-1 text-xs font-semibold text-forest-800">
                      <Clock size={12} />
                      Sáb 3 oct
                    </span>
                  </div>
                  <p className="mt-1.5 text-xs font-medium text-warn">▲ Saldo pendiente de $320.000 al check-in</p>
                </div>
              </div>
            </Card>

            <Card className="p-5">
              <CardHeader title="Próximos check-outs" />
              <div className="divide-y divide-sand-200">
                <div className="py-3 first:pt-0">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-sm font-semibold text-ink">Laura Gómez</p>
                      <p className="text-[13px] text-ink-soft">Hab. 101 Jardín · 2 huéspedes</p>
                    </div>
                    <span className="flex items-center gap-1 rounded-md bg-sand-100 px-2 py-1 text-xs font-semibold text-forest-800">
                      <Clock size={12} />
                      Vie 2 oct, 11:00 am
                    </span>
                  </div>
                  <p className="mt-1.5 text-xs font-medium text-ok">✓ Habitación saldada · 3 consumos en tienda</p>
                </div>

                <div className="py-3 last:pb-0">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-sm font-semibold text-ink">Andrés Martínez</p>
                      <p className="text-[13px] text-ink-soft">Hab. 102 Familiar</p>
                    </div>
                    <span className="flex items-center gap-1 rounded-md bg-sand-100 px-2 py-1 text-xs font-semibold text-forest-800">
                      <Clock size={12} />
                      Dom 4 oct, 11:00 am
                    </span>
                  </div>
                  <p className="mt-1.5 text-xs font-medium text-warn">▲ Saldo restante $435.000</p>
                </div>
              </div>
            </Card>
          </div>
        </div>

        {/* Right Sidebar: Alerts & Room Distribution */}
        <div className="space-y-6">
          <Card className="p-5">
            <CardHeader
              title="Bloqueos temporales por vencer"
              hint="Reservas en espera de comprobante de pago"
            />
            <Alert
              tone="warn"
              title="Suite Satori (202) vence hoy 6:00 pm"
              action={
                <Button
                  variant="secondary"
                  className="h-8 px-3 text-xs"
                  onClick={() => show('Recordatorio enviado', 'WhatsApp enviado a María Fernanda Rojas')}
                >
                  Recordar
                </Button>
              }
            >
              María Fernanda Rojas · Faltan 5h 20m. Si no se registra el abono, la habitación vuelve a estado libre automáticamente.
            </Alert>
            <p className="mt-3 flex items-center gap-1.5 text-xs text-ink-soft">
              <Info size={14} /> Los bloqueos temporales en línea expiran a los 15 minutos sin confirmación.
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

      {/* Checkout Modal */}
      {checkoutModalOpen && (
        <ConfirmModal
          title="¿Registrar check-out de Laura Gómez?"
          confirm="Registrar salida"
          onCancel={() => setCheckoutModalOpen(false)}
          onConfirm={() => {
            setCheckoutModalOpen(false);
            setRoomStatus('101', 'limpieza', { note: 'Aseo de salida iniciado' });
            log('Registró check-out de Laura Gómez (Hab. 101)', 'Check-out');
            show('Check-out registrado exitosamente', 'Hab. 101 Jardín pasó a estado En limpieza');
          }}
        >
          La habitación 101 Jardín quedará en estado de <strong>limpieza</strong> y se notificará al personal de camarería.
          Verifica que la cuenta de habitación y consumos de Salgados Café se encuentren completamente liquidados.
        </ConfirmModal>
      )}

      {node}
    </div>
  );
}
