import React, { useState, useEffect } from 'react';
import {
  CheckCircle2,
  BedDouble,
  Sparkles,
  Wrench,
  Clock,
  AlertTriangle,
  AlertCircle,
  Info,
  X,
  ChevronDown,
  Search,
  Calendar,
  Check,
  LucideIcon
} from 'lucide-react';

export const cn = (...classes: (string | boolean | undefined | null)[]) =>
  classes.filter(Boolean).join(' ');

export type RoomStatusKey = 'libre' | 'ocupada' | 'limpieza' | 'mantenimiento' | 'bloqueada';

export const ROOM_STATUS_META: Record<RoomStatusKey, {
  label: string;
  short: string;
  icon: LucideIcon;
  text: string;
  bg: string;
  bar: string;
  dot: string;
}> = {
  libre: {
    label: 'Libre',
    short: 'Lista para huéspedes',
    icon: CheckCircle2,
    text: 'text-ok',
    bg: 'bg-ok-bg',
    bar: 'bg-ok',
    dot: '#2f7d4f',
  },
  ocupada: {
    label: 'Ocupada',
    short: 'Huésped en casa',
    icon: BedDouble,
    text: 'text-terra-600',
    bg: 'bg-terra-100',
    bar: 'bg-terra-500',
    dot: '#c4704f',
  },
  limpieza: {
    label: 'En limpieza',
    short: 'Aseo en curso',
    icon: Sparkles,
    text: 'text-clean',
    bg: 'bg-clean-bg',
    bar: 'bg-clean',
    dot: '#23707f',
  },
  mantenimiento: {
    label: 'En mantenimiento',
    short: 'Fuera de servicio',
    icon: Wrench,
    text: 'text-maint',
    bg: 'bg-maint-bg',
    bar: 'bg-maint',
    dot: '#4b514d',
  },
  bloqueada: {
    label: 'Bloqueada temporalmente',
    short: 'Retenida sin pago',
    icon: Clock,
    text: 'text-warn',
    bg: 'bg-warn-bg',
    bar: 'bg-[#d99a1e]',
    dot: '#d99a1e',
  },
};

export const formatCurrency = (val: number | string = 0) => {
  const num = typeof val === 'string' ? parseFloat(val) : val;
  return '$' + (isNaN(num) ? 0 : Math.round(num)).toLocaleString('es-CO');
};

export function BadgeStatus({
  status,
  size = 'md',
}: {
  status: RoomStatusKey;
  size?: 'sm' | 'md';
}) {
  const meta = ROOM_STATUS_META[status] || ROOM_STATUS_META.libre;
  const Icon = meta.icon;
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full font-semibold whitespace-nowrap',
        meta.bg,
        meta.text,
        size === 'sm' ? 'px-2 py-0.5 text-[11px]' : 'px-2.5 py-1 text-xs'
      )}
    >
      <Icon size={size === 'sm' ? 12 : 14} strokeWidth={2.25} />
      {meta.label}
    </span>
  );
}

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost' | 'terra';
  icon?: React.ReactNode;
}

export function Button({
  variant = 'primary',
  icon,
  className,
  children,
  ...props
}: ButtonProps) {
  const variants = {
    primary: 'bg-forest-800 text-white hover:bg-forest-700 active:bg-forest-900',
    secondary: 'bg-white text-forest-800 border border-sand-300 hover:bg-sand-50 hover:border-forest-700',
    danger: 'bg-bad text-white hover:bg-[#9c352e]',
    ghost: 'text-forest-800 hover:bg-forest-100',
    terra: 'bg-terra-500 text-white hover:bg-terra-600',
  };

  return (
    <button
      {...props}
      className={cn(
        'inline-flex h-10 items-center justify-center gap-2 rounded-lg px-4 text-sm font-semibold transition-colors cursor-pointer',
        'disabled:bg-sand-200 disabled:text-ink-soft/60 disabled:border-transparent disabled:cursor-not-allowed',
        variants[variant],
        className
      )}
    >
      {icon}
      {children}
    </button>
  );
}

export function Card({ className, children }: { className?: string; children: React.ReactNode }) {
  return (
    <div className={cn('rounded-xl border border-sand-200 bg-white shadow-[0_1px_1px_rgba(0,0,0,0.06)]', className)}>
      {children}
    </div>
  );
}

export function CardHeader({
  title,
  hint,
  action,
}: {
  title: string;
  hint?: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="mb-4 flex items-end justify-between gap-4 border-b border-sand-200 pb-3">
      <div>
        <h2 className="font-display text-lg font-semibold text-forest-900">{title}</h2>
        {hint && <p className="text-sm text-ink-soft">{hint}</p>}
      </div>
      {action}
    </div>
  );
}

