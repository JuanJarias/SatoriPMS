import fs from 'node:fs';
import { test, expect, Page } from '@playwright/test';

async function loginAs(page: Page, username: string, password: string) {
  await page.goto('/');
  await page.getByPlaceholder('Usuario (ej. admin o recepcion)').fill(username);
  await page.getByPlaceholder('••••••••').fill(password);
  await page.getByRole('button', { name: 'Iniciar Sesión' }).click();
}

test.describe('Torre Satori PMS — E2E Real contra FastAPI + PostgreSQL', () => {
  test('Login JWT rechaza clave errónea, persiste F5 y aplica RBAC Recepción vs Admin', async ({ page }) => {
    // 1. Login inválido -> alerta real de la API
    await loginAs(page, 'admin', 'clave_incorrecta_999');
    await expect(page.getByText('Error de autenticación')).toBeVisible();

    // 2. Login válido como Administrador
    await loginAs(page, 'admin', 'admin123');
    await expect(page.getByRole('heading', { name: 'Resumen del Hotel' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Finanzas & Egresos' })).toBeVisible();

    // 3. F5 mantiene la sesión JWT vía /api/v1/auth/me
    await page.reload();
    await expect(page.getByRole('heading', { name: 'Resumen del Hotel' })).toBeVisible();

    // 4. Logout y login como Recepcionista: vistas Admin ocultas por RBAC
    await page.getByRole('button', { name: 'Cerrar Sesión' }).click();
    await expect(page.getByRole('button', { name: 'Iniciar Sesión' })).toBeVisible();

    await loginAs(page, 'recepcion', 'recepcion123');
    await expect(page.getByRole('button', { name: 'Habitaciones' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Finanzas & Egresos' })).toHaveCount(0);
    await expect(page.getByRole('button', { name: 'Recepcionistas' })).toHaveCount(0);
    await expect(page.getByRole('button', { name: 'Logs Auditoría' })).toHaveCount(0);

    await page.getByRole('button', { name: 'Habitaciones' }).click();
    await expect(page.getByText('Edición de inventario: Solo Administrador')).toBeVisible();
    await expect(page.getByRole('button', { name: /Agregar habitación/i })).toHaveCount(0);
  });

  test('Habitaciones semilla 1–9 y edición de número persistente sin colisión Room.id', async ({ page }) => {
    await loginAs(page, 'admin', 'admin123');
    await page.getByRole('button', { name: 'Habitaciones' }).click();

    await expect(page.getByText('Todas · 9')).toBeVisible();
    await expect(page.getByText('101')).toHaveCount(0);

    // Editar Habitación 9 -> número '90' -> F5 -> restaurar a '9'
    const editButtons = page.getByRole('button', { name: 'Editar' });
    await expect(editButtons).toHaveCount(9);
    await editButtons.nth(8).click();

    const numInput = page.getByPlaceholder('Ej. 1, 2, 10');
    await expect(numInput).toHaveValue('9');
    await numInput.fill('90');
    await page.getByRole('button', { name: 'Guardar cambios' }).click();
    await expect(page.getByText('Habitación actualizada')).toBeVisible();

    await page.reload();
    await page.getByRole('button', { name: 'Habitaciones' }).click();
    await expect(page.locator('span', { hasText: /^90$/ }).first()).toBeVisible();

    // Restaurar a '9'
    await page.getByRole('button', { name: 'Editar' }).nth(8).click();
    await page.getByPlaceholder('Ej. 1, 2, 10').fill('9');
    await page.getByRole('button', { name: 'Guardar cambios' }).click();
    await expect(page.getByText('Habitación actualizada')).toBeVisible();
  });

  test('Reserva manual, persistencia F5, rechazo GiST 409 por solapamiento y cancelación RN-03', async ({ page }) => {
    await loginAs(page, 'recepcion', 'recepcion123');
    await page.getByRole('button', { name: 'Reservas' }).click();

    // 1. Crear reserva manual para fechas futuras aisladas
    await page.getByRole('button', { name: 'Nueva reserva manual' }).click();
    const dateInputs = page.locator('input[type="date"]');
    await dateInputs.nth(0).fill('2028-03-10');
    await dateInputs.nth(1).fill('2028-03-12');
    await page.getByRole('button', { name: 'Continuar' }).click();

    await page.getByPlaceholder('Ej. Laura Gómez').fill('Playwright Huésped E2E');
    await page.getByPlaceholder('+57 310 555 0123').fill('+573001112233');
    await page.getByPlaceholder('CC 1.113.555.201').fill('1099888777');
    await page.getByRole('button', { name: 'Continuar' }).click();

    await page.getByRole('button', { name: 'Confirmar y Guardar Reserva' }).click();
    await expect(page.getByText('Reserva creada exitosamente')).toBeVisible();
    await expect(page.getByText('Playwright Huésped E2E', { exact: true })).toBeVisible();

    // 2. Recargar F5 y validar que sigue en PostgreSQL
    await page.reload();
    await page.getByRole('button', { name: 'Reservas' }).click();
    await expect(page.getByText('Playwright Huésped E2E').first()).toBeVisible();

    // 3. Intentar crear otra reserva solapada en misma habitación 1 -> debe devolver conflicto 409
    await page.getByRole('button', { name: 'Nueva reserva manual' }).click();
    const overlapDates = page.locator('input[type="date"]');
    await overlapDates.nth(0).fill('2028-03-11');
    await overlapDates.nth(1).fill('2028-03-13');
    await page.getByRole('button', { name: 'Continuar' }).click();
    await page.getByPlaceholder('Ej. Laura Gómez').fill('Choque Solape E2E');
    await page.getByPlaceholder('+57 310 555 0123').fill('+573002223344');
    await page.getByRole('button', { name: 'Continuar' }).click();
    await page.getByRole('button', { name: 'Confirmar y Guardar Reserva' }).click();

    await expect(page.getByText('No se pudo crear la reserva')).toBeVisible();
    await page.getByRole('dialog', { name: 'Nueva Reserva Manual' }).getByRole('button', { name: 'Cerrar' }).click();

    // 4. Limpieza: cancelar la reserva creada para dejar satoripms_test limpio
    await page.getByText('Playwright Huésped E2E').first().click();
    await page.getByRole('button', { name: 'Cancelar reserva' }).click();
    await page.getByRole('button', { name: 'Confirmar cancelación' }).click();
    await expect(page.getByText(/cancelada/i).first()).toBeVisible();
  });

  test('Tienda venta real, descarga Excel (.xlsx) y trazabilidad en Auditoría', async ({ page }) => {
    await loginAs(page, 'recepcion', 'recepcion123');
    await page.getByRole('button', { name: 'Tienda Hotel' }).click();

    await page.getByRole('button', { name: 'Agregar' }).first().click();
    await page.getByRole('button', { name: 'Pago Inmediato' }).click();
    await page.getByRole('button', { name: 'Confirmar Cobro' }).click();
    await expect(page.getByText('Venta completada')).toBeVisible();

    // Exportación real de Excel (.xlsx) como Admin y lectura de Auditoría
    await page.getByRole('button', { name: 'Cerrar Sesión' }).click();
    await loginAs(page, 'admin', 'admin123');

    await page.getByRole('button', { name: 'Reportes & Excel' }).click();
    const downloadPromise = page.waitForEvent('download');
    await page.getByRole('button', { name: /Exportar a Excel/i }).click();
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toMatch(/\.xlsx$/i);
    const savedPath = await download.path();
    expect(savedPath).toBeTruthy();
    const bytes = fs.readFileSync(savedPath!);
    expect(bytes.subarray(0, 2).toString()).toBe('PK');

    await page.getByRole('button', { name: 'Logs Auditoría' }).click();
    await expect(page.getByRole('heading', { name: 'Logs de Auditoría Inmutables' })).toBeVisible();
    await expect(page.getByText(/STORE_SALE_REGISTERED/i).first()).toBeVisible();
  });
});
