import React, { useState } from 'react';
import {
  Building2,
  BedDouble,
  Calendar,
  Clock,
  Sparkles,
  ArrowRight,
  ShoppingBag,
  MessageSquare,
  ShieldCheck,
  TrendingUp,
  FileText,
  Users,
  Lock,
  UtensilsCrossed,
  Tag,
  LogOut,
  Settings
} from 'lucide-react';
import { StoreProvider, useStore } from './store';
import { cn } from './ui';

// Pantallas Operativas
import { Login } from './screens/Login';
import { Dashboard } from './screens/Dashboard';
import { Rooms } from './screens/Rooms';
import { CalendarView } from './screens/CalendarView';
import { Reservas } from './screens/Reservas';
import { Operacion } from './screens/Operacion';
import { Tienda } from './screens/Tienda';
import { Restaurante } from './screens/Restaurante';
import { Eventos } from './screens/Eventos';
import { Chatbot } from './screens/Chatbot';
import { Admin } from './screens/Admin';
import { AccountSettingsModal } from './screens/AccountSettingsModal';

const NAV_RECEPTION = [
  { k: 'dashboard', label: 'Dashboard', icon: Building2 },
  { k: 'habitaciones', label: 'Habitaciones', icon: BedDouble },
  { k: 'calendario', label: 'Calendario', icon: Calendar },
  { k: 'reservas', label: 'Reservas', icon: Clock, also: ['reserva-nueva', 'reserva-detalle'] },
  { k: 'llegadas', label: 'Llegadas', icon: Sparkles, also: ['checkin'] },
  { k: 'salidas', label: 'Salidas', icon: ArrowRight, also: ['checkout'] },
  { k: 'tienda', label: 'Tienda Hotel', icon: ShoppingBag },
  { k: 'restaurante', label: 'Salgados Café', icon: UtensilsCrossed },
];

const NAV_ADMIN = [
  { k: 'a-dash', label: 'Resumen Global', icon: Building2 },
  { k: 'a-fin', label: 'Finanzas & Egresos', icon: TrendingUp },
  { k: 'a-rep', label: 'Reportes & Excel', icon: FileText },
  { k: 'a-usr', label: 'Recepcionistas', icon: Users },
  { k: 'a-log', label: 'Logs Auditoría', icon: ShieldCheck },
  { k: 'eventos', label: 'Eventos & Descuentos', icon: Tag },
];

