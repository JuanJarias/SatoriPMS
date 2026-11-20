# Sistema de Diseño — Presentación Final SatoriPMS (Fase 2)

Documento rector de diseño visual y especificación técnica para construir la presentación final de **Torre Satori PMS** en Figma (`1920 × 1080 px`), basado en la estructura de [SatoriPMS_PF2.pdf](SatoriPMS_PF2.pdf) (generado desde [SatoriPMS_PF2.html](SatoriPMS_PF2.html)) con paleta **café con leche (clara)** de alto contraste para proyector y lenguaje visual orientado al cliente.

---

## 1. Lienzo, Grilla y Fondo

- **Formato:** `1920 × 1080 px` (16:9).
- **Márgenes fijos en todas las diapositivas:**
  - Izquierdo y derecho: `120 px` (ancho útil: `1680 px`).
  - Superior: `95 px` (área de cabecera: `Y = 95` a `Y = 230`).
  - Inferior: `60 px` (pie de página en `Y = 995` a `Y = 1020`).
- **Grilla:** `12` columnas, `gutter = 40 px` (`103.33 px` por columna).
- **Fondo único:** Color sólido `#EDE0D4` (*Café con leche*) en todas las diapositivas, con marco perimetral sutil opcional o borde de tarjeta unificado (`radio = 16 px`, `grosor = 1.5 px`).

---

## 2. Paleta de Colores (HEX y Uso)

| Token | HEX | Uso | Contraste vs. fondo |
| :--- | :--- | :--- | :--- |
| `Canvas/Latte` | `#EDE0D4` | Fondo único de todas las diapositivas (café con leche claro) | Base |
| `Surface/Card` | `#FAF5F0` | Superficie de tarjetas principales (crema marfil) | Claro sobre latte |
| `Surface/Nested` | `#E6D5C3` | Tarjetas anidadas, encabezados de tabla, contenedores secundarios | Tono medio |
| `Surface/Espresso` | `#5C3D2E` | Tarjetas de contraste o énfasis (doble bloqueo, resumen clave) | Oscuro cálido |
| `Border/Subtle` | `#D6C2B0` | Borde de tarjetas (`1.5 px`) y líneas divisoras | Sutil |
| `Text/Primary` | `#2B1D16` | Títulos H1/H2, cifras KPI, texto principal sobre fondo claro | > 11:1 (Excelente) |
| `Text/Secondary` | `#634B3F` | Subtítulos, descripciones, pies de página y etiquetas | > 5.5:1 (Óptimo) |
| `Text/OnDark` | `#FAF5F0` | Texto principal sobre `Surface/Espresso` o `Accent/Terracotta` | > 8:1 |
| `Accent/Terracotta` | `#9C5A3C` | Acento principal: badges activos, íconos, paso destacado, barra 1 | > 4.6:1 |
| `Accent/Caramel` | `#C07A4B` | Acento secundario: isotipo Ensō, líneas de conexión, categoría 2 | Complemento |
| `Chart/Green` | `#2F6F4E` | Gráfico/estado positivo: SatoriPMS, aprobado, 0 sobreventas | > 5.2:1 |
| `Chart/SlateBlue` | `#3A5A78` | Gráfico categoría comparativa 3 / neutro técnico | > 5.8:1 |
| `Chart/BrickRed` | `#B84A39` | Gráfico/alerta: PMS comercial, riesgo crítico, P1 | > 4.7:1 |
| `Status/SuccessBg` | `#E3EFE8` | Fondo suave de tarjeta aprobada (con texto `#2F6F4E`) | Alto |
| `Status/AlertBg` | `#F6E4E0` | Fondo suave de alerta o badge de sección (con texto `#9C5A3C`) | Alto |

---

## 3. Tipografía (Google Fonts en Figma, con tildes y ñ)

- **Tipografía 1 (Títulos y KPI):** `Merriweather` (serifa editorial cálida, fiel al estilo de `SatoriPMS_PF2.pdf`, con soporte completo de español).
  - *Excepción de marca en Portada/Logo:* `Inter` Bold (`Satori`) + `Inter` Light (`PMS`), respetando el logotipo oficial.
