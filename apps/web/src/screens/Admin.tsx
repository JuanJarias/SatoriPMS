import React, { useState } from 'react';
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Users,
  ShieldCheck,
  FileText,
  Download,
  Plus,
  Trash2,
  Calendar,
  AlertTriangle,
  CheckCircle2,
  Lock,
  ArrowRight
} from 'lucide-react';
import { useStore, ExpenseItem, UserItem } from '../store';
import {
  PageHeader,
  Card,
  CardHeader,
  Button,
  Select,
  DateField,
  Modal,
  ConfirmModal,
  Field,
  Input,
  TableHeader,
  EmptyState,
  Alert,
  useToast,
  formatCurrency,
  cn
} from '../ui';

export function Admin({
  subview = 'dash',
  go,
}: {
  subview?: 'dash' | 'fin' | 'rep' | 'usr' | 'log';
  go: (view: string, param?: string) => void;
}) {
  const {
    role,
    rooms,
    bookings,
    expenses,
    financeSummary,
    addExpense,
    voidExpense,
    users,
    createUser,
    toggleUserActive,
    exportExcelReport,
    audit,
    products,
  } = useStore();
  const { show, node } = useToast();
  const todayIso = new Date().toISOString().slice(0, 10);

  // Modal registrar egreso
  const [expenseModalOpen, setExpenseModalOpen] = useState(false);
  const [expDate, setExpDate] = useState(todayIso);
  const [expAmount, setExpAmount] = useState('');
  const [expCat, setExpCat] = useState('Servicios públicos');
  const [expDesc, setExpDesc] = useState('');
  const [voidTarget, setVoidTarget] = useState<ExpenseItem | null>(null);

  // Modal nuevo usuario / recepcionista
  const [userModalOpen, setUserModalOpen] = useState(false);
  const [userUsername, setUserUsername] = useState('');
  const [userName, setUserName] = useState('');
  const [userPassword, setUserPassword] = useState('');
  const [userRole, setUserRole] = useState('Recepcionista');
  const [userToggleTarget, setUserToggleTarget] = useState<UserItem | null>(null);

  // Filtros de Auditoría
  const [auditModule, setAuditModule] = useState('todos');
  const [auditSearch, setAuditSearch] = useState('');

  const isAdmin = role === 'admin';

  // Cálculos financieros reales desde PostgreSQL (/api/v1/finance/summary)
  const activeExpenses = expenses.filter((e) => !e.voided);
  const totalExpenses = financeSummary?.totalExpenses ?? activeExpenses.reduce((acc, e) => acc + e.amount, 0);
  const lodgingIncome = financeSummary?.lodgingIncome ?? 0;
  const chargesIncome = financeSummary?.chargesIncome ?? 0;
  const totalIncome = financeSummary?.totalIncome ?? lodgingIncome + chargesIncome;
  const netBalance = financeSummary?.netBalance ?? totalIncome - totalExpenses;
  const occupiedCount = rooms.filter((r) => r.status === 'ocupada').length;
  const occupancyPct = rooms.length > 0 ? Math.round((occupiedCount / rooms.length) * 100) : 0;
  const activeBookingsCount = bookings.filter((b) => b.status === 'confirmada' || b.status === 'enCurso').length;

  const lowStockProducts = products.filter((p) => p.stock <= 5);

  const categories = [
    'Servicios públicos',
    'Nómina',
    'Insumos',
    'Mantenimiento',
    'Compra de tienda & Salgados Café',
    'Internet y telefonía',
    'Otros',
  ];

  const handleSaveExpense = async () => {
    const amt = Number(expAmount);
    if (!expDesc.trim() || isNaN(amt) || amt <= 0) {
      show('Datos inválidos', 'Por favor ingresa descripción y valor positivo', 'bad');
      return;
    }
    const res = await addExpense({
      date: expDate,
      amount: amt,
      category: expCat,
      desc: expDesc.trim(),
    });
    if (!res.success) {
      show('No se pudo registrar el egreso', res.message || 'Error en servidor', 'bad');
      return;
    }
    show('Egreso registrado', `${expDesc} · ${formatCurrency(amt)}`);
    setExpenseModalOpen(false);
    setExpDesc('');
    setExpAmount('');
  };

  const handleCreateUser = async () => {
    if (!userUsername.trim() || !userName.trim() || userPassword.length < 6) {
      show(
        'Faltan campos obligatorios',
        'Ingresa usuario, nombre completo y contraseña (mínimo 6 caracteres)',
        'bad'
      );
      return;
    }
    const res = await createUser({
      username: userUsername.trim(),
      name: userName.trim(),
      password: userPassword,
      role: userRole,
    });
    if (!res.success) {
      show('No se pudo crear el usuario', res.message || 'Error creando cuenta', 'bad');
      return;
    }
    show('Usuario creado', `${userName.trim()} asignado como ${userRole}`);
    setUserModalOpen(false);
    setUserUsername('');
    setUserName('');
    setUserPassword('');
    setUserRole('Recepcionista');
  };

  const handleToggleUserActive = async () => {
    if (!userToggleTarget) return;
    const res = await toggleUserActive(userToggleTarget.id, userToggleTarget.active);
    if (!res.success) {
      show('Error al actualizar usuario', res.message || 'No se pudo cambiar el estado', 'bad');
      return;
    }
    show(
      userToggleTarget.active ? 'Usuario desactivado' : 'Usuario reactivado',
      `Acceso de ${userToggleTarget.name} actualizado`
    );
    setUserToggleTarget(null);
  };

  if (!isAdmin) {
    return (
      <Card className="mx-auto max-w-md p-8 text-center mt-12">
        <Lock size={32} className="mx-auto mb-3 text-bad" />
        <h1 className="font-display text-2xl font-semibold text-forest-900">
          Acceso Restringido a Gerencia
        </h1>
        <p className="mt-2 text-ink-soft text-sm">
          Los módulos de finanzas globales, egresos, usuarios y auditoría son exclusivos del rol de Administrador.
        </p>
        <Button className="mt-5" onClick={() => go('dashboard')}>
          Volver al panel de recepción
        </Button>
      </Card>
    );
  }

  // --- SUBVIEW: RESUMEN GENERAL (a-dash) ---
  if (subview === 'dash') {
    return (
      <div>
        <PageHeader
          eyebrow="Gerencia Hotelera · Vista Ejecutiva"
          title="Resumen del Hotel"
          desc="Supervisión global de ingresos, balance operativo, inventario crítico y reputación."
          actions={
            <Button variant="secondary" onClick={() => go('a-fin')}>
              Ver flujo de finanzas
            </Button>
          }
        />

        <div className="grid grid-cols-2 gap-4 min-[1100px]:grid-cols-4">
          <Card className="p-4">
            <span className="text-xs font-medium text-ink-soft">Ocupación Actual</span>
            <p className="mt-2 font-display text-2xl font-bold text-forest-900">{occupancyPct}%</p>
            <span className="text-xs text-ink-soft">
              {occupiedCount} de {rooms.length} habitaciones · {activeBookingsCount} reserva(s) activa(s)
            </span>
          </Card>
          <Card className="p-4">
            <span className="text-xs font-medium text-ink-soft">Ingresos Totales</span>
            <p className="mt-2 font-display text-2xl font-bold text-forest-900">{formatCurrency(totalIncome)}</p>
            <span className="text-xs text-ink-soft">Hospedaje + Consumos</span>
          </Card>
          <Card className="p-4">
            <span className="text-xs font-medium text-ink-soft">Egresos & Costos</span>
            <p className="mt-2 font-display text-2xl font-bold text-forest-900">{formatCurrency(totalExpenses)}</p>
            <span className="text-xs text-ink-soft">{activeExpenses.length} comprobante(s) vigentes</span>
          </Card>
          <Card className="p-4">
            <span className="text-xs font-medium text-ink-soft">Beneficio Neto</span>
            <p className={cn('mt-2 font-display text-2xl font-bold', netBalance >= 0 ? 'text-ok' : 'text-bad')}>
              {formatCurrency(netBalance)}
            </p>
            <span className="text-xs text-ink-soft">Margen neto operativo</span>
          </Card>
        </div>

        <div className="mt-6 grid gap-6 min-[1100px]:grid-cols-[1.5fr_1fr]">
          <Card className="p-5">
            <CardHeader
              title="Desglose Financiero Real"
              hint="Consolidado de hospedaje, cargos a habitación y canales registrados en PostgreSQL"
            />
            <div className="space-y-3 pt-2 text-sm">
              <div className="border-b border-sand-200 pb-2 flex justify-between">
                <span className="font-semibold text-ink">Ingresos por Hospedaje (confirmadas / en curso)</span>
                <span className="font-bold text-forest-900">{formatCurrency(lodgingIncome)}</span>
              </div>
              <div className="border-b border-sand-200 pb-2 flex justify-between">
                <span className="font-semibold text-ink">Cargos a Habitación (Tienda & Salgados Café)</span>
                <span className="font-bold text-terra-600">{formatCurrency(chargesIncome)}</span>
              </div>
              {(financeSummary?.channels ?? []).map((c) => (
                <div key={c.channel} className="border-b border-sand-200 pb-2">
                  <div className="flex justify-between font-semibold text-ink">
                    <span>Canal: {c.channel}</span>
                    <span>{c.pct}%</span>
                  </div>
                  <div className="flex justify-between text-xs text-ink-soft mt-1">
                    <span>{c.bookings} reserva(s)</span>
                    <span>{formatCurrency(c.income)}</span>
                  </div>
                </div>
              ))}
              {(financeSummary?.channels ?? []).length === 0 && (
                <p className="text-xs text-ink-soft">Aún no hay reservas confirmadas o en curso registradas.</p>
              )}
            </div>
          </Card>

          <Card className="p-5">
            <CardHeader
              title="Inventario con Stock Bajo"
              hint="Productos que requieren reposición prioritaria"
            />
            {lowStockProducts.length === 0 ? (
              <p className="text-xs text-ink-soft">Todos los productos cuentan con existencias óptimas.</p>
            ) : (
              <ul className="divide-y divide-sand-200 text-sm">
                {lowStockProducts.map((p) => (
                  <li key={p.id} className="py-2.5 flex justify-between items-center">
                    <div>
                      <p className="font-semibold text-ink">{p.name}</p>
                      <p className="text-xs text-ink-soft">{p.category}</p>
                    </div>
                    <span className={cn('text-xs font-bold px-2 py-0.5 rounded', p.stock === 0 ? 'bg-bad-bg text-bad' : 'bg-warn-bg text-warn')}>
                      {p.stock === 0 ? 'Agotado' : `Quedan ${p.stock}`}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </Card>
        </div>
      </div>
    );
  }

  // --- SUBVIEW: FINANZAS Y EGRESOS (a-fin) ---
  if (subview === 'fin') {
    return (
      <div>
        <PageHeader
          eyebrow="Administración · Finanzas"
          title="Panel Financiero & Egresos"
          desc="Control de costos, nómina, compras de cafetería y trazabilidad auditada de egresos."
          actions={
            <Button
              variant="terra"
              icon={<Plus size={16} />}
              onClick={() => setExpenseModalOpen(true)}
            >
              Registrar nuevo egreso
            </Button>
          }
        />

        <div className="grid grid-cols-2 gap-4 min-[1100px]:grid-cols-3 mb-6">
          <Card className="p-4">
            <span className="text-xs font-medium text-ink-soft">Ingresos Brutos</span>
            <p className="mt-2 font-display text-2xl font-bold text-forest-900">{formatCurrency(totalIncome)}</p>
          </Card>
          <Card className="p-4">
            <span className="text-xs font-medium text-ink-soft">Total Egresos</span>
            <p className="mt-2 font-display text-2xl font-bold text-bad">−{formatCurrency(totalExpenses)}</p>
          </Card>
          <Card className="p-4">
            <span className="text-xs font-medium text-ink-soft">Balance Neto</span>
            <p className={cn('mt-2 font-display text-2xl font-bold', netBalance >= 0 ? 'text-ok' : 'text-bad')}>
              {formatCurrency(netBalance)}
            </p>
          </Card>
        </div>

        <Card className="overflow-hidden">
          <div className="p-4 border-b border-sand-200 flex justify-between items-center">
            <h2 className="font-display font-semibold text-forest-900 text-base">
              Movimientos de Egreso Registrados
            </h2>
            <span className="text-xs text-ink-soft">
              {expenses.length} comprobante(s)
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-sand-50">
                <tr>
                  <TableHeader>Fecha</TableHeader>
                  <TableHeader>Concepto / Detalle</TableHeader>
                  <TableHeader>Categoría</TableHeader>
                  <TableHeader right>Monto</TableHeader>
                  <TableHeader right>Acción</TableHeader>
                </tr>
              </thead>
              <tbody className="divide-y divide-sand-200">
                {expenses.map((e) => (
                  <tr
                    key={e.id}
                    className={cn('hover:bg-forest-50 transition-colors', e.voided && 'line-through opacity-50 bg-sand-50/50')}
                  >
                    <td className="px-4 py-3 text-xs">{e.date}</td>
                    <td className="px-4 py-3 font-medium text-ink">
                      {e.desc}
                      {e.voided && <span className="ml-2 text-xs text-bad font-semibold no-underline">[Anulado]</span>}
                    </td>
                    <td className="px-4 py-3 text-xs text-ink-soft">{e.category}</td>
                    <td className="px-4 py-3 text-right font-bold tabular-nums text-bad">
                      −{formatCurrency(e.amount)}
                    </td>
                    <td className="px-4 py-3 text-right">
                      {!e.voided && (
                        <button
                          type="button"
                          onClick={() => setVoidTarget(e)}
                          className="text-xs text-ink-soft hover:text-bad p-1 cursor-pointer"
                          title="Anular comprobante"
                        >
                          <Trash2 size={15} />
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>

        {/* Modal: Registrar Egreso */}
        {expenseModalOpen && (
          <Modal
            title="Registrar Nuevo Egreso"
            onClose={() => setExpenseModalOpen(false)}
            footer={
              <>
                <Button variant="secondary" onClick={() => setExpenseModalOpen(false)}>
                  Cancelar
                </Button>
                <Button variant="primary" onClick={handleSaveExpense}>
                  Guardar comprobante de egreso
                </Button>
              </>
            }
          >
            <div className="grid grid-cols-2 gap-3">
              <Field label="Fecha del comprobante">
                <DateField value={expDate} onChange={setExpDate} />
              </Field>
              <Field label="Valor en COP *">
                <Input
                  type="number"
                  value={expAmount}
                  onChange={(e) => setExpAmount(e.target.value)}
                  placeholder="Ej. 185000"
                />
              </Field>
            </div>

            <Field label="Categoría de egreso">
              <Select
                value={expCat}
                onChange={setExpCat}
                options={categories.map((c) => ({ value: c, label: c }))}
              />
            </Field>

            <Field label="Descripción / Concepto *">
              <Input
                value={expDesc}
                onChange={(e) => setExpDesc(e.target.value)}
                placeholder="Ej. Compra de grano verde Salgados Café, Arreglo bomba de agua"
              />
            </Field>

            <p className="text-xs text-ink-soft">
              Todo egreso registrado quedará formalmente asentado en los logs de auditoría de SatoriPMS.
            </p>
          </Modal>
        )}

        {/* Modal: Anular Egreso */}
        {voidTarget && (
          <ConfirmModal
            title="¿Anular este comprobante de egreso?"
            confirm="Confirmar anulación"
            danger
            onCancel={() => setVoidTarget(null)}
            onConfirm={async () => {
              const res = await voidExpense(voidTarget.id);
              if (!res.success) {
                show('Error al anular egreso', res.message || 'Intenta nuevamente', 'bad');
                return;
              }
              show('Egreso anulado', `${voidTarget.desc} marcado como anulado`);
              setVoidTarget(null);
            }}
          >
            Se anulará el egreso <strong>{voidTarget.desc} ({formatCurrency(voidTarget.amount)})</strong>.
            El registro no se borrará para preservar la trazabilidad fiscal y quedará archivado como anulado.
          </ConfirmModal>
        )}

        {node}
      </div>
    );
  }

  // --- SUBVIEW: REPORTES Y EXPORTACIÓN EXCEL (a-rep) ---
  if (subview === 'rep') {
    return (
      <div>
        <PageHeader
          eyebrow="Administración · Informes"
          title="Reportes Operativos & Financieros"
          desc="Consolidación de ventas, ocupación y exportación de datos a Excel / CSV para contabilidad."
          actions={
            <Button
              variant="secondary"
              icon={<Download size={16} />}
              onClick={async () => {
                const res = await exportExcelReport();
                if (res.success) {
                  show('Archivo generado', 'Reporte Excel descargado desde el servidor');
                } else {
                  show('Error al exportar', res.message || 'No se pudo descargar el Excel', 'bad');
                }
              }}
            >
              Exportar a Excel (.xlsx)
            </Button>
          }
        />

        <div className="grid gap-6 min-[1100px]:grid-cols-2">
          <Card className="p-5">
            <CardHeader title="Catálogo Actual en Inventario" hint="Precios y stock en tiempo real desde base de datos" />
            <div className="space-y-3 pt-2 text-sm">
              {products.length === 0 ? (
                <p className="text-xs text-ink-soft">No hay productos registrados en tienda.</p>
              ) : (
                products.slice(0, 8).map((item) => (
                  <div key={item.id} className="flex justify-between items-center border-b border-sand-200 pb-2">
                    <div>
                      <p className="font-semibold text-ink">{item.name}</p>
                      <p className="text-xs text-ink-soft">
                        {item.category} · Stock: {item.stock} uds.
                      </p>
                    </div>
                    <span className="font-bold text-forest-900">{formatCurrency(item.price)}</span>
                  </div>
                ))
              )}
            </div>
          </Card>

          <Card className="p-5">
            <CardHeader title="Canales de Reserva (Desglose Real)" />
            <div className="space-y-3 pt-2 text-sm">
              {(financeSummary?.channels ?? []).length === 0 ? (
                <p className="text-xs text-ink-soft">Aún no hay reservas confirmadas para calcular participación por canal.</p>
              ) : (
                (financeSummary?.channels ?? []).map((c) => (
                  <div key={c.channel} className="border-b border-sand-200 pb-2">
                    <div className="flex justify-between font-semibold text-ink">
                      <span>{c.channel}</span>
                      <span className="text-forest-800">{c.pct}%</span>
                    </div>
                    <div className="flex justify-between text-xs text-ink-soft mt-1">
                      <span>{c.bookings} reserva(s) confirmada(s)</span>
                      <span>{formatCurrency(c.income)}</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </Card>
        </div>
        {node}
      </div>
    );
  }

  // --- SUBVIEW: USUARIOS & RECEPCIONISTAS (a-usr) ---
  if (subview === 'usr') {
    return (
      <div>
        <PageHeader
          eyebrow="Administración · Seguridad y Accesos"
          title="Gestión de Recepcionistas"
          desc="Administra al equipo de recepción y camarería autorizado para operar el PMS."
          actions={
            <Button
              variant="terra"
              icon={<Plus size={16} />}
              onClick={() => setUserModalOpen(true)}
            >
              Nuevo recepcionista
            </Button>
          }
        />

        <Card className="overflow-hidden">
          <table className="w-full text-left text-sm">
            <thead className="bg-sand-50">
              <tr>
                <TableHeader>Nombre</TableHeader>
                <TableHeader>Usuario</TableHeader>
                <TableHeader>Rol</TableHeader>
                <TableHeader>Último acceso</TableHeader>
                <TableHeader>Estado</TableHeader>
                <TableHeader right>Acción</TableHeader>
              </tr>
            </thead>
            <tbody className="divide-y divide-sand-200">
              {users.map((u) => (
                <tr key={u.id} className="hover:bg-forest-50 transition-colors">
                  <td className="px-4 py-3 font-semibold text-ink">
                    {u.name}
                  </td>
                  <td className="px-4 py-3 text-xs font-mono text-ink-soft">@{u.username}</td>
                  <td className="px-4 py-3 text-xs font-medium">{u.role}</td>
                  <td className="px-4 py-3 text-xs text-ink-soft">{u.last}</td>
                  <td className="px-4 py-3">
                    <span className={cn('text-xs font-semibold px-2 py-0.5 rounded-full', u.active ? 'bg-ok-bg text-ok' : 'bg-sand-200 text-ink-soft')}>
                      {u.active ? '● Activo' : '○ Inactivo'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <Button
                      variant="secondary"
                      className="h-8 text-xs px-2.5"
                      onClick={() => setUserToggleTarget(u)}
                    >
                      {u.active ? 'Desactivar' : 'Reactivar'}
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>

        {/* Modal: Crear Recepcionista / Usuario */}
        {userModalOpen && (
          <Modal
            title="Nuevo Usuario PMS"
            onClose={() => setUserModalOpen(false)}
            footer={
              <>
                <Button variant="secondary" onClick={() => setUserModalOpen(false)}>
                  Cancelar
                </Button>
                <Button variant="primary" onClick={handleCreateUser}>
                  Crear usuario
                </Button>
              </>
            }
          >
            <Field label="Usuario (username para iniciar sesión) *">
              <Input
                value={userUsername}
                onChange={(e) => setUserUsername(e.target.value)}
                placeholder="Ej. julian.perez"
              />
            </Field>
            <Field label="Nombre completo *">
              <Input
                value={userName}
                onChange={(e) => setUserName(e.target.value)}
                placeholder="Ej. Julián Pérez"
              />
            </Field>
            <Field label="Contraseña inicial (mínimo 6 caracteres) *">
              <Input
                type="password"
                value={userPassword}
                onChange={(e) => setUserPassword(e.target.value)}
                placeholder="••••••••"
              />
            </Field>
            <Field label="Rol asignado">
              <Select
                value={userRole}
                onChange={setUserRole}
                options={[
                  { value: 'Recepcionista', label: 'Recepcionista' },
                  { value: 'Administrador', label: 'Administrador' },
                ]}
              />
            </Field>
          </Modal>
        )}

        {/* Modal: Desactivar / Reactivar Usuario */}
        {userToggleTarget && (
          <ConfirmModal
            title={`¿${userToggleTarget.active ? 'Desactivar' : 'Reactivar'} a ${userToggleTarget.name}?`}
            confirm={userToggleTarget.active ? 'Desactivar' : 'Reactivar'}
            danger={userToggleTarget.active}
            onCancel={() => setUserToggleTarget(null)}
            onConfirm={handleToggleUserActive}
          >
            {userToggleTarget.active
              ? `El recepcionista ${userToggleTarget.name} no podrá iniciar sesión en SatoriPMS. Su historial y registros se conservarán intactos.`
              : `Se restaurarán los permisos de acceso para ${userToggleTarget.name}.`}
          </ConfirmModal>
        )}

        {node}
      </div>
    );
  }

  // --- SUBVIEW: AUDITORÍA INMUTABLE (a-log) ---
  if (subview === 'log') {
    const modules = Array.from(new Set(audit.map((a) => a.module)));

    const filteredAudit = audit.filter((item) => {
      const matchesMod = auditModule === 'todos' || item.module === auditModule;
      const q = auditSearch.trim().toLowerCase();
      const matchesSearch = !q || item.action.toLowerCase().includes(q) || item.user.toLowerCase().includes(q);
      return matchesMod && matchesSearch;
    });

    return (
      <div>
        <PageHeader
          eyebrow="Administración · Seguridad y Cumplimiento"
          title="Logs de Auditoría Inmutables"
          desc="Trazabilidad histórica de todas las acciones operativas en Torre Satori PMS."
        />

        <Card className="p-4 mb-5">
          <div className="grid gap-3 sm:grid-cols-2">
            <Input
              value={auditSearch}
              onChange={(e) => setAuditSearch(e.target.value)}
              placeholder="Buscar acción, habitación o usuario…"
            />
            <Select
              value={auditModule}
              onChange={setAuditModule}
              options={[
                { value: 'todos', label: 'Todos los módulos' },
                ...modules.map((m) => ({ value: m, label: m })),
              ]}
            />
          </div>
        </Card>

        <Card className="overflow-hidden">
          <table className="w-full text-left text-sm">
            <thead className="bg-sand-50">
              <tr>
                <TableHeader>Fecha y Hora</TableHeader>
                <TableHeader>Usuario</TableHeader>
                <TableHeader>Rol</TableHeader>
                <TableHeader>Acción Realizada</TableHeader>
                <TableHeader>Módulo</TableHeader>
              </tr>
            </thead>
            <tbody className="divide-y divide-sand-200">
              {filteredAudit.map((a, idx) => (
                <tr key={idx} className="hover:bg-forest-50 transition-colors">
                  <td className="px-4 py-3 text-xs text-ink-soft whitespace-nowrap">{a.at}</td>
                  <td className="px-4 py-3 font-semibold text-ink">{a.user}</td>
                  <td className="px-4 py-3 text-xs">{a.role}</td>
                  <td className="px-4 py-3 text-sm">{a.action}</td>
                  <td className="px-4 py-3">
                    <span className="rounded bg-forest-100 px-2 py-0.5 text-xs font-semibold text-forest-800">
                      {a.module}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
        {node}
      </div>
    );
  }

  return null;
}
