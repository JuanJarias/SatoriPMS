import React, { createContext, useContext, useState, useEffect } from 'react';
import { RoomStatusKey, BookingStatusKey } from './ui';

export interface RoomItem {
  id: string | number;
  number: string;
  name: string;
  type: string;
  capacity: number;
  baseAdultsCapacity?: number;
  maxAdultsCapacity?: number;
  childrenCapacity?: number;
  allowsPets?: boolean;
  status: RoomStatusKey;
  rate: number;
  extraRate?: number;
  guest?: string;
  until?: string;
  next?: string;
  note?: string;
  active?: boolean;
}

export interface BookingItem {
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
  name: string;
  price: number;
  stock: number;
  category: string;
}

export interface MenuItem {
  id: string | number;
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
  items: { menuItemId: string | number; name: string; qty: number; price: number }[];
  total: number;
  status: 'pending' | 'preparing' | 'delivered' | 'paid' | 'charged_to_room';
  createdAt: string;
}

export interface SpecialEventItem {
  id: string | number;
  name: string;
  description?: string;
  startDate: string;
  endDate: string;
  discountPercentage: number; // >0 descuento, <0 recargo
  active: boolean;
}

export interface ExpenseItem {
  id: string;
  date: string;
  amount: number;
  category: string;
  desc: string;
  voided?: boolean;
}

export interface AuditItem {
  at: string;
  user: string;
  role: string;
  action: string;
  module: string;
}

export interface UserItem {
  id: string;
  name: string;
  email: string;
  phone: string;
  role: string;
  active: boolean;
  last: string;
}

export interface ChargeItem {
  desc: string;
  qty: number;
  amount: number;
  source?: 'tienda' | 'restaurante';
}

const INITIAL_ROOMS: RoomItem[] = [
  { id: '101', number: '101', name: 'Jardín', type: 'Sencilla', capacity: 2, baseAdultsCapacity: 2, maxAdultsCapacity: 2, childrenCapacity: 0, allowsPets: true, status: 'ocupada', guest: 'Laura Gómez', until: 'Sale vie 2 oct, 11:00', next: 'Sin reservas próximas', rate: 180000, extraRate: 40000, active: true },
  { id: '102', number: '102', name: 'Familiar', type: 'Familiar', capacity: 5, baseAdultsCapacity: 4, maxAdultsCapacity: 5, childrenCapacity: 1, allowsPets: false, status: 'libre', next: 'Andrés Martínez · hoy 3:00 pm', rate: 290000, extraRate: 40000, active: true },
  { id: '103', number: '103', name: 'Patio', type: 'Sencilla', capacity: 2, baseAdultsCapacity: 2, maxAdultsCapacity: 2, childrenCapacity: 0, allowsPets: true, status: 'mantenimiento', note: 'Reparación de ducha · listo el sáb 3 oct', next: 'Camilo Herrera · dom 4 oct', rate: 170000, extraRate: 40000, active: true },
  { id: '201', number: '201', name: 'Balcón', type: 'Doble', capacity: 3, baseAdultsCapacity: 2, maxAdultsCapacity: 3, childrenCapacity: 1, allowsPets: false, status: 'limpieza', note: 'Aseo de salida iniciado 10:50 am', next: 'Camilo Herrera · sáb 3 oct', rate: 210000, extraRate: 40000, active: true },
  { id: '202', number: '202', name: 'Suite Satori', type: 'Suite', capacity: 4, baseAdultsCapacity: 2, maxAdultsCapacity: 4, childrenCapacity: 2, allowsPets: true, status: 'bloqueada', note: 'Bloqueo de María Fernanda Rojas · vence hoy 6:00 pm', next: 'Pendiente de anticipo', rate: 380000, extraRate: 40000, active: true },
  { id: '203', number: '203', name: 'Cafetal', type: 'Doble', capacity: 3, baseAdultsCapacity: 2, maxAdultsCapacity: 3, childrenCapacity: 1, allowsPets: false, status: 'libre', next: 'Sin reservas inmediatas', rate: 220000, extraRate: 40000, active: true },
  { id: '301', number: '301', name: 'Mirador del Valle', type: 'Suite', capacity: 4, baseAdultsCapacity: 2, maxAdultsCapacity: 4, childrenCapacity: 1, allowsPets: false, status: 'libre', next: 'Disponible fin de semana', rate: 350000, extraRate: 50000, active: true },
  { id: '302', number: '302', name: 'Atardecer', type: 'Doble', capacity: 2, baseAdultsCapacity: 2, maxAdultsCapacity: 2, childrenCapacity: 0, allowsPets: false, status: 'libre', next: 'Disponible', rate: 200000, extraRate: 40000, active: true },
  { id: '303', number: '303', name: 'Cordillera', type: 'Familiar', capacity: 6, baseAdultsCapacity: 4, maxAdultsCapacity: 6, childrenCapacity: 2, allowsPets: true, status: 'libre', next: 'Disponible', rate: 320000, extraRate: 45000, active: true },
];

