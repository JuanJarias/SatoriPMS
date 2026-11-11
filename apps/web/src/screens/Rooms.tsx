import React, { useState } from 'react';
import {
  Plus,
  Users,
  Calendar,
  User,
  CheckCircle2,
  Edit2,
  Trash2,
  ShieldAlert,
  Sparkles,
  Wrench,
  Clock,
  ArrowRight,
  Info
} from 'lucide-react';
import { useStore, RoomItem } from '../store';
import {
  PageHeader,
  Card,
  Button,
  BadgeStatus,
  SearchBar,
  Select,
  DateField,
  FilterChip,
  Modal,
  ConfirmModal,
  Field,
  Input,
  useToast,
  formatCurrency,
  RoomStatusKey,
  ROOM_STATUS_META
} from '../ui';

export function Rooms() {
  const { role, rooms, addRoom, updateRoom, deleteRoom, setRoomStatus, log } = useStore();
  const [filterStatus, setFilterStatus] = useState<string>('todas');
  const [filterType, setFilterType] = useState<string>('todos');
  const [search, setSearch] = useState<string>('');
  const [filterDate, setFilterDate] = useState<string>('2026-10-01');

  // Modales
  const [addModalOpen, setAddModalOpen] = useState(false);
  const [editRoom, setEditRoom] = useState<RoomItem | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<RoomItem | null>(null);
  const [statusModalTarget, setStatusModalTarget] = useState<RoomItem | null>(null);
  const [newStatusValue, setNewStatusValue] = useState<RoomStatusKey>('libre');
  const [statusNote, setStatusNote] = useState('');

  // Form State para Crear / Editar
  const [formNumber, setFormNumber] = useState('');
  const [formName, setFormName] = useState('');
  const [formType, setFormType] = useState('Sencilla');
  const [formCapacity, setFormCapacity] = useState(2);
  const [formBaseAdults, setFormBaseAdults] = useState(2);
  const [formMaxAdults, setFormMaxAdults] = useState(2);
  const [formChildren, setFormChildren] = useState(0);
  const [formRate, setFormRate] = useState(180000);
  const [formExtraRate, setFormExtraRate] = useState(40000);
  const [formAllowsPets, setFormAllowsPets] = useState(false);

  const { show, node } = useToast();

  const isAdmin = role === 'admin';

  const filteredRooms = rooms.filter((r) => {
    const matchesStatus = filterStatus === 'todas' || r.status === filterStatus;
    const matchesType = filterType === 'todos' || r.type === filterType;
    const matchesSearch =
      search.trim() === '' ||
      r.number.toLowerCase().includes(search.toLowerCase()) ||
      r.name.toLowerCase().includes(search.toLowerCase()) ||
      (r.guest && r.guest.toLowerCase().includes(search.toLowerCase()));
    return matchesStatus && matchesType && matchesSearch;
  });

  const openAddModal = () => {
    setFormNumber('');
    setFormName('');
    setFormType('Doble');
    setFormCapacity(2);
    setFormBaseAdults(2);
    setFormMaxAdults(2);
    setFormChildren(0);
    setFormRate(200000);
    setFormExtraRate(40000);
    setFormAllowsPets(false);
    setAddModalOpen(true);
  };

  const openEditModal = (room: RoomItem) => {
    setFormNumber(room.number);
    setFormName(room.name);
    setFormType(room.type);
    setFormCapacity(room.capacity);
    setFormBaseAdults(room.baseAdultsCapacity || 2);
    setFormMaxAdults(room.maxAdultsCapacity || room.capacity);
    setFormChildren(room.childrenCapacity || 0);
    setFormRate(room.rate);
    setFormExtraRate(room.extraRate || 40000);
    setFormAllowsPets(!!room.allowsPets);
    setEditRoom(room);
  };

  const handleSaveRoom = () => {
    if (!formNumber.trim() || !formName.trim()) {
      show('Faltan campos obligatorios', 'Por favor ingresa número y nombre', 'bad');
      return;
    }

    if (editRoom) {
      const res = updateRoom(editRoom.id, {
        name: formName.trim(),
        type: formType,
        capacity: Number(formCapacity),
        baseAdultsCapacity: Number(formBaseAdults),
        maxAdultsCapacity: Number(formMaxAdults),
        childrenCapacity: Number(formChildren),
        rate: Number(formRate),
        extraRate: Number(formExtraRate),
        allowsPets: formAllowsPets,
      });
      if (res.success) {
        show('Habitación actualizada', `Hab. ${editRoom.number} modificada por Administrador`);
        setEditRoom(null);
      } else {
        show('Error al actualizar', res.message, 'bad');
      }
    } else {
      const res = addRoom({
        number: formNumber.trim(),
        name: formName.trim(),
        type: formType,
        capacity: Number(formCapacity),
        baseAdultsCapacity: Number(formBaseAdults),
        maxAdultsCapacity: Number(formMaxAdults),
        childrenCapacity: Number(formChildren),
        rate: Number(formRate),
        extraRate: Number(formExtraRate),
        allowsPets: formAllowsPets,
        status: 'libre',
      });
      if (res.success) {
        show('Habitación creada', `Hab. ${formNumber} agregada al inventario hotelero`);
        setAddModalOpen(false);
      } else {
        show('Error al crear', res.message, 'bad');
      }
    }
  };

  const handleDeleteConfirm = () => {
    if (!deleteTarget) return;
    const res = deleteRoom(deleteTarget.id);
    if (res.success) {
      show('Habitación eliminada', `Hab. ${deleteTarget.number} retirada del inventario`);
      setDeleteTarget(null);
    } else {
      show('Acción no permitida', res.message, 'bad');
      setDeleteTarget(null);
    }
  };

  const handleApplyStatusChange = () => {
    if (!statusModalTarget) return;
    setRoomStatus(statusModalTarget.id, newStatusValue, {
      note: statusNote.trim() ? statusNote.trim() : undefined,
    });
    log(`Cambió estado de Hab. ${statusModalTarget.number} a ${ROOM_STATUS_META[newStatusValue].label}`, 'Habitaciones');
    show(`Hab. ${statusModalTarget.number} actualizada`, `Estado: ${ROOM_STATUS_META[newStatusValue].label}`);
    setStatusModalTarget(null);
    setStatusNote('');
  };

  return (
    <div>
      <PageHeader
        eyebrow="Operación diaria & Catálogo"
        title="Habitaciones"
        desc={`Estado en tiempo real de las ${rooms.length} habitaciones de Torre Satori.`}
        actions={
          isAdmin ? (
            <Button
              variant="terra"
              icon={<Plus size={16} />}
              onClick={openAddModal}
            >
              Agregar habitación (Admin)
            </Button>
          ) : (
            <span className="flex items-center gap-1.5 text-xs text-ink-soft bg-white border border-sand-300 rounded-lg px-3 py-2 shadow-sm">
              <ShieldAlert size={14} className="text-forest-700" />
              Edición de inventario: Solo Administrador
            </span>
          )
        }
      />

      {/* Filter Bar */}
      <Card className="mb-5 p-4">
        <div className="grid items-center gap-3 min-[1100px]:grid-cols-[1.4fr_200px_180px]">
          <SearchBar
            value={search}
            onChange={setSearch}
            placeholder="Buscar por número, nombre o huésped…"
          />
          <Select
            label="Tipo de habitación"
            value={filterType}
            onChange={setFilterType}
            options={[
              { value: 'todos', label: 'Todos los tipos' },
              { value: 'Sencilla', label: 'Sencilla' },
              { value: 'Doble', label: 'Doble' },
              { value: 'Familiar', label: 'Familiar' },
              { value: 'Suite', label: 'Suite' },
            ]}
          />
          <DateField label="Fecha" value={filterDate} onChange={setFilterDate} />
        </div>

        <div className="mt-4 flex flex-wrap items-center gap-2 border-t border-sand-200 pt-3">
          <span className="mr-1 text-xs font-semibold uppercase tracking-wider text-ink-soft">
            Estado
          </span>
          <FilterChip
            active={filterStatus === 'todas'}
            onClick={() => setFilterStatus('todas')}
          >
            Todas · {rooms.length}
          </FilterChip>
          {(Object.keys(ROOM_STATUS_META) as RoomStatusKey[]).map((st) => (
            <FilterChip
              key={st}
              active={filterStatus === st}
              onClick={() => setFilterStatus(st)}
            >
              {ROOM_STATUS_META[st].label} · {rooms.filter((r) => r.status === st).length}
            </FilterChip>
          ))}
        </div>
      </Card>

      {/* Status Legend */}
      <div className="mb-5 flex flex-wrap items-center gap-x-5 gap-y-2 rounded-lg bg-sand-50 px-4 py-2.5 ring-1 ring-sand-200 text-xs">
        <span className="font-semibold uppercase tracking-wider text-ink-soft">Leyenda:</span>
        {(Object.keys(ROOM_STATUS_META) as RoomStatusKey[]).map((st) => {
          const meta = ROOM_STATUS_META[st];
          const Icon = meta.icon;
          return (
            <span key={st} className={`flex items-center gap-1.5 font-medium ${meta.text}`}>
              <Icon size={14} strokeWidth={2.25} />
              <b>{meta.label}</b>
              <span className="text-ink-soft">· {meta.short}</span>
            </span>
          );
        })}
      </div>

      {/* Room Cards Grid */}
      {filteredRooms.length === 0 ? (
        <Card className="grid place-items-center gap-2 p-14 text-center">
          <Info size={28} className="text-ink-soft" />
          <p className="font-semibold text-ink">Ninguna habitación coincide con estos filtros</p>
          <Button
            variant="secondary"
            onClick={() => {
              setFilterStatus('todas');
              setFilterType('todos');
              setSearch('');
            }}
          >
            Limpiar filtros
          </Button>
        </Card>
      ) : (
        <div className="grid gap-5 min-[760px]:grid-cols-2 min-[1200px]:grid-cols-3">
          {filteredRooms.map((room) => {
            const meta = ROOM_STATUS_META[room.status] || ROOM_STATUS_META.libre;
            return (
              <Card
                key={room.id}
                className="flex flex-col overflow-hidden transition-all hover:border-forest-700 hover:shadow-md"
              >
                <div className={`h-1.5 ${meta.bar}`} />
                <div className="flex flex-1 flex-col p-5">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-baseline gap-3">
                      <span className="font-display text-[40px] font-semibold leading-none text-forest-900">
                        {room.number}
                      </span>
                      <div>
                        <p className="text-base font-semibold text-ink">{room.name}</p>
                        <p className="text-[13px] text-ink-soft">{room.type}</p>
                      </div>
                    </div>
                    <BadgeStatus status={room.status} />
                  </div>

                  <div className="mt-4 flex flex-wrap items-center gap-4 text-[13px] text-ink-soft">
                    <span className="flex items-center gap-1.5">
                      <Users size={14} />
                      Hasta {room.capacity} pers.
                    </span>
                    <span className="font-semibold text-ink">
                      {formatCurrency(room.rate)}{' '}
                      <span className="font-normal text-ink-soft">/ noche</span>
                    </span>
                    {room.allowsPets && (
                      <span className="rounded bg-ok-bg text-ok px-1.5 py-0.5 text-[11px] font-semibold">
                        Acepta mascotas
                      </span>
                    )}
                  </div>

                  {/* Room Details DL */}
                  <dl className="mt-4 space-y-2.5 border-t border-sand-200 pt-3 text-sm">
                    <div className="flex gap-2.5">
                      <User size={15} className="mt-0.5 shrink-0 text-ink-soft" />
                      <div>
                        <dt className="text-xs text-ink-soft">Huésped / Estado</dt>
                        <dd className="font-medium text-ink">
                          {room.guest ?? (
                            <span className="text-ink-soft">{room.note ?? 'Sin huésped en casa'}</span>
                          )}
                        </dd>
                        {room.until && (
                          <dd className="text-xs text-ink-soft">{room.until}</dd>
                        )}
                      </div>
                    </div>

                    <div className="flex gap-2.5">
                      <Calendar size={15} className="mt-0.5 shrink-0 text-ink-soft" />
                      <div>
                        <dt className="text-xs text-ink-soft">Próxima reserva</dt>
                        <dd className="font-medium text-ink">
                          {room.next ?? 'Disponible para reserva'}
                        </dd>
                      </div>
                    </div>
                  </dl>

                  {/* Primary Action Button: Change Status */}
                  <div className="mt-5 pt-3 border-t border-sand-200 flex flex-col gap-2">
                    <Button
                      variant="secondary"
                      className="w-full text-xs h-9"
                      onClick={() => {
                        setStatusModalTarget(room);
                        setNewStatusValue(room.status);
                        setStatusNote(room.note || '');
                      }}
                    >
                      Cambiar estado operativo
                    </Button>

                    {/* Admin Actions (Editar / Eliminar) */}
                    {isAdmin && (
                      <div className="flex items-center justify-end gap-2 pt-1">
                        <button
                          onClick={() => openEditModal(room)}
                          className="flex items-center gap-1 text-xs font-semibold text-forest-700 hover:text-forest-900 cursor-pointer p-1"
                        >
                          <Edit2 size={13} />
                          Editar
                        </button>
                        <button
                          onClick={() => setDeleteTarget(room)}
                          className="flex items-center gap-1 text-xs font-semibold text-bad hover:text-[#9c352e] cursor-pointer p-1 ml-2"
                        >
                          <Trash2 size={13} />
                          Eliminar
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      )}

      {/* Modal: Cambiar Estado Operativo */}
      {statusModalTarget && (
        <Modal
          title={`Estado de Habitación ${statusModalTarget.number}`}
          onClose={() => setStatusModalTarget(null)}
          footer={
            <>
              <Button variant="secondary" onClick={() => setStatusModalTarget(null)}>
                Cancelar
              </Button>
              <Button variant="primary" onClick={handleApplyStatusChange}>
                Guardar estado
              </Button>
            </>
          }
        >
          <Field label="Seleccionar nuevo estado">
            <Select
              value={newStatusValue}
              onChange={(val) => setNewStatusValue(val as RoomStatusKey)}
              options={(Object.keys(ROOM_STATUS_META) as RoomStatusKey[]).map((k) => ({
                value: k,
                label: ROOM_STATUS_META[k].label,
              }))}
            />
          </Field>
          <Field
            label="Nota operativa u observación"
            hint="Ej: Aseo de sábanas en curso, arreglo de bombillo, etc."
          >
            <Input
              value={statusNote}
              onChange={(e) => setStatusNote(e.target.value)}
              placeholder="Detalles para camarería o recepción"
            />
          </Field>
        </Modal>
      )}

      {/* Modal: Crear / Editar Habitación (Solo Administrador) */}
      {(addModalOpen || editRoom) && (
        <Modal
          title={editRoom ? `Editar Habitación ${editRoom.number}` : 'Nueva Habitación'}
          onClose={() => {
            setAddModalOpen(false);
            setEditRoom(null);
          }}
          footer={
            <>
              <Button
                variant="secondary"
                onClick={() => {
                  setAddModalOpen(false);
                  setEditRoom(null);
                }}
              >
                Cancelar
              </Button>
              <Button variant="primary" onClick={handleSaveRoom}>
                {editRoom ? 'Guardar cambios' : 'Crear habitación'}
              </Button>
            </>
          }
        >
          <div className="grid grid-cols-2 gap-3">
            <Field label="Número de habitación *">
              <Input
                value={formNumber}
                onChange={(e) => setFormNumber(e.target.value)}
                placeholder="Ej. 104, 204"
                disabled={!!editRoom}
              />
            </Field>
            <Field label="Nombre comercial *">
              <Input
                value={formName}
                onChange={(e) => setFormName(e.target.value)}
                placeholder="Ej. Mirador, Jacaranda"
              />
            </Field>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <Field label="Tipo de habitación">
              <Select
                value={formType}
                onChange={setFormType}
                options={[
                  { value: 'Sencilla', label: 'Sencilla' },
                  { value: 'Doble', label: 'Doble' },
                  { value: 'Familiar', label: 'Familiar' },
                  { value: 'Suite', label: 'Suite' },
                ]}
              />
            </Field>
            <Field label="Capacidad total máxima">
              <Input
                type="number"
                value={formCapacity}
                onChange={(e) => setFormCapacity(Number(e.target.value))}
              />
            </Field>
          </div>

          <div className="grid grid-cols-3 gap-3">
            <Field label="Adultos Base">
              <Input
                type="number"
                value={formBaseAdults}
                onChange={(e) => setFormBaseAdults(Number(e.target.value))}
              />
            </Field>
            <Field label="Adultos Máx">
              <Input
                type="number"
                value={formMaxAdults}
                onChange={(e) => setFormMaxAdults(Number(e.target.value))}
              />
            </Field>
            <Field label="Niños Máx">
              <Input
                type="number"
                value={formChildren}
                onChange={(e) => setFormChildren(Number(e.target.value))}
              />
            </Field>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <Field label="Tarifa base por noche (COP) *">
              <Input
                type="number"
                value={formRate}
                onChange={(e) => setFormRate(Number(e.target.value))}
              />
            </Field>
            <Field label="Tarifa huésped adicional">
              <Input
                type="number"
                value={formExtraRate}
                onChange={(e) => setFormExtraRate(Number(e.target.value))}
              />
            </Field>
          </div>

          <div className="pt-2">
            <label className="flex items-center gap-2 cursor-pointer text-sm font-medium text-ink">
              <input
                type="checkbox"
                checked={formAllowsPets}
                onChange={(e) => setFormAllowsPets(e.target.checked)}
                className="h-4 w-4 rounded border-sand-300 text-forest-800"
              />
              Esta habitación admite mascotas (Pet-friendly)
            </label>
          </div>
        </Modal>
      )}

      {/* Modal: Confirmar Eliminación con Validación Estricta */}
      {deleteTarget && (
        <ConfirmModal
          title={`¿Eliminar habitación ${deleteTarget.number}?`}
          confirm="Sí, eliminar"
          danger
          onCancel={() => setDeleteTarget(null)}
          onConfirm={handleDeleteConfirm}
        >
          Esta acción retirará la habitación <strong>{deleteTarget.number} ({deleteTarget.name})</strong> del sistema.
          <br /><br />
          <em>Nota de seguridad:</em> El sistema verificará que la habitación no tenga reservas activas o pendientes de pago antes de proceder.
        </ConfirmModal>
      )}

      {node}
    </div>
  );
}
