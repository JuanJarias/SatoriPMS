import React, { useState } from 'react';
import {
  Calendar,
  Tag,
  Plus,
  Percent,
  TrendingUp,
  TrendingDown,
  CheckCircle2,
  XCircle,
  Clock,
  Sparkles
} from 'lucide-react';
import { useStore, SpecialEventItem } from '../store';
import {
  PageHeader,
  Card,
  CardHeader,
  Button,
  Modal,
  Field,
  Input,
  DateField,
  Alert,
  useToast,
  cn
} from '../ui';

export function Eventos() {
  const { events, addEvent, toggleEventActive, role } = useStore();
  const [createModalOpen, setCreateModalOpen] = useState(false);

  // Form State
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [startDate, setStartDate] = useState('2026-10-15');
  const [endDate, setEndDate] = useState('2026-10-25');
  const [percentage, setPercentage] = useState(15);
  const [eventType, setEventType] = useState<'discount' | 'surcharge'>('discount');

  const { show, node } = useToast();
  const isAdmin = role === 'admin';

  const handleSaveEvent = () => {
    if (!name.trim()) {
      show('Nombre obligatorio', 'Por favor ingresa un nombre para el evento', 'bad');
      return;
    }
    const finalPct = eventType === 'discount' ? Math.abs(percentage) : -Math.abs(percentage);

    addEvent({
      name: name.trim(),
      description: description.trim() || undefined,
      startDate,
      endDate,
      discountPercentage: finalPct,
      active: true,
    });

    show('Evento especial creado', `${name} activo del ${startDate} al ${endDate}`);
    setCreateModalOpen(false);
    setName('');
    setDescription('');
  };

  return (
    <div>
      <PageHeader
        eyebrow="Tarifas Dinámicas & Promociones"
        title="Eventos Especiales & Descuentos"
        desc="Configuración de temporadas altas, ferias locales en Sevilla y promociones automáticas para WhatsApp y recepción."
        actions={
          isAdmin ? (
            <Button
              variant="terra"
              icon={<Plus size={16} />}
              onClick={() => setCreateModalOpen(true)}
            >
              Nuevo evento o descuento
            </Button>
          ) : (
            <span className="text-xs text-ink-soft bg-white border border-sand-300 rounded-lg px-3 py-2">
              Solo Administrador puede crear eventos
            </span>
          )
        }
      />

      <div className="space-y-6">
        <Alert tone="info" title="Impacto automático en cotizaciones y WhatsApp">
          Cualquier evento activo con fechas coincidentes aplicará el descuento o recargo de inmediato cuando un cliente cotice o reserve en línea o en el PMS.
        </Alert>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {events.map((ev) => {
            const isDiscount = ev.discountPercentage > 0;
            const pctVal = Math.abs(ev.discountPercentage);

            return (
              <Card
                key={ev.id}
                className={cn(
                  'p-5 flex flex-col justify-between transition-all hover:border-forest-700',
                  !ev.active && 'opacity-60 bg-sand-50/70'
                )}
              >
                <div>
                  <div className="flex items-start justify-between gap-2">
                    <span
                      className={cn(
                        'inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold',
                        isDiscount ? 'bg-ok-bg text-ok' : 'bg-terra-100 text-terra-600'
                      )}
                    >
                      {isDiscount ? <TrendingDown size={14} /> : <TrendingUp size={14} />}
                      {isDiscount ? `${pctVal}% Descuento` : `+${pctVal}% Recargo Temporada`}
                    </span>

                    <button
                      type="button"
                      onClick={() => toggleEventActive(ev.id)}
                      className={cn(
                        'text-xs font-semibold px-2 py-0.5 rounded cursor-pointer transition-colors',
                        ev.active ? 'bg-forest-100 text-forest-800 hover:bg-forest-200' : 'bg-sand-200 text-ink-soft hover:bg-sand-300'
                      )}
                    >
                      {ev.active ? 'Activo' : 'Inactivo'}
                    </button>
                  </div>

                  <h3 className="font-display font-semibold text-lg text-forest-900 mt-3">
                    {ev.name}
                  </h3>
                  {ev.description && (
                    <p className="text-xs text-ink-soft mt-1 leading-relaxed">
                      {ev.description}
                    </p>
                  )}
                </div>

                <div className="mt-5 pt-3 border-t border-sand-200 space-y-2 text-xs">
                  <div className="flex items-center justify-between text-ink-soft">
                    <span className="flex items-center gap-1.5">
                      <Calendar size={14} />
                      Fechas de vigencia:
                    </span>
                    <span className="font-semibold text-ink">
                      {ev.startDate} → {ev.endDate}
                    </span>
                  </div>

                  <div className="flex items-center justify-between text-ink-soft">
                    <span className="flex items-center gap-1.5">
                      <Clock size={14} />
                      Canal aplicado:
                    </span>
                    <span className="font-medium text-forest-800">
                      WhatsApp, Web & PMS
                    </span>
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      </div>

      {/* Modal: Crear Evento */}
      {createModalOpen && (
        <Modal
          title="Nuevo Evento o Promoción"
          onClose={() => setCreateModalOpen(false)}
          footer={
            <>
              <Button variant="secondary" onClick={() => setCreateModalOpen(false)}>
                Cancelar
              </Button>
              <Button variant="primary" onClick={handleSaveEvent}>
                Guardar y Activar
              </Button>
            </>
          }
        >
          <Field label="Nombre del evento o promoción *">
            <Input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Ej. Festival Bandola de Sevilla, Fin de Semana Romántico"
            />
          </Field>

          <Field label="Descripción">
            <Input
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Detalles sobre por qué aplica la tarifa especial"
            />
          </Field>

          <div className="grid grid-cols-2 gap-3">
            <Field label="Fecha de inicio">
              <DateField value={startDate} onChange={setStartDate} />
            </Field>
            <Field label="Fecha de finalización">
              <DateField value={endDate} onChange={setEndDate} />
            </Field>
          </div>

          <Field label="Tipo de ajuste tarifario">
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => setEventType('discount')}
                className={cn(
                  'p-2.5 rounded-lg border text-xs font-semibold flex items-center justify-center gap-1.5 cursor-pointer',
                  eventType === 'discount'
                    ? 'border-forest-800 bg-forest-50 text-forest-900 ring-1 ring-forest-800'
                    : 'border-sand-300 bg-white text-ink-soft'
                )}
              >
                <TrendingDown size={14} className="text-ok" />
                Descuento (%)
              </button>
              <button
                type="button"
                onClick={() => setEventType('surcharge')}
                className={cn(
                  'p-2.5 rounded-lg border text-xs font-semibold flex items-center justify-center gap-1.5 cursor-pointer',
                  eventType === 'surcharge'
                    ? 'border-forest-800 bg-forest-50 text-forest-900 ring-1 ring-forest-800'
                    : 'border-sand-300 bg-white text-ink-soft'
                )}
              >
                <TrendingUp size={14} className="text-terra-600" />
                Recargo Temporada Alta (%)
              </button>
            </div>
          </Field>

          <Field label={`Porcentaje (${eventType === 'discount' ? 'Descuento' : 'Recargo'})`}>
            <div className="relative">
              <Percent size={16} className="absolute left-3 top-3 text-ink-soft" />
              <Input
                type="number"
                min={1}
                max={90}
                value={percentage}
                onChange={(e) => setPercentage(Number(e.target.value))}
                className="pl-9"
              />
            </div>
          </Field>
        </Modal>
      )}

      {node}
    </div>
  );
}