export function PageHeader({
  eyebrow,
  title,
  desc,
  actions,
}: {
  eyebrow?: string;
  title: string;
  desc?: string;
  actions?: React.ReactNode;
}) {
  return (
    <header className="mb-7 flex flex-wrap items-end justify-between gap-4">
      <div>
        {eyebrow && (
          <p className="mb-1 text-xs font-semibold uppercase tracking-[0.14em] text-terra-600">
            {eyebrow}
          </p>
        )}
        <h1 className="font-display text-[32px] font-semibold leading-tight tracking-tight text-forest-900">
          {title}
        </h1>
        {desc && <p className="mt-1 max-w-xl text-[15px] text-ink-soft">{desc}</p>}
      </div>
      {actions && <div className="flex gap-2">{actions}</div>}
    </header>
  );
}

export const inputClass =
  'h-10 w-full rounded-lg border border-sand-300 bg-white px-3 text-sm text-ink placeholder:text-ink-soft/70 hover:border-forest-700 focus:border-forest-700 focus:outline-none focus:ring-2 focus:ring-forest-700/20';

export function Field({
  label,
  hint,
  error,
  children,
}: {
  label: string;
  hint?: string;
  error?: string;
  children: React.ReactNode;
}) {
  return (
    <label className="block">
      <span className="mb-1.5 block text-sm font-medium text-ink">{label}</span>
      {children}
      {error ? (
        <span className="mt-1 flex items-center gap-1 text-xs text-bad">
          <AlertCircle size={12} />
          {error}
        </span>
      ) : hint ? (
        <span className="mt-1 block text-xs text-ink-soft">{hint}</span>
      ) : null}
    </label>
  );
}

export function Input(props: React.InputHTMLAttributes<HTMLInputElement>) {
  return <input {...props} className={cn(inputClass, props.className)} />;
}

export function Select({
  value,
  onChange,
  options,
  label,
  className,
}: {
  value: string | number;
  onChange: (val: string) => void;
  options: { value: string | number; label: string }[];
  label?: string;
  className?: string;
}) {
  return (
    <div className={cn('relative', className)}>
      <select
        aria-label={label}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className={cn(inputClass, 'appearance-none pr-9 cursor-pointer')}
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
      <ChevronDown size={16} className="pointer-events-none absolute right-3 top-3 text-ink-soft" />
    </div>
  );
}

export function SearchBar({
  value,
  onChange,
  placeholder = 'Buscar huésped, habitación o código…',
}: {
  value?: string;
  onChange?: (val: string) => void;
  placeholder?: string;
}) {
  return (
    <div className="relative">
      <Search size={16} className="absolute left-3 top-3 text-ink-soft" />
      <input
        aria-label="Buscar"
        value={value}
        onChange={(e) => onChange?.(e.target.value)}
        placeholder={placeholder}
        className={cn(inputClass, 'pl-9')}
      />
    </div>
  );
}

export function DateField({
  value,
  onChange,
  label,
}: {
  value: string;
  onChange: (val: string) => void;
  label?: string;
}) {
  return (
    <div className="relative">
      <Calendar size={16} className="pointer-events-none absolute left-3 top-3 text-ink-soft" />
      <input
        aria-label={label}
        type="date"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className={cn(inputClass, 'pl-9')}
      />
    </div>
  );
}

export function FilterChip({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      aria-pressed={active}
      className={cn(
        'h-8 cursor-pointer rounded-full border px-3 text-[13px] font-semibold transition-colors',
        active
          ? 'border-forest-800 bg-forest-800 text-white'
          : 'border-sand-300 bg-white text-ink hover:border-forest-700'
      )}
    >
      {children}
    </button>
  );
}

