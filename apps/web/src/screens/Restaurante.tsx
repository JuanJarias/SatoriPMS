import React, { useState } from 'react';
import {
  Coffee,
  UtensilsCrossed,
  Plus,
  Minus,
  Trash2,
  BedDouble,
  CheckCircle2,
  Clock,
  Sparkles,
  ChefHat,
  Award
} from 'lucide-react';
import { useStore, MenuItem, RestaurantOrder } from '../store';
import {
  PageHeader,
  Card,
  CardHeader,
  Button,
  Select,
  FilterChip,
  BadgeStatus,
  EmptyState,
  Alert,
  useToast,
  formatCurrency,
  cn
} from '../ui';

export function Restaurante({ go }: { go: (view: string, param?: string) => void }) {
  const { menu, orders, rooms, addRestaurantOrder, updateOrderStatus, log } = useStore();
  const [selectedCat, setSelectedCat] = useState<string>('todas');
  const [activeTab, setActiveTab] = useState<'menu' | 'comandas'>('menu');

  // Carrito de comanda
  const [orderItems, setOrderItems] = useState<{ menuItemId: string | number; name: string; qty: number; price: number }[]>([]);
  const [orderDestination, setOrderDestination] = useState<'room' | 'table'>('room');
  const [selectedRoomNum, setSelectedRoomNum] = useState<string>('101');
  const [tableNumber, setTableNumber] = useState<string>('Mesa 1');

  const { show, node } = useToast();

  const occupiedRooms = rooms.filter((r) => r.status === 'ocupada');

  const categories = [
    { key: 'todas', label: 'Toda la carta' },
    { key: 'breakfast', label: 'Desayunos' },
    { key: 'coffee', label: 'Salgados Café de Origen' },
    { key: 'experience', label: 'Catas & Barismo' },
    { key: 'bakery', label: 'Repostería' },
  ];

  const filteredMenu = menu.filter((item) => {
    if (selectedCat === 'todas') return true;
    return item.category === selectedCat;
  });

  const addItemToOrder = (item: MenuItem) => {
    setOrderItems((prev) => {
      const exists = prev.find((i) => i.menuItemId === item.id);
      if (exists) {
        return prev.map((i) =>
          i.menuItemId === item.id ? { ...i, qty: i.qty + 1 } : i
        );
      }
      return [...prev, { menuItemId: item.id, name: item.name, qty: 1, price: item.price }];
    });
  };

  const updateItemQty = (id: string | number, delta: number) => {
    setOrderItems((prev) =>
      prev
        .map((i) => {
          if (i.menuItemId === id) {
            const newQty = i.qty + delta;
            return newQty > 0 ? { ...i, qty: newQty } : null;
          }
          return i;
        })
        .filter(Boolean) as { menuItemId: string | number; name: string; qty: number; price: number }[]
    );
  };

  const removeItem = (id: string | number) => {
    setOrderItems((prev) => prev.filter((i) => i.menuItemId !== id));
  };

  const orderTotal = orderItems.reduce((acc, i) => acc + i.price * i.qty, 0);

  const handleSendOrder = () => {
    if (orderItems.length === 0) return;

    const guestRoomObj = rooms.find((r) => r.number === selectedRoomNum);

    addRestaurantOrder({
      roomNumber: orderDestination === 'room' ? selectedRoomNum : undefined,
      tableNumber: orderDestination === 'table' ? tableNumber : undefined,
      guestName: orderDestination === 'room' ? guestRoomObj?.guest || 'Huésped' : undefined,
      items: orderItems,
      total: orderTotal,
      status: orderDestination === 'room' ? 'charged_to_room' : 'pending',
    });

    if (orderDestination === 'room') {
      show(
        'Comanda enviada con cargo a habitación',
        `Hab. ${selectedRoomNum} (${guestRoomObj?.guest || ''}) · Total: ${formatCurrency(orderTotal)}`
      );
    } else {
      show(
        'Comanda enviada a cocina',
        `${tableNumber} · Total: ${formatCurrency(orderTotal)}`
      );
    }

    setOrderItems([]);
    setActiveTab('comandas');
  };

  return (
    <div>
      <PageHeader
        eyebrow="Gastronomía & Cafetería de Especialidad"
        title="Salgados Café & Restaurante"
        desc="Desayunos típicos, métodos de preparación de café de origen Sevilla, catas guiadas y comandas con cargo a habitación."
        actions={
          <div className="flex gap-2">
            <Button
              variant={activeTab === 'menu' ? 'primary' : 'secondary'}
              onClick={() => setActiveTab('menu')}
            >
              Carta y Nueva Comanda
            </Button>
            <Button
              variant={activeTab === 'comandas' ? 'primary' : 'secondary'}
              onClick={() => setActiveTab('comandas')}
            >
              Comandas Activas ({orders.length})
            </Button>
          </div>
        }
      />

      {activeTab === 'menu' ? (
        <div className="grid gap-6 min-[1100px]:grid-cols-[1.5fr_1fr]">
          {/* Columna Izquierda: Carta */}
          <div className="space-y-4">
            <Card className="p-4">
              <div className="flex flex-wrap gap-2">
                {categories.map((c) => (
                  <FilterChip
                    key={c.key}
                    active={selectedCat === c.key}
                    onClick={() => setSelectedCat(c.key)}
                  >
                    {c.label}
                  </FilterChip>
                ))}
              </div>
            </Card>

            <div className="grid gap-3 sm:grid-cols-2">
              {filteredMenu.map((item) => {
                const inOrder = orderItems.find((i) => i.menuItemId === item.id);
                const isSpecialCoffee = item.category === 'coffee' || item.category === 'experience';

                return (
                  <Card
                    key={item.id}
                    className={cn(
                      'p-4 flex flex-col justify-between transition-all hover:border-forest-700',
                      isSpecialCoffee && 'border-terra-500/40 bg-sand-50/50'
                    )}
                  >
                    <div>
                      <div className="flex justify-between items-start">
                        <span className="text-[11px] uppercase tracking-wider font-semibold text-terra-600 bg-terra-100 px-2 py-0.5 rounded-full">
                          {item.category === 'coffee' ? 'Café de Especialidad' : item.category === 'experience' ? 'Experiencia Sensorial' : item.category === 'breakfast' ? 'Desayuno' : 'Repostería'}
                        </span>
                        <span className="font-display font-bold text-forest-900 text-sm">
                          {formatCurrency(item.price)}
                        </span>
                      </div>

                      <h3 className="font-semibold text-ink text-sm mt-2">{item.name}</h3>
                      {item.description && (
                        <p className="text-xs text-ink-soft mt-1 leading-relaxed">
                          {item.description}
                        </p>
                      )}
                    </div>

                    <div className="mt-4 pt-3 border-t border-sand-200 flex justify-between items-center">
                      {inOrder ? (
                        <div className="flex items-center gap-2">
                          <Button
                            variant="secondary"
                            className="h-8 w-8 px-0"
                            onClick={() => updateItemQty(item.id, -1)}
                          >
                            <Minus size={14} />
                          </Button>
                          <span className="font-bold text-sm w-6 text-center">{inOrder.qty}</span>
                          <Button
                            variant="secondary"
                            className="h-8 w-8 px-0"
                            onClick={() => updateItemQty(item.id, 1)}
                          >
                            <Plus size={14} />
                          </Button>
                        </div>
                      ) : (
                        <Button
                          variant={isSpecialCoffee ? 'terra' : 'secondary'}
                          className="h-8 text-xs px-3 ml-auto"
                          onClick={() => addItemToOrder(item)}
                        >
                          <Plus size={14} />
                          Agregar a comanda
                        </Button>
                      )}
                    </div>
                  </Card>
                );
              })}
            </div>
          </div>

          {/* Columna Derecha: Comanda Actual */}
          <div>
            <Card className="p-5 sticky top-6">
              <CardHeader
                title="Comanda en Preparación"
                hint={`${orderItems.length} ítem(s) seleccionados`}
              />

              {orderItems.length === 0 ? (
                <EmptyState
                  icon={<UtensilsCrossed size={26} />}
                  title="No hay ítems en la comanda"
                >
                  Selecciona desayunos, cafés Salgados o experiencias sensoriales.
                </EmptyState>
              ) : (
                <div className="space-y-4">
                  <div className="divide-y divide-sand-200 max-h-60 overflow-y-auto pr-1">
                    {orderItems.map((item) => (
                      <div key={item.menuItemId} className="py-2.5 flex justify-between items-center text-sm">
                        <div className="min-w-0 flex-1 mr-2">
                          <p className="font-medium text-ink truncate">{item.name}</p>
                          <p className="text-xs text-ink-soft">
                            {item.qty} × {formatCurrency(item.price)}
                          </p>
                        </div>
                        <div className="flex items-center gap-2 shrink-0">
                          <span className="font-semibold tabular-nums text-forest-900">
                            {formatCurrency(item.price * item.qty)}
                          </span>
                          <button
                            onClick={() => removeItem(item.menuItemId)}
                            className="text-ink-soft hover:text-bad p-1 cursor-pointer"
                          >
                            <Trash2 size={14} />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="border-t border-sand-200 pt-3 flex justify-between text-base font-bold">
                    <span className="text-forest-900">Total Comanda:</span>
                    <span className="text-terra-600">{formatCurrency(orderTotal)}</span>
                  </div>

                  {/* Destino de la Comanda */}
                  <div className="space-y-3 pt-2 border-t border-sand-200">
                    <span className="text-xs font-semibold uppercase tracking-wider text-ink-soft block">
                      Destino de la comanda
                    </span>
                    <div className="grid grid-cols-2 gap-2">
                      <button
                        type="button"
                        onClick={() => setOrderDestination('room')}
                        className={cn(
                          'p-2.5 rounded-lg border text-xs font-semibold flex items-center justify-center gap-1.5 cursor-pointer',
                          orderDestination === 'room'
                            ? 'border-forest-800 bg-forest-50 text-forest-900 ring-1 ring-forest-800'
                            : 'border-sand-300 bg-white text-ink-soft'
                        )}
                      >
                        <BedDouble size={14} />
                        Cargo a Habitación
                      </button>
                      <button
                        type="button"
                        onClick={() => setOrderDestination('table')}
                        className={cn(
                          'p-2.5 rounded-lg border text-xs font-semibold flex items-center justify-center gap-1.5 cursor-pointer',
                          orderDestination === 'table'
                            ? 'border-forest-800 bg-forest-50 text-forest-900 ring-1 ring-forest-800'
                            : 'border-sand-300 bg-white text-ink-soft'
                        )}
                      >
                        <UtensilsCrossed size={14} />
                        Mesa Cafetería
                      </button>
                    </div>

                    {orderDestination === 'room' ? (
                      <div>
                        <label className="text-xs font-medium text-ink block mb-1">
                          Seleccionar habitación ocupada:
                        </label>
                        <Select
                          value={selectedRoomNum}
                          onChange={setSelectedRoomNum}
                          options={occupiedRooms.map((r) => ({
                            value: r.number,
                            label: `Hab. ${r.number} (${r.guest || r.name})`,
                          }))}
                        />
                      </div>
                    ) : (
                      <div>
                        <label className="text-xs font-medium text-ink block mb-1">
                          Número de Mesa / Ubicación:
                        </label>
                        <Select
                          value={tableNumber}
                          onChange={setTableNumber}
                          options={[
                            { value: 'Mesa 1', label: 'Mesa 1 (Kiosko Terraza)' },
                            { value: 'Mesa 2', label: 'Mesa 2 (Barra de Barismo)' },
                            { value: 'Mesa 3', label: 'Mesa 3 (Jardín Central)' },
                            { value: 'Mesa 4', label: 'Mesa 4 (Salón Principal)' },
                          ]}
                        />
                      </div>
                    )}

                    <Button
                      variant="terra"
                      className="w-full mt-2"
                      onClick={handleSendOrder}
                    >
                      Enviar comanda {orderDestination === 'room' ? 'y cargar a cuenta' : 'a preparación'}
                    </Button>
                  </div>
                </div>
              )}
            </Card>
          </div>
        </div>
      ) : (
        /* Pestaña de Comandas Activas */
        <div className="space-y-4">
          <Card className="overflow-hidden">
            <div className="p-4 border-b border-sand-200 flex justify-between items-center">
              <h2 className="font-display font-semibold text-lg text-forest-900">
                Historial de Comandas del Día
              </h2>
              <span className="text-xs text-ink-soft">
                {orders.length} comanda(s) registradas
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="bg-sand-50">
                  <tr>
                    <th className="px-4 py-2.5 font-semibold text-xs text-ink-soft">Hora</th>
                    <th className="px-4 py-2.5 font-semibold text-xs text-ink-soft">Destino</th>
                    <th className="px-4 py-2.5 font-semibold text-xs text-ink-soft">Detalle de Comanda</th>
                    <th className="px-4 py-2.5 font-semibold text-xs text-ink-soft">Total</th>
                    <th className="px-4 py-2.5 font-semibold text-xs text-ink-soft">Estado</th>
                    <th className="px-4 py-2.5 font-semibold text-xs text-ink-soft text-right">Acción</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-sand-200">
                  {orders.map((ord) => (
                    <tr key={ord.id} className="hover:bg-forest-50 transition-colors">
                      <td className="px-4 py-3 text-xs text-ink-soft">{ord.createdAt}</td>
                      <td className="px-4 py-3 font-semibold text-forest-900">
                        {ord.roomNumber ? `Hab. ${ord.roomNumber}` : ord.tableNumber}
                        {ord.guestName && (
                          <span className="block text-xs font-normal text-ink-soft">
                            {ord.guestName}
                          </span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-xs">
                        <ul className="list-disc list-inside space-y-0.5">
                          {ord.items.map((i, idx) => (
                            <li key={idx}>
                              {i.qty}× {i.name}
                            </li>
                          ))}
                        </ul>
                      </td>
                      <td className="px-4 py-3 font-bold tabular-nums text-forest-800">
                        {formatCurrency(ord.total)}
                      </td>
                      <td className="px-4 py-3">
                        <span
                          className={cn(
                            'inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-semibold',
                            ord.status === 'charged_to_room'
                              ? 'bg-ok-bg text-ok'
                              : ord.status === 'delivered'
                              ? 'bg-clean-bg text-clean'
                              : 'bg-warn-bg text-warn'
                          )}
                        >
                          {ord.status === 'charged_to_room'
                            ? 'Cargado a habitación'
                            : ord.status === 'delivered'
                            ? 'Entregado'
                            : 'En preparación'}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-right">
                        {ord.status === 'pending' && (
                          <Button
                            variant="secondary"
                            className="h-8 text-xs px-2.5"
                            onClick={() => updateOrderStatus(ord.id, 'delivered')}
                          >
                            Marcar entregado
                          </Button>
                        )}
                        {ord.status === 'charged_to_room' && (
                          <span className="text-xs text-ok font-medium">Liquidación en check-out</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      )}

      {node}
    </div>
  );
}
