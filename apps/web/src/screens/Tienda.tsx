import React, { useState } from 'react';
import {
  ShoppingBag,
  Plus,
  Minus,
  Trash2,
  CreditCard,
  Banknote,
  BedDouble,
  Tag,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import { useStore, ProductItem } from '../store';
import {
  PageHeader,
  Card,
  CardHeader,
  Button,
  SearchBar,
  Select,
  FilterChip,
  Alert,
  EmptyState,
  useToast,
  formatCurrency,
  cn
} from '../ui';

export function Tienda({ go }: { go: (view: string, param?: string) => void }) {
  const { products, rooms, sell, addCharges, log } = useStore();
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('todas');

  // Carrito de compras
  const [cart, setCart] = useState<{ id: string; qty: number }[]>([]);
  const [paymentTarget, setPaymentTarget] = useState<'efectivo' | 'habitacion'>('habitacion');
  const [targetRoom, setTargetRoom] = useState<string>('101');

  const { show, node } = useToast();

  const categories = ['todas', 'Café de Origen', 'Bebidas', 'Snacks', 'Cuidado personal'];

  const filteredProducts = products.filter((p) => {
    const q = search.trim().toLowerCase();
    const matchesSearch = !q || p.name.toLowerCase().includes(q) || p.category.toLowerCase().includes(q);
    const matchesCat = selectedCategory === 'todas' || p.category === selectedCategory;
    return matchesSearch && matchesCat;
  });

  const occupiedRooms = rooms.filter((r) => r.status === 'ocupada');

  const addToCart = (product: ProductItem) => {
    if (product.stock <= 0) {
      show('Sin inventario disponible', `No hay stock de ${product.name}`, 'bad');
      return;
    }
    setCart((prev) => {
      const existing = prev.find((item) => item.id === product.id);
      if (existing) {
        if (existing.qty >= product.stock) {
          show('Límite de stock', `Solo hay ${product.stock} unidades disponibles`, 'warn');
          return prev;
        }
        return prev.map((item) =>
          item.id === product.id ? { ...item, qty: item.qty + 1 } : item
        );
      }
      return [...prev, { id: product.id, qty: 1 }];
    });
  };

  const updateCartQty = (id: string, delta: number) => {
    setCart((prev) =>
      prev
        .map((item) => {
          if (item.id === id) {
            const prod = products.find((p) => p.id === id);
            const newQty = item.qty + delta;
            if (newQty <= 0) return null;
            if (prod && newQty > prod.stock) {
              show('Límite de stock', `Stock máximo: ${prod.stock}`, 'warn');
              return item;
            }
            return { ...item, qty: newQty };
          }
          return item;
        })
        .filter(Boolean) as { id: string; qty: number }[]
    );
  };

  const removeFromCart = (id: string) => {
    setCart((prev) => prev.filter((item) => item.id !== id));
  };

  const cartTotal = cart.reduce((acc, item) => {
    const prod = products.find((p) => p.id === item.id);
    return acc + (prod ? prod.price * item.qty : 0);
  }, 0);

  const handleCheckout = () => {
    if (cart.length === 0) return;

    if (paymentTarget === 'habitacion') {
      if (!targetRoom) {
        show('Selecciona una habitación', 'Debes indicar a qué habitación cargar el consumo', 'bad');
        return;
      }
      const chargeItems = cart.map((item) => {
        const prod = products.find((p) => p.id === item.id)!;
        return {
          desc: prod.name,
          qty: item.qty,
          amount: prod.price * item.qty,
          source: 'tienda' as const,
        };
      });

      addCharges(targetRoom, chargeItems);
      sell(cart);
      log(`Cargó ${cart.length} productos de tienda a la Hab. ${targetRoom} (${formatCurrency(cartTotal)})`, 'Tienda');
      show('Consumo cargado a habitación', `Hab. ${targetRoom} · Total: ${formatCurrency(cartTotal)}`);
    } else {
      sell(cart);
      log(`Venta directa en recepción (${formatCurrency(cartTotal)})`, 'Tienda');
      show('Venta completada', `Recaudado en caja: ${formatCurrency(cartTotal)}`);
    }

    setCart([]);
  };

  return (
    <div>
      <PageHeader
        eyebrow="Inventario & Tienda de Hotel"
        title="Tienda Torre Satori"
        desc="Venta de bebidas, snacks, insumos y café especial de origen de la casa: Salgados Café."
      />

      <div className="grid gap-6 min-[1100px]:grid-cols-[1.5fr_1fr]">
        {/* Catálogo de Productos */}
        <div className="space-y-4">
          <Card className="p-4">
            <div className="flex flex-col sm:flex-row gap-3">
              <div className="flex-1">
                <SearchBar
                  value={search}
                  onChange={setSearch}
                  placeholder="Buscar en la tienda (Salgados Café, agua, snacks)…"
                />
              </div>
            </div>

            <div className="mt-3 flex flex-wrap gap-2 border-t border-sand-200 pt-3">
              {categories.map((cat) => (
                <FilterChip
                  key={cat}
                  active={selectedCategory === cat}
                  onClick={() => setSelectedCategory(cat)}
                >
                  {cat === 'todas' ? 'Todos los productos' : cat}
                </FilterChip>
              ))}
            </div>
          </Card>

          <div className="grid gap-3 sm:grid-cols-2">
            {filteredProducts.map((p) => {
              const inCart = cart.find((c) => c.id === p.id);
              const isOriginCoffee = p.category === 'Café de Origen';

              return (
                <Card
                  key={p.id}
                  className={cn(
                    'p-4 flex flex-col justify-between transition-all hover:border-forest-700',
                    isOriginCoffee && 'border-terra-500/40 bg-sand-50/60'
                  )}
                >
                  <div>
                    <div className="flex justify-between items-start gap-2">
                      <span className={cn('text-xs font-semibold px-2 py-0.5 rounded-full', isOriginCoffee ? 'bg-terra-100 text-terra-600' : 'bg-sand-100 text-ink-soft')}>
                        {p.category}
                      </span>
                      <span className={cn('text-xs font-medium tabular-nums', p.stock > 5 ? 'text-ink-soft' : p.stock > 0 ? 'text-warn' : 'text-bad')}>
                        {p.stock > 0 ? `${p.stock} en stock` : 'Agotado'}
                      </span>
                    </div>

                    <h3 className="font-semibold text-ink text-sm mt-2">{p.name}</h3>
                    <p className="font-display text-base font-bold text-forest-900 mt-1">
                      {formatCurrency(p.price)}
                    </p>
                  </div>

                  <div className="mt-4 pt-3 border-t border-sand-200 flex items-center justify-between">
                    {inCart ? (
                      <div className="flex items-center gap-2">
                        <Button
                          variant="secondary"
                          className="h-8 w-8 px-0"
                          onClick={() => updateCartQty(p.id, -1)}
                        >
                          <Minus size={14} />
                        </Button>
                        <span className="font-bold text-sm w-6 text-center">{inCart.qty}</span>
                        <Button
                          variant="secondary"
                          className="h-8 w-8 px-0"
                          onClick={() => updateCartQty(p.id, 1)}
                        >
                          <Plus size={14} />
                        </Button>
                      </div>
                    ) : (
                      <Button
                        variant={isOriginCoffee ? 'terra' : 'secondary'}
                        className="h-8 text-xs px-3"
                        disabled={p.stock <= 0}
                        onClick={() => addToCart(p)}
                      >
                        <Plus size={14} />
                        Agregar
                      </Button>
                    )}
                  </div>
                </Card>
              );
            })}
          </div>
        </div>

        {/* Carrito & Liquidación */}
        <div>
          <Card className="p-5 sticky top-6">
            <CardHeader
              title="Caja Registradora"
              hint={`${cart.length} producto(s) en orden`}
            />

            {cart.length === 0 ? (
              <EmptyState
                icon={<ShoppingBag size={26} />}
                title="El carrito de tienda está vacío"
              >
                Haz clic en "Agregar" en cualquiera de los productos del catálogo.
              </EmptyState>
            ) : (
              <div className="space-y-4">
                <div className="divide-y divide-sand-200 max-h-60 overflow-y-auto pr-1">
                  {cart.map((item) => {
                    const prod = products.find((p) => p.id === item.id)!;
                    return (
                      <div key={item.id} className="py-2.5 flex justify-between items-center text-sm">
                        <div className="min-w-0 flex-1 mr-2">
                          <p className="font-medium text-ink truncate">{prod.name}</p>
                          <p className="text-xs text-ink-soft">
                            {item.qty} × {formatCurrency(prod.price)}
                          </p>
                        </div>
                        <div className="flex items-center gap-2 shrink-0">
                          <span className="font-semibold tabular-nums text-forest-900">
                            {formatCurrency(prod.price * item.qty)}
                          </span>
                          <button
                            onClick={() => removeFromCart(item.id)}
                            className="text-ink-soft hover:text-bad p-1 cursor-pointer"
                          >
                            <Trash2 size={14} />
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>

                <div className="border-t border-sand-200 pt-3 flex justify-between text-base font-bold">
                  <span className="text-forest-900">Total Venta:</span>
                  <span className="text-forest-800">{formatCurrency(cartTotal)}</span>
                </div>

                {/* Método de cobro */}
                <div className="space-y-3 pt-2 border-t border-sand-200">
                  <span className="text-xs font-semibold uppercase tracking-wider text-ink-soft block">
                    Destino del cobro
                  </span>
                  <div className="grid grid-cols-2 gap-2">
                    <button
                      type="button"
                      onClick={() => setPaymentTarget('habitacion')}
                      className={cn(
                        'p-2.5 rounded-lg border text-xs font-semibold flex items-center justify-center gap-1.5 cursor-pointer',
                        paymentTarget === 'habitacion'
                          ? 'border-forest-800 bg-forest-50 text-forest-900 ring-1 ring-forest-800'
                          : 'border-sand-300 bg-white text-ink-soft'
                      )}
                    >
                      <BedDouble size={14} />
                      Cargo a Habitación
                    </button>
                    <button
                      type="button"
                      onClick={() => setPaymentTarget('efectivo')}
                      className={cn(
                        'p-2.5 rounded-lg border text-xs font-semibold flex items-center justify-center gap-1.5 cursor-pointer',
                        paymentTarget === 'efectivo'
                          ? 'border-forest-800 bg-forest-50 text-forest-900 ring-1 ring-forest-800'
                          : 'border-sand-300 bg-white text-ink-soft'
                      )}
                    >
                      <Banknote size={14} />
                      Pago Inmediato
                    </button>
                  </div>

                  {paymentTarget === 'habitacion' && (
                    <div>
                      <label className="text-xs font-medium text-ink block mb-1">
                        Cargar a huésped en casa:
                      </label>
                      <Select
                        value={targetRoom}
                        onChange={setTargetRoom}
                        options={occupiedRooms.map((r) => ({
                          value: r.number,
                          label: `Hab. ${r.number} (${r.guest || r.name})`,
                        }))}
                      />
                    </div>
                  )}

                  <Button
                    variant="terra"
                    className="w-full mt-2"
                    onClick={handleCheckout}
                  >
                    Confirmar {paymentTarget === 'habitacion' ? 'Cargo a Habitación' : 'Cobro'}
                  </Button>
                </div>
              </div>
            )}
          </Card>
        </div>
      </div>

      {node}
    </div>
  );
}
