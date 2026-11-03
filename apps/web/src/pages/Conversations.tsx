import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api/client';

export default function Conversations() {
  const { data, isLoading, isError } = useQuery<any[]>({
    queryKey: ['conversations'],
    queryFn: () => apiClient.get('/api/conversations').then((res) => res.data as any[]),
    refetchInterval: 5000, // refresco simple por polling, no WebSocket
  });

  if (isLoading) return <div className="p-4">Cargando conversaciones...</div>;
  if (isError) return <div className="p-4 text-red-600">Error al cargar conversaciones.</div>;

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Conversaciones (vista de verificación)</h1>
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr className="text-left border-b">
            <th className="p-2">WhatsApp</th>
            <th className="p-2">Estado</th>
            <th className="p-2">Paso</th>
            <th className="p-2">Fechas</th>
            <th className="p-2">Habitación</th>
            <th className="p-2">Personas</th>
            <th className="p-2">Mascota</th>
            <th className="p-2">Total</th>
          </tr>
        </thead>
        <tbody>
          {Array.isArray(data) && data.map((c: any) => (
            <tr key={c.id} className="border-b">
              <td className="p-2">{c.whatsappPhone}</td>
              <td className="p-2">{c.status}</td>
              <td className="p-2">{c.step}</td>
              <td className="p-2">{c.checkIn} → {c.checkOut}</td>
              <td className="p-2">{c.selectedRoomId ?? '—'}</td>
              <td className="p-2">{c.adults}A / {c.children}N</td>
              <td className="p-2">{c.withPet ? 'Sí' : 'No'}</td>
              <td className="p-2">{c.quotedTotal ?? '—'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}