import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { apiClient, downloadAuthorizedFile, getApiBaseUrl } from './api/client';
import { RoomStatusKey, BookingStatusKey } from './ui';

export interface RoomItem {
  id: number;
  number: string;
  name: string;
  type: string;
  capacity: number;
  baseAdultsCapacity: number;
  maxAdultsCapacity: number;
  childrenCapacity: number;
  allowsPets: boolean;
  status: RoomStatusKey;
  rate: number;
  extraRate: number;
  guest?: string;
  until?: string;
  next?: string;
  note?: string;
  active?: boolean;
}

export interface BookingItem {
  id?: number;
  code: string;
  reservationGroupId?: string;
  guest: string;
  guestId?: number;
  room: string;
  roomId?: number;
  checkIn: string;
  checkOut: string;
  guests: number;
  adults?: number;
  children?: number;
  hasPet?: boolean;
  status: BookingStatusKey;
  channel: 'WhatsApp' | 'Recepción' | 'Teléfono' | 'Web';
  phone: string;
  total: number;
  paid: number;
  doc?: string;
  note?: string;
}

export interface ProductItem {
  id: string;
  numericId?: number;
  name: string;
  price: number;
  stock: number;
  category: string;
}

export interface MenuItem {
  id: string | number;
  code?: string;
  name: string;
  category: 'breakfast' | 'coffee' | 'bakery' | 'beverage' | 'experience';
  price: number;
  description?: string;
  available: boolean;
}

export interface RestaurantOrder {
  id: string;
  roomNumber?: string;
  tableNumber?: string;
  guestName?: string;
  items: { menuItemId?: string | number; name: string; qty: number; price: number }[];
  total: number;
  status: 'pending' | 'preparing' | 'delivered' | 'paid' | 'charged_to_room' | 'cancelled';
  createdAt: string;
}

export interface SpecialEventItem {
  id: number | string;
  name: string;
  description?: string;
  startDate: string;
  endDate: string;
  discountPercentage: number;
  active: boolean;
}

export interface ExpenseItem {
  id: string;
  numericId?: number;
  date: string;
  amount: number;
  category: string;
  desc: string;
  voided?: boolean;
}

export interface FinanceSummary {
  totalIncome: number;
  lodgingIncome: number;
  chargesIncome: number;
  totalExpenses: number;
  netBalance: number;
  channels: { channel: string; bookings: number; income: number; pct: string }[];
}

export interface AuditItem {
  id?: number;
  at: string;
  user: string;
  role: string;
  action: string;
  module: string;
}

export interface UserItem {
  id: string | number;
  username: string;
  name: string;
  role: string;
  active: boolean;
  last: string;
}

export interface ConversationMessage {
  from: string;
  author: string;
  text: string;
  sentAt: string;
  dispatched?: boolean;
}

export interface ConversationItem {
  id: number;
  waId: string;
  guestName: string;
  guestPhone: string;
  status: 'escalated' | 'active';
  step: string;
  state: string;
  agentActive: boolean;
  messages?: ConversationMessage[];
  updatedAt?: string;
}

export interface ChargeItem {
  id?: number;
  bookingId?: number;
  roomId?: number;
  roomNumber?: string;
  desc: string;
  qty: number;
  amount: number;
  paid?: boolean;
  source?: 'tienda' | 'restaurante';
}

export interface UserSession {
  id: string;
  username: string;
  name: string;
  email: string;
  role: 'recepcion' | 'admin';
  avatarUrl?: string;
  lastLogin?: string;
}

export interface ActionResult {
  success: boolean;
  message?: string;
  data?: unknown;
}

const DB_ROOM_STATUS_TO_UI: Record<string, RoomStatusKey> = {
  available: 'libre',
  occupied: 'ocupada',
  cleaning: 'limpieza',
  maintenance: 'mantenimiento',
};

const UI_ROOM_STATUS_TO_DB: Record<RoomStatusKey, string> = {
  libre: 'available',
  ocupada: 'occupied',
  limpieza: 'cleaning',
  mantenimiento: 'maintenance',
  bloqueada: 'available',
};