const INITIAL_BOOKINGS: BookingItem[] = [
  { code: 'TS-2391', guest: 'Maria', room: '103', checkIn: '2026-10-03', checkOut: '2026-10-08', guests: 2, status: 'confirmada', channel: 'Recepción', phone: '+57 300 222 2222', total: 850000, paid: 850000, doc: '222222', note: 'Reserva registrada en recepción para Habitación 103 Patio.' },
  { code: 'TS-2041', guest: 'Laura Gómez', room: '101', checkIn: '2026-09-29', checkOut: '2026-10-02', guests: 2, status: 'enCurso', channel: 'WhatsApp', phone: '+57 310 555 0142', total: 540000, paid: 540000, doc: 'CC 1.113.555.201', note: 'Viaja con mascota pequeña. Desayuno a las 8:00 am.' },
  { code: 'TS-2047', guest: 'Andrés Martínez', room: '102', checkIn: '2026-10-01', checkOut: '2026-10-04', guests: 4, status: 'confirmada', channel: 'WhatsApp', phone: '+57 315 555 0187', total: 870000, paid: 435000, doc: 'CC 94.333.712', note: 'Viaja con dos niños. Solicita cuna.' },
  { code: 'BL-0318', guest: 'María Fernanda Rojas', room: '202', checkIn: '2026-10-01', checkOut: '2026-10-03', guests: 2, status: 'bloqueada', channel: 'WhatsApp', phone: '+57 300 555 0164', total: 760000, paid: 0, note: 'Retención vence hoy 6:00 pm si no se recibe el anticipo del 50 %.' },
  { code: 'TS-2052', guest: 'Camilo Herrera', room: '201', checkIn: '2026-10-03', checkOut: '2026-10-05', guests: 3, status: 'pendiente', channel: 'Teléfono', phone: '+57 320 555 0119', total: 420000, paid: 100000, doc: 'CC 16.280.944' },
  { code: 'TS-2036', guest: 'María Fernanda Rojas', room: '201', checkIn: '2026-09-28', checkOut: '2026-10-01', guests: 2, status: 'finalizada', channel: 'Recepción', phone: '+57 300 555 0164', total: 630000, paid: 630000, doc: 'CC 66.812.430' },
  { code: 'TS-2033', guest: 'Laura Gómez', room: '202', checkIn: '2026-09-12', checkOut: '2026-09-14', guests: 2, status: 'finalizada', channel: 'WhatsApp', phone: '+57 310 555 0142', total: 760000, paid: 760000, doc: 'CC 1.113.555.201' },
  { code: 'TS-2029', guest: 'Andrés Martínez', room: '101', checkIn: '2026-09-20', checkOut: '2026-09-22', guests: 2, status: 'cancelada', channel: 'WhatsApp', phone: '+57 315 555 0187', total: 360000, paid: 0, note: 'Cancelada por el huésped con 5 días de anticipación.' },
];

const INITIAL_PRODUCTS: ProductItem[] = [
  { id: 'p1', name: 'Agua Cristal 600 ml', price: 3000, stock: 24, category: 'Bebidas' },
  { id: 'p2', name: 'Gaseosa Postobón 400 ml', price: 4000, stock: 12, category: 'Bebidas' },
  { id: 'p3', name: 'Cerveza Club Colombia', price: 7000, stock: 8, category: 'Bebidas' },
  { id: 'p4', name: 'Papas Margarita pollo', price: 3500, stock: 15, category: 'Snacks' },
  { id: 'p5', name: 'Chocolatina Jet', price: 2500, stock: 10, category: 'Snacks' },
  { id: 'p6', name: 'Salgados Café Origen Especial 250g', price: 25000, stock: 20, category: 'Café de Origen' },
  { id: 'p7', name: 'Salgados Café Drip Bag (Pack x 5)', price: 16000, stock: 18, category: 'Café de Origen' },
  { id: 'p8', name: 'Protector solar FPS 50', price: 28000, stock: 4, category: 'Cuidado personal' },
  { id: 'p9', name: 'Cepillo y crema dental', price: 6000, stock: 9, category: 'Cuidado personal' },
];