function AppLayout() {
  const { role, currentUser, logout } = useStore();
  const [accountModalOpen, setAccountModalOpen] = useState(false);
  const [currentView, setCurrentView] = useState<string>(() => {
    return role === 'admin' ? 'a-dash' : 'dashboard';
  });
  const [viewParam, setViewParam] = useState<string | undefined>(undefined);

  const go = (view: string, param?: string) => {
    setCurrentView(view);
    setViewParam(param);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // Si no hay usuario autenticado, renderizar la pantalla de Login
  if (!currentUser) {
    return (
      <Login
        onLoginSuccess={(targetRole) => {
          setCurrentView(targetRole === 'admin' ? 'a-dash' : 'dashboard');
        }}
      />
    );
  }

  const isAdminView = currentView.startsWith('a-') || currentView === 'eventos';

  const NavButton = ({
    k,
    label,
    icon: Icon,
    also,
  }: {
    k: string;
    label: string;
    icon: React.ElementType;
    also?: string[];
  }) => {
    const isActive = currentView === k || (also && also.includes(currentView));
    return (
      <button
        onClick={() => go(k)}
        aria-current={isActive ? 'page' : undefined}
        className={cn(
          'flex h-10 w-full shrink-0 cursor-pointer items-center gap-3 rounded-lg px-3 text-sm font-semibold transition-colors',
          isActive
            ? 'bg-forest-700 text-white shadow-sm'
            : 'text-sand-200 hover:bg-forest-700/60'
        )}
      >
        <Icon size={18} />
        <span className="lbl">{label}</span>
      </button>
    );
  };

  const SectionLabel = ({ text }: { text: string }) => (
    <p className="lbl mt-4 px-3 text-[11px] font-semibold uppercase tracking-wider text-sand-300/70">
      {text}
    </p>
  );

  return (
    <div className="grid min-h-screen grid-cols-[240px_1fr] max-[1000px]:grid-cols-[72px_1fr] bg-[#f4eee2]">
      {/* Barra Lateral (Sidebar) */}
      <aside className="sticky top-0 flex h-screen flex-col gap-1 overflow-y-auto bg-forest-800 p-4 max-[1000px]:items-center max-[1000px]:px-2 [&_button]:max-[1000px]:justify-center [&_button]:max-[1000px]:px-0 [&_.lbl]:max-[1000px]:hidden border-r border-forest-900 shadow-lg">
        {/* Logo / Inicio */}
        <button
          onClick={() => go(role === 'admin' ? 'a-dash' : 'dashboard')}
          className="mb-4 flex shrink-0 cursor-pointer items-center gap-3 px-1 text-left"
          aria-label="Ir a panel principal"
        >
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-forest-900 text-sand-50 font-display font-bold text-sm shadow">
            TS
          </div>
          <div className="lbl font-display text-base font-semibold leading-tight text-sand-50">
            Torre Satori
            <span className="block text-[11px] font-normal text-sand-300">
              PMS · {role === 'admin' ? 'Administración' : 'Recepción'}
            </span>
          </div>
        </button>

        {/* Sección de Navegación Exclusiva Admin */}
        {role === 'admin' && (
          <>
            <SectionLabel text="Administración" />
            {NAV_ADMIN.map((item) => (
              <NavButton key={item.k} {...item} />
            ))}
          </>
        )}

        {/* Sección de Operación / Recepción */}
        <SectionLabel text={role === 'admin' ? 'Operación' : 'Recepción'} />
        {NAV_RECEPTION.map((item) => (
          <NavButton key={item.k} {...item} />
        ))}

        {role === 'recepcion' && (
          <div className="lbl mt-3 flex items-start gap-2 rounded-lg bg-forest-900/50 p-2.5 text-xs text-sand-300">
            <Lock size={13} className="mt-0.5 shrink-0 text-terra-100" />
            Finanzas y usuarios: solo Administración
          </div>
        )}

        {/* Zona Inferior: Chatbot, Cerrar Sesión y Perfil Interactivo */}
        <div className="mt-auto space-y-2 pt-4 border-t border-forest-700/60">
          <NavButton k="chatbot" label="WhatsApp & Bot" icon={MessageSquare} />

          {/* Botón de Cerrar Sesión (Colocado ARRIBA del perfil) */}
          <button
            type="button"
            onClick={logout}
            className="flex h-9 w-full shrink-0 cursor-pointer items-center gap-2.5 rounded-lg px-3 text-xs font-semibold text-sand-300 hover:bg-forest-900 hover:text-bad-bg transition-colors"
            title="Cerrar sesión y volver al login"
          >
            <LogOut size={16} className="text-sand-300" />
            <span className="lbl">Cerrar Sesión</span>
          </button>

          {/* Perfil de Usuario Autenticado (Clickeable: abre Configuración de Perfil) */}
          <button
            type="button"
            onClick={() => setAccountModalOpen(true)}
            className="flex w-full items-center gap-3 p-2 rounded-xl bg-forest-900/60 hover:bg-forest-900 border border-forest-700/50 hover:border-forest-600 transition cursor-pointer text-left group"
            title="Haz clic para cambiar foto o contraseña"
          >
            {currentUser.avatarUrl ? (
              <img
                src={currentUser.avatarUrl}
                alt={currentUser.name}
                className="h-9 w-9 shrink-0 rounded-full object-cover border border-forest-600 ring-2 ring-forest-700/50"
              />
            ) : (
              <span className={cn(
                'grid h-9 w-9 shrink-0 place-items-center rounded-full text-xs font-bold text-white shadow-sm',
                role === 'admin' ? 'bg-terra-600' : 'bg-forest-900 ring-2 ring-forest-700'
              )}>
                {currentUser.name
                  .split(' ')
                  .map((n) => n[0])
                  .slice(0, 2)
                  .join('')}
              </span>
            )}
            <div className="lbl min-w-0 flex-1 text-sm text-sand-50 leading-tight">
              <div className="flex items-center justify-between">
                <span className="block font-semibold truncate group-hover:text-white">
                  {currentUser.name}
                </span>
                <Settings size={13} className="text-sand-300/70 group-hover:text-sand-100 transition-colors" />
              </div>
              <span className="block text-[11px] text-sand-300">
                {role === 'admin' ? 'Administrador' : 'Recepcionista'}
              </span>
            </div>
          </button>
        </div>
      </aside>

      {/* Modal de Configuración de Cuenta y Perfil */}
      <AccountSettingsModal
        isOpen={accountModalOpen}
        onClose={() => setAccountModalOpen(false)}
      />

      {/* Contenido Principal (Main) */}
      <main className="min-w-0 p-8 max-[1000px]:p-5">
        {isAdminView && role !== 'admin' ? (
          <div className="mx-auto max-w-md pt-20 text-center">
            <Lock size={32} className="mx-auto mb-3 text-bad" />
            <h1 className="font-display text-2xl font-semibold text-forest-900">
              Acceso Restringido
            </h1>
            <p className="mt-1 text-ink-soft text-sm">
              Esta sección es exclusiva de la Gerencia / Administración de Torre Satori.
            </p>
            <button
              onClick={() => go('dashboard')}
              className="mt-5 inline-flex h-10 items-center justify-center rounded-lg bg-forest-800 px-4 text-sm font-semibold text-white cursor-pointer hover:bg-forest-700"
            >
              Volver al dashboard
            </button>
          </div>
        ) : (
          <>
            {currentView === 'dashboard' && <Dashboard go={go} />}
            {currentView === 'habitaciones' && <Rooms />}
            {currentView === 'calendario' && <CalendarView go={go} />}
            {currentView === 'reservas' && <Reservas go={go} initialCode={viewParam} />}
            {currentView === 'reserva-detalle' && <Reservas go={go} initialCode={viewParam} />}
            {currentView === 'llegadas' && <Operacion subview="llegadas" go={go} />}
            {currentView === 'checkin' && <Operacion subview="checkin" code={viewParam} go={go} />}
            {currentView === 'salidas' && <Operacion subview="salidas" go={go} />}
            {currentView === 'checkout' && <Operacion subview="checkout" code={viewParam} go={go} />}
            {currentView === 'tienda' && <Tienda go={go} />}
            {currentView === 'restaurante' && <Restaurante go={go} />}
            {currentView === 'eventos' && <Eventos />}
            {currentView === 'chatbot' && <Chatbot go={go} />}
            {currentView === 'a-dash' && <Admin subview="dash" go={go} />}
            {currentView === 'a-fin' && <Admin subview="fin" go={go} />}
            {currentView === 'a-rep' && <Admin subview="rep" go={go} />}
            {currentView === 'a-usr' && <Admin subview="usr" go={go} />}
            {currentView === 'a-log' && <Admin subview="log" go={go} />}
          </>
        )}
      </main>
    </div>
  );
}

export default function App() {
  return (
    <StoreProvider>
      <AppLayout />
    </StoreProvider>
  );
}