- **Tipografía 2 (Cuerpo, tablas y etiquetas):** `Inter` (sans-serif geométrica de alta legibilidad en proyector).
- **Tamaño mínimo absoluto:** `22 px` (texto de apoyo y pies de página); el texto de cuerpo en tarjetas va entre `26` y `34 px` para que se lea en proyector.

| Estilo | Fuente | Peso | Tamaño | Interlineado | Color por defecto |
| :--- | :--- | :--- | :---: | :---: | :--- |
| `KPI` | `Merriweather` | Bold (700) | `72 px` | `80 px` | `#2B1D16` / `#9C5A3C` |
| `H1` | `Merriweather` | Bold (700) | `48 px` | `58 px` | `#2B1D16` |
| `H2` | `Inter` | Bold (700) | `28 px` | `36 px` | `#2B1D16` |
| `H3` | `Inter` | SemiBold (600) | `24 px` | `32 px` | `#2B1D16` |
| `Body` | `Inter` | Regular (400) | `22 px` | `32 px` | `#2B1D16` / `#634B3F` |
| `Label / Badge` | `Inter` | SemiBold (600) | `20 px` | `26 px` | `#9C5A3C` / `#FAF5F0` |
| `Footer / Source` | `Inter` | Regular (400) | `22 px` | `26 px` | `#634B3F` |

---

## 4. Estilos de Elementos y Componentes Reutilizables en Figma

### 4.1 Estilos de Elementos
- **Título (`Header/Title`):** `H1`, `X=120`, `Y=112`, ancho máx `1380 px`.
- **Encabezado sin etiqueta de sección:** las diapositivas no llevan el *pill* "PREGUNTA N · TEMA"; solo el título `H1` (`X=120`, `Y=112`) y los puntos de progreso. Los *pills* quedan reservados para etiquetas dentro de tarjetas (por ejemplo, *CONFIANZA* o *APROBADO*).
- **Indicador de pregunta (`Header/ProgressDots`):** 5 círculos de `36×36 px` arriba a la derecha (`X=1560..1764`, `Y=137`), activo en `#9C5A3C` texto `#FAF5F0`, completado en `#5C3D2E`, pendiente borde `#634B3F`.
- **Dato KPI (`KPI/Card`):** Fondo `#FAF5F0`, borde `#D6C2B0` `1.5 px`, radio `16 px`, padding `36 px`, ícono circular `56×56 px`, cifra `72 px` + etiqueta `22 px`.
- **Tarjeta (`Card/Base`):** Fondo `#FAF5F0`, borde `#D6C2B0` `1.5 px`, radio `16 px`, padding `32 px`, sombra suave `0 6px 20px rgba(43,29,22,0.06)`.
- **Tarjeta anidada (`Card/Nested`):** Fondo `#E6D5C3`, radio `12 px`, padding `24 px`.
- **Tabla (`Table/Row`):** Alto de fila `56 px`, encabezado `#E6D5C3`, filas alternas `#FAF5F0` y `#F4ECE4`, borde inferior `#D6C2B0` `1 px`, texto `20–22 px`.
- **Badge (`Badge/Pill`):** Radio `999 px`, padding `6×18 px`, texto `20 px` SemiBold.
- **Línea de tiempo (`Timeline/Step`) y Flujograma (`Flow/Node`):** Nodos redondeados (`radio 14 px`, `240×140 px` o `300×180 px`), conectores vectoriales de `2.5 px` en `#9C5A3C` con punta de flecha.
- **Diagrama de arquitectura (`Diagram/Node`):** Cajas agrupadas con bordes discontinuos para contenedores/servidor y líneas bidireccionales limpias sin tecnicismos excesivos.
- **Matriz / Cuadrícula (`Matrix/Cell`):** Cuatro cuadrantes con badge de severidad (`P1`–`P4`) y tiempos resaltados.
- **Gráficos (vectoriales editables en Figma):**
  - *Barras:* barras redondeadas (`radio 8 px`), etiqueta de valor directa a la derecha o encima (`22 px` Bold), sin ejes recargados.
  - *Dona:* anillo `320×320 px` (grosor `64 px`), porcentajes directos sobre cada arco y leyenda breve debajo.