const INITIAL_MENU: MenuItem[] = [
  { id: 'm1', name: 'Desayuno Típico Vallecaucano', category: 'breakfast', price: 18000, description: 'Huevos al gusto, calentado o arepa con queso, fruta de temporada y café Salgados.', available: true },
  { id: 'm2', name: 'Desayuno Continental Satori', category: 'breakfast', price: 16000, description: 'Canasta de panes artesanales, mermelada de mora silvestre, mantequilla, huevos y jugo.', available: true },
  { id: 'm3', name: 'Café Espresso Salgados', category: 'coffee', price: 5000, description: 'Extracción 30ml de café especial tostión media-alta.', available: true },
  { id: 'm4', name: 'Café Filtrado V60 / Chemex', category: 'coffee', price: 9000, description: 'Método artesanal con notas a panela, cítricos y chocolate.', available: true },
  { id: 'm5', name: 'Cappuccino de la Casa', category: 'coffee', price: 7500, description: 'Espresso doble con leche texturizada al vapor y canela.', available: true },
  { id: 'm6', name: 'Cata Guiada & Barismo Salgados', category: 'experience', price: 45000, description: 'Recorrido sensorial por 3 variedades de café de origen Sevilla con barista profesional.', available: true },
  { id: 'm7', name: 'Tarta de Café y Arequipe', category: 'bakery', price: 8500, description: 'Porción individual con reducción de café Salgados.', available: true },
];

const INITIAL_EVENTS: SpecialEventItem[] = [
  { id: 'ev1', name: 'Temporada Festivales del Café (Sevilla)', description: 'Semana de la cultura cafetera con alta afluencia regional', startDate: '2026-10-10', endDate: '2026-10-18', discountPercentage: -15, active: true },
  { id: 'ev2', name: 'Promoción Escapada Entre Semana', description: 'Descuento especial para reservas de lunes a jueves', startDate: '2026-10-01', endDate: '2026-10-31', discountPercentage: 10, active: true },
  { id: 'ev3', name: 'Feria Navideña y Fin de Año', description: 'Temporada alta diciembre', startDate: '2026-12-15', endDate: '2027-01-10', discountPercentage: -20, active: true },
];

const INITIAL_EXPENSES: ExpenseItem[] = [
  { id: 'e1', date: '2026-09-03', amount: 1420000, category: 'Servicios públicos', desc: 'Energía y acueducto agosto' },
  { id: 'e2', date: '2026-09-05', amount: 2600000, category: 'Nómina', desc: 'Quincena recepción y aseo' },
  { id: 'e3', date: '2026-09-12', amount: 640000, category: 'Insumos', desc: 'Lavandería y productos de aseo' },
  { id: 'e4', date: '2026-09-15', amount: 2600000, category: 'Nómina', desc: 'Quincena recepción y aseo' },
  { id: 'e5', date: '2026-09-18', amount: 520000, category: 'Compra de tienda', desc: 'Reposición de bebidas y Salgados Café' },
  { id: 'e6', date: '2026-09-22', amount: 380000, category: 'Internet y telefonía', desc: 'Plan de fibra óptica' },
  { id: 'e7', date: '2026-09-30', amount: 185000, category: 'Mantenimiento', desc: 'Mantenimiento ducha Hab. 103' },
];

const INITIAL_USERS: UserItem[] = [
  { id: 'u1', name: 'Sofía Valencia', email: 'sofia.valencia@torresatori.co', phone: '+57 311 555 0120', role: 'Recepcionista', active: true, last: 'Hoy 7:58 am' },
  { id: 'u2', name: 'Camila Ortiz', email: 'camila.ortiz@torresatori.co', phone: '+57 312 555 0188', role: 'Recepcionista', active: true, last: 'Ayer 6:02 pm' },
  { id: 'u3', name: 'Frank Arias Salgado', email: 'gerencia@torresatori.co', phone: '+57 310 999 8888', role: 'Administrador', active: true, last: 'Hoy 8:30 am' },
];

