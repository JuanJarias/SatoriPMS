import React, { useState, useEffect, useRef } from 'react';
import {
  MessageSquare,
  Send,
  User,
  Bot,
  Clock,
  CheckCheck,
  Smartphone,
  Phone,
  Calendar,
  AlertTriangle,
  RotateCcw,
  Sparkles,
  BedDouble,
  ShieldCheck,
  CheckCircle2,
  XCircle,
  Users
} from 'lucide-react';
import { useStore, RoomItem, BookingItem } from '../store';
import {
  PageHeader,
  Card,
  CardHeader,
  Button,
  BadgeStatus,
  Alert,
  useToast,
  formatCurrency,
  cn
} from '../ui';

export function Chatbot({ go }: { go?: (view: string, param?: string) => void }) {
  const { rooms, conversations, addBooking, escalateConversation } = useStore();
  const [activeTab, setActiveTab] = useState<'inbox' | 'simulator'>('inbox');

  const [selectedConvId, setSelectedConvId] = useState<number | null>(null);
  const selectedConv =
    conversations.find((c) => c.id === selectedConvId) || conversations[0] || null;

  const { show, node } = useToast();

  const todayIso = new Date().toISOString().slice(0, 10);
  const twoDaysIso = new Date(Date.now() + 2 * 86400000).toISOString().slice(0, 10);

  // --- ESTADO SIMULADOR SANDBOX WHATSAPP ---
  const [simStep, setSimStep] = useState<number>(1);
  const [simCheckIn, setSimCheckIn] = useState(todayIso);
  const [simCheckOut, setSimCheckOut] = useState(twoDaysIso);
  const [simAdults, setSimAdults] = useState(2);
  const [simKids, setSimKids] = useState(0);
  const [simPet, setSimPet] = useState(false);
  const [simSelectedRoom, setSimSelectedRoom] = useState<string>('1');
  const [simTimer, setSimTimer] = useState(900); // 15 minutos (900 seg)
  const [simPaymentMethod, setSimPaymentMethod] = useState<'tarjeta' | 'pse' | 'transferencia'>('transferencia');
  const [simConfirmedCode, setSimConfirmedCode] = useState<string | null>(null);

  const simNights = Math.max(1, Math.round((new Date(simCheckOut).getTime() - new Date(simCheckIn).getTime()) / (1000 * 60 * 60 * 24)));
  const simTotalGuests = simAdults + simKids;
  const currentRoom = rooms.find((r) => r.number === simSelectedRoom || String(r.id) === simSelectedRoom) || rooms[0];
  const simBasePrice = (currentRoom?.rate || 0) * simNights;

  // Temporizador regresivo de 15 minutos en el simulador
  useEffect(() => {
    if (simStep !== 4 || simConfirmedCode) return;
    const interval = setInterval(() => {
      setSimTimer((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);
    return () => clearInterval(interval);
  }, [simStep, simConfirmedCode]);

  const formatTimer = (secs: number) => {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  };

  const handleEscalateConv = async (id: number) => {
    const res = await escalateConversation(id);
    if (res.success) {
      show('Conversación escalada', 'El bot queda en pausa para atención humana en PostgreSQL');
    } else {
      show('Error al escalar', res.message, 'bad');
    }
  };

  const handleSimConfirmBooking = async () => {
    if (!currentRoom) {
      show('Sin habitaciones', 'No hay habitaciones cargadas desde el servidor', 'bad');
      return;
    }
    const res = await addBooking({
      roomId: currentRoom.id,
      checkIn: simCheckIn,
      checkOut: simCheckOut,
      adults: simAdults,
      children: simKids,
      hasPet: simPet,
      guestName: 'Huésped Sandbox WhatsApp',
      phone: '+573000000000',
      paymentOption: 'half',
      source: 'chatbot',
    });
    if (!res.success) {
      show('Conflicto al reservar', res.message, 'bad');
      return;
    }
    const newCode = (res.data as { code?: string } | undefined)?.code || 'TS-BOT';
    setSimConfirmedCode(newCode);
    setSimStep(5);
  };

  return (
    <div>
      <PageHeader
        eyebrow="Canal Directo & Automatización"
        title="WhatsApp & Asistente Satori"
        desc="Bandeja real de sesiones conversacionales en PostgreSQL 16 (n8n V10 sin Redis) y simulador de reservas."
        actions={
          <div className="flex gap-2">
            <Button
              variant={activeTab === 'inbox' ? 'primary' : 'secondary'}
              icon={<MessageSquare size={16} />}
              onClick={() => setActiveTab('inbox')}
            >
              Sesiones WhatsApp ({conversations.length})
            </Button>
            <Button
              variant={activeTab === 'simulator' ? 'primary' : 'secondary'}
              icon={<Smartphone size={16} />}
              onClick={() => setActiveTab('simulator')}
            >
              Simulador Sandbox
            </Button>
          </div>
        }
      />

      {activeTab === 'inbox' ? (
        /* BANDEJA REAL DE SESIONES POSTGRESQL */
        <div className="grid gap-6 min-[1000px]:grid-cols-[320px_1fr]">
          <Card className="p-4 h-[600px] flex flex-col">
            <CardHeader title="Conversaciones WhatsApp" hint="Sesiones activas en PostgreSQL" />
            {conversations.length === 0 ? (
              <p className="text-xs text-ink-soft py-4">Aún no hay sesiones conversacionales registradas en PostgreSQL.</p>
            ) : (
              <div className="divide-y divide-sand-200 overflow-y-auto flex-1">
                {conversations.map((c) => (
                  <button
                    key={c.id}
                    type="button"
                    onClick={() => setSelectedConvId(c.id)}
                    className={cn(
                      'w-full p-3 text-left flex items-start gap-3 cursor-pointer transition-colors',
                      selectedConv?.id === c.id ? 'bg-forest-50' : 'hover:bg-sand-50'
                    )}
                  >
                    <div className="h-9 w-9 rounded-full bg-forest-800 text-white flex items-center justify-center font-bold text-xs shrink-0">
                      {(c.guestName || 'H').split(' ').map((n) => n[0]).slice(0, 2).join('')}
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="flex justify-between items-baseline">
                        <p className="font-semibold text-sm text-ink truncate">{c.guestName}</p>
                        <span className="text-[11px] text-ink-soft">{c.status === 'escalated' ? 'Humano' : 'Bot'}</span>
                      </div>
                      <p className="text-xs text-ink-soft truncate mt-0.5">{c.waId} · {c.state}:{c.step}</p>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </Card>

          <Card className="flex flex-col h-[600px]">
            {selectedConv ? (
              <>
                <div className="p-4 border-b border-sand-200 flex justify-between items-center bg-sand-50/50">
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-full bg-forest-700 text-white flex items-center justify-center font-bold text-sm">
                      <User size={18} />
                    </div>
                    <div>
                      <h3 className="font-semibold text-ink text-sm">{selectedConv.guestName} ({selectedConv.waId})</h3>
                      <p className="text-xs text-ok font-medium flex items-center gap-1">
                        <span className="h-2 w-2 rounded-full bg-ok inline-block" />
                        Estado: {selectedConv.state} / Paso: {selectedConv.step}
                      </p>
                    </div>
                  </div>
                  <Button
                    variant={selectedConv.agentActive ? 'danger' : 'secondary'}
                    className="h-8 text-xs px-3"
                    onClick={() => handleEscalateConv(selectedConv.id)}
                  >
                    {selectedConv.agentActive ? 'Escalamiento Humano Activo' : 'Activar Atención Humana'}
                  </Button>
                </div>
                <div className="flex-1 p-6 space-y-3 text-sm text-ink-soft">
                  <Alert tone="info" title="Sesión persistida en PostgreSQL 16 (sin Redis)">
                    Número WhatsApp: <strong>{selectedConv.waId}</strong> · Modo actual:{' '}
                    <strong>{selectedConv.agentActive ? 'Bot en silencio (Atención humana)' : 'Bot n8n V10 activo'}</strong>.
                    {selectedConv.updatedAt && ` Última actividad: ${new Date(selectedConv.updatedAt).toLocaleString('es-CO')}.`}
                  </Alert>
                </div>
              </>
            ) : (
              <div className="flex-1 grid place-items-center p-8 text-center text-sm text-ink-soft">
                Selecciona una conversación de WhatsApp o prueba el flujo desde el Simulador Sandbox.
              </div>
            )}
          </Card>
        </div>
      ) : (
        /* SIMULADOR INTERACTIVO SANDBOX WHATSAPP */
        <div className="grid gap-6 min-[1100px]:grid-cols-[1.2fr_1fr] items-start">
          {/* Instrucciones del Sandbox */}
          <div className="space-y-4">
            <Alert tone="info" title="Sandbox de Pruebas WhatsApp Sin Costo">
              Este simulador emula el flujo conversacional completo que experimenta un huésped al escribir a la línea oficial de Torre Satori PMS, incluyendo verificación de 15 minutos, bloqueo anti-doble reserva y cobro de anticipo.
            </Alert>

            <Card className="p-5">
              <CardHeader title="Controles Rápidos del Simulador" />
              <div className="space-y-3">
                <div className="flex justify-between items-center text-sm">
                  <span className="font-medium text-ink">Paso del flujo:</span>
                  <div className="flex gap-1.5">
                    {[1, 2, 3, 4, 5].map((s) => (
                      <button
                        key={s}
                        type="button"
                        onClick={() => {
                          setSimStep(s);
                          if (s === 4) setSimTimer(900);
                        }}
                        className={cn(
                          'h-7 w-7 rounded-full text-xs font-bold cursor-pointer',
                          simStep === s ? 'bg-forest-800 text-white' : 'bg-sand-200 text-ink-soft'
                        )}
                      >
                        {s}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="text-xs text-ink-soft space-y-1 pt-2 border-t border-sand-200">
                  <p><strong>Paso 1:</strong> Bienvenida e intenciones de usuario.</p>
                  <p><strong>Paso 2:</strong> Selección interactiva de fechas, huéspedes y mascota.</p>
                  <p><strong>Paso 3:</strong> Tarjetas de habitaciones disponibles de las 9 de Satori.</p>
                  <p><strong>Paso 4:</strong> Bloqueo temporal distribuido (15 min) y resumen de pago.</p>
                  <p><strong>Paso 5:</strong> Confirmación atómica y código de reserva generado.</p>
                </div>

                <Button
                  variant="secondary"
                  className="w-full mt-3 text-xs"
                  icon={<RotateCcw size={14} />}
                  onClick={() => {
                    setSimStep(1);
                    setSimTimer(900);
                    setSimConfirmedCode(null);
                  }}
                >
                  Reiniciar simulador a inicio
                </Button>
              </div>
            </Card>
          </div>

          {/* Maqueta de Teléfono Smartphone */}
          <div className="mx-auto w-[360px] h-[720px] rounded-[36px] border-[8px] border-ink bg-ink shadow-2xl overflow-hidden flex flex-col">
            {/* Barra de Estado del Teléfono */}
            <div className="bg-forest-900 text-sand-50 text-[11px] font-semibold px-5 pt-2 pb-1 flex justify-between items-center shrink-0">
              <span>10:43</span>
              <span className="flex items-center gap-1.5">
                <span className="text-[10px]">4G</span>
                <span>85%</span>
              </span>
            </div>

            {/* Cabecera de WhatsApp */}
            <div className="bg-forest-800 text-white px-3 py-2.5 flex items-center gap-2.5 shrink-0">
              <div className="h-9 w-9 rounded-full bg-sand-50 text-forest-900 flex items-center justify-center font-bold text-xs">
                TS
              </div>
              <div className="min-w-0 flex-1">
                <p className="font-semibold text-sm leading-tight truncate">Torre Satori Hotel</p>
                <p className="text-[11px] text-[#9bd7a8] flex items-center gap-1">
                  <span className="h-1.5 w-1.5 rounded-full bg-[#9bd7a8]" /> Asistente Satori · en línea
                </p>
              </div>
              <Phone size={16} className="text-sand-200" />
            </div>

            {/* Área de Mensajes de WhatsApp */}
            <div
              className="flex-1 p-3 overflow-y-auto space-y-2.5 bg-sand-100 text-[13px]"
              style={{
                backgroundImage: 'radial-gradient(rgba(60,80,60,.06) 1px, transparent 1px)',
                backgroundSize: '12px 12px',
              }}
            >
              {/* PASO 1: BIENVENIDA */}
              {simStep >= 1 && (
                <>
                  <div className="bg-white p-2.5 rounded-2xl rounded-tl-sm shadow-sm max-w-[90%] text-ink space-y-1">
                    <p>¡Hola! Soy el asistente virtual de <strong>Torre Satori</strong> en Sevilla, Valle del Cauca.</p>
                    <p className="text-ink-soft text-xs">Te ayudo a consultar disponibilidad y reservar en segundos.</p>
                    <span className="text-[10px] text-ink-soft float-right">10:42 am</span>
                  </div>

                  {simStep === 1 && (
                    <div className="space-y-1.5 pt-1">
                      <button
                        onClick={() => setSimStep(2)}
                        className="w-full bg-forest-800 text-white py-2 px-3 rounded-full text-xs font-semibold hover:bg-forest-700 cursor-pointer text-center"
                      >
                        Reservar habitación
                      </button>
                      <button
                        onClick={() => go?.('reservas')}
                        className="w-full bg-white border border-sand-300 text-forest-800 py-2 px-3 rounded-full text-xs font-semibold hover:bg-sand-50 cursor-pointer text-center"
                      >
                        Consultar mi reserva previa
                      </button>
                    </div>
                  )}
                </>
              )}

              {/* PASO 2: FORMULARIO INTERACTIVO DE FECHAS */}
              {simStep >= 2 && (
                <>
                  <div className="bg-forest-100 p-2.5 rounded-2xl rounded-tr-sm shadow-sm ml-auto max-w-[85%] text-forest-900 text-right">
                    Quiero reservar habitación
                    <span className="text-[10px] text-forest-700 block mt-0.5">10:43 am</span>
                  </div>

                  {simStep === 2 ? (
                    <div className="bg-white p-3 rounded-2xl shadow-sm space-y-2.5">
                      <p className="font-semibold text-xs text-forest-900">Selecciona fechas y huéspedes:</p>
                      <div className="grid grid-cols-2 gap-2 text-xs">
                        <div>
                          <label className="text-[10px] text-ink-soft block">Llegada</label>
                          <input
                            type="date"
                            value={simCheckIn}
                            onChange={(e) => setSimCheckIn(e.target.value)}
                            className="w-full border border-sand-300 rounded p-1 text-xs"
                          />
                        </div>
                        <div>
                          <label className="text-[10px] text-ink-soft block">Salida</label>
                          <input
                            type="date"
                            value={simCheckOut}
                            onChange={(e) => setSimCheckOut(e.target.value)}
                            className="w-full border border-sand-300 rounded p-1 text-xs"
                          />
                        </div>
                      </div>

                      <div className="flex justify-between items-center text-xs pt-1 border-t border-sand-200">
                        <span>Adultos:</span>
                        <div className="flex items-center gap-2">
                          <button onClick={() => setSimAdults(Math.max(1, simAdults - 1))} className="px-2 py-0.5 border rounded">−</button>
                          <span className="font-bold">{simAdults}</span>
                          <button onClick={() => setSimAdults(simAdults + 1)} className="px-2 py-0.5 border rounded">+</button>
                        </div>
                      </div>

                      <div className="flex justify-between items-center text-xs">
                        <span>Mascota:</span>
                        <button
                          onClick={() => setSimPet(!simPet)}
                          className={cn('px-2.5 py-0.5 rounded-full font-semibold', simPet ? 'bg-ok-bg text-ok' : 'bg-sand-200 text-ink-soft')}
                        >
                          {simPet ? 'Sí, llevo mascota' : 'No'}
                        </button>
                      </div>

                      <button
                        onClick={() => setSimStep(3)}
                        className="w-full bg-forest-800 text-white py-2 rounded-lg text-xs font-semibold mt-2 cursor-pointer"
                      >
                        Ver habitaciones libres ({simNights} noches)
                      </button>
                    </div>
                  ) : null}
                </>
              )}

              {/* PASO 3: CATÁLOGO DE HABITACIONES DISPONIBLES */}
              {simStep >= 3 && (
                <>
                  <div className="bg-forest-100 p-2 rounded-2xl rounded-tr-sm ml-auto text-xs text-forest-900 text-right">
                    Del {simCheckIn} al {simCheckOut} para {simTotalGuests} personas
                  </div>

                  {simStep === 3 ? (
                    <div className="space-y-2">
                      <p className="text-xs text-ink-soft px-1">Habitaciones disponibles en esas fechas:</p>
                      {rooms.slice(0, 3).map((r) => (
                        <div key={r.id} className="bg-white p-3 rounded-xl border border-sand-200 space-y-2 shadow-sm">
                          <div className="flex justify-between items-start">
                            <div>
                              <p className="font-bold text-sm text-forest-900">Hab. {r.number} {r.name}</p>
                              <p className="text-[11px] text-ink-soft">{r.type} · Hasta {r.capacity} personas</p>
                            </div>
                            <span className="font-bold text-xs text-forest-800">
                              {formatCurrency(r.rate)}/noche
                            </span>
                          </div>
                          {r.allowsPets && (
                            <span className="text-[10px] bg-ok-bg text-ok px-2 py-0.5 rounded font-semibold inline-block">
                              ✓ Acepta mascotas
                            </span>
                          )}
                          <button
                            onClick={() => {
                              setSimSelectedRoom(r.number);
                              setSimStep(4);
                              setSimTimer(900);
                            }}
                            className="w-full bg-terra-500 hover:bg-terra-600 text-white py-1.5 rounded-lg text-xs font-semibold cursor-pointer"
                          >
                            Seleccionar y Bloquear 15 min
                          </button>
                        </div>
                      ))}
                    </div>
                  ) : null}
                </>
              )}

              {/* PASO 4: BLOQUEO TEMPORAL Y PAGO */}
              {simStep >= 4 && (
                <>
                  <div className="bg-forest-100 p-2 rounded-2xl rounded-tr-sm ml-auto text-xs text-forest-900 text-right">
                    Elegí la Hab. {currentRoom.number} {currentRoom.name}
                  </div>

                  <div className="bg-warn-bg text-warn border border-[#d99a1e]/40 p-2.5 rounded-xl text-xs space-y-1">
                    <div className="flex justify-between items-center font-bold">
                      <span className="flex items-center gap-1">
                        <Clock size={13} /> Bloqueo temporal activo:
                      </span>
                      <span className="font-display text-sm tabular-nums">{formatTimer(simTimer)}</span>
                    </div>
                    <p className="text-[11px] text-ink-soft">
                      La habitación está retenida solo para ti. Nadie más puede reservarla mientras realizas el pago.
                    </p>
                  </div>

                  {simStep === 4 && (
                    <div className="bg-white p-3 rounded-2xl shadow-sm space-y-2 text-xs">
                      <p className="font-bold text-sm text-forest-900">Resumen de Liquidación:</p>
                      <div className="space-y-1 text-ink-soft border-b border-sand-200 pb-2">
                        <div className="flex justify-between">
                          <span>{simNights} noche(s) × {formatCurrency(currentRoom.rate)}:</span>
                          <span className="font-semibold text-ink">{formatCurrency(simBasePrice)}</span>
                        </div>
                        <div className="flex justify-between text-ok font-semibold">
                          <span>Anticipo requerido (50%):</span>
                          <span>{formatCurrency(simBasePrice / 2)}</span>
                        </div>
                      </div>

                      <p className="font-semibold text-ink pt-1">Método de pago:</p>
                      <div className="grid grid-cols-3 gap-1">
                        {['transferencia', 'pse', 'tarjeta'].map((m) => (
                          <button
                            key={m}
                            type="button"
                            onClick={() => setSimPaymentMethod(m as any)}
                            className={cn(
                              'p-1.5 rounded border text-[11px] capitalize cursor-pointer font-medium',
                              simPaymentMethod === m ? 'border-forest-800 bg-forest-50 text-forest-900 font-bold' : 'border-sand-300'
                            )}
                          >
                            {m}
                          </button>
                        ))}
                      </div>

                      <button
                        onClick={handleSimConfirmBooking}
                        className="w-full bg-forest-800 text-white py-2 rounded-lg font-bold text-xs mt-2 cursor-pointer hover:bg-forest-700"
                      >
                        Pagar anticipo {formatCurrency(simBasePrice / 2)}
                      </button>
                    </div>
                  )}
                </>
              )}

              {/* PASO 5: CONFIRMACIÓN DE RESERVA */}
              {simStep === 5 && simConfirmedCode && (
                <div className="bg-white p-4 rounded-2xl border border-sand-200 text-center space-y-2 shadow-sm">
                  <div className="h-10 w-10 rounded-full bg-ok-bg text-ok flex items-center justify-center mx-auto">
                    <CheckCircle2 size={22} />
                  </div>
                  <h4 className="font-display font-bold text-base text-forest-900">
                    ¡Reserva Confirmada!
                  </h4>
                  <div className="bg-forest-50 border border-dashed border-forest-700/50 p-2 rounded-lg">
                    <span className="text-[10px] text-ink-soft uppercase tracking-wider block">Código de Reserva</span>
                    <span className="font-display font-bold text-xl text-forest-900 tracking-wider">
                      {simConfirmedCode}
                    </span>
                  </div>
                  <p className="text-[11px] text-ink-soft">
                    Tu anticipo fue verificado y el bloqueo de 15 minutos se convirtió en reserva confirmada en el calendario del hotel.
                  </p>
                  <Button
                    variant="terra"
                    className="w-full text-xs h-8 mt-2"
                    onClick={() => {
                      go?.('reservas', simConfirmedCode);
                    }}
                  >
                    Ver en pantalla de Reservas
                  </Button>
                </div>
              )}
            </div>

            {/* Input Simulado Inferior */}
            <div className="bg-sand-50 p-2 flex items-center gap-2 border-t border-sand-200 shrink-0">
              <div className="flex-1 bg-white rounded-full px-3 py-1.5 text-xs text-ink-soft border border-sand-300 truncate">
                Responde seleccionando las opciones…
              </div>
              <div className="h-8 w-8 rounded-full bg-forest-800 text-white flex items-center justify-center shrink-0">
                <Send size={14} />
              </div>
            </div>
          </div>
        </div>
      )}

      {node}
    </div>
  );
}