### 4.2 Componentes Reutilizables (`_Sistema` en Figma)
`Header`, `Footer`, `Logo`, `Card`, `KPI`, `Badge`, `TableRow`, `Step`, `DiagramNode`, `Connector`, `Chart`.

---

## 5. Reglas de Visualización y Variedad de Composición

- Todos los gráficos muestran los valores directamente sobre barras o arcos.
- Cero datos inventados: todas las cifras provienen de [BackendAPI.md](../modulos/BackendAPI.md), [tests/backend/](../../tests/backend/README.md), las mediciones de rendimiento del 20 de noviembre de 2026, [Presupuesto.md](../Presupuesto/Presupuesto.md) y [Actividad5_Transicion_Servicio.md](../Actividades/Actividad5_Transicion_Servicio.md).
- **Alternancia de composiciones** (nunca más de 2 seguidas iguales): portada central → 3 columnas foto → divisor KPI → 5 tarjetas → 3 tarjetas impacto → bloque + 6 módulos → diagrama arquitectura → flujograma 2 pasos + KPI → 4 tarjetas + bloque lateral → línea de tiempo → 2 columnas comparativas → flujograma 8 pasos → 5 tarjetas flujo → cuadrícula seguridad → 4 KPIs → KPI gigante + 4 métricas → KPIs + dona → barras comparativas → matriz SLA → lista + tabla → 3 KPIs ROI → 2 columnas mejora → cierre de impacto.

---

## 6. Especificación Detallada por Diapositiva (22 Slides)

> Coordenadas en lienzo `1920 × 1080 px`. Márgenes: `X: 120..1800` (`W=1680`), `Y: 95..1020`. Pie de página en todas (excepto Slide 1): `Footer` con número de slide en `X=1760, Y=995` (`20 px`, `#634B3F`).

