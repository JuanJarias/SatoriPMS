import React, { useState, useRef } from 'react';
import {
  X,
  User,
  KeyRound,
  Camera,
  CheckCircle2,
  AlertCircle,
  Shield,
  Trash2,
  Upload
} from 'lucide-react';
import { useStore } from '../store';
import { Button, Alert, cn } from '../ui';

interface AccountSettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function AccountSettingsModal({ isOpen, onClose }: AccountSettingsModalProps) {
  const { currentUser, updateUserProfile, changePassword } = useStore();
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Estados de cambio de contraseña
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passwordMsg, setPasswordMsg] = useState<{ type: 'ok' | 'bad'; text: string } | null>(null);

  // Estado de foto de perfil
  const [photoMsg, setPhotoMsg] = useState<string | null>(null);

  if (!isOpen || !currentUser) return null;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      setPhotoMsg('Por favor selecciona un archivo de imagen válido (PNG, JPG, WEBP).');
      return;
    }

    if (file.size > 3 * 1024 * 1024) {
      setPhotoMsg('La imagen no debe superar los 3 MB.');
      return;
    }

    const reader = new FileReader();
    reader.onload = (event) => {
      const base64Url = event.target?.result as string;
      updateUserProfile({ avatarUrl: base64Url });
      setPhotoMsg('Foto de perfil actualizada exitosamente.');
      setTimeout(() => setPhotoMsg(null), 3500);
    };
    reader.readAsDataURL(file);
  };

  const handleRemovePhoto = () => {
    updateUserProfile({ avatarUrl: undefined });
    setPhotoMsg('Foto de perfil eliminada.');
    setTimeout(() => setPhotoMsg(null), 3000);
  };

  const handleChangePasswordSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPasswordMsg(null);

    if (newPassword !== confirmPassword) {
      setPasswordMsg({ type: 'bad', text: 'La nueva contraseña y su confirmación no coinciden.' });
      return;
    }

    const res = changePassword(currentPassword, newPassword);
    if (res.success) {
      setPasswordMsg({ type: 'ok', text: res.message });
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } else {
      setPasswordMsg({ type: 'bad', text: res.message });
    }
  };

  const initials = currentUser.name
    .split(' ')
    .map((n) => n[0])
    .slice(0, 2)
    .join('');

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-xs animate-in fade-in duration-200">
      <div className="relative w-full max-w-lg bg-white rounded-3xl border border-sand-300 shadow-2xl p-6 sm:p-7 overflow-hidden">
        {/* Cabecera del Modal */}
        <div className="flex items-center justify-between pb-4 border-b border-sand-200">
          <div>
            <h2 className="font-display text-xl font-bold text-forest-900">
              Configuración de Perfil
            </h2>
            <p className="text-xs text-ink-soft">
              Administra tu información personal, foto y credenciales de acceso.
            </p>
          </div>
          <button
            onClick={onClose}
            className="h-8 w-8 rounded-full flex items-center justify-center text-ink-soft hover:bg-sand-100 hover:text-ink cursor-pointer transition"
          >
            <X size={18} />
          </button>
        </div>

        <div className="mt-6 space-y-6 max-h-[75vh] overflow-y-auto pr-1">
          {/* SECCIÓN 1: FOTO DE PERFIL */}
          <div className="bg-sand-50/70 p-4 rounded-2xl border border-sand-200">
            <h3 className="text-xs font-bold uppercase tracking-wider text-forest-900 mb-3 flex items-center gap-1.5">
              <Camera size={14} className="text-terra-600" />
              Foto de Perfil
            </h3>

            <div className="flex items-center gap-4">
              {/* Avatar Preview */}
              <div className="relative group">
                <div className="h-20 w-20 rounded-full overflow-hidden border-2 border-forest-800 shadow-sm bg-forest-900 flex items-center justify-center text-white text-xl font-bold">
                  {currentUser.avatarUrl ? (
                    <img
                      src={currentUser.avatarUrl}
                      alt={currentUser.name}
                      className="h-full w-full object-cover"
                    />
                  ) : (
                    <span>{initials}</span>
                  )}
                </div>
              </div>

              {/* Botones de acción para foto */}
              <div className="space-y-1.5 flex-1">
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileChange}
                  accept="image/png, image/jpeg, image/webp"
                  className="hidden"
                />

                <div className="flex flex-wrap gap-2">
                  <Button
                    type="button"
                    variant="primary"
                    className="h-8 text-xs cursor-pointer px-3"
                    icon={<Upload size={13} />}
                    onClick={() => fileInputRef.current?.click()}
                  >
                    Subir nueva foto
                  </Button>

                  {currentUser.avatarUrl && (
                    <Button
                      type="button"
                      variant="secondary"
                      className="h-8 text-xs cursor-pointer px-2.5 text-bad hover:bg-bad-bg/40"
                      icon={<Trash2 size={13} />}
                      onClick={handleRemovePhoto}
                    >
                      Quitar
                    </Button>
                  )}
                </div>

                <p className="text-[11px] text-ink-soft">
                  Recomendado: imagen cuadrada JPG, PNG o WebP de hasta 3 MB.
                </p>
              </div>
            </div>

            {photoMsg && (
              <p className="mt-2.5 text-xs text-ok font-semibold flex items-center gap-1">
                <CheckCircle2 size={13} /> {photoMsg}
              </p>
            )}
          </div>

          {/* SECCIÓN 2: INFORMACIÓN DE LA CUENTA */}
          <div className="bg-sand-50/70 p-4 rounded-2xl border border-sand-200">
            <h3 className="text-xs font-bold uppercase tracking-wider text-forest-900 mb-3 flex items-center gap-1.5">
              <User size={14} className="text-terra-600" />
              Datos del Usuario
            </h3>

            <div className="grid grid-cols-2 gap-3 text-xs">
              <div>
                <span className="block text-ink-soft text-[11px]">Nombre Completo</span>
                <span className="font-semibold text-ink">{currentUser.name}</span>
              </div>
              <div>
                <span className="block text-ink-soft text-[11px]">Rol Asignado</span>
                <span className="font-semibold text-forest-800 capitalize">
                  {currentUser.role === 'admin' ? 'Administrador' : 'Recepcionista'}
                </span>
              </div>
              <div className="col-span-2">
                <span className="block text-ink-soft text-[11px]">Correo Institucional</span>
                <span className="font-medium text-ink">{currentUser.email}</span>
              </div>
            </div>
          </div>

          {/* SECCIÓN 3: CAMBIAR CONTRASEÑA */}
          <div className="bg-sand-50/70 p-4 rounded-2xl border border-sand-200">
            <h3 className="text-xs font-bold uppercase tracking-wider text-forest-900 mb-3 flex items-center gap-1.5">
              <KeyRound size={14} className="text-terra-600" />
              Cambiar Contraseña
            </h3>

            {passwordMsg && (
              <div className="mb-3">
                <Alert
                  tone={passwordMsg.type}
                  title={passwordMsg.type === 'ok' ? 'Contraseña actualizada' : 'Error'}
                >
                  {passwordMsg.text}
                </Alert>
              </div>
            )}

            <form onSubmit={handleChangePasswordSubmit} className="space-y-3">
              <div>
                <label className="block text-[11px] font-semibold text-ink-soft mb-1">
                  Contraseña Actual
                </label>
                <input
                  type="password"
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                  placeholder="Ingresa tu contraseña actual"
                  required
                  className="w-full h-9 px-3 rounded-lg border border-sand-300 bg-white text-xs text-ink focus:outline-none focus:ring-2 focus:ring-forest-800"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-semibold text-ink-soft mb-1">
                    Nueva Contraseña
                  </label>
                  <input
                    type="password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="Mínimo 6 caracteres"
                    required
                    className="w-full h-9 px-3 rounded-lg border border-sand-300 bg-white text-xs text-ink focus:outline-none focus:ring-2 focus:ring-forest-800"
                  />
                </div>

                <div>
                  <label className="block text-[11px] font-semibold text-ink-soft mb-1">
                    Confirmar Nueva
                  </label>
                  <input
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Repite la nueva contraseña"
                    required
                    className="w-full h-9 px-3 rounded-lg border border-sand-300 bg-white text-xs text-ink focus:outline-none focus:ring-2 focus:ring-forest-800"
                  />
                </div>
              </div>

              <div className="pt-2">
                <Button
                  variant="primary"
                  className="h-9 text-xs font-semibold cursor-pointer w-full justify-center"
                >
                  Guardar nueva contraseña
                </Button>
              </div>
            </form>
          </div>
        </div>

        {/* Pie del modal */}
        <div className="mt-5 pt-3 border-t border-sand-200 flex justify-end">
          <Button variant="secondary" onClick={onClose} className="h-9 text-xs">
            Cerrar
          </Button>
        </div>
      </div>
    </div>
  );
}