const DB_BOOKING_STATUS_TO_UI: Record<string, BookingStatusKey> = {
  CONFIRMADA: 'confirmada',
  confirmed: 'confirmada',
  BLOQUEADA_TEMPORAL: 'bloqueada',
  PENDIENTE_PAGO: 'pendiente',
  pending_payment: 'pendiente',
  EN_CURSO: 'enCurso',
  occupied: 'enCurso',
  EXPIRADA: 'cancelada',
  CANCELADA: 'cancelada',
  cancelled: 'cancelada',
  finished: 'finalizada',
};

interface StoreContextType {
  role: 'recepcion' | 'admin';
  currentUser: UserSession | null;
  login: (username: string, pass: string) => Promise<{ success: boolean; role?: 'recepcion' | 'admin'; message?: string }>;
  logout: () => void;
  updateUserProfile: (data: Partial<UserSession>) => void;
  changePassword: (currentPass: string, newPass: string) => Promise<{ success: boolean; message: string }>;
  rooms: RoomItem[];
  bookings: BookingItem[];
  charges: Record<string, ChargeItem[]>;
  products: ProductItem[];
  menu: MenuItem[];
  orders: RestaurantOrder[];
  events: SpecialEventItem[];
  expenses: ExpenseItem[];
  financeSummary: FinanceSummary | null;
  audit: AuditItem[];
  users: UserItem[];
  conversations: ConversationItem[];
  log: (action: string, module: string) => void;
  // Room Actions
  setRoomStatus: (id: string | number, status: RoomStatusKey) => Promise<ActionResult>;
  addRoom: (room: Omit<RoomItem, 'id'>) => Promise<ActionResult>;
  updateRoom: (id: string | number, data: Partial<RoomItem>) => Promise<ActionResult>;
  deleteRoom: (id: string | number) => Promise<ActionResult>;
  // Booking Actions
  setBookingStatus: (code: string, status: BookingStatusKey) => Promise<ActionResult>;
  addBooking: (payload: {
    roomId: number;
    checkIn: string;
    checkOut: string;
    adults: number;
    children?: number;
    hasPet?: boolean;
    guestName: string;
    phone: string;
    doc?: string;
    paymentOption?: 'full' | 'half' | 'none';
    source?: string;
  }) => Promise<ActionResult>;
  payRemainingBooking: (code: string) => Promise<ActionResult>;
  // Store & Folio Actions
  sell: (cart: { id: string; qty: number }[], chargeToRoom: boolean, roomNumber?: string) => Promise<ActionResult>;
  addProduct: (payload: { name: string; category: string; price: number; stock: number }) => Promise<ActionResult>;
  updateProduct: (id: string, payload: { name: string; category: string; price: number; stock: number }) => Promise<ActionResult>;
  deleteProduct: (id: string) => Promise<ActionResult>;
  // Restaurant Actions
  addRestaurantOrder: (order: {
    roomNumber?: string;
    tableNumber?: string;
    guestName?: string;
    items: { menuItemId?: string | number; name: string; qty: number; price: number }[];
    status: RestaurantOrder['status'];
  }) => Promise<ActionResult>;
  updateOrderStatus: (id: string, status: RestaurantOrder['status']) => Promise<ActionResult>;
  // Events Actions
  addEvent: (event: Omit<SpecialEventItem, 'id'>) => Promise<ActionResult>;
  toggleEventActive: (id: number | string) => Promise<ActionResult>;
  // Expenses, Users, Reports & Chatbot Actions
  addExpense: (expense: Omit<ExpenseItem, 'id'>) => Promise<ActionResult>;
  voidExpense: (id: string) => Promise<ActionResult>;
  createUser: (payload: { username: string; name: string; password: string; role: string }) => Promise<ActionResult>;
  toggleUserActive: (id: string | number, currentActive: boolean) => Promise<ActionResult>;
  escalateConversation: (id: number) => Promise<ActionResult>;
  toggleConversationBot: (id: number, botActive?: boolean) => Promise<ActionResult>;
  sendConversationMessage: (id: number, text: string) => Promise<ActionResult>;
  exportExcelReport: () => Promise<ActionResult>;
  refreshBackendData: () => Promise<void>;
}

