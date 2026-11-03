import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../api/client';

type BookingRow = {
  id: number;
  reservationGroupId: string | null;
  status: string;
  paymentStatus: string;
  checkIn: string;
  checkOut: string;
  roomId: number;
  roomNumber: string | null;
  roomName: string | null;
  guestId: number;
  guestName: string | null;
  guestPhone: string | null;
  guestDocument: string | null;
  adults: number;
  children: number;
  withPet: boolean;
  companions: string | null;
  totalPrice: string;
  source: string;
  createdAt: string;
  updatedAt: string;
};

type Room = {
  id: number;
  number: string;
  name: string;
  type: string;
  pricePerNight: number;
  maxAdultsCapacity: number;
  childrenCapacity: number;
  allowsPets: boolean;
};

const statusColors: Record<string, string> = {
  pending_payment: '#f59e0b',
  confirmed: '#22c55e',
  cancelled: '#ef4444',
  finished: '#6b7280',
};

const paymentColors: Record<string, string> = {
  pending: '#f59e0b',
  paid: '#22c55e',
  refunded: '#3b82f6',
};

export default function ReservasDebug() {
  const queryClient = useQueryClient();
  const [mutationError, setMutationError] = useState<string | null>(null);
  const [form, setForm] = useState({
    waId: '573001234567',
    guestName: '',
    guestDocument: '',
    companions: '',
    checkIn: '',
    checkOut: '',
    adults: 2,
    children: 0,
    hasPet: false,
    roomId: 0,
  });

  const { data: rooms = [] } = useQuery({
    queryKey: ['rooms-debug', form.checkIn, form.checkOut, form.adults, form.children, form.hasPet],
    queryFn: () => apiClient.get<Room[]>('/api/rooms/availability', {
      params: {
        checkIn: form.checkIn,
        checkOut: form.checkOut,
        adults: String(form.adults),
        children: String(form.children),
        pet: String(form.hasPet),
      },
    }).then(res => res.data),
    enabled: Boolean(form.checkIn && form.checkOut && form.adults > 0),
  });

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['reservas-debug'],
    queryFn: () => apiClient.get<BookingRow[]>('/api/bookings/debug').then(res => res.data),
    refetchInterval: 5000,
  });

  const mutation = useMutation({
    mutationFn: async () => {
      setMutationError(null);
      const selectedRoomId = Number(form.roomId);
      if (!selectedRoomId) throw new Error('Selecciona una habitación');

      // Step 1: Lock the room
      const lock = await apiClient.post<{ lockToken: string }>('/api/bookings/lock', {
        roomId: selectedRoomId,
        checkIn: form.checkIn,
        checkOut: form.checkOut,
      });

      // Step 2: Confirm the booking
      return apiClient.post('/api/bookings/confirm', {
        waId: form.waId,
        guestName: form.guestName,
        guestDocument: form.guestDocument,
        companions: form.companions || null,
        checkIn: form.checkIn,
        checkOut: form.checkOut,
        adults: Number(form.adults),
        children: Number(form.children),
        hasPet: Boolean(form.hasPet),
        rooms: [{
          roomId: selectedRoomId,
          lockToken: lock.data.lockToken,
        }],
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reservas-debug'] });
      queryClient.invalidateQueries({ queryKey: ['rooms-debug'] });
      setForm(c => ({ ...c, guestName: '', guestDocument: '', companions: '' }));
    },
    onError: (err: Error) => {
      setMutationError(err.message || 'Error desconocido');
    },
  });

  const canSubmit = form.guestName.trim().length > 0
    && /^\d{6,10}$/.test(form.guestDocument)
    && form.checkIn && form.checkOut
    && form.checkIn < form.checkOut
    && Number(form.roomId) > 0
    && rooms.length > 0
    && !mutation.isPending;

  return (
    <div style={{ padding: '24px 32px', fontFamily: "'Inter', 'Segoe UI', sans-serif", maxWidth: 1200, margin: '0 auto' }}>
      <header style={{ marginBottom: 32 }}>
        <h1 style={{ fontSize: 28, fontWeight: 800, margin: 0, color: '#111827' }}>
          🏨 SatoriPMS — Reservas
        </h1>
        <p style={{ color: '#6b7280', marginTop: 4, fontSize: 14 }}>
          Vista de verificación: datos directamente desde PostgreSQL. Se actualiza cada 5 segundos.
        </p>
      </header>

      {/* ── Formulario ── */}
      <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 12, padding: 20, marginBottom: 28, boxShadow: '0 1px 3px rgba(0,0,0,0.06)' }}>
        <h2 style={{ fontSize: 16, fontWeight: 700, marginTop: 0, marginBottom: 16 }}>
          ✍️ Crear reserva desde la web
        </h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 14 }}>
          <Field label="WhatsApp ID" value={form.waId} onChange={v => setForm({ ...form, waId: v })} />
          <Field label="Nombre completo *" value={form.guestName} onChange={v => setForm({ ...form, guestName: v })} />
          <Field label="Identificación * (6-10 dígitos)" value={form.guestDocument} onChange={v => setForm({ ...form, guestDocument: v.replace(/\D/g, '') })} maxLength={10} />
          <Field label="Check-in *" type="date" value={form.checkIn} onChange={v => setForm({ ...form, checkIn: v })} />
          <Field label="Check-out *" type="date" value={form.checkOut} onChange={v => setForm({ ...form, checkOut: v })} />
          <Field label="Adultos" type="number" value={String(form.adults)} onChange={v => setForm({ ...form, adults: Number(v) || 1 })} />
          <Field label="Niños" type="number" value={String(form.children)} onChange={v => setForm({ ...form, children: Number(v) || 0 })} />
          <div>
            <label style={{ fontSize: 12, fontWeight: 600, color: '#374151', display: 'block', marginBottom: 4 }}>Habitación *</label>
            <select value={form.roomId} onChange={e => setForm({ ...form, roomId: Number(e.target.value) })} style={fieldStyle}>
              <option value={0}>— Seleccionar —</option>
              {rooms.map(room => (
                <option key={room.id} value={room.id}>
                  #{room.number} · {room.name} · ${Number(room.pricePerNight).toLocaleString('es-CO')}/noche
                </option>
              ))}
            </select>
            {form.checkIn && form.checkOut && rooms.length === 0 && (
              <span style={{ fontSize: 11, color: '#f59e0b' }}>No hay habitaciones disponibles para esas fechas</span>
            )}
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, paddingTop: 24 }}>
            <input type="checkbox" id="pet" checked={form.hasPet} onChange={e => setForm({ ...form, hasPet: e.target.checked })} />
            <label htmlFor="pet" style={{ fontSize: 13 }}>🐾 Con mascota</label>
          </div>
          <div style={{ gridColumn: '1 / -1' }}>
            <Field label="Acompañantes (nombres)" value={form.companions} onChange={v => setForm({ ...form, companions: v })} />
          </div>
        </div>

        <div style={{ marginTop: 16, display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
          <button
            type="button"
            onClick={() => mutation.mutate()}
            disabled={!canSubmit}
            style={{
              background: canSubmit ? '#111827' : '#9ca3af',
              color: '#fff', border: 'none', borderRadius: 8,
              padding: '10px 20px', cursor: canSubmit ? 'pointer' : 'not-allowed',
              fontWeight: 600, fontSize: 14, transition: 'background 0.2s',
            }}
          >
            {mutation.isPending ? '⏳ Guardando...' : '💾 Guardar reserva'}
          </button>
          {mutation.isSuccess && <span style={{ color: '#15803d', fontWeight: 600 }}>✅ Reserva guardada correctamente.</span>}
          {mutation.isError && <span style={{ color: '#b91c1c', fontWeight: 600 }}>❌ {mutationError}</span>}
        </div>
      </div>

      {/* ── Tabla de reservas ── */}
      {isLoading ? (
        <div style={{ padding: 24, textAlign: 'center', color: '#6b7280' }}>Cargando reservas...</div>
      ) : isError ? (
        <div style={{ padding: 24, color: 'crimson', background: '#fef2f2', borderRadius: 8 }}>
          ❌ Error al cargar reservas: {String(error)}
        </div>
      ) : (!data || data.length === 0) ? (
        <div style={{ padding: 20, background: '#f9fafb', borderRadius: 8, textAlign: 'center', color: '#6b7280' }}>
          No hay reservas guardadas por ahora. Crea una desde el formulario o desde WhatsApp.
        </div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
            <thead>
              <tr style={{ background: '#111827', color: '#fff' }}>
                {['ID', 'Estado', 'Pago', 'Habitación', 'Huésped', 'Fechas', 'Ocupación', 'Total', 'Fuente'].map(h => (
                  <th key={h} style={thStyle}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.map((row, i) => (
                <tr key={row.id} style={{ background: i % 2 === 0 ? '#fff' : '#f9fafb' }}>
                  <td style={tdStyle}><strong>{row.id}</strong></td>
                  <td style={tdStyle}>
                    <span style={{ ...badgeStyle, background: statusColors[row.status] || '#6b7280' }}>
                      {row.status}
                    </span>
                  </td>
                  <td style={tdStyle}>
                    <span style={{ ...badgeStyle, background: paymentColors[row.paymentStatus] || '#6b7280' }}>
                      {row.paymentStatus}
                    </span>
                  </td>
                  <td style={tdStyle}>
                    <strong>{row.roomNumber ?? row.roomId}</strong>
                    {row.roomName ? <><br /><span style={{ fontSize: 11, color: '#6b7280' }}>{row.roomName}</span></> : ''}
                  </td>
                  <td style={tdStyle}>
                    <strong>{row.guestName ?? '—'}</strong><br />
                    <span style={{ fontSize: 11, color: '#6b7280' }}>{row.guestPhone ?? '—'}</span><br />
                    <span style={{ fontSize: 11, color: '#6b7280' }}>CC: {row.guestDocument ?? '—'}</span>
                  </td>
                  <td style={tdStyle}>{row.checkIn} → {row.checkOut}</td>
                  <td style={tdStyle}>
                    {row.adults}A / {row.children}N
                    {row.withPet ? ' 🐾' : ''}
                    {row.companions ? <><br /><span style={{ fontSize: 11, color: '#6b7280' }}>{row.companions}</span></> : ''}
                  </td>
                  <td style={{ ...tdStyle, fontWeight: 700 }}>${Number(row.totalPrice).toLocaleString('es-CO')}</td>
                  <td style={tdStyle}>
                    <span style={{ ...badgeStyle, background: row.source === 'chatbot' ? '#8b5cf6' : '#3b82f6' }}>
                      {row.source}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function Field({ label, value, onChange, type = 'text', maxLength }: {
  label: string; value: string; onChange: (v: string) => void;
  type?: string; maxLength?: number;
}) {
  return (
    <div>
      <label style={{ fontSize: 12, fontWeight: 600, color: '#374151', display: 'block', marginBottom: 4 }}>{label}</label>
      <input type={type} value={value} maxLength={maxLength}
        onChange={e => onChange(e.target.value)} style={fieldStyle} />
    </div>
  );
}

const fieldStyle: React.CSSProperties = {
  width: '100%', padding: '8px 10px', border: '1px solid #d1d5db',
  borderRadius: 8, boxSizing: 'border-box', fontSize: 14,
};

const thStyle: React.CSSProperties = {
  padding: '10px 8px', border: '1px solid #374151', textAlign: 'left', fontSize: 12, fontWeight: 700,
};

const tdStyle: React.CSSProperties = {
  padding: '10px 8px', border: '1px solid #e5e7eb', verticalAlign: 'top',
};

const badgeStyle: React.CSSProperties = {
  color: '#fff', padding: '2px 8px', borderRadius: 12, fontSize: 11, fontWeight: 700, whiteSpace: 'nowrap',
};