export function Tabs<T extends string>({
  tabs,
  value,
  onChange,
}: {
  tabs: { value: T; label: string }[];
  value: T;
  onChange: (val: T) => void;
}) {
  return (
    <div role="tablist" className="flex gap-6 border-b border-sand-200">
      {tabs.map((tab) => (
        <button
          key={tab.value}
          role="tab"
          aria-selected={value === tab.value}
          onClick={() => onChange(tab.value)}
          className={cn(
            '-mb-px cursor-pointer border-b-2 pb-2.5 text-sm font-semibold transition-colors',
            value === tab.value
              ? 'border-terra-500 text-forest-900'
              : 'border-transparent text-ink-soft hover:text-ink'
          )}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}

const ALERT_STYLES = {
  ok: { cls: 'bg-ok-bg text-[#1f5a37] border-ok/30', icon: CheckCircle2 },
  warn: { cls: 'bg-warn-bg text-[#6e4700] border-[#d99a1e]/50', icon: AlertTriangle },
  bad: { cls: 'bg-bad-bg text-[#862b25] border-bad/30', icon: AlertCircle },
  info: { cls: 'bg-clean-bg text-[#17525e] border-clean/30', icon: Info },
};

export function Alert({
  tone = 'info',
  title,
  children,
  action,
}: {
  tone?: 'ok' | 'warn' | 'bad' | 'info';
  title: string;
  children?: React.ReactNode;
  action?: React.ReactNode;
}) {
  const conf = ALERT_STYLES[tone];
  const Icon = conf.icon;
  return (
    <div role="alert" className={cn('flex items-start gap-3 rounded-lg border p-3.5', conf.cls)}>
      <Icon size={18} className="mt-0.5 shrink-0" />
      <div className="flex-1 text-sm">
        <p className="font-semibold">{title}</p>
        {children && <p className="mt-0.5 opacity-90">{children}</p>}
      </div>
      {action}
    </div>
  );
}

export function Toast({
  tone = 'ok',
  title,
  children,
  onClose,
}: {
  tone?: 'ok' | 'warn' | 'bad' | 'info';
  title: string;
  children?: React.ReactNode;
  onClose?: () => void;
}) {
  const conf = ALERT_STYLES[tone];
  const Icon = conf.icon;
  return (
    <div
      role="status"
      className="flex w-[360px] items-start gap-3 rounded-xl border border-sand-200 bg-white p-4 shadow-[0_6px_20px_rgba(31,58,46,0.12)]"
    >
      <span className={cn('grid h-8 w-8 shrink-0 place-items-center rounded-full', conf.cls.split(' ').slice(0, 2).join(' '))}>
        <Icon size={16} />
      </span>
      <div className="flex-1 text-sm">
        <p className="font-semibold text-ink">{title}</p>
        {children && <p className="text-ink-soft">{children}</p>}
      </div>
      {onClose && (
        <button
          aria-label="Cerrar"
          onClick={onClose}
          className="cursor-pointer text-ink-soft hover:text-ink"
        >
          <X size={16} />
        </button>
      )}
    </div>
  );
}

export function useToast() {
  const [toast, setToast] = useState<{
    title: string;
    body?: string;
    tone: 'ok' | 'warn' | 'bad' | 'info';
  } | null>(null);

  const show = (title: string, body?: string, tone: 'ok' | 'warn' | 'bad' | 'info' = 'ok') => {
    setToast({ title, body, tone });
    setTimeout(() => setToast(null), 4000);
  };

  const node = toast && (
    <div className="fixed bottom-6 right-6 z-[60] slide-in">
      <Toast tone={toast.tone} title={toast.title} onClose={() => setToast(null)}>
        {toast.body}
      </Toast>
    </div>
  );

  return { show, node };
}

export function ConfirmModal({
  title,
  children,
  confirm = 'Confirmar',
  danger = false,
  onCancel,
  onConfirm,
}: {
  title: string;
  children: React.ReactNode;
  confirm?: string;
  danger?: boolean;
  onCancel: () => void;
  onConfirm: () => void;
}) {
  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-forest-900/40 p-4">
      <div
        role="dialog"
        aria-modal="true"
        aria-label={title}
        className="w-[420px] max-w-full rounded-2xl bg-white p-6 shadow-[0_12px_40px_rgba(22,41,31,0.18)]"
      >
        <div
          className={cn(
            'mb-4 grid h-10 w-10 place-items-center rounded-full',
            danger ? 'bg-bad-bg text-bad' : 'bg-forest-100 text-forest-800'
          )}
        >
          {danger ? <AlertTriangle size={20} /> : <CheckCircle2 size={20} />}
        </div>
        <h3 className="font-display text-xl font-semibold text-forest-900">{title}</h3>
        <div className="mt-1.5 text-sm text-ink-soft">{children}</div>
        <div className="mt-6 flex justify-end gap-2">
          <Button variant="secondary" onClick={onCancel}>
            Volver
          </Button>
          <Button variant={danger ? 'danger' : 'primary'} onClick={onConfirm}>
            {confirm}
          </Button>
        </div>
      </div>
    </div>
  );
}

export function Modal({
  title,
  children,
  onClose,
  footer,
  maxWidth = 'max-w-lg',
}: {
  title: string;
  children: React.ReactNode;
  onClose: () => void;
  footer?: React.ReactNode;
  maxWidth?: string;
}) {
  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-forest-900/40 p-4 overflow-y-auto">
      <div
        role="dialog"
        aria-modal="true"
        aria-label={title}
        className={cn('w-full rounded-2xl bg-white shadow-[0_12px_40px_rgba(22,41,31,0.18)] my-8', maxWidth)}
      >
        <div className="flex items-center justify-between border-b border-sand-200 px-6 py-4">
          <h3 className="font-display text-xl font-semibold text-forest-900">{title}</h3>
          <button
            aria-label="Cerrar"
            onClick={onClose}
            className="cursor-pointer text-ink-soft hover:text-ink"
          >
            <X size={18} />
          </button>
        </div>
        <div className="space-y-4 px-6 py-5 max-h-[75vh] overflow-y-auto">{children}</div>
        {footer && (
          <div className="flex justify-end gap-2 border-t border-sand-200 px-6 py-4">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
}

export type BookingStatusKey = 'confirmada' | 'pendiente' | 'bloqueada' | 'enCurso' | 'finalizada' | 'cancelada';

export const BOOKING_STATUS_META: Record<BookingStatusKey, {
  label: string;
  icon: LucideIcon;
  cls: string;
}> = {
  confirmada: { label: 'Confirmada', icon: CheckCircle2, cls: 'bg-ok-bg text-ok' },
  pendiente: { label: 'Pendiente de pago', icon: Clock, cls: 'bg-warn-bg text-warn' },
  bloqueada: { label: 'Bloqueada temporalmente', icon: Clock, cls: 'bg-warn-bg text-warn' },
  enCurso: { label: 'En curso', icon: BedDouble, cls: 'bg-terra-100 text-terra-600' },
  finalizada: { label: 'Finalizada', icon: Check, cls: 'bg-maint-bg text-maint' },
  cancelada: { label: 'Cancelada', icon: X, cls: 'bg-bad-bg text-bad' },
};

export function BookingStatusBadge({ status }: { status: BookingStatusKey }) {
  const meta = BOOKING_STATUS_META[status] || BOOKING_STATUS_META.confirmada;
  const Icon = meta.icon;
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 whitespace-nowrap rounded-full px-2.5 py-1 text-xs font-semibold',
        meta.cls
      )}
    >
      <Icon size={14} strokeWidth={2.25} />
      {meta.label}
    </span>
  );
}

export function Stepper({ steps, current }: { steps: string[]; current: number }) {
  return (
    <ol className="mb-6 flex items-center gap-3">
      {steps.map((step, idx) => (
        <li
          key={step}
          className="flex items-center gap-3"
          aria-current={idx === current ? 'step' : undefined}
        >
          <span
            className={cn(
              'grid h-7 w-7 place-items-center rounded-full text-xs font-bold',
              idx < current
                ? 'bg-ok text-white'
                : idx === current
                ? 'bg-forest-800 text-white'
                : 'bg-sand-200 text-ink-soft'
            )}
          >
            {idx < current ? <Check size={14} /> : idx + 1}
          </span>
          <span
            className={cn(
              'text-sm font-semibold',
              idx === current ? 'text-forest-900' : 'text-ink-soft'
            )}
          >
            {step}
          </span>
          {idx < steps.length - 1 && <span className="h-px w-10 bg-sand-300" />}
        </li>
      ))}
    </ol>
  );
}

export function TableHeader({
  children,
  right = false,
}: {
  children: React.ReactNode;
  right?: boolean;
}) {
  return (
    <th className={cn('px-4 py-2.5 font-semibold text-left text-xs uppercase tracking-wider text-ink-soft', right && 'text-right')}>
      {children}
    </th>
  );
}

export function EmptyState({
  icon,
  title,
  children,
}: {
  icon?: React.ReactNode;
  title: string;
  children?: React.ReactNode;
}) {
  return (
    <div className="grid place-items-center gap-2 p-14 text-center text-ink-soft">
      {icon}
      <p className="font-semibold text-ink text-base">{title}</p>
      {children && <p className="text-sm">{children}</p>}
    </div>
  );
}

/**
 * Hook para sincronizar la aplicación con la fecha y hora en tiempo real.
 * Actualiza cada segundo y entrega formato en español de Colombia.
 */
export function useRealtimeClock() {
  const [now, setNow] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      setNow(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const weekdayStr = now.toLocaleDateString('es-CO', { weekday: 'long' });
  const day = now.getDate();
  const monthStr = now.toLocaleDateString('es-CO', { month: 'long' });
  const year = now.getFullYear();

  // Ej: "Martes 10 de noviembre de 2026"
  const formattedDate = `${weekdayStr.charAt(0).toUpperCase() + weekdayStr.slice(1)} ${day} de ${monthStr} de ${year}`;

  const formattedTime = now.toLocaleTimeString('es-CO', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: true,
  });

  const hour = now.getHours();
  let greeting = 'Buenos días';
  if (hour >= 12 && hour < 18) {
    greeting = 'Buenas tardes';
  } else if (hour >= 18 || hour < 5) {
    greeting = 'Buenas noches';
  }

  const isoDate = `${year}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;

  return {
    now,
    isoDate,
    formattedDate,
    formattedTime,
    greeting,
  };
}