| Slide | Frame | Composición | Capas, Posición `(x, y)`, Tamaño `(w × h)` y Estilo |
| :---: | :--- | :--- | :--- |
| **01** | `Slide_01_Portada` | Portada central minimalista | `Bg` (`0,0`, `1920×1080`, `#EDE0D4`); `Logo_Enso` (`850,210`, `220×220`, `#9C5A3C` trazo `18px`); `Title_SatoriPMS` (`560,470`, `800×95`, `Inter` Black/Light `84px`, `#2B1D16` + `#9C5A3C`); `Sub_Ubicacion` (`560,585`, `800×36`, `Inter` SemiBold `22px` tracking `+4`, `#634B3F`, *"TORRE SATORI · SEVILLA"*); `Line_Accent` (`780,650`, `360×2`, `#C07A4B`); `Slogan` (`460,685`, `1000×44`, `Merriweather` Italic `28px`, `#2B1D16`). |
| **02** | `Slide_02_Equipo` | 3 columnas con foto | `Header` (`120,95`, *"EQUIPO"* + `H1` *"Equipo del proyecto"*); `Logo_Small` (`1580,100`, `220×40`); 3× `Card/Base` (`Y=260`, `W=533, H=690`, `X=120, 693, 1266`): `Photo_Circle` (`220×220`, borde `4px` `#9C5A3C`, fotos de `.antigravity/images/`); `Name` (`H2 26px`), `Badge_Role` (`#9C5A3C`, texto `#FAF5F0` `20px`), `Focus_List` (`Body 21px`, `#634B3F`: Esteban — Gobernanza y Chatbot n8n; Juan José — Negocio y App Web; Juan Felipe — Arquitectura FastAPI, Doble Bloqueo PostgreSQL 16 y Pruebas). |
| **03** | `Slide_03_Contexto` | Divisor P1 + 3 KPIs | `Header_P1` (`ProgressDots` 1 activo, `H1` *"¿Qué necesidad identificamos?"*, `Sub` *"Contexto operativo del Hotel Torre Satori (Sevilla, Valle del Cauca)"*); 3× `KPI/Card` (`Y=360`, `W=533, H=520`, `X=120, 693, 1266`): `9` habitaciones + Salgados Café, `2` canales (WhatsApp y mostrador), `0` bases de datos (libreta y hoja de cálculo). |
| **04** | `Slide_04_Necesidades` | 5 tarjetas verticales | `Header` (`H1` *"Necesidades identificadas"*); 5× `Card` (`Y=270`, `W=312, H=650`, `X=120, 462, 804, 1146, 1488`). `N-01`, `N-03`, `N-04`, `N-05` en `#FAF5F0`; `N-02` (*Riesgo de doble reserva*) destacada en `Surface/Espresso` `#5C3D2E` o `#9C5A3C` con texto `#FAF5F0`. |
| **05** | `Slide_05_Impacto` | 3 tarjetas de impacto | `Header` (`H1` *"Impacto en el negocio"*); 3× `KPI/Card` (`Y=290`, `W=533, H=600`, `X=120, 693, 1266`): **CONFIANZA** `1` sobreventa = mala reseña en Google; **INGRESO** `18 %` comisión por reserva en agencia; **TIEMPO** `25 min` promedio en registro manual en recepción. |
| **06** | `Slide_06_Objetivo` | Bloque objetivo + 6 módulos | `Header` (`H1` *"Objetivo y alcance"*); `Banner_Objetivo` (`120,250`, `1680×240`, `#5C3D2E`, texto `#FAF5F0` `Merriweather` `28px`); `Label_Modulos` (`120,530`, `20px`); 6× `Card/Base` (`Y=580`, `W=260, H=340`, gap `24px`, `X=120..1540`): Chatbot WhatsApp, Recepción y check-in, Finanzas, Tienda y Salgados Café, Reseñas, Roles y seguridad. |
| **07** | `Slide_07_Arquitectura` | Diagrama de arquitectura en un solo lienzo | `Header_P2` (`ProgressDots` 2 activo, `H1` *"Arquitectura de la solución"*); `Diagram` SVG (`120,255`, `1680×640`) con flechas bidireccionales de `4 px`: **Huésped · WhatsApp** (`0,235`, `300×170`) ↔ `Meta` ↔ **n8n · Chatbot** (`450,245`, `330×150`) ↔ **FastAPI · Reglas y seguridad** (`900,245`, `330×150`, `#5C3D2E`) ↔ **PostgreSQL 16 · Doble candado** (`1330,245`, `310×150`, `#9C5A3C`); los tres últimos dentro del contenedor discontinuo *"Servidor único · Docker Compose"* (`400,170`, `1280×300`); servicios externos **Gemini AI** (arriba de n8n) y **Wompi** (abajo de n8n); **Recepción · Aplicación web** (`900,520`) conectada a FastAPI; `Caption` (`120,912`, `1500×90`): *"Un solo cerebro central: WhatsApp y la web consultan el mismo servidor y la misma base de datos…"*. |
| **08** | `Slide_08_Sobreventas` | Diagrama de flujo (SVG) | `Header` (`H1` *"Control de sobreventas"*, `ProgressDots` 2 activo); `Diagram` SVG (`120,240`, `1680×720`) con flechas de `4 px`: **fila 1**, recorrido del viajero A: *Viajero A (elige una habitación)* → **Bloqueo temporal** (`#5C3D2E`, *dura 15 minutos*) → **Pendiente de pago** (`#9C5A3C`, *24 h con el link*) → **Confirmada** (`#E3EFE8`, *pago aprobado*); llave superior *"Mientras está en estos estados, nadie más puede tomar la habitación"*; **fila 2**, flechas discontinuas desde Bloqueo y Pendiente (*sin avance o cancela*, *no paga a tiempo*) hacia **Habitación libre de nuevo**; **fila 3**, viajero B: *Viajero B (pide las mismas fechas)* → **PostgreSQL 16** (*regla EXCLUDE GiST · ¿se cruzan las fechas?*) → **RECHAZADA** (`#F6E4E0`, *error 409*); tarjeta final **0 sobreventas** (`#E3EFE8`, *necesidad N-02*). |
| **09** | `Slide_09_Decisiones` | 4 tarjetas + bloque lateral | `Header` (`H1` *"Decisiones de diseño"*); Grid 2×2 `Card/Base` (`X=120` y `680`, `Y=270` y `600`, `W=520, H=290`): Conversación en n8n; IA solo ofrece opciones reales de BD; Pago por link externo Wompi; Stack 100 % código abierto; `Panel_Beneficio` (`1240,270`, `560×620`, `#F6E4E0`): qué gana Torre Satori (autonomía, cero datos de tarjeta, $0 licencias). |
| **10** | `Slide_10_AlcanceV1` | Divisor P3 + 2 columnas | `Header_P3` (`ProgressDots` 3 activo, `H1` *"Alcance implementado (v1.0.0)"*); 2× `Card/Base` (`Y=290`, `W=810, H=620`, `X=120` y `990`): Columna izquierda **El huésped · WhatsApp** (reserva guiada/IA, abono 50/100 %, consulta/cancelación, reseñas, hablar con recepción); Columna derecha **El hotel · Aplicación web** (dashboard, check-in/out, Salgados Café a habitación, eventos, finanzas y auditoría). |
| **11** | `Slide_11_ChatbotN8N` | Flujograma 8 pasos + concurrencia | `Header` (`H1` *"Reserva por WhatsApp (n8n)"*); Grid 4×2 de `Step` (`W=300, H=290`, `X=120, 445, 770, 1095`, `Y=280` y `600`): `1` Fechas → `2` Habitación libre → `3` Apartada 15 min (`#F6E4E0`) → `4` Personas/mascota → `5` Cotización → `6` Ley 1581 → `7` Abono Wompi → `8` Código `TS-XXXX`; `Card_Concurrencia` (`1440,280`, `360×610`, `#5C3D2E`): 2.ª solicitud simultánea → **Rechazada (409)**. |
| **12** | `Slide_12_AppWeb` | 5 tarjetas de flujo operativo | `Header` (`H1` *"Operación en aplicación web"*); 5× `Card/Base` (`Y=280`, `W=312, H=620`, `X=120..1488`): Reserva visible al instante; Check-in con documento y llaves; Pedido de Salgados Café cargado a habitación; Evento de temporada (+15 % web y WhatsApp); Bitácora de auditoría. |
| **13** | `Slide_13_Seguridad` | Cuadrícula 2×2 de seguridad | `Header` (`H1` *"Seguridad y protección de datos"*); 4× `Card/Base` (`W=810, H=300`, `X=120` y `990`, `Y=270` y `610`): **Roles y acceso** (JWT + bcrypt: Admin y Recepción); **Ley 1581** (consentimiento y datos mínimos); **Pagos seguros** (Wompi externo + firma HMAC, sin guardar tarjetas); **Auditoría inmutable** (registro de fecha, actor y acción). |
| **14** | `Slide_14_Pruebas` | 5 tarjetas KPI de validación | `Header` (`H1` *"Validación y pruebas"*); 5× `KPI/Card` (`Y=280`, `W=312, H=600`, `X=120, 462, 804, 1146, 1488`, badge `#E3EFE8` *"APROBADO"*): `37/37` servidor (`pytest`), `4/4` web E2E (Playwright), `65/65` suite del chatbot, `11/11` pasarela Wompi, `7/7` pruebas en vivo. Pie: *"Fuente: ejecución de las pruebas del repositorio (corte 19–20 nov 2026)."* |
| **15** | `Slide_15_Rendimiento` | KPI gigante + 4 métricas | `Header` (`H1` *"Concurrencia y rendimiento"*); `Card_Hero` (`120,270`, `540×630`, `#5C3D2E`, KPI `0` dobles reservas: 50 solicitudes simultáneas, 1 aceptada y 49 rechazadas con 409); Grid 2×2 (`W=540, H=300`, `X=700` y `1260`): `< 0,4 s` respuesta más lenta con 50 cotizaciones simultáneas (promedio 0,13–0,31 s; meta `< 1,5 s`); `< 1 s` restauración de un respaldo completo (≈ 9 MB); `< 0,1 s` para que una reserva nueva aparezca en la web; `< 0,05 s` emisión del código `TS-XXXX`. Pie: *"Mediciones propias del servidor (3 corridas, 20 nov 2026), sin contar la red de WhatsApp."* |
| **16** | `Slide_16_Inversion` | Divisor P4 + 3 KPIs + Dona | `Header_P4` (`ProgressDots` 4 activo, `H1` *"Inversión del proyecto"*); 3× filas KPI (`X=120, W=760`, `Y=310, 500, 690`): `600 h` ingeniería, `$24,7 M COP` inversión total, `$0` en licencias; `Chart_Donut` (`1060,290`, `680×600`, fondo `#FAF5F0`, dona `340×340`: `85 %` Construcción `#9C5A3C`, `6 %` Puesta en marcha `#C07A4B`, `9 %` Contingencia `#3A5A78`). Fuente: `Presupuesto_SatoriPMS.xlsx`. |
| **17** | `Slide_17_CostosOp` | Barras comparativas + desglose | `Header` (`H1` *"Costos de operación"*); `Chart_Bars` (`120,270`, `820×630`, `#FAF5F0`): barra **PMS comercial** `$1.369.500` (`#B84A39`) vs. **SatoriPMS** `$289.842` (`#2F6F4E`); Desglose derecha (`X=980, W=820`): 3 tarjetas (`Servidor y dominio $54.642`, `WhatsApp, IA y línea $55.200`, `Soporte 5 h/mes $180.000`) + tarjeta resumen `#5C3D2E` (`≈ $2.700 por reserva`). |
| **18** | `Slide_18_Disponibilidad` | Matriz 2×2 continuidad y SLA | `Header` (`H1` *"Disponibilidad, fallos y soporte"*); 4× `Card/Base` (`W=810, H=300`, `X=120` y `990`, `Y=270` y `610`): **Disponibilidad** (`Uptime ≥ 99,5 %`, respaldo cifrado diario `03:00 a. m.` en Cloudflare R2, restauración probada `< 1 s` con los datos actuales); **Plan ante fallos** (si falla IA → menú guiado; si falla Meta → panel web); **Soporte N1 y N2** (recepción vs. ingeniería); **Tickets y SLA** (reporte por canal de tickets: `P1 Crítico < 15 min` respuesta / `< 2 h` solución, `P2 < 45 min`, `P3 < 3 h`). |
| **19** | `Slide_19_Resultados` | Divisor P5 + Lista + Tabla | `Header_P5` (`ProgressDots` 5 activo, `H1` *"Resultados alcanzados"*); `List_Necesidades` (`120,270`, `960×620`, 5 filas `N-01`–`N-05` con check `#2F6F4E`); `Table_Indicadores` (`1120,270`, `680×620`, `#FAF5F0`): Respuesta con 50 solicitudes simultáneas `< 0,4 s`, Pruebas `37/37 · 65/65` y `11/11 · 7/7 · 4/4`, Capacitación `100 %`, Dictamen **Piloto autorizado**. |
| **20** | `Slide_20_ROI` | 3 tarjetas KPI de retorno | `Header` (`H1` *"Retorno de la inversión"*); 3× `KPI/Card` (`Y=290`, `W=533, H=560`, `X=120, 693, 1266`): `13,7` meses para recuperar inversión (`#5C3D2E` destacada), `$13 M` ahorro anual frente a PMS comercial, `3` reservas directas al mes cubren operación técnica; `Footer_Note` (`120,890`, `20px`: *"Proyección con 40 reservas/mes, tarifa promedio $180.000 COP."*). |
| **21** | `Slide_21_Mejoras` | 2 columnas (Producto / Proceso) | `Header` (`H1` *"Oportunidades de mejora"*); 2× `Card/Base` (`Y=280`, `W=810, H=620`, `X=120` y `990`): **Producto** (Wompi en producción + facturación DIAN v1.2.0, reseñas automáticas Google, alta disponibilidad multi-servidor, usabilidad con huéspedes); **Proceso** (holgura integraciones externas, trámites Meta día 1, documentación continua, pruebas concurrencia en CI). |
| **22** | `Slide_22_Cierre` | Cierre de impacto + agradecimiento | `Bg` (`#EDE0D4`); `H1_Cierre` (`120,160`, `1680×70`, `Merriweather` `52px`, *"Torre Satori · Listo para operar"*); 3× `Card_Summary` (`Y=250`, `W=533, H=300`, `X=120, 693, 1266`, `#5C3D2E`): `24/7` reservas WhatsApp, `0` sobreventas, `v1.0.0` piloto controlado; `Gracias_Title` (`120,640`, `1680×140`, `Merriweather` Bold `130 px`, *"Gracias"*) y firma `SatoriPMS · Torre Satori · Sevilla` (`120,810`, `36 px`). No incluye la sección de preguntas ni los nombres del equipo. |