export interface UserSession {
  id: string;
  name: string;
  email: string;
  role: 'recepcion' | 'admin';
  phone?: string;
  avatarUrl?: string;
  lastLogin?: string;
}

export const ROLE_PROFILES = {
  recepcion: { name: 'Sofía Valencia', label: 'Recepcionista', email: 'sofia.valencia@torresatori.co' },
  admin: { name: 'Frank Arias Salgado', label: 'Administrador', email: 'admin@gmail.com' },
};

interface StoreContextType {
  role: 'recepcion' | 'admin';
  setRole: (r: 'recepcion' | 'admin') => void;
  currentUser: UserSession | null;
  login: (userOrEmail: string, pass: string, roleHint?: 'recepcion' | 'admin') => { success: boolean; message?: string };
  logout: () => void;
  updateUserProfile: (data: Partial<UserSession>) => void;
  changePassword: (currentPass: string, newPass: string) => { success: boolean; message: string };
  rooms: RoomItem[];
  bookings: BookingItem[];
  charges: Record<string, ChargeItem[]>;
  products: ProductItem[];
  menu: MenuItem[];
  orders: RestaurantOrder[];
  events: SpecialEventItem[];
  expenses: ExpenseItem[];
  audit: AuditItem[];
  users: UserItem[];
  log: (action: string, module: string) => void;
  // Room Actions
  setRoomStatus: (id: string | number, status: RoomStatusKey, extra?: Partial<RoomItem>) => void;
  addRoom: (room: Omit<RoomItem, 'id'>) => { success: boolean; message?: string };
  updateRoom: (id: string | number, data: Partial<RoomItem>) => { success: boolean; message?: string };
  deleteRoom: (id: string | number) => { success: boolean; message?: string };
  // Booking Actions
  patchBooking: (code: string, patch: Partial<BookingItem>) => void;
  setBookingStatus: (code: string, status: BookingStatusKey) => void;
  addBooking: (booking: BookingItem) => void;
  // Charge & Sales Actions
  addCharges: (roomNum: string, newCharges: ChargeItem[]) => void;
  clearCharges: (roomNum: string) => void;
  sell: (cart: { id: string; qty: number }[]) => void;
  // Restaurant Actions
  addRestaurantOrder: (order: Omit<RestaurantOrder, 'id' | 'createdAt'>) => void;
  updateOrderStatus: (id: string, status: RestaurantOrder['status']) => void;
  // Events Actions
  addEvent: (event: Omit<SpecialEventItem, 'id'>) => void;
  toggleEventActive: (id: string | number) => void;
  // Expenses & Users Actions
  addExpense: (expense: Omit<ExpenseItem, 'id'>) => void;
  voidExpense: (id: string) => void;
  setUsers: React.Dispatch<React.SetStateAction<UserItem[]>>;
  refreshBackendData: () => Promise<void>;
}

const StoreContext = createContext<StoreContextType | null>(null);

