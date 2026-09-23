import React, { useEffect } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../api/client';

export default function Calendario() {
  const queryClient = useQueryClient();

  // Ejemplo de fetch de disponibilidad
  const { data, isLoading } = useQuery({
    queryKey: ['habitaciones'],
    queryFn: () => apiClient.get('/habitaciones/disponibilidad?desde=2026-10-12&hasta=2026-10-15&adultos=2&ninos=0&mascota=false').then(res => res.data)
  });

  // Efecto para conectar WebSocket
  useEffect(() => {
    // TODO: Implementar conexion STOMP con sockjs-client o stompjs
    console.log("Connect to WebSocket /ws here");

    // Al recibir evento:
    // queryClient.invalidateQueries({ queryKey: ['habitaciones'] });

    return () => {
      // TODO: Desconectar
    };
  }, [queryClient]);

  if (isLoading) return <div>Cargando calendario... (Skeleton)</div>;

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Calendario de Habitaciones</h1>
      <pre>{JSON.stringify(data, null, 2)}</pre>
      {/* TODO: Renderizar grilla de habitaciones x fechas */}
    </div>
  );
}
