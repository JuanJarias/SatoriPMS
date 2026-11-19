import React, { useState, useMemo } from 'react';
import {
  Plus,
  Search,
  Calendar,
  Clock,
  ArrowRight,
  CheckCircle2,
  AlertTriangle,
  X,
  CreditCard,
  Banknote,
  Send,
  User,
  Info
} from 'lucide-react';
import { useStore, BookingItem } from '../store';
import {
  PageHeader,
  Card,
  CardHeader,
  Button,
  Select,
  DateField,
  BookingStatusBadge,
  BadgeStatus,
  TableHeader,
  EmptyState,
  Modal,
  ConfirmModal,
  Alert,
  Stepper,
  Field,
  Input,
  useToast,
  formatCurrency,
  BookingStatusKey,
  BOOKING_STATUS_META
} from '../ui';

export function Reservas({ go, initialCode }: { go: (view: string, param?: string) => void; initialCode?: string }) {
  const { rooms, bookings, addBooking, patchBooking, setBookingStatus, setRoomStatus, charges, log } = useStore();
  const [selectedCode, setSelectedCode] = useState<string | null>(initialCode || null);
  const [newBookingModalOpen, setNewBookingModalOpen] = useState(false);

  // Filtros
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('todos');
  const [roomFilter, setRoomFilter] = useState('todas');
  const [channelFilter, setChannelFilter] = useState('todos');

  // Cancel Modal & Refund Calculation
  const [cancelModalBooking, setCancelModalBooking] = useState<BookingItem | null>(null);

  const { show, node } = useToast();

  const filteredBookings = bookings.filter((b) => {
    const q = search.trim().toLowerCase();
    const matchesSearch =
      !q ||
      b.code.toLowerCase().includes(q) ||
      b.guest.toLowerCase().includes(q) ||
      b.phone.toLowerCase().includes(q) ||
      b.room.toLowerCase().includes(q);
    const matchesStatus = statusFilter === 'todos' || b.status === statusFilter;
    const matchesRoom = roomFilter === 'todas' || b.room === roomFilter;
    const matchesChannel = channelFilter === 'todos' || b.channel === channelFilter;
    return matchesSearch && matchesStatus && matchesRoom && matchesChannel;
  });

  const selectedBooking = bookings.find((b) => b.code === selectedCode) || null;

  // Calculo de reembolso según regla RN-03 (+72h: 100%, 24h-72h: 50%, <24h: 0%) sobre lo pagado
  const calculateRefund = (b: BookingItem) => {
    const checkInDate = new Date(`${b.checkIn}T15:00:00`);
    const now = new Date('2026-10-01T10:00:00'); // Fecha de contexto SatoriPMS
    const diffHours = (checkInDate.getTime() - now.getTime()) / (1000 * 60 * 60);

    let pct = 0;
    let desc = '';
    if (diffHours > 72) {
      pct = 100;
      desc = 'Reembolso del 100% de lo pagado (más de 72h antes del check-in)';
    } else if (diffHours >= 24) {
      pct = 50;
      desc = 'Reembolso del 50% de lo pagado (entre 24h y 72h antes del check-in)';
    } else {
      pct = 0;
      desc = 'Sin reembolso (menos de 24h antes del check-in)';
    }

    const refundAmount = Math.round((b.paid * pct) / 100);
    return { pct, desc, refundAmount };
  };

  const handleConfirmCancel = () => {
    if (!cancelModalBooking) return;
    const { refundAmount } = calculateRefund(cancelModalBooking);
    setBookingStatus(cancelModalBooking.code, 'cancelada');
    setRoomStatus(cancelModalBooking.room, 'libre');
    log(
      `Canceló la reserva ${cancelModalBooking.code} (Huésped: ${cancelModalBooking.guest}, Reembolso: ${formatCurrency(refundAmount)})`,
      'Reservas'
    );
    show(
      'Reserva cancelada exitosamente',
      `Habitación ${cancelModalBooking.room} liberada. Reembolso: ${formatCurrency(refundAmount)}`
    );
    setCancelModalBooking(null);
  };

  // State para asistente de Nueva Reserva
  const [step, setStep] = useState(0);
  const [nbCheckIn, setNbCheckIn] = useState('2026-10-03');
  const [nbCheckOut, setNbCheckOut] = useState('2026-10-05');
  const [nbGuests, setNbGuests] = useState(2);
  const [nbRoomId, setNbRoomId] = useState('102');
  const [nbGuestName, setNbGuestName] = useState('');
  const [nbGuestPhone, setNbGuestPhone] = useState('');
  const [nbGuestDoc, setNbGuestDoc] = useState('');
  const [nbChannel, setNbChannel] = useState<'Recepción' | 'WhatsApp' | 'Teléfono'>('Recepción');
  const [nbPaymentMethod, setNbPaymentMethod] = useState<'efectivo' | 'transferencia' | 'datafono' | 'pendiente'>('transferencia');
  const [nbDepositType, setNbDepositType] = useState<'full' | 'half' | 'none'>('half');

  const selectedRoomObj = rooms.find((r) => r.number === nbRoomId || r.id === nbRoomId);
  const nights = Math.max(1, Math.round((new Date(nbCheckOut).getTime() - new Date(nbCheckIn).getTime()) / (1000 * 60 * 60 * 24)));
  const roomPricePerNight = selectedRoomObj ? selectedRoomObj.rate : 200000;
  const rawTotal = roomPricePerNight * nights;
  const calculatedDeposit = nbDepositType === 'full' ? rawTotal : nbDepositType === 'half' ? Math.round(rawTotal / 2) : 0;

  const handleCreateBooking = () => {
    if (!nbGuestName.trim() || !nbGuestPhone.trim()) {
      show('Faltan datos obligatorios', 'Por favor ingresa nombre y teléfono del huésped', 'bad');
      return;
    }
    const newCode = 'TS-' + Math.floor(1000 + Math.random() * 9000);
    const newB: BookingItem = {
      code: newCode,
      guest: nbGuestName.trim(),
      room: selectedRoomObj ? selectedRoomObj.number : '102',
      checkIn: nbCheckIn,
      checkOut: nbCheckOut,
      guests: nbGuests,
      channel: nbChannel,
      phone: nbGuestPhone.trim(),
      doc: nbGuestDoc.trim() || undefined,
      total: rawTotal,
      paid: calculatedDeposit,
      status: calculatedDeposit > 0 ? 'confirmada' : 'pendiente',
    };
    addBooking(newB);
    show('Reserva creada exitosamente', `Código: ${newCode} (${newB.guest})`);
    setNewBookingModalOpen(false);
    setSelectedCode(newCode);
    setStep(0);
    setNbGuestName('');
    setNbGuestPhone('');
  };

  return (
    <div>
      <PageHeader
        eyebrow="Gestión Hotelera"
        title="Reservas & Cancelaciones"
        desc="Consulta, emisión de reservas manuales, cobro de anticipos y liquidación de reembolsos."
        actions={
          <Button
            variant="terra"
            icon={<Plus size={16} />}
            onClick={() => setNewBookingModalOpen(true)}
          >
            Nueva reserva manual
          </Button>
        }
      />

      {/* Si hay una reserva seleccionada para ver detalle */}
      {selectedBooking ? (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <Button variant="secondary" onClick={() => setSelectedCode(null)}>
              ← Volver al listado de reservas
            </Button>
            <div className="flex items-center gap-2">
              {['confirmada', 'pendiente', 'bloqueada'].includes(selectedBooking.status) && (
                <Button
                  variant="danger"
                  onClick={() => setCancelModalBooking(selectedBooking)}
                >
                  Cancelar reserva
                </Button>
              )}
              {selectedBooking.status === 'confirmada' && (
                <Button
                  variant="primary"
                  onClick={() => go('checkin', selectedBooking.code)}
                >
                  Realizar Check-in
                </Button>
              )}
              {selectedBooking.status === 'enCurso' && (
                <Button
                  variant="terra"
                  onClick={() => go('checkout', selectedBooking.code)}
                >
                  Realizar Check-out
                </Button>
              )}
            </div>
          </div>

          <div className="grid gap-6 min-[1100px]:grid-cols-3">
            <Card className="p-5">
              <CardHeader title="Información de la Reserva" />
              <dl className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <dt className="text-ink-soft">Código de reserva:</dt>
                  <dd className="font-bold text-forest-900">{selectedBooking.code}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-ink-soft">Estado:</dt>
                  <dd><BookingStatusBadge status={selectedBooking.status} /></dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-ink-soft">Habitación asignada:</dt>
                  <dd className="font-semibold text-ink">Hab. {selectedBooking.room}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-ink-soft">Fechas de estancia:</dt>
                  <dd className="font-medium text-ink">{selectedBooking.checkIn} → {selectedBooking.checkOut}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-ink-soft">Canal de origen:</dt>
                  <dd className="font-medium text-ink">{selectedBooking.channel}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-ink-soft">Ocupación:</dt>
                  <dd className="font-medium text-ink">{selectedBooking.guests} persona(s)</dd>
                </div>
              </dl>
            </Card>

            <Card className="p-5">
              <CardHeader title="Datos del Huésped" />
              <dl className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <dt className="text-ink-soft">Nombre:</dt>
                  <dd className="font-semibold text-ink">{selectedBooking.guest}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-ink-soft">WhatsApp / Teléfono:</dt>
                  <dd className="font-medium text-forest-700">{selectedBooking.phone}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-ink-soft">Documento:</dt>
                  <dd className="font-medium text-ink">{selectedBooking.doc || 'Por registrar en check-in'}</dd>
                </div>
                {selectedBooking.note && (
                  <div className="pt-2 border-t border-sand-200">
                    <dt className="text-xs text-ink-soft mb-1">Notas especiales:</dt>
                    <dd className="text-xs italic bg-sand-50 p-2 rounded text-ink">{selectedBooking.note}</dd>
                  </div>
                )}
              </dl>
            </Card>

            <Card className="p-5">
              <CardHeader title="Balance Financiero" />
              <dl className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <dt className="text-ink-soft">Valor hospedaje:</dt>
                  <dd className="font-semibold text-ink">{formatCurrency(selectedBooking.total)}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-ink-soft">Abono pagado:</dt>
                  <dd className="font-semibold text-ok">{formatCurrency(selectedBooking.paid)}</dd>
                </div>
                <div className="flex justify-between border-t border-sand-200 pt-2 text-base font-bold">
                  <dt className="text-ink">Saldo pendiente:</dt>
                  <dd className={selectedBooking.total - selectedBooking.paid > 0 ? 'text-warn' : 'text-ok'}>
                    {formatCurrency(selectedBooking.total - selectedBooking.paid)}
                  </dd>
                </div>
              </dl>

              {selectedBooking.total - selectedBooking.paid > 0 && selectedBooking.status !== 'cancelada' && (
                <div className="mt-4">
                  <Button
                    variant="secondary"
                    className="w-full text-xs"
                    onClick={() => {
                      patchBooking(selectedBooking.code, { paid: selectedBooking.total });
                      show('Pago liquidado', `Saldo de ${selectedBooking.code} saldado al 100%`);
                    }}
                  >
                    Registrar pago de saldo restante
                  </Button>
                </div>
              )}
            </Card>
          </div>
        </div>
      ) : (
        /* Listado Principal */
        <div className="space-y-5">
          <Card className="p-4">
            <div className="grid gap-3 min-[1100px]:grid-cols-4">
              <div className="relative">
                <Search size={16} className="absolute left-3 top-3 text-ink-soft" />
                <Input
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Código TS-2047, huésped, teléfono…"
                  className="pl-9"
                />
              </div>

              <Select
                label="Estado"
                value={statusFilter}
                onChange={setStatusFilter}
                options={[
                  { value: 'todos', label: 'Todos los estados' },
                  ...(Object.keys(BOOKING_STATUS_META) as BookingStatusKey[]).map((k) => ({
                    value: k,
                    label: BOOKING_STATUS_META[k].label,
                  })),
                ]}
              />

              <Select
                label="Habitación"
                value={roomFilter}
                onChange={setRoomFilter}
                options={[
                  { value: 'todas', label: 'Todas las habitaciones' },
                  ...rooms.map((r) => ({ value: r.number, label: `Hab. ${r.number} ${r.name}` })),
                ]}
              />

              <Select
                label="Canal"
                value={channelFilter}
                onChange={setChannelFilter}
                options={[
                  { value: 'todos', label: 'Todos los canales' },
                  { value: 'WhatsApp', label: 'WhatsApp' },
                  { value: 'Recepción', label: 'Recepción' },
                  { value: 'Teléfono', label: 'Teléfono' },
                  { value: 'Web', label: 'Web' },
                ]}
              />
            </div>
          </Card>

          <Card className="overflow-hidden">
            {filteredBookings.length === 0 ? (
              <EmptyState
                icon={<Clock size={28} />}
                title="Ninguna reserva coincide con los filtros"
              >
                <Button
                  variant="secondary"
                  className="mt-3"
                  onClick={() => {
                    setSearch('');
                    setStatusFilter('todos');
                    setRoomFilter('todas');
                    setChannelFilter('todos');
                  }}
                >
                  Limpiar filtros
                </Button>
              </EmptyState>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead className="bg-sand-50">
                    <tr>
                      <TableHeader>Código</TableHeader>
                      <TableHeader>Huésped</TableHeader>
                      <TableHeader>Habitación</TableHeader>
                      <TableHeader>Fechas</TableHeader>
                      <TableHeader>Canal</TableHeader>
                      <TableHeader>Estado</TableHeader>
                      <TableHeader right>Saldo</TableHeader>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-sand-200">
                    {filteredBookings.map((b) => {
                      const balance = b.total - b.paid;
                      return (
                        <tr
                          key={b.code}
                          onClick={() => setSelectedCode(b.code)}
                          className="cursor-pointer hover:bg-forest-50 transition-colors"
                        >
                          <td className="px-4 py-3 font-semibold text-forest-800">{b.code}</td>
                          <td className="px-4 py-3">
                            <p className="font-medium text-ink">{b.guest}</p>
                            <p className="text-xs text-ink-soft">{b.code === 'TS-2391' ? (b.doc || b.phone) : (b.phone || b.doc)}</p>
                          </td>
                          <td className="px-4 py-3 font-medium">Hab. {b.room}</td>
                          <td className="px-4 py-3">
                            <p className="text-xs font-medium text-ink">{b.checkIn} → {b.checkOut}</p>
                          </td>
                          <td className="px-4 py-3 text-ink-soft text-xs">{b.channel}</td>
                          <td className="px-4 py-3">
                            <BookingStatusBadge status={b.status} />
                          </td>
                          <td className={`px-4 py-3 text-right font-semibold tabular-nums ${balance > 0 && b.status !== 'cancelada' ? 'text-warn' : 'text-ink-soft'}`}>
                            {b.status === 'cancelada' ? '—' : formatCurrency(balance)}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </Card>
        </div>
      )}

      {/* Modal: Asistente para Nueva Reserva */}
      {newBookingModalOpen && (
        <Modal
          title="Nueva Reserva Manual"
          maxWidth="max-w-xl"
          onClose={() => setNewBookingModalOpen(false)}
          footer={
            <div className="flex justify-between w-full">
              {step > 0 ? (
                <Button variant="secondary" onClick={() => setStep(step - 1)}>
                  Atrás
                </Button>
              ) : <div />}
              {step < 2 ? (
                <Button variant="primary" onClick={() => setStep(step + 1)}>
                  Continuar
                </Button>
              ) : (
                <Button variant="terra" onClick={handleCreateBooking}>
                  Confirmar y Guardar Reserva
                </Button>
              )}
            </div>
          }
        >
          <Stepper
            steps={['Fechas y Habitación', 'Huésped', 'Pago y Confirmación']}
            current={step}
          />

          {step === 0 && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <Field label="Fecha de Llegada (Check-in)">
                  <DateField value={nbCheckIn} onChange={setNbCheckIn} />
                </Field>
                <Field label="Fecha de Salida (Check-out)">
                  <DateField value={nbCheckOut} onChange={setNbCheckOut} />
                </Field>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <Field label="Habitación a reservar">
                  <Select
                    value={nbRoomId}
                    onChange={setNbRoomId}
                    options={rooms.map((r) => ({
                      value: r.number,
                      label: `Hab. ${r.number} ${r.name} (${formatCurrency(r.rate)}/noche)`,
                    }))}
                  />
                </Field>
                <Field label="Cantidad de personas">
                  <Input
                    type="number"
                    min={1}
                    max={6}
                    value={nbGuests}
                    onChange={(e) => setNbGuests(Number(e.target.value))}
                  />
                </Field>
              </div>

              <Alert tone="info" title="Resumen de tarifa">
                {nights} noche(s) × {formatCurrency(roomPricePerNight)} = <strong>{formatCurrency(rawTotal)}</strong>
              </Alert>
            </div>
          )}

          {step === 1 && (
            <div className="space-y-4">
              <Field label="Nombre y Apellidos del Huésped *">
                <Input
                  value={nbGuestName}
                  onChange={(e) => setNbGuestName(e.target.value)}
                  placeholder="Ej. Laura Gómez"
                />
              </Field>
              <div className="grid grid-cols-2 gap-3">
                <Field label="Teléfono / WhatsApp *">
                  <Input
                    value={nbGuestPhone}
                    onChange={(e) => setNbGuestPhone(e.target.value)}
                    placeholder="+57 310 555 0123"
                  />
                </Field>
                <Field label="Documento de Identidad">
                  <Input
                    value={nbGuestDoc}
                    onChange={(e) => setNbGuestDoc(e.target.value)}
                    placeholder="CC 1.113.555.201"
                  />
                </Field>
              </div>
              <Field label="Canal de Recepción">
                <Select
                  value={nbChannel}
                  onChange={(val) => setNbChannel(val as any)}
                  options={[
                    { value: 'Recepción', label: 'Recepción directa' },
                    { value: 'WhatsApp', label: 'WhatsApp Hotel' },
                    { value: 'Teléfono', label: 'Llamada Telefónica' },
                  ]}
                />
              </Field>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-4">
              <Field label="Opción de abono / pago">
                <div className="grid grid-cols-3 gap-2">
                  <button
                    type="button"
                    onClick={() => setNbDepositType('half')}
                    className={`p-3 rounded-lg border text-xs font-semibold text-center cursor-pointer ${nbDepositType === 'half' ? 'border-forest-800 bg-forest-50 text-forest-900 ring-1 ring-forest-800' : 'border-sand-300'}`}
                  >
                    Anticipo 50%
                    <span className="block mt-1 font-bold text-sm text-forest-800">
                      {formatCurrency(Math.round(rawTotal / 2))}
                    </span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setNbDepositType('full')}
                    className={`p-3 rounded-lg border text-xs font-semibold text-center cursor-pointer ${nbDepositType === 'full' ? 'border-forest-800 bg-forest-50 text-forest-900 ring-1 ring-forest-800' : 'border-sand-300'}`}
                  >
                    Pago Total 100%
                    <span className="block mt-1 font-bold text-sm text-forest-800">
                      {formatCurrency(rawTotal)}
                    </span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setNbDepositType('none')}
                    className={`p-3 rounded-lg border text-xs font-semibold text-center cursor-pointer ${nbDepositType === 'none' ? 'border-forest-800 bg-forest-50 text-forest-900 ring-1 ring-forest-800' : 'border-sand-300'}`}
                  >
                    Pendiente $0
                    <span className="block mt-1 font-bold text-sm text-warn">
                      $0
                    </span>
                  </button>
                </div>
              </Field>

              <Field label="Método de pago">
                <Select
                  value={nbPaymentMethod}
                  onChange={(val) => setNbPaymentMethod(val as any)}
                  options={[
                    { value: 'transferencia', label: 'Transferencia bancaria / Nequi / Daviplata' },
                    { value: 'efectivo', label: 'Efectivo en recepción' },
                    { value: 'datafono', label: 'Datáfono (Tarjeta)' },
                    { value: 'pendiente', label: 'Sin pago inicial' },
                  ]}
                />
              </Field>

              <div className="bg-sand-50 p-3 rounded-lg text-xs space-y-1">
                <div className="flex justify-between">
                  <span>Total reserva:</span>
                  <span className="font-bold">{formatCurrency(rawTotal)}</span>
                </div>
                <div className="flex justify-between text-ok font-semibold">
                  <span>Abono registrado ahora:</span>
                  <span>{formatCurrency(calculatedDeposit)}</span>
                </div>
                <div className="flex justify-between text-warn font-semibold">
                  <span>Saldo a pagar al Check-in:</span>
                  <span>{formatCurrency(rawTotal - calculatedDeposit)}</span>
                </div>
              </div>
            </div>
          )}
        </Modal>
      )}

      {/* Modal: Cancelación con Regla de Reembolso RN-03 */}
      {cancelModalBooking && (() => {
        const { pct, desc, refundAmount } = calculateRefund(cancelModalBooking);
        return (
          <ConfirmModal
            title={`¿Cancelar reserva ${cancelModalBooking.code}?`}
            confirm="Confirmar cancelación"
            danger
            onCancel={() => setCancelModalBooking(null)}
            onConfirm={handleConfirmCancel}
          >
            <div className="space-y-3">
              <p>
                Estás cancelando la reserva de <strong>{cancelModalBooking.guest}</strong> para la habitación {cancelModalBooking.room}.
              </p>
              <div className="bg-sand-50 p-3 rounded-lg border border-sand-200 text-xs space-y-1.5">
                <p className="font-semibold text-forest-900">Aplicación de Política Hotelera RN-03:</p>
                <p className="text-ink-soft">{desc}</p>
                <div className="flex justify-between pt-1 border-t border-sand-200 text-sm">
                  <span>Total abonado previamente:</span>
                  <span className="font-bold">{formatCurrency(cancelModalBooking.paid)}</span>
                </div>
                <div className="flex justify-between text-sm text-ok font-bold">
                  <span>Monto a reembolsar ({pct}%):</span>
                  <span>{formatCurrency(refundAmount)}</span>
                </div>
              </div>
              <p className="text-xs text-ink-soft">
                Al confirmar, la habitación quedará inmediatamente libre en el calendario y se registrará el movimiento en la auditoría.
              </p>
            </div>
          </ConfirmModal>
        );
      })()}

      {node}
    </div>
  );
}
