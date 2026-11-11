import React, { useState } from 'react';
import {
  Lock,
  Mail,
  ArrowRight,
  ShieldCheck,
  Coffee
} from 'lucide-react';
import { useStore } from '../store';
import { Button, Alert } from '../ui';

interface LoginProps {
  onLoginSuccess: (role: 'recepcion' | 'admin') => void;
}

export function Login({ onLoginSuccess }: LoginProps) {
  const { login } = useStore();
  const [emailOrUser, setEmailOrUser] = useState('admin@gmail.com');
  const [password, setPassword] = useState('admin123');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    setLoading(true);

    setTimeout(() => {
      const result = login(emailOrUser, password);
      setLoading(false);
      if (result.success) {
        const targetRole = emailOrUser.toLowerCase().includes('admin') ? 'admin' : 'recepcion';
        onLoginSuccess(targetRole);
      } else {
        setErrorMsg(result.message || 'Credenciales incorrectas');
      }
    }, 250);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#f4eee2] px-4 py-12 relative overflow-hidden">
      {/* Elementos decorativos sutiles de fondo */}
      <div className="absolute -top-32 -left-32 w-96 h-96 bg-sand-200/50 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute -bottom-32 -right-32 w-96 h-96 bg-terra-100/40 rounded-full blur-3xl pointer-events-none" />

      <div className="w-full max-w-md bg-white rounded-3xl border border-sand-300/80 shadow-2xl p-8 relative z-10">
        {/* Cabecera y Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex h-16 w-16 items-center justify-center rounded-2xl bg-forest-900 text-sand-50 shadow-md mb-4 ring-4 ring-sand-100">
            <span className="font-display font-bold text-2xl tracking-tight">TS</span>
          </div>

          <h1 className="font-display text-2xl font-bold text-forest-900 tracking-tight">
            Torre Satori PMS
          </h1>
          <p className="text-xs text-ink-soft mt-1 flex items-center justify-center gap-1.5 font-medium">
            <Coffee size={13} className="text-terra-600" />
            Hotel Boutique & Experiencia de Café · Sevilla, Valle
          </p>
        </div>

        {errorMsg && (
          <div className="mb-5">
            <Alert tone="bad" title="Error de autenticación">{errorMsg}</Alert>
          </div>
        )}

        {/* Formulario Estándar */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-ink-soft mb-1.5">
              Usuario o Correo
            </label>
            <div className="relative">
              <Mail size={17} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-ink-soft" />
              <input
                type="text"
                value={emailOrUser}
                onChange={(e) => setEmailOrUser(e.target.value)}
                placeholder="admin@gmail.com"
                required
                className="w-full h-11 pl-10 pr-3 rounded-xl border border-sand-300 bg-sand-50/50 text-sm text-ink placeholder:text-sand-300 focus:outline-none focus:ring-2 focus:ring-forest-800 focus:border-transparent transition"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-ink-soft mb-1.5">
              Contraseña
            </label>
            <div className="relative">
              <Lock size={17} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-ink-soft" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                className="w-full h-11 pl-10 pr-3 rounded-xl border border-sand-300 bg-sand-50/50 text-sm text-ink placeholder:text-sand-300 focus:outline-none focus:ring-2 focus:ring-forest-800 focus:border-transparent transition"
              />
            </div>
          </div>

          <Button
            variant="primary"
            className="w-full h-11 justify-center text-sm font-semibold mt-4 cursor-pointer shadow-md"
            icon={<ArrowRight size={17} />}
          >
            {loading ? 'Verificando...' : 'Iniciar Sesión'}
          </Button>
        </form>

        {/* Pie de seguridad */}
        <div className="mt-8 pt-4 border-t border-sand-200 text-center">
          <p className="text-[11px] text-ink-soft flex items-center justify-center gap-1.5 font-medium">
            <ShieldCheck size={14} className="text-ok" />
            Acceso seguro y protegido
          </p>
        </div>
      </div>
    </div>
  );
}
