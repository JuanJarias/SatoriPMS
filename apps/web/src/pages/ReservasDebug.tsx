import { useMemo, useState } from 'react';
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
  pricePerNight: number;
};

export default function ReservasDebug() {
  const queryClient = useQueryClient();
  const [form, setForm] = useState({
    waId: '573001234567',
    guestName: 'Ana García',
    guestDocument: '12345678',
    companions: '',
    checkIn: '2026-12-15',
    checkOut: '2026-12-17',
    adults: 2,
    children: 1,
    hasPet: false,
    roomId: 1,
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
      const lock = await apiClient.post<{ lockToken: string }>('/api/bookings/lock', {
        roomId: Number(form.roomId),
        checkIn: form.checkIn,
        checkOut: form.checkOut,
      });
      return apiClient.post('/api/bookings/confirm', { ...payload, rooms: [{
        roomId: Number(form.roomId),
        lockToken: lock.data.lockToken,
      }] });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reservas-debug'] });
      setForm((current) => ({ ...current, guestName: '', guestDocument: '' }));
    },
  });

  const payload = useMemo(() => ({
    waId: form.waId,
    guestName: form.guestName,
    guestDocument: form.guestDocument,
    companions: form.companions,
    checkIn: form.checkIn,
    checkOut: form.checkOut,
    adults: Number(form.adults),
    children: Number(form.children),
    hasPet: Boolean(form.hasPet),
    rooms: [],
  }), [form]);

  if (isLoading) {
    return <div style={{ padding: 24 }}>Cargando reservas...</div>;
  }

  if (isError) {
    return <div style={{ padding: 24, color: 'crimson' }}>Error: {String(error)}</div>;
  }

  return (
    <div style={{ padding: 24, fontFamily: 'sans-serif' }}>
      <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 20 }}>Reservas en BD (debug)</h1>
      <p style={{ marginBottom: 20, color: '#444' }}>
        Esta vista refleja directamente lo que existe en la base de datos. Sirve para verificar que se están guardando las reservas y que quedan visibles correctamente.
      </p>

      <div style={{ background: '#f9fafb', border: '1px solid #e5e7eb', borderRadius: 12, padding: 16, marginBottom: 24 }}>
        <h2 style={{ fontSize: 18, marginTop: 0, marginBottom: 12 }}>Guardar reserva de prueba</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 12 }}>
          <label>waId<input value={form.waId} onChange={(e) => setForm({ ...form, waId: e.target.value })} style={fieldStyle} /></label>
          <label>Nombre<input value={form.guestName} onChange={(e) => setForm({ ...form, guestName: e.target.value })} style={fieldStyle} /></label>
          <label>Identificación<input value={form.guestDocument} inputMode="numeric" pattern="[0-9]{6,10}" maxLength={10} onChange={(e) => setForm({ ...form, guestDocument: e.target.value.replace(/\D/g, '') })} style={fieldStyle} /></label>
          <label>Check-in<input type="date" value={form.checkIn} onChange={(e) => setForm({ ...form, checkIn: e.target.value })} style={fieldStyle} /></label>
          <label>Check-out<input type="date" value={form.checkOut} onChange={(e) => setForm({ ...form, checkOut: e.target.value })} style={fieldStyle} /></label>
          <label>Adultos<input type="number" min={1} value={form.adults} onChange={(e) => setForm({ ...form, adults: Number(e.target.value) })} style={fieldStyle} /></label>
          <label>Niños<input type="number" min={0} value={form.children} onChange={(e) => setForm({ ...form, children: Number(e.target.value) })} style={fieldStyle} /></label>
          <label>Habitación<select value={form.roomId} onChange={(e) => setForm({ ...form, roomId: Number(e.target.value) })} style={fieldStyle}>
            {rooms.length === 0 && <option value={form.roomId}>No hay habitaciones disponibles</option>}
            {rooms.map(room => <option key={room.id} value={room.id}>#{room.number} · {room.name} · ${room.pricePerNight}</option>)}
          </select></label>
          <label style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <input type="checkbox" checked={form.hasPet} onChange={(e) => setForm({ ...form, hasPet: e.target.checked })} />
            Mascota
          </label>
          <label style={{ gridColumn: '1 / -1' }}>Acompañantes<input value={form.companions} onChange={(e) => setForm({ ...form, companions: e.target.value })} style={fieldStyle} /></label>
        </div>

        <div style={{ marginTop: 16, display: 'flex', gap: 12, alignItems: 'center' }}>
          <button
            type="button"
            onClick={() => mutation.mutate()}
            disabled={mutation.isPending || !/^\d{6,10}$/.test(form.guestDocument) || rooms.length === 0}
            style={{ background: '#111827', color: '#fff', border: 'none', borderRadius: 8, padding: '10px 16px', cursor: 'pointer' }}
          >
            {mutation.isPending ? 'Guardando...' : 'Guardar reserva'}
          </button>
          {mutation.isSuccess && <span style={{ color: '#15803d' }}>Reserva guardada correctamente.</span>}
          {mutation.isError && <span style={{ color: '#b91c1c' }}>No se pudo guardar la reserva.</span>}
        </div>
      </div>

      {(!data || data.length === 0) ? (
        <div style={{ padding: 16, background: '#f5f5f5', borderRadius: 8 }}>
          No hay reservas guardadas por ahora.
        </div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
            <thead>
              <tr style={{ background: '#111827', color: '#fff' }}>
                <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>ID</th>
                <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Grupo</th>
                <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Estado</th>
                <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Pago</th>
                <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Habitación</th>
                <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Huésped</th>
                <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Fechas</th>
                <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Ocupación</th>
                <th style={{ padding: 8, border: '1px solid #d1d5db', textAlign: 'left' }}>Total</th>
              </tr>
            </thead>
            <tbody>
              {data.map(row => (
                <tr key={row.id} style={{ background: '#fff' }}>
                  <td style={{ padding: 8, border: '1px solid #e5e7eb' }}>{row.id}</td>
                  <td style={{ padding: 8, border: '1px solid #e5e7eb' }}>{row.reservationGroupId ?? '-'}</td>
                  <td style={{ padding: 8, border: '1px solid #e5e7eb' }}>{row.status}</td>
                  <td style={{ padding: 8, border: '1px solid #e5e7eb' }}>{row.paymentStatus}</td>
                  <td style={{ padding: 8, border: '1px solid #e5e7eb' }}>
                    {row.roomNumber ?? row.roomId}
                    {row.roomName ? ` · ${row.roomName}` : ''}
                  </td>
                  <td style={{ padding: 8, border: '1px solid #e5e7eb' }}>
                    {row.guestName ?? '-'}<br />
                    {row.guestPhone ?? '-'}<br />
                    {row.guestDocument ?? '-'}
                  </td>
                  <td style={{ padding: 8, border: '1px solid #e5e7eb' }}>
                    {row.checkIn} → {row.checkOut}
                  </td>
                  <td style={{ padding: 8, border: '1px solid #e5e7eb' }}>
                    {row.adults} adultos / {row.children} niños / {row.withPet ? 'con mascota' : 'sin mascota'}
                  </td>
                  <td style={{ padding: 8, border: '1px solid #e5e7eb' }}>{row.totalPrice}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

const fieldStyle: React.CSSProperties = {
  width: '100%',
  padding: '8px 10px',
  border: '1px solid #d1d5db',
  borderRadius: 8,
  marginTop: 6,
  boxSizing: 'border-box',
};