const StoreContext = createContext<StoreContextType | null>(null);

export function StoreProvider({ children }: { children: React.ReactNode }) {
  const [currentUser, setCurrentUser] = useState<UserSession | null>(() => {
    try {
      const saved = localStorage.getItem('satori_auth_user');
      const token = localStorage.getItem('token');
      return saved && token ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });

  const role: 'recepcion' | 'admin' = currentUser?.role ?? 'recepcion';

  const [rooms, setRooms] = useState<RoomItem[]>([]);
  const [bookings, setBookings] = useState<BookingItem[]>([]);
  const [charges, setCharges] = useState<Record<string, ChargeItem[]>>({});
  const [products, setProducts] = useState<ProductItem[]>([]);
  const [menu, setMenu] = useState<MenuItem[]>([]);
  const [orders, setOrders] = useState<RestaurantOrder[]>([]);
  const [events, setEvents] = useState<SpecialEventItem[]>([]);
  const [expenses, setExpenses] = useState<ExpenseItem[]>([]);
  const [financeSummary, setFinanceSummary] = useState<FinanceSummary | null>(null);
  const [users, setUsers] = useState<UserItem[]>([]);
  const [audit, setAudit] = useState<AuditItem[]>([]);
  const [conversations, setConversations] = useState<ConversationItem[]>([]);

  const logout = useCallback(() => {
    setCurrentUser(null);
    setRooms([]);
    setBookings([]);
    setCharges({});
    setProducts([]);
    setMenu([]);
    setOrders([]);
    setEvents([]);
    setExpenses([]);
    setFinanceSummary(null);
    setUsers([]);
    setAudit([]);
    setConversations([]);
    localStorage.removeItem('token');
    localStorage.removeItem('satori_auth_user');
  }, []);

  const refreshBackendData = useCallback(async () => {
    const token = localStorage.getItem('token');
    if (!token) return;

    try {
      const meRes = await apiClient.get<{ id: number; username: string; role: string; name: string }>('/api/v1/auth/me');
      const uiRole: 'admin' | 'recepcion' = meRes.data.role === 'Administrador' ? 'admin' : 'recepcion';
      const activeUser: UserSession = {
        id: String(meRes.data.id),
        username: meRes.data.username,
        name: meRes.data.name,
        email: `${meRes.data.username}@torresatori.co`,
        role: uiRole,
        avatarUrl: currentUser?.avatarUrl,
      };
      setCurrentUser(activeUser);
      localStorage.setItem('satori_auth_user', JSON.stringify(activeUser));

      const [roomsRes, bookingsRes, prodRes, menuRes, ordersRes, eventsRes, chargesRes, convRes] = await Promise.all([
        apiClient.get<any[]>('/api/v1/rooms'),
        apiClient.get<any[]>('/api/v1/bookings'),
        apiClient.get<any[]>('/api/v1/store/products'),
        apiClient.get<any[]>('/api/v1/restaurant/menu'),
        apiClient.get<any[]>('/api/v1/restaurant/orders'),
        apiClient.get<any[]>('/api/v1/events'),
        apiClient.get<any[]>('/api/v1/folio-charges'),
        apiClient.get<any[]>('/api/v1/conversations'),
      ]);

      const mappedBookings: BookingItem[] = (bookingsRes.data || []).map((b) => ({
        id: b.id,
        code: b.bookingCode || `TS-${b.id}`,
        reservationGroupId: b.reservationGroupId,
        guest: b.guestName || 'Huésped Torre Satori',
        guestId: b.guestId,
        room: b.roomNumber || String(b.roomId || ''),
        roomId: b.roomId,
        checkIn: b.checkIn,
        checkOut: b.checkOut,
        guests: (b.adults || 1) + (b.children || 0),
        adults: b.adults,
        children: b.children,
        hasPet: b.withPet,
        status: b.paymentStatus === 'paid' && b.status === 'EN_CURSO' ? 'enCurso' : (DB_BOOKING_STATUS_TO_UI[b.status] || 'confirmada'),
        channel: b.source === 'chatbot' ? 'WhatsApp' : 'Recepción',
        phone: b.guestPhone || '',
        doc: b.guestDocument || '',
        total: Number(b.totalPrice) || 0,
        paid: Number(b.paidAmount) || 0,
      }));
      setBookings(mappedBookings);

      const mappedRooms: RoomItem[] = (roomsRes.data || []).map((r) => {
        const activeInHouse = mappedBookings.find((b) => b.roomId === r.id && b.status === 'enCurso');
        const activeLock = mappedBookings.find((b) => b.roomId === r.id && b.status === 'bloqueada');
        const upcoming = mappedBookings.find((b) => b.roomId === r.id && b.status === 'confirmada');
        let uiStatus: RoomStatusKey = DB_ROOM_STATUS_TO_UI[r.status] || 'libre';
        if (uiStatus === 'libre' && activeLock) {
          uiStatus = 'bloqueada';
        }
        return {
          id: r.id,
          number: r.number,
          name: r.name,
          type: r.type,
          capacity: r.maxAdultsCapacity || 2,
          baseAdultsCapacity: r.baseAdultsCapacity || 2,
          maxAdultsCapacity: r.maxAdultsCapacity || 2,
          childrenCapacity: r.childrenCapacity || 0,
          allowsPets: Boolean(r.allowsPets),
          status: uiStatus,
          rate: Number(r.pricePerNight) || 0,
          extraRate: Number(r.extraGuestPrice) || 0,
          guest: activeInHouse?.guest,
          until: activeInHouse ? `Sale ${activeInHouse.checkOut}, 11:00` : undefined,
          next: upcoming ? `${upcoming.guest} · ${upcoming.checkIn}` : undefined,
          note: activeLock ? `Bloqueo activo de ${activeLock.guest}` : undefined,
          active: r.active,
        };
      });
      setRooms(mappedRooms);

      setProducts(
        (prodRes.data || []).map((p) => ({
          id: p.code || String(p.id),
          numericId: p.numericId,
          name: p.name,
          price: Number(p.price),
          stock: Number(p.stock),
          category: p.category,
        }))
      );
      setMenu(menuRes.data || []);
      setOrders(ordersRes.data || []);
      setEvents(eventsRes.data || []);
      setConversations(convRes.data || []);

      const groupedCharges: Record<string, ChargeItem[]> = {};
      (chargesRes.data || []).forEach((c) => {
        if (c.paid || !c.roomNumber) return;
        if (!groupedCharges[c.roomNumber]) groupedCharges[c.roomNumber] = [];
        groupedCharges[c.roomNumber].push({
          id: c.id,
          bookingId: c.bookingId,
          roomId: c.roomId,
          roomNumber: c.roomNumber,
          desc: c.desc,
          qty: c.qty,
          amount: Number(c.amount),
          paid: c.paid,
          source: c.source,
        });
      });
      setCharges(groupedCharges);

      if (uiRole === 'admin') {
        const [expRes, finRes, usrRes, auditRes] = await Promise.all([
          apiClient.get<ExpenseItem[]>('/api/v1/expenses'),
          apiClient.get<FinanceSummary>('/api/v1/finance/summary'),
          apiClient.get<any[]>('/api/v1/auth/users'),
          apiClient.get<any[]>('/api/v1/auth/audit-logs'),
        ]);
        setExpenses(expRes.data || []);
        setFinanceSummary(finRes.data || null);
        setUsers(
          (usrRes.data || []).map((u) => ({
            id: u.id,
            username: u.username,
            name: u.name,
            role: u.role,
            active: u.active,
            last: u.createdAt ? new Date(u.createdAt).toLocaleDateString('es-CO') : '—',
          }))
        );
        setAudit(
          (auditRes.data || []).map((a) => ({
            id: a.id,
            at: a.timestamp ? new Date(a.timestamp).toLocaleString('es-CO') : '',
            user: a.actor_username,
            role: 'Sistema',
            action: `${a.action}${a.entity_id ? ` (${a.entity_id})` : ''}`,
            module: a.entity,
          }))
        );
      }
    } catch {
      // Mantiene estado actual en fallos transitorios; 401 se gestiona por evento
    }
  }, [currentUser?.avatarUrl]);

  useEffect(() => {
    const onUnauth = () => logout();
    window.addEventListener('satori:unauthorized', onUnauth);
    return () => window.removeEventListener('satori:unauthorized', onUnauth);
  }, [logout]);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) return;

    refreshBackendData();

    const sseUrl = new URL('/api/v1/events/stream', getApiBaseUrl());
    sseUrl.searchParams.set('token', token);
    let source: EventSource | null = null;
    try {
      source = new EventSource(sseUrl.toString());
      const reloadHandler = () => {
        refreshBackendData();
      };
      ['booking.locked', 'booking.unlocked', 'booking.confirmed', 'booking.cancelled', 'booking.expired', 'booking.checkin', 'booking.checkout', 'room.status', 'store.sale', 'restaurant.order_created'].forEach((evName) => {
        source?.addEventListener(evName, reloadHandler);
      });
    } catch {
      // Fallback a polling si el navegador bloquea EventSource
    }

    const interval = setInterval(refreshBackendData, 15000);
    return () => {
      source?.close();
      clearInterval(interval);
    };
  }, [currentUser?.username, refreshBackendData]);

  const login = async (username: string, pass: string) => {
    try {
      const cleanUser = username.trim().split('@')[0];
      const res = await apiClient.post<{
        access_token: string;
        username: string;
        role: string;
        name: string;
      }>('/api/v1/auth/login', { username: cleanUser, password: pass });

      localStorage.setItem('token', res.data.access_token);
      const uiRole: 'admin' | 'recepcion' = res.data.role === 'Administrador' ? 'admin' : 'recepcion';
      const sessionUser: UserSession = {
        id: res.data.username,
        username: res.data.username,
        name: res.data.name,
        email: `${res.data.username}@torresatori.co`,
        role: uiRole,
        lastLogin: new Date().toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' }),
      };
      localStorage.setItem('satori_auth_user', JSON.stringify(sessionUser));
      setCurrentUser(sessionUser);
      await refreshBackendData();
      return { success: true, role: uiRole };
    } catch (err) {
      return {
        success: false,
        message: err instanceof Error ? err.message : 'Credenciales inválidas',
      };
    }
  };

  const updateUserProfile = (data: Partial<UserSession>) => {
    if (!currentUser) return;
    const updated = { ...currentUser, ...data };
    setCurrentUser(updated);
    localStorage.setItem('satori_auth_user', JSON.stringify(updated));
  };

  const changePassword = async (currentPass: string, newPass: string) => {
    if (!newPass || newPass.trim().length < 6) {
      return { success: false, message: 'La nueva contraseña debe tener mínimo 6 caracteres.' };
    }
    try {
      const res = await apiClient.post<{ message: string }>('/api/v1/auth/change-password', {
        current_password: currentPass,
        new_password: newPass.trim(),
      });
      return { success: true, message: res.data.message };
    } catch (err) {
      return { success: false, message: err instanceof Error ? err.message : 'No se pudo cambiar la contraseña' };
    }
  };

  const log = (_action: string, _module: string) => {
    // La auditoría oficial se registra de forma inmutable en PostgreSQL desde FastAPI
  };

  const setRoomStatus = async (id: string | number, status: RoomStatusKey): Promise<ActionResult> => {
    try {
      await apiClient.patch(`/api/v1/rooms/${id}/status`, {
        status: UI_ROOM_STATUS_TO_DB[status] || 'available',
      });
      await refreshBackendData();
      return { success: true };
    } catch (err) {
      return { success: false, message: err instanceof Error ? err.message : 'Error al actualizar estado' };
    }
  };

  const addRoom = async (roomData: Omit<RoomItem, 'id'>): Promise<ActionResult> => {
    try {
      await apiClient.post('/api/v1/rooms', {
        number: roomData.number,
        name: roomData.name,
        type: roomData.type,
        baseAdultsCapacity: roomData.baseAdultsCapacity,
        maxAdultsCapacity: roomData.maxAdultsCapacity,
        childrenCapacity: roomData.childrenCapacity,
        pricePerNight: roomData.rate,
        extraGuestPrice: roomData.extraRate,
        allowsPets: roomData.allowsPets,
      });
      await refreshBackendData();
      return { success: true };
    } catch (err) {
      return { success: false, message: err instanceof Error ? err.message : 'Error al crear habitación' };
    }
  };

  const updateRoom = async (id: string | number, data: Partial<RoomItem>): Promise<ActionResult> => {
    try {
      await apiClient.put(`/api/v1/rooms/${id}`, {
        ...(data.number !== undefined ? { number: data.number } : {}),
        ...(data.name !== undefined ? { name: data.name } : {}),
        ...(data.type !== undefined ? { type: data.type } : {}),
        ...(data.baseAdultsCapacity !== undefined ? { baseAdultsCapacity: data.baseAdultsCapacity } : {}),
        ...(data.maxAdultsCapacity !== undefined ? { maxAdultsCapacity: data.maxAdultsCapacity } : {}),
        ...(data.childrenCapacity !== undefined ? { childrenCapacity: data.childrenCapacity } : {}),
        ...(data.rate !== undefined ? { pricePerNight: data.rate } : {}),
        ...(data.extraRate !== undefined ? { extraGuestPrice: data.extraRate } : {}),
        ...(data.allowsPets !== undefined ? { allowsPets: data.allowsPets } : {}),
      });
      await refreshBackendData();
      return { success: true };
    } catch (err) {
      return { success: false, message: err instanceof Error ? err.message : 'Error al actualizar habitación' };
    }
  };

  const deleteRoom = async (id: string | number): Promise<ActionResult> => {
    try {
      await apiClient.delete(`/api/v1/rooms/${id}`);
      await refreshBackendData();
      return { success: true };
    } catch (err) {
      return { success: false, message: err instanceof Error ? err.message : 'No se puede eliminar la habitación' };
    }
  };

  const setBookingStatus = async (code: string, status: BookingStatusKey): Promise<ActionResult> => {
    try {
      if (status === 'enCurso') {
        await apiClient.post(`/api/v1/bookings/${encodeURIComponent(code)}/check-in`);
      } else if (status === 'finalizada') {
        await apiClient.post(`/api/v1/bookings/${encodeURIComponent(code)}/check-out`);
      } else if (status === 'cancelada') {
        await apiClient.post(`/api/v1/bookings/group/${encodeURIComponent(code)}/cancellation`);
      }
      await refreshBackendData();
      return { success: true };
    } catch (err) {
      return { success: false, message: err instanceof Error ? err.message : 'Error actualizando reserva' };
    }
  };

  const addBooking = async (payload: {
    roomId: number;
    checkIn: string;
    checkOut: string;
    adults: number;
    children?: number;
    hasPet?: boolean;
    guestName: string;
    phone: string;
    doc?: string;
    paymentOption?: 'full' | 'half' | 'none';
    source?: string;
  }): Promise<ActionResult> => {
    try {
      const res = await apiClient.post<{ code: string }>('/api/v1/bookings/manual', {
        rooms: [{ roomId: payload.roomId, checkIn: payload.checkIn, checkOut: payload.checkOut }],
        adults: payload.adults,
        children: payload.children || 0,
        hasPet: Boolean(payload.hasPet),
        guest: {
          name: payload.guestName,
          phone: payload.phone,
          documentNumber: payload.doc || '',
        },
        source: payload.source || 'web',
      });
      await refreshBackendData();
      return { success: true, data: res.data };
    } catch (err) {
      return { success: false, message: err instanceof Error ? err.message : 'Conflicto al crear reserva' };
    }
  };

  const payRemainingBooking = async (code: string): Promise<ActionResult> => {
    try {
      await apiClient.post(`/api/v1/bookings/group/${encodeURIComponent(code)}/pay-remaining`);
      await refreshBackendData();
      return { success: true };
    } catch (err) {
      return { success: false, message: err instanceof Error ? err.message : 'Error registrando pago' };
    }
  };

  const sell = async (
    cart: { id: string; qty: number }[],
    chargeToRoom: boolean,
    roomNumber?: string
  ): Promise<ActionResult> => {
    try {
      await apiClient.post('/api/v1/store/sales', {
        items: cart.map((c) => ({ productId: c.id, qty: c.qty })),
        chargeToRoom,
        roomNumber,
      });
      await refreshBackendData();
      return { success: true };
    } catch (err) {
      return { success: false, message: err instanceof Error ? err.message : 'Error registrando venta' };
    }
  };

  const addProduct = async (payload: {
    name: string;
    category: string;
    price: number;
    stock: number;
  }): Promise<ActionResult> => {
    try {
      await apiClient.post('/api/v1/store/products', payload);
      await refreshBackendData();
      return { success: true };
    } catch (err) {
      return { success: false, message: err instanceof Error ? err.message : 'Error creando producto' };
    }
  };

  const updateProduct = async (
    id: string,
    payload: { name: string; category: string; price: number; stock: number }
  ): Promise<ActionResult> => {
    try {
      await apiClient.put(`/api/v1/store/products/${encodeURIComponent(id)}`, payload);
      await refreshBackendData();
      return { success: true };
    } catch (err) {
      return { success: false, message: err instanceof Error ? err.message : 'Error actualizando producto' };
    }
  };

  const deleteProduct = async (id: string): Promise<ActionResult> => {
    try {
      await apiClient.delete(`/api/v1/store/products/${encodeURIComponent(id)}`);
      await refreshBackendData();
      return { success: true };
    } catch (err) {
      return { success: false, message: err instanceof Error ? err.message : 'Error eliminando producto' };
    }
  };

  const addRestaurantOrder = async (orderData: {
    roomNumber?: string;
    tableNumber?: string;
    guestName?: string;
    items: { menuItemId?: string | number; name: string; qty: number; price: number }[];
    status: RestaurantOrder['status'];
  }): Promise<ActionResult> => {
    try {
      await apiClient.post('/api/v1/restaurant/orders', orderData);
      await refreshBackendData();
      return { success: true };
    } catch (err) {
      return { success: false, message: err instanceof Error ? err.message : 'Error creando comanda' };
    }
  };

  const updateOrderStatus = async (id: string, status: RestaurantOrder['status']): Promise<ActionResult> => {
    try {
      await apiClient.patch(`/api/v1/restaurant/orders/${encodeURIComponent(id)}/status`, { status });
      await refreshBackendData();
      return { success: true };
    } catch (err) {
      return { success: false, message: err instanceof Error ? err.message : 'Error actualizando comanda' };
    }
  };

  const addEvent = async (eventData: Omit<SpecialEventItem, 'id'>): Promise<ActionResult> => {
    try {
      await apiClient.post('/api/v1/events', eventData);
      await refreshBackendData();
      return { success: true };
    } catch (err) {
      return { success: false, message: err instanceof Error ? err.message : 'Error creando evento' };
    }
  };

  const toggleEventActive = async (id: number | string): Promise<ActionResult> => {
    try {
      await apiClient.patch(`/api/v1/events/${id}/toggle`);
      await refreshBackendData();
      return { success: true };
    } catch (err) {
      return { success: false, message: err instanceof Error ? err.message : 'Error cambiando estado del evento' };
    }
  };

  const addExpense = async (expenseData: Omit<ExpenseItem, 'id'>): Promise<ActionResult> => {
    try {
      await apiClient.post('/api/v1/expenses', expenseData);
      await refreshBackendData();
      return { success: true };
    } catch (err) {
      return { success: false, message: err instanceof Error ? err.message : 'Error registrando egreso' };
    }
  };

  const voidExpense = async (id: string): Promise<ActionResult> => {
    try {
      await apiClient.post(`/api/v1/expenses/${id}/void`, {});
      await refreshBackendData();
      return { success: true };
    } catch (err) {
      return { success: false, message: err instanceof Error ? err.message : 'Error anulando egreso' };
    }
  };

  const createUser = async (payload: {
    username: string;
    name: string;
    password: string;
    role: string;
  }): Promise<ActionResult> => {
    try {
      await apiClient.post('/api/v1/auth/users', payload);
      await refreshBackendData();
      return { success: true };
    } catch (err) {
      return { success: false, message: err instanceof Error ? err.message : 'Error creando usuario' };
    }
  };

  const toggleUserActive = async (id: string | number, currentActive: boolean): Promise<ActionResult> => {
    try {
      await apiClient.patch(`/api/v1/auth/users/${id}`, { active: !currentActive });
      await refreshBackendData();
      return { success: true };
    } catch (err) {
      return { success: false, message: err instanceof Error ? err.message : 'Error actualizando usuario' };
    }
  };

  const escalateConversation = async (id: number): Promise<ActionResult> => {
    try {
      await apiClient.post(`/api/v1/conversations/${id}/escalation`, {});
      await refreshBackendData();
      return { success: true };
    } catch (err) {
      return { success: false, message: err instanceof Error ? err.message : 'Error escalando conversación' };
    }
  };

  const toggleConversationBot = async (id: number, botActive?: boolean): Promise<ActionResult> => {
    try {
      await apiClient.post(
        `/api/v1/conversations/${id}/toggle-bot`,
        botActive === undefined ? {} : { bot_active: botActive }
      );
      await refreshBackendData();
      return { success: true };
    } catch (err) {
      return { success: false, message: err instanceof Error ? err.message : 'Error cambiando modo del bot' };
    }
  };

  const sendConversationMessage = async (id: number, text: string): Promise<ActionResult> => {
    try {
      const res = await apiClient.post(`/api/v1/conversations/${id}/messages`, { text });
      await refreshBackendData();
      return { success: true, data: res.data };
    } catch (err) {
      return { success: false, message: err instanceof Error ? err.message : 'Error enviando mensaje manual' };
    }
  };

  const exportExcelReport = async (): Promise<ActionResult> => {
    try {
      await downloadAuthorizedFile('/api/v1/reports/export.xlsx', 'Reporte_TorreSatori.xlsx');
      return { success: true };
    } catch (err) {
      return { success: false, message: err instanceof Error ? err.message : 'Error exportando Excel' };
    }
  };

  return (
    <StoreContext.Provider
      value={{
        role,
        currentUser,
        login,
        logout,
        updateUserProfile,
        changePassword,
        rooms,
        bookings,
        charges,
        products,
        menu,
        orders,
        events,
        expenses,
        financeSummary,
        audit,
        users,
        conversations,
        log,
        setRoomStatus,
        addRoom,
        updateRoom,
        deleteRoom,
        setBookingStatus,
        addBooking,
        payRemainingBooking,
        sell,
        addProduct,
        updateProduct,
        deleteProduct,
        addRestaurantOrder,
        updateOrderStatus,
        addEvent,
        toggleEventActive,
        addExpense,
        voidExpense,
        createUser,
        toggleUserActive,
        escalateConversation,
        toggleConversationBot,
        sendConversationMessage,
        exportExcelReport,
        refreshBackendData,
      }}
    >
      {children}
    </StoreContext.Provider>
  );
}

export function useStore() {
  const ctx = useContext(StoreContext);
  if (!ctx) throw new Error('useStore must be used within a StoreProvider');
  return ctx;
}
