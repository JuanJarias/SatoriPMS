import React, { useState } from 'react';
import {
  ArrowRight,
  Clock,
  CheckCircle2,
  AlertTriangle,
  UserCheck,
  ShieldCheck,
  CreditCard,
  Banknote,
  Send,
  Sparkles,
  ShoppingBag,
  Info
} from 'lucide-react';
import { useStore, BookingItem } from '../store';
import {
  PageHeader,
  Card,
  CardHeader,
  Button,
  BadgeStatus,
  BookingStatusBadge,
  TableHeader,
  EmptyState,
  Alert,
  Stepper,
  Field,
  Input,
  Select,
  useToast,
  formatCurrency,
  RoomStatusKey,
  cn
} from '../ui';

export function Operacion({
  subview = 'llegadas',
  code,
  go,
}: {
  subview?: 'llegadas' | 'salidas' | 'checkin' | 'checkout';
  code?: string;
  go: (view: string, param?: string) => void;
}) {
  const { rooms, bookings, charges, clearCharges, patchBooking, setBookingStatus, setRoomStatus, log } = useStore();
  const { show, node } = useToast();

  const todayStr = '2026-10-01';

  // --- SUBVIEW: LLEGADAS (Check-in hoy) ---
  if (subview === 'llegadas') {
    const todayArrivals = bookings.filter(
      (b) => b.checkIn === todayStr && b.status !== 'cancelada'
    );

    return (
      <div>
        <PageHeader
          eyebrow="Operación de Recepción · Jueves 1 de oct"
          title="Llegadas & Check-in"
          desc="Huéspedes con reserva para ingresar hoy. Verifica su identidad y entrega de llaves."
        />

        <Card className="overflow-hidden">
          {todayArrivals.length === 0 ? (
            <EmptyState
              icon={<Clock size={28} />}
              title="No hay más llegadas programadas para hoy"
            />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="bg-sand-50">
                  <tr>
                    <TableHeader>Huésped</TableHeader>
                    <TableHeader>Habitación</TableHeader>
                    <TableHeader>Personas</TableHeader>
                    <TableHeader>Estado</TableHeader>
                    <TableHeader>Pago</TableHeader>
                    <TableHeader right>Acción</TableHeader>
                  </tr>
                </thead>
                <tbody className="divide-y divide-sand-200">
                  {todayArrivals.map((b) => {
                    const roomObj = rooms.find((r) => r.number === b.room || r.id === b.room);
                    const isPending = b.status === 'pendiente' || b.status === 'bloqueada';
                    const balance = b.total - b.paid;

                    return (
                      <tr key={b.code} className="hover:bg-forest-50 transition-colors">
                        <td className="px-4 py-3">
                          <p className="font-semibold text-ink">{b.guest}</p>
                          <p className="text-xs text-ink-soft">{b.code} · {b.phone}</p>
                        </td>
                        <td className="px-4 py-3 font-medium">
                          Hab. {b.room} {roomObj?.name}
                        </td>
                        <td className="px-4 py-3">{b.guests} pers.</td>
                        <td className="px-4 py-3">
                          <BookingStatusBadge status={b.status} />
                        </td>
                        <td className="px-4 py-3">
                          <span className={cn('font-semibold text-xs tabular-nums', balance > 0 ? 'text-warn' : 'text-ok')}>
                            {balance > 0 ? `Saldo ${formatCurrency(balance)}` : '100% Pagado'}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-right">
                          {b.status === 'enCurso' ? (
                            <span className="text-xs font-semibold text-ok">Check-in realizado</span>
                          ) : isPending ? (
                            <Button
                              variant="secondary"
                              className="h-8 px-3 text-xs"
                              onClick={() => go('reservas', b.code)}
                            >
                              Confirmar anticipo
                            </Button>
                          ) : (
                            <Button
                              variant="primary"
                              className="h-8 px-3 text-xs"
                              onClick={() => go('checkin', b.code)}
                            >
                              Hacer check-in
                            </Button>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </Card>
        {node}
      </div>
    );
  }

  // --- SUBVIEW: CHECK-IN ASISTIDO ---
  if (subview === 'checkin') {
    const booking = bookings.find((b) => b.code === code) || bookings.find((b) => b.code === 'TS-2047');
    const roomObj = rooms.find((r) => r.number === booking?.room || r.id === booking?.room);

    const [ciStep, setCiStep] = useState(0);
    const [docType, setDocType] = useState('CC');
    const [docNumber, setDocNumber] = useState(booking?.doc?.replace(/^\w+ /, '') || '94.333.712');
    const [verifiedDoc, setVerifiedDoc] = useState(false);
    const [actualGuests, setActualGuests] = useState(booking?.guests || 2);
    const [paymentOption, setPaymentOption] = useState<'efectivo' | 'datafono' | 'transferencia' | 'pendiente'>('efectivo');
    const [completed, setCompleted] = useState(false);

    if (!booking || !roomObj) {
      return (
        <Card className="p-8 text-center">
          <p className="font-semibold text-ink">No se encontró la reserva solicitada.</p>
          <Button variant="secondary" className="mt-4" onClick={() => go('llegadas')}>
            Volver a llegadas
          </Button>
        </Card>
      );
    }

    const pendingBalance = booking.total - booking.paid;

    const handleFinishCheckIn = () => {
      patchBooking(booking.code, {
        doc: `${docType} ${docNumber}`,
        guests: actualGuests,
        paid: paymentOption === 'pendiente' ? booking.paid : booking.total,
      });
      setBookingStatus(booking.code, 'enCurso');
      setRoomStatus(roomObj.id, 'ocupada', {
        guest: booking.guest,
        until: `Sale ${booking.checkOut}, 11:00 am`,
      });
      log(`Registró check-in de ${booking.guest} (Hab. ${roomObj.number})`, 'Check-in');
      setCompleted(true);
    };

    if (completed) {
      return (
        <div className="mx-auto max-w-lg pt-10 text-center">
          <Card className="p-8">
            <span className="mx-auto mb-4 grid h-12 w-12 place-items-center rounded-full bg-ok-bg text-ok">
              <CheckCircle2 size={26} />
            </span>
            <h1 className="font-display text-2xl font-semibold text-forest-900">
              Check-in completado con éxito
            </h1>
            <p className="mt-2 text-ink-soft text-sm">
              {booking.guest} ha quedado registrado en la <strong>Hab. {roomObj.number} {roomObj.name}</strong> hasta el {booking.checkOut}.
            </p>
            <div className="mt-4 inline-flex items-center gap-2 rounded-lg bg-sand-50 border border-sand-200 px-4 py-2 text-xs font-semibold text-ink">
              <span>Hab. {roomObj.number}:</span>
              <BadgeStatus status="libre" size="sm" />
              <span>→</span>
              <BadgeStatus status="ocupada" size="sm" />
            </div>
            <div className="mt-6 flex justify-center gap-2">
              <Button variant="primary" onClick={() => go('habitaciones')}>
                Ver panel de habitaciones
              </Button>
              <Button variant="secondary" onClick={() => go('llegadas')}>
                Volver a llegadas
              </Button>
            </div>
          </Card>
        </div>
      );
    }

    return (
      <div>
        <PageHeader
          eyebrow={`Check-in Asistido · ${booking.code}`}
          title={`Recepción de ${booking.guest}`}
          desc={`Hab. ${roomObj.number} ${roomObj.name} · Llegada ${booking.checkIn} a ${booking.checkOut}`}
          actions={
            <Button variant="secondary" onClick={() => go('llegadas')}>
              Cancelar
            </Button>
          }
        />

        <Stepper steps={['Verificación de Identidad', 'Ocupación', 'Liquidación']} current={ciStep} />

        <div className="grid gap-6 min-[1100px]:grid-cols-[1.3fr_1fr]">
          <Card className="p-5">
            {ciStep === 0 && (
              <div className="space-y-4">
                <CardHeader title="Verificación de Documento de Identidad" />
                <div className="grid grid-cols-[120px_1fr] gap-3">
                  <Field label="Tipo">
                    <Select
                      value={docType}
                      onChange={setDocType}
                      options={[
                        { value: 'CC', label: 'CC' },
                        { value: 'CE', label: 'CE' },
                        { value: 'Pasaporte', label: 'Pasaporte' },
                        { value: 'TI', label: 'TI' },
                      ]}
                    />
                  </Field>
                  <Field label="Número de documento">
                    <Input
                      value={docNumber}
                      onChange={(e) => setDocNumber(e.target.value)}
                      placeholder="Número del titular"
                    />
                  </Field>
                </div>

                <label className="flex items-start gap-3 rounded-lg border border-sand-200 bg-sand-50 p-3 text-sm cursor-pointer">
                  <input
                    type="checkbox"
                    checked={verifiedDoc}
                    onChange={(e) => setVerifiedDoc(e.target.checked)}
                    className="mt-1 h-4 w-4 rounded border-sand-300 text-forest-800"
                  />
                  <div>
                    <span className="font-semibold text-forest-900 block">
                      Documento físico verificado en recepción
                    </span>
                    <span className="text-xs text-ink-soft">
                      Confirmo que el documento coincide con los datos del huésped.
                    </span>
                  </div>
                </label>

                <div className="flex justify-end pt-3">
                  <Button
                    variant="primary"
                    disabled={!verifiedDoc || docNumber.trim().length < 5}
                    onClick={() => setCiStep(1)}
                  >
                    Continuar a ocupación
                  </Button>
                </div>
              </div>
            )}

            {ciStep === 1 && (
              <div className="space-y-4">
                <CardHeader
                  title="Conteo de Huéspedes en Habitación"
                  hint={`Capacidad base: ${roomObj.baseAdultsCapacity || 2}, Máxima: ${roomObj.capacity}`}
                />
                <Field label="Personas que se alojarán">
                  <div className="flex items-center gap-3">
                    <Button
                      variant="secondary"
                      className="w-10 px-0"
                      onClick={() => setActualGuests(Math.max(1, actualGuests - 1))}
                    >
                      −
                    </Button>
                    <span className="font-display text-2xl font-bold w-10 text-center">
                      {actualGuests}
                    </span>
                    <Button
                      variant="secondary"
                      className="w-10 px-0"
                      onClick={() => setActualGuests(Math.min(roomObj.capacity, actualGuests + 1))}
                    >
                      +
                    </Button>
                  </div>
                </Field>

                {actualGuests > (roomObj.baseAdultsCapacity || 2) && (
                  <Alert tone="warn" title="Persona adicional sobre capacidad base">
                    Se adiciona tarifa de persona extra por noche según parámetros de administración.
                  </Alert>
                )}

                <div className="flex justify-between pt-3">
                  <Button variant="secondary" onClick={() => setCiStep(0)}>
                    Atrás
                  </Button>
                  <Button variant="primary" onClick={() => setCiStep(2)}>
                    Continuar a pago
                  </Button>
                </div>
              </div>
            )}

            {ciStep === 2 && (
              <div className="space-y-4">
                <CardHeader title="Liquidación de Saldo al Ingreso" />
                {pendingBalance > 0 ? (
                  <>
                    <Alert tone="warn" title={`Saldo pendiente por cobrar: ${formatCurrency(pendingBalance)}`}>
                      Puedes recaudar el saldo ahora en recepción o dejarlo pendiente para el Check-out.
                    </Alert>

                    <Field label="Método de recaudación">
                      <Select
                        value={paymentOption}
                        onChange={(val) => setPaymentOption(val as any)}
                        options={[
                          { value: 'efectivo', label: 'Efectivo en recepción' },
                          { value: 'datafono', label: 'Datáfono (Tarjeta débito / crédito)' },
                          { value: 'transferencia', label: 'Transferencia bancaria / Nequi' },
                          { value: 'pendiente', label: 'Dejar saldo pendiente para el check-out' },
                        ]}
                      />
                    </Field>
                  </>
                ) : (
                  <Alert tone="ok" title="Cuenta de hospedaje saldada al 100%">
                    La reserva ya fue pagada en su totalidad con anterioridad.
                  </Alert>
                )}

                <div className="flex justify-between pt-3">
                  <Button variant="secondary" onClick={() => setCiStep(1)}>
                    Atrás
                  </Button>
                  <Button variant="terra" onClick={handleFinishCheckIn}>
                    Completar check-in y entregar llaves
                  </Button>
                </div>
              </div>
            )}
          </Card>

          <Card className="p-5 h-fit">
            <CardHeader title="Resumen de Habitación" />
            <div className="flex items-center justify-between mb-4 border-b border-sand-200 pb-3">
              <span className="font-display text-3xl font-bold text-forest-900">
                Hab. {roomObj.number}
              </span>
              <BadgeStatus status={roomObj.status} />
            </div>
            <dl className="space-y-2 text-sm">
              <div className="flex justify-between">
                <dt className="text-ink-soft">Nombre:</dt>
                <dd className="font-semibold text-ink">{roomObj.name}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-ink-soft">Tarifa por noche:</dt>
                <dd className="font-medium text-ink">{formatCurrency(roomObj.rate)}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-ink-soft">Total estancia:</dt>
                <dd className="font-bold text-forest-900">{formatCurrency(booking.total)}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-ink-soft">Abonado previamente:</dt>
                <dd className="font-bold text-ok">{formatCurrency(booking.paid)}</dd>
              </div>
            </dl>
          </Card>
        </div>
        {node}
      </div>
    );
  }

  // --- SUBVIEW: SALIDAS (Check-out hoy) ---
  if (subview === 'salidas') {
    const activeDepartures = bookings.filter(
      (b) => b.status === 'enCurso' || (b.status === 'finalizada' && b.checkOut === todayStr)
    );

    return (
      <div>
        <PageHeader
          eyebrow="Operación de Recepción · Jueves 1 de oct"
          title="Salidas & Check-out"
          desc="Huéspedes que finalizan su estancia. Liquida consumos de tienda y restaurante Salgados Café."
        />

        <Card className="overflow-hidden">
          {activeDepartures.length === 0 ? (
            <EmptyState
              icon={<ArrowRight size={28} />}
              title="No hay salidas pendientes para hoy"
            />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="bg-sand-50">
                  <tr>
                    <TableHeader>Huésped</TableHeader>
                    <TableHeader>Habitación</TableHeader>
                    <TableHeader>Fecha de salida</TableHeader>
                    <TableHeader>Estado</TableHeader>
                    <TableHeader>Consumos adicionales</TableHeader>
                    <TableHeader right>Acción</TableHeader>
                  </tr>
                </thead>
                <tbody className="divide-y divide-sand-200">
                  {activeDepartures.map((b) => {
                    const roomObj = rooms.find((r) => r.number === b.room || r.id === b.room);
                    const roomCharges = charges[b.room] || [];
                    const chargesTotal = roomCharges.reduce((acc, c) => acc + c.amount, 0);

                    return (
                      <tr key={b.code} className="hover:bg-forest-50 transition-colors">
                        <td className="px-4 py-3">
                          <p className="font-semibold text-ink">{b.guest}</p>
                          <p className="text-xs text-ink-soft">{b.code}</p>
                        </td>
                        <td className="px-4 py-3 font-medium">Hab. {b.room} {roomObj?.name}</td>
                        <td className="px-4 py-3 text-xs">{b.checkOut}, 11:00 am</td>
                        <td className="px-4 py-3">
                          <BookingStatusBadge status={b.status} />
                        </td>
                        <td className="px-4 py-3">
                          <span className={cn('text-xs font-semibold tabular-nums', chargesTotal > 0 ? 'text-warn' : 'text-ink-soft')}>
                            {chargesTotal > 0 ? `${formatCurrency(chargesTotal)} pendiente` : 'Sin consumos'}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-right">
                          {b.status === 'enCurso' ? (
                            <Button
                              variant="terra"
                              className="h-8 px-3 text-xs"
                              onClick={() => go('checkout', b.code)}
                            >
                              Hacer check-out
                            </Button>
                          ) : (
                            <span className="text-xs font-semibold text-ok">Check-out liquidado</span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </Card>
        {node}
      </div>
    );
  }

  // --- SUBVIEW: CHECK-OUT ASISTIDO CON CONSOLIDACIÓN DE CONSUMOS ---
  if (subview === 'checkout') {
    const booking = bookings.find((b) => b.code === code && b.status === 'enCurso') || bookings.find((b) => b.status === 'enCurso');
    const roomObj = rooms.find((r) => r.number === booking?.room || r.id === booking?.room);

    const [paymentMethod, setPaymentMethod] = useState<'efectivo' | 'datafono' | 'transferencia'>('efectivo');
    const [targetRoomStatus, setTargetRoomStatus] = useState<RoomStatusKey>('limpieza');
    const [checkoutCompleted, setCheckoutCompleted] = useState(false);

    if (!booking || !roomObj) {
      return (
        <Card className="p-8 text-center">
          <p className="font-semibold text-ink">No hay ningún huésped activo en casa para check-out.</p>
          <Button variant="secondary" className="mt-4" onClick={() => go('salidas')}>
            Volver a salidas
          </Button>
        </Card>
      );
    }

    const roomCharges = charges[booking.room] || [];
    const chargesTotal = roomCharges.reduce((acc, c) => acc + c.amount, 0);
    const roomBalance = booking.total - booking.paid;
    const grandTotal = roomBalance + chargesTotal;

    const handleExecuteCheckout = () => {
      patchBooking(booking.code, { paid: booking.total });
      setBookingStatus(booking.code, 'finalizada');
      clearCharges(booking.room);
      setRoomStatus(roomObj.id, targetRoomStatus, {
        guest: undefined,
        until: undefined,
        note: targetRoomStatus === 'limpieza' ? 'Aseo de salida iniciado' : undefined,
      });
      log(
        `Registró check-out de ${booking.guest} (Hab. ${roomObj.number}). Total liquidado: ${formatCurrency(grandTotal)}`,
        'Check-out'
      );
      setCheckoutCompleted(true);
    };

    if (checkoutCompleted) {
      return (
        <div className="mx-auto max-w-lg pt-10 text-center">
          <Card className="p-8">
            <span className="mx-auto mb-4 grid h-12 w-12 place-items-center rounded-full bg-ok-bg text-ok">
              <CheckCircle2 size={26} />
            </span>
            <h1 className="font-display text-2xl font-semibold text-forest-900">
              Check-out liquidado exitosamente
            </h1>
            <p className="mt-2 text-ink-soft text-sm">
              {booking.guest} ha desocupado la <strong>Hab. {roomObj.number}</strong>. Cuenta saldada por completo.
            </p>
            <div className="mt-4 inline-flex items-center gap-2 rounded-lg bg-sand-50 border border-sand-200 px-4 py-2 text-xs font-semibold text-ink">
              <span>Hab. {roomObj.number}:</span>
              <BadgeStatus status="ocupada" size="sm" />
              <span>→</span>
              <BadgeStatus status={targetRoomStatus} size="sm" />
            </div>
            <div className="mt-6 flex justify-center gap-2">
              <Button variant="primary" onClick={() => go('salidas')}>
                Volver a salidas
              </Button>
              <Button variant="secondary" onClick={() => go('habitaciones')}>
                Ver habitaciones
              </Button>
            </div>
          </Card>
        </div>
      );
    }

    return (
      <div>
        <PageHeader
          eyebrow={`Liquidación de Salida · ${booking.code}`}
          title={`Check-out de ${booking.guest}`}
          desc={`Hab. ${roomObj.number} ${roomObj.name} · Salida hoy`}
          actions={
            <Button variant="secondary" onClick={() => go('salidas')}>
              Cancelar
            </Button>
          }
        />

        <div className="grid gap-6 min-[1100px]:grid-cols-[1.4fr_1fr]">
          <div className="space-y-5">
            {/* Cuenta Consolidada */}
            <Card className="p-5">
              <CardHeader title="Estado de Cuenta Consolidado" />
              <table className="w-full text-sm">
                <thead className="bg-sand-50 text-xs uppercase tracking-wider text-ink-soft">
                  <tr>
                    <TableHeader>Concepto</TableHeader>
                    <TableHeader right>Cant.</TableHeader>
                    <TableHeader right>Valor</TableHeader>
                  </tr>
                </thead>
                <tbody className="divide-y divide-sand-200">
                  <tr>
                    <td className="px-4 py-2.5 font-medium">Hospedaje (Reserva {booking.code})</td>
                    <td className="px-4 text-right">1</td>
                    <td className="px-4 text-right tabular-nums">{formatCurrency(booking.total)}</td>
                  </tr>
                  {roomCharges.map((c, idx) => (
                    <tr key={idx}>
                      <td className="px-4 py-2.5 text-xs">
                        <span className="font-semibold text-forest-800">
                          {c.source === 'restaurante' ? 'Restaurante / Salgados Café' : 'Tienda'}:
                        </span>{' '}
                        {c.desc}
                      </td>
                      <td className="px-4 text-right text-xs">{c.qty}</td>
                      <td className="px-4 text-right tabular-nums text-xs">{formatCurrency(c.amount)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>

              <div className="mt-4 border-t border-sand-200 pt-3 space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-ink-soft">Total Hospedaje:</span>
                  <span>{formatCurrency(booking.total)}</span>
                </div>
                <div className="flex justify-between text-ok">
                  <span>Abono Hospedaje Registrado:</span>
                  <span>−{formatCurrency(booking.paid)}</span>
                </div>
                {chargesTotal > 0 && (
                  <div className="flex justify-between text-forest-800 font-medium">
                    <span>Consumos adicionales (Tienda & Café):</span>
                    <span>+{formatCurrency(chargesTotal)}</span>
                  </div>
                )}
                <div className="flex justify-between text-base font-bold pt-2 border-t border-sand-200">
                  <span className="text-forest-900">Total a Pagar en Recepción:</span>
                  <span className={grandTotal > 0 ? 'text-terra-600' : 'text-ok'}>
                    {formatCurrency(grandTotal)}
                  </span>
                </div>
              </div>
            </Card>

            {/* Recaudación */}
            <Card className="p-5">
              <CardHeader title="Registro de Pago para Salida" />
              {grandTotal > 0 ? (
                <div className="space-y-4">
                  <Field label="Medio de pago recaudado">
                    <Select
                      value={paymentMethod}
                      onChange={(val) => setPaymentMethod(val as any)}
                      options={[
                        { value: 'efectivo', label: 'Efectivo en recepción' },
                        { value: 'datafono', label: 'Datáfono (Tarjeta)' },
                        { value: 'transferencia', label: 'Transferencia bancaria / Nequi' },
                      ]}
                    />
                  </Field>
                </div>
              ) : (
                <Alert tone="ok" title="Cuenta en $0">
                  Todos los consumos y el hospedaje están completamente cancelados.
                </Alert>
              )}
            </Card>
          </div>

          {/* Right Column: Room Next Status */}
          <div className="space-y-5">
            <Card className="p-5">
              <CardHeader
                title="Estado Posterior de la Habitación"
                hint="¿A qué estado pasa la habitación al salir el huésped?"
              />
              <div className="space-y-2">
                {[
                  { key: 'limpieza', label: 'En limpieza (Recomendado)', desc: 'Notifica a camarería para aseo y cambio de sábanas' },
                  { key: 'libre', label: 'Libre de inmediato', desc: 'Lista directamente para nuevo huésped' },
                ].map((opt) => (
                  <button
                    key={opt.key}
                    type="button"
                    onClick={() => setTargetRoomStatus(opt.key as RoomStatusKey)}
                    className={cn(
                      'w-full flex flex-col items-start p-3 rounded-lg border text-left cursor-pointer transition-colors',
                      targetRoomStatus === opt.key
                        ? 'border-forest-800 bg-forest-50 ring-1 ring-forest-800'
                        : 'border-sand-200 hover:border-forest-700'
                    )}
                  >
                    <span className="text-sm font-semibold text-forest-900">{opt.label}</span>
                    <span className="text-xs text-ink-soft">{opt.desc}</span>
                  </button>
                ))}
              </div>

              <Button
                variant="terra"
                className="w-full mt-6"
                onClick={handleExecuteCheckout}
              >
                Liquidará y Registrar Salida
              </Button>
            </Card>
          </div>
        </div>
        {node}
      </div>
    );
  }

  return null;
}