export function StoreProvider({ children }: { children: React.ReactNode }) {
  // Estado de usuario autenticado con persistencia
  const [currentUser, setCurrentUser] = useState<UserSession | null>(() => {
    try {
      const saved = localStorage.getItem('satori_auth_user');
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });

  const [role, setRoleState] = useState<'recepcion' | 'admin'>(() => {
    return currentUser ? currentUser.role : 'recepcion';
  });

  const setRole = (r: 'recepcion' | 'admin') => {
    setRoleState(r);
    if (currentUser) {
      const updated = { ...currentUser, role: r };
      setCurrentUser(updated);
      localStorage.setItem('satori_auth_user', JSON.stringify(updated));
    }
  };

  const login = (userOrEmail: string, pass: string, roleHint?: 'recepcion' | 'admin') => {
    const cleanUser = userOrEmail.trim().toLowerCase();
    
    // Si viene por acceso rápido con roleHint
    if (roleHint) {
      const sessionUser: UserSession = {
        id: roleHint === 'admin' ? 'u3' : 'u1',
        name: ROLE_PROFILES[roleHint].name,
        email: ROLE_PROFILES[roleHint].email,
        role: roleHint,
        phone: roleHint === 'admin' ? '+57 310 999 8888' : '+57 311 555 0120',
        lastLogin: new Date().toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' }),
      };
      setCurrentUser(sessionUser);
      setRoleState(roleHint);
      localStorage.setItem('satori_auth_user', JSON.stringify(sessionUser));
      return { success: true };
    }

    // Cuenta de Administrador (admin@gmail.com / admin123)
    if (
      cleanUser === 'admin@gmail.com' ||
      cleanUser === 'admin' ||
      cleanUser.includes('admin') ||
      cleanUser === 'gerencia@torresatori.co' ||
      cleanUser === 'admin@satoripms.com'
    ) {
      const storedPass = localStorage.getItem(`pass_${cleanUser}`) || 'admin123';
      if (pass !== storedPass && pass !== 'admin123' && pass.length < 4) {
        return { success: false, message: 'Contraseña incorrecta para la cuenta Administrador.' };
      }
      const sessionUser: UserSession = {
        id: 'u3',
        name: 'Frank Arias Salgado',
        email: cleanUser === 'admin@gmail.com' ? 'admin@gmail.com' : 'admin@gmail.com',
        role: 'admin',
        phone: '+57 310 999 8888',
        lastLogin: new Date().toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' }),
      };
      setCurrentUser(sessionUser);
      setRoleState('admin');
      localStorage.setItem('satori_auth_user', JSON.stringify(sessionUser));
      return { success: true };
    }

    if (cleanUser.includes('recep') || cleanUser.includes('sofia') || cleanUser === 'recepcion@satoripms.com') {
      const storedPass = localStorage.getItem(`pass_${cleanUser}`) || 'recepcion123';
      if (pass !== storedPass && pass !== 'recepcion123' && pass.length < 4) {
        return { success: false, message: 'Contraseña incorrecta para Recepción.' };
      }
      const sessionUser: UserSession = {
        id: 'u1',
        name: 'Sofía Valencia',
        email: 'sofia.valencia@torresatori.co',
        role: 'recepcion',
        phone: '+57 311 555 0120',
        lastLogin: new Date().toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' }),
      };
      setCurrentUser(sessionUser);
      setRoleState('recepcion');
      localStorage.setItem('satori_auth_user', JSON.stringify(sessionUser));
      return { success: true };
    }

    // Si ingresó cualquier otro usuario de recepción válido
    const matchedUser = INITIAL_USERS.find(
      (u) => u.email.toLowerCase() === cleanUser || u.name.toLowerCase().includes(cleanUser)
    );
    if (matchedUser) {
      const rKey = matchedUser.role.toLowerCase().includes('admin') ? 'admin' : 'recepcion';
      const sessionUser: UserSession = {
        id: matchedUser.id,
        name: matchedUser.name,
        email: matchedUser.email,
        role: rKey,
        phone: matchedUser.phone,
        lastLogin: new Date().toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' }),
      };
      setCurrentUser(sessionUser);
      setRoleState(rKey);
      localStorage.setItem('satori_auth_user', JSON.stringify(sessionUser));
      return { success: true };
    }

    return { success: false, message: 'Usuario o contraseña no reconocidos en el sistema.' };
  };

  const logout = () => {
    setCurrentUser(null);
    setRoleState('recepcion');
    localStorage.removeItem('satori_auth_user');
  };

  const updateUserProfile = (data: Partial<UserSession>) => {
    if (!currentUser) return;
    const updated = { ...currentUser, ...data };
    setCurrentUser(updated);
    localStorage.setItem('satori_auth_user', JSON.stringify(updated));
    log(`Actualizó perfil de usuario: ${currentUser.name}`, 'Seguridad');
  };

  const changePassword = (currentPass: string, newPass: string) => {
    if (!currentUser) return { success: false, message: 'No hay sesión de usuario activa.' };
    const storedPass = localStorage.getItem(`pass_${currentUser.email}`) || 'admin123';
    if (currentPass !== storedPass && currentPass !== 'admin123' && currentPass !== 'recepcion123') {
      return { success: false, message: 'La contraseña actual ingresada es incorrecta.' };
    }
    if (!newPass || newPass.trim().length < 6) {
      return { success: false, message: 'La nueva contraseña debe tener mínimo 6 caracteres.' };
    }
    localStorage.setItem(`pass_${currentUser.email}`, newPass.trim());
    log(`Actualizó la contraseña de acceso (${currentUser.email})`, 'Seguridad');
    return { success: true, message: 'Contraseña cambiada exitosamente.' };
  };

  const [rooms, setRooms] = useState<RoomItem[]>(INITIAL_ROOMS);
  const [bookings, setBookings] = useState<BookingItem[]>(INITIAL_BOOKINGS);
  const [charges, setCharges] = useState<Record<string, ChargeItem[]>>({
    '101': [
      { desc: 'Cerveza Club Colombia', qty: 2, amount: 14000, source: 'tienda' },
      { desc: 'Papas Margarita pollo', qty: 1, amount: 3500, source: 'tienda' },
      { desc: 'Gaseosa Postobón 400 ml', qty: 1, amount: 4000, source: 'tienda' },
    ],
  });
  const [products, setProducts] = useState<ProductItem[]>(INITIAL_PRODUCTS);
  const [menu, setMenu] = useState<MenuItem[]>(INITIAL_MENU);
  const [orders, setOrders] = useState<RestaurantOrder[]>([
    {
      id: 'ord-101',
      roomNumber: '101',
      guestName: 'Laura Gómez',
      items: [
        { menuItemId: 'm1', name: 'Desayuno Típico Vallecaucano', qty: 2, price: 18000 },
        { menuItemId: 'm4', name: 'Café Filtrado V60 / Chemex', qty: 2, price: 9000 },
      ],
      total: 54000,
      status: 'charged_to_room',
      createdAt: 'Hoy 08:15',
    },
  ]);
  const [events, setEvents] = useState<SpecialEventItem[]>(INITIAL_EVENTS);
  const [expenses, setExpenses] = useState<ExpenseItem[]>(INITIAL_EXPENSES);
  const [users, setUsers] = useState<UserItem[]>(INITIAL_USERS);
  const [audit, setAudit] = useState<AuditItem[]>([
    { at: '2026-10-01 09:12', user: 'Sofía Valencia', role: 'Recepcionista', action: 'Registró check-in de Laura Gómez (TS-2041)', module: 'Check-in' },
    { at: '2026-10-01 10:40', user: 'Sofía Valencia', role: 'Recepcionista', action: 'Registró check-out de María Fernanda Rojas (TS-2036)', module: 'Check-out' },
    { at: '2026-10-01 10:52', user: 'Sofía Valencia', role: 'Recepcionista', action: 'Marcó Hab. 201 como En limpieza', module: 'Habitaciones' },
    { at: '2026-10-01 11:05', user: 'Sofía Valencia', role: 'Recepcionista', action: 'Creó bloqueo temporal BL-0318 en Hab. 202', module: 'Reservas' },
    { at: '2026-09-30 17:30', user: 'Frank Arias Salgado', role: 'Administrador', action: 'Registró egreso: Mantenimiento ducha Hab. 103 ($185.000)', module: 'Finanzas' },
    { at: '2026-09-30 16:10', user: 'Frank Arias Salgado', role: 'Administrador', action: 'Configuró evento especial: Festival del Café (-15%)', module: 'Eventos' },
  ]);

  const log = (action: string, module: string) => {
    const profile = ROLE_PROFILES[role];
    const nowStr = '2026-10-01 ' + new Date().toTimeString().slice(0, 5);
    setAudit((prev) => [{ at: nowStr, user: profile.name, role: profile.label, action, module }, ...prev]);
  };

  const setRoomStatus = (id: string | number, status: RoomStatusKey, extra: Partial<RoomItem> = {}) => {
    setRooms((prev) =>
      prev.map((r) => (r.id === id || r.number === String(id) ? { ...r, status, ...extra } : r))
    );
  };

  const addRoom = (roomData: Omit<RoomItem, 'id'>) => {
    if (role !== 'admin') {
      return { success: false, message: 'Operación denegada: Solo el Administrador puede agregar habitaciones.' };
    }
    const exists = rooms.some((r) => r.number === roomData.number);
    if (exists) {
      return { success: false, message: `Ya existe una habitación con el número ${roomData.number}.` };
    }
    const newRoom: RoomItem = {
      ...roomData,
      id: roomData.number,
      active: true,
      status: roomData.status || 'libre',
    };
    setRooms((prev) => [...prev, newRoom]);
    log(`Creó nueva habitación: Hab. ${roomData.number} (${roomData.name})`, 'Habitaciones');
    return { success: true };
  };

  const updateRoom = (id: string | number, data: Partial<RoomItem>) => {
    if (role !== 'admin') {
      return { success: false, message: 'Operación denegada: Solo el Administrador puede editar habitaciones.' };
    }
    setRooms((prev) =>
      prev.map((r) => (r.id === id || r.number === String(id) ? { ...r, ...data } : r))
    );
    log(`Modificó parámetros de Hab. ${id}`, 'Habitaciones');
    return { success: true };
  };

  const deleteRoom = (id: string | number) => {
    if (role !== 'admin') {
      return { success: false, message: 'Operación denegada: Solo el Administrador puede eliminar habitaciones.' };
    }
    const targetRoom = rooms.find((r) => r.id === id || r.number === String(id));
    if (!targetRoom) {
      return { success: false, message: 'La habitación no existe.' };
    }
    // REGLA CLAVE: No se puede eliminar si tiene reservas activas o pendientes
    const activeBookings = bookings.filter(
      (b) =>
        (b.room === targetRoom.number || b.roomId === Number(targetRoom.id)) &&
        ['confirmada', 'pendiente', 'bloqueada', 'enCurso'].includes(b.status)
    );
    if (activeBookings.length > 0) {
      return {
        success: false,
        message: `No se puede eliminar la habitación ${targetRoom.number}. Tiene ${activeBookings.length} reserva(s) activa(s) o en curso (ej. código ${activeBookings[0].code}).`,
      };
    }
    setRooms((prev) => prev.filter((r) => r.id !== id && r.number !== String(id)));
    log(`Eliminó la habitación ${targetRoom.number} (${targetRoom.name})`, 'Habitaciones');
    return { success: true };
  };

  const patchBooking = (code: string, patch: Partial<BookingItem>) => {
    setBookings((prev) => prev.map((b) => (b.code === code ? { ...b, ...patch } : b)));
  };

  const setBookingStatus = (code: string, status: BookingStatusKey) => {
    patchBooking(code, { status });
  };

  // Sincronización continua con el Backend (PostgreSQL + Redis + Chatbot)
  const refreshBackendData = async () => {
    try {
      const res = await fetch('/api/bookings/debug');
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data) && data.length > 0) {
          setBookings((prevLocal) => {
            const statusMap: Record<string, BookingStatusKey> = {
              confirmed: 'confirmada',
              pending_payment: 'pendiente',
              finished: 'finalizada',
              cancelled: 'cancelada',
              occupied: 'enCurso',
            };

            const backendItems: BookingItem[] = data.map((b: any) => {
              let cleanCode = 'TS-' + b.id;
              if (b.companions && b.companions.startsWith('TS-')) {
                cleanCode = b.companions;
              } else if (b.reservationGroupId) {
                const sub = String(b.reservationGroupId).replace(/-/g, '').slice(-4).toUpperCase();
                cleanCode = 'TS-' + sub;
              }

              return {
                code: cleanCode,
                reservationGroupId: b.reservationGroupId,
                guest: b.guestName || 'Huésped Satori',
                guestId: b.guestId,
                room: b.roomNumber || String(b.roomId || '101'),
                roomId: b.roomId,
                checkIn: b.checkIn,
                checkOut: b.checkOut,
                guests: (b.adults || 1) + (b.children || 0),
                adults: b.adults,
                children: b.children,
                hasPet: b.withPet,
                status: statusMap[b.status] || 'confirmada',
                channel: b.source === 'chatbot' ? 'WhatsApp' : 'Recepción',
                phone: b.guestPhone || '',
                doc: b.guestDocument || '',
                total: Number(b.totalPrice) || 0,
                paid: Number(b.paidAmount) || 0,
              };
            });

            // Merge unificando por código de reserva
            const codeMap = new Map<string, BookingItem>();
            prevLocal.forEach((item) => codeMap.set(item.code, item));
            backendItems.forEach((item) => codeMap.set(item.code, item));
            return Array.from(codeMap.values());
          });
        }
      }
    } catch {
      // Si el backend no responde, se mantiene el estado reactivo en memoria
    }
  };

  useEffect(() => {
    refreshBackendData();
    const interval = setInterval(refreshBackendData, 4000);
    return () => clearInterval(interval);
  }, []);

  const addBooking = (booking: BookingItem) => {
    setBookings((prev) => [booking, ...prev]);
    log(`Nueva reserva registrada: ${booking.code} (${booking.guest})`, 'Reservas');

    // Sincronizar asíncronamente con el backend si está activo
    try {
      fetch('/api/bookings/test-paid', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          rooms: [
            {
              roomId: Number(booking.room) || 1,
              lockToken: 'sandbox-' + Date.now(),
              checkIn: booking.checkIn,
              checkOut: booking.checkOut,
            },
          ],
          guest: {
            name: booking.guest,
            phone: booking.phone || '+57 300 000 0000',
            documentNumber: booking.doc || 'CC 0000000',
          },
          companions: booking.code,
        }),
      }).catch(() => {
        // En modo frontend-only se mantiene local sin error
      });
    } catch {
      // Ignorar error de red si corre sin contenedor
    }
  };

  const addCharges = (roomNum: string, newCharges: ChargeItem[]) => {
    setCharges((prev) => ({
      ...prev,
      [roomNum]: [...(prev[roomNum] ?? []), ...newCharges],
    }));
  };

  const clearCharges = (roomNum: string) => {
    setCharges((prev) => ({ ...prev, [roomNum]: [] }));
  };

  const sell = (cart: { id: string; qty: number }[]) => {
    setProducts((prev) =>
      prev.map((p) => {
        const item = cart.find((c) => c.id === p.id);
        return item ? { ...p, stock: Math.max(0, p.stock - item.qty) } : p;
      })
    );
  };

  const addRestaurantOrder = (orderData: Omit<RestaurantOrder, 'id' | 'createdAt'>) => {
    const newOrd: RestaurantOrder = {
      ...orderData,
      id: 'ord-' + Date.now().toString().slice(-4),
      createdAt: 'Hoy ' + new Date().toTimeString().slice(0, 5),
    };
    setOrders((prev) => [newOrd, ...prev]);
    if (orderData.status === 'charged_to_room' && orderData.roomNumber) {
      const chargeItems: ChargeItem[] = orderData.items.map((i) => ({
        desc: `Restaurante: ${i.name}`,
        qty: i.qty,
        amount: i.price * i.qty,
        source: 'restaurante',
      }));
      addCharges(orderData.roomNumber, chargeItems);
    }
    log(`Comanda de restaurante creada (${orderData.items.length} ítems)`, 'Restaurante');
  };

  const updateOrderStatus = (id: string, status: RestaurantOrder['status']) => {
    setOrders((prev) => prev.map((o) => (o.id === id ? { ...o, status } : o)));
  };

  const addEvent = (eventData: Omit<SpecialEventItem, 'id'>) => {
    const newEv: SpecialEventItem = {
      ...eventData,
      id: 'ev-' + Date.now().toString().slice(-4),
    };
    setEvents((prev) => [newEv, ...prev]);
    log(`Creó evento especial / descuento: ${eventData.name} (${eventData.discountPercentage}%)`, 'Eventos');
  };

  const toggleEventActive = (id: string | number) => {
    setEvents((prev) =>
      prev.map((e) => (e.id === id ? { ...e, active: !e.active } : e))
    );
  };

  const addExpense = (expenseData: Omit<ExpenseItem, 'id'>) => {
    const newExp: ExpenseItem = {
      ...expenseData,
      id: 'e' + Date.now().toString().slice(-4),
    };
    setExpenses((prev) => [newExp, ...prev]);
    log(`Registró egreso: ${expenseData.desc} ($${expenseData.amount.toLocaleString('es-CO')})`, 'Finanzas');
  };

  const voidExpense = (id: string) => {
    setExpenses((prev) =>
      prev.map((e) => (e.id === id ? { ...e, voided: true } : e))
    );
    log(`Anuló comprobante de egreso ${id}`, 'Finanzas');
  };

  return (
    <StoreContext.Provider
      value={{
        role,
        setRole,
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
        audit,
        users,
        log,
        setRoomStatus,
        addRoom,
        updateRoom,
        deleteRoom,
        patchBooking,
        setBookingStatus,
        addBooking,
        addCharges,
        clearCharges,
        sell,
        addRestaurantOrder,
        updateOrderStatus,
        addEvent,
        toggleEventActive,
        addExpense,
        voidExpense,
        setUsers,
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
