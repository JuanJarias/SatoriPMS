#!/usr/bin/env python3
import json
import uuid

def reorganize():
    with open('flows/n8n/V8_ChatbotReservas.json', 'r', encoding='utf-8') as f:
        flow = json.load(f)

    nodes = flow['nodes']
    connections = flow['connections']

    # 1. Remove dead nodes
    dead_nodes = {'H Confirmar Bloqueo', 'H En Construcción', '¿IA Fechas Válidas?'}
    nodes = [n for n in nodes if n['name'] not in dead_nodes]
    nodes_dict = {n['name']: n for n in nodes}

    # Clean up references in connections to dead nodes
    for src in list(connections.keys()):
        if src in dead_nodes:
            del connections[src]
        else:
            for conn_type in list(connections[src].keys()):
                for branch in connections[src][conn_type]:
                    branch[:] = [t for t in branch if t.get('node') not in dead_nodes]

    # In 'Enrutar por Estado1', fallback output (branch 16) redirects to H Menú Principal
    enrutar_node = nodes_dict.get('Enrutar por Estado1')
    if enrutar_node:
        enrutar_node['parameters']['options']['renameFallbackOutput'] = 'Ruta Desconocida (Menú)'
        if 'Enrutar por Estado1' in connections:
            branches = connections['Enrutar por Estado1'].get('main', [])
            if len(branches) == 16:
                branches.append([{"node": "H Menú Principal", "type": "main", "index": 0}])
            elif len(branches) == 17:
                branches[16] = [{"node": "H Menú Principal", "type": "main", "index": 0}]
            connections['Enrutar por Estado1']['main'] = branches

    # 2. Update H F1 Inicio IA
    nodes_dict['H F1 Inicio IA']['parameters']['jsCode'] = """const J = $input.first().json;
const wa_id = J.wa_id;
const sender_name = J.sender_name || 'Huésped';

const msg = `*Asistente Inteligente de Reservas — Satori Hotel*\\n\\n` +
            `¡Hola ${sender_name}! Puedes escribir en *un solo mensaje* todos los detalles de tu estadía.\\n\\n` +
            `*Por favor incluye en tu mensaje:*\\n` +
            `• Fechas de entrada y salida (Check-in y Check-out)\\n` +
            `• Cantidad de adultos y niños\\n` +
            `• Nombres completos de todos los huéspedes (titular y acompañantes)\\n` +
            `• Número de cédula/documento del titular\\n` +
            `• Si viajan con mascota (Sí / No)\\n\\n` +
            `*Ejemplo:* «Quiero reservar del 2026-11-20 al 2026-11-23 para 2 adultos y 1 niño, sin mascota. Mi nombre es Juan Gómez, cédula 1094900111, y me acompañan María Gómez y Pedrito Gómez.»\\n\\n` +
            `*Aviso de Privacidad (Ley 1581 de 2012):* Al suministrar tus datos autorizas a Torre Satori para tratarlos exclusivamente en la gestión de tu reserva.\\n\\n` +
            `Escribe *menú* en cualquier momento para volver al inicio.`;

return [{
    json: {
        wa_id,
        sender_name,
        response_text: msg,
        session: {
            state: 'ia_reserva',
            step: 'esperando_datos',
            agent_active: false,
            wa_id,
            sender_name,
            ia_draft: {}
        }
    }
}];"""

    # 3. Update H Normalizar IA
    nodes_dict['H Normalizar IA']['parameters']['jsCode'] = """const J = $input.first().json;
const S = J.session || {};
const draft = S.ia_draft || {};
const text = String(J.message_text || '').trim();
const normalized = text.toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g, '').trim();

const keep = (newDraft, nextStep) => ({
    state: 'ia_reserva',
    step: nextStep,
    agent_active: false,
    wa_id: J.wa_id,
    sender_name: J.sender_name,
    ia_draft: newDraft
});

const reset = () => ({
    state: 'menu',
    step: 'esperando_opcion',
    agent_active: false,
    wa_id: J.wa_id,
    sender_name: J.sender_name,
    reservation_draft: {}
});

const reply = (msg, newSession, extra = {}) => [{
    json: Object.assign({
        wa_id: J.wa_id,
        sender_name: J.sender_name,
        response_text: msg,
        session: newSession,
        api_action: 'reply'
    }, extra)
}];

// PASO 1: Procesar mensaje inicial con datos completos
if (S.step === 'esperando_datos' || !S.step) {
    const today = new Date(Date.now() - 5 * 3600 * 1000).toISOString().slice(0, 10);
    const prompt = `Eres un asistente de reservas de hotel. Extrae los datos de reserva del texto del usuario en formato JSON estricto.
Fecha de referencia hoy (Colombia): ${today}.
Propiedades requeridas:
- checkIn: string YYYY-MM-DD o null si no se menciona
- checkOut: string YYYY-MM-DD o null si no se menciona
- adults: número entero >= 1 (por defecto 1 si no se aclara)
- children: número entero >= 0 (por defecto 0)
- hasPet: boolean (true si menciona mascota/perro/gato, false si no)
- guestName: string con el nombre del titular si se menciona, o null
- guestDocument: string con cédula/identificación si se menciona, o null
- companions: string con acompañantes si se mencionan, o ""
- missingInfo: array de strings con campos esenciales faltantes entre: ["fechas", "nombre", "identificacion"]
- summary: resumen breve y amable en español de lo entendido.

Texto del usuario: "${text}"`;

    return [{
        json: Object.assign({}, J, {
            api_action: 'gemini_ia',
            geminiRequest: {
                contents: [{ parts: [{ text: prompt }] }],
                generationConfig: { temperature: 0.1, responseMimeType: 'application/json' }
            },
            session: keep(draft, 'interpretando')
        })
    }];
}

// PASO 2: Confirmación o Corrección de los datos interpretados
if (S.step === 'confirmar_datos') {
    const isConfirm = ['si', 'sí', 'correcto', 'de acuerdo', 'ok', 'yes', 'claro', 'dale', 'confirmo', 'así es', 'asi es'].some(k => normalized === k || normalized.startsWith(k + ' ') || normalized.endsWith(' ' + k));
    
    if (isConfirm) {
        // Proceder a buscar habitaciones disponibles en la API
        return [{
            json: Object.assign({}, J, {
                api_action: 'availability',
                checkIn: draft.checkIn,
                checkOut: draft.checkOut,
                adults: draft.adults || 1,
                children: draft.children || 0,
                pet: Boolean(draft.hasPet),
                session: keep(draft, 'buscando_disponibilidad')
            })
        }];
    } else {
        // El usuario envía correcciones
        const today = new Date(Date.now() - 5 * 3600 * 1000).toISOString().slice(0, 10);
        const prompt = `Eres un asistente de reservas de hotel. El usuario tenía este borrador de reserva:
${JSON.stringify(draft)}
Y ahora envía este mensaje de corrección o ajuste: "${text}".
Fecha de referencia hoy (Colombia): ${today}.
Actualiza los datos del borrador con las correcciones del usuario en formato JSON estricto:
- checkIn: string YYYY-MM-DD
- checkOut: string YYYY-MM-DD
- adults: número entero >= 1
- children: número entero >= 0
- hasPet: boolean
- guestName: string (nombre del titular)
- guestDocument: string (cédula)
- companions: string (acompañantes)
- summary: resumen breve y amable en español de los cambios aplicados.`;

        return [{
            json: Object.assign({}, J, {
                api_action: 'gemini_ia',
                geminiRequest: {
                    contents: [{ parts: [{ text: prompt }] }],
                    generationConfig: { temperature: 0.1, responseMimeType: 'application/json' }
                },
                session: keep(draft, 'corrigiendo')
            })
        }];
    }
}

// PASO 3: Selección de una o varias habitaciones
if (S.step === 'ia_seleccion_habitacion') {
    const rooms = Array.isArray(draft.availableRooms) ? draft.availableRooms : [];
    const nums = (text.match(/\\d+/g) || []).map(Number);
    const chosenRooms = [];

    for (const n of nums) {
        const found = rooms.find((r, idx) => idx + 1 === n || Number(r.number) === n || Number(r.id) === n);
        if (found && !chosenRooms.some(cr => cr.id === found.id)) {
            chosenRooms.push(found);
        }
    }

    if (!chosenRooms.length) {
        return reply('No encontré esa opción de habitación. Por favor responde con el número o números de la lista (ej: *1* o *1, 2*) o escribe *menú* para cancelar.', S);
    }

    const newDraft = Object.assign({}, draft, { selectedRooms: chosenRooms, chosenCount: chosenRooms.length });
    
    // Emitir un item por cada habitación para que la API las bloquee todas
    return chosenRooms.map(room => ({
        json: Object.assign({}, J, {
            api_action: 'lock',
            roomId: room.id,
            checkIn: draft.checkIn,
            checkOut: draft.checkOut,
            lockRoom: room,
            session: keep(newDraft, 'bloqueando')
        })
    }));
}

// PASO 4: Selección de Modalidad de Pago
if (S.step === 'ia_pago') {
    let opt = null;
    if (['1', '100', '100%', 'total', 'pago_100', 'completo'].some(k => normalized.includes(k))) opt = 'full';
    else if (['2', '50', '50%', 'mitad', 'anticipo', 'pago_50'].some(k => normalized.includes(k))) opt = 'deposit';
    else if (['3', 'cancelar', 'no'].some(k => normalized.includes(k))) {
        return reply('Reserva cancelada. Los bloqueos de las habitaciones fueron liberados. Escribe *menú* para volver al inicio.', reset());
    }

    if (!opt) {
        return reply('Selecciona una opción válida:\\n1. Pagar 100%\\n2. Pagar 50% de anticipo\\n3. Cancelar', S);
    }

    const lockTokens = Array.isArray(draft.lockTokens) ? draft.lockTokens : [];
    const payload = {
        waId: J.wa_id,
        guestName: draft.guestName || J.sender_name || 'Huésped',
        guestDocument: draft.guestDocument || '12345678',
        companions: draft.companions || '',
        checkIn: draft.checkIn,
        checkOut: draft.checkOut,
        adults: Number(draft.adults || 1),
        children: Number(draft.children || 0),
        hasPet: Boolean(draft.hasPet),
        rooms: lockTokens.map(lt => ({ roomId: lt.roomId, lockToken: lt.lockToken })),
        paymentOption: opt
    };

    const optMsg = opt === 'deposit' ? 'el 50% de anticipo' : 'el 100% total';
    return [{
        json: Object.assign({}, J, {
            api_action: 'confirm',
            payload,
            session: keep(Object.assign({}, draft, { payload, paymentOption: opt }), 'confirmando'),
            response_text: `Confirmando tu reserva con ${optMsg}...`
        })
    }];
}

return reply('Escribe *menú* para volver al inicio.', reset());"""

    # 4. Update H Procesar Gemini IA
    nodes_dict['H Procesar Gemini IA']['parameters']['jsCode'] = """const geminiRes = $input.first().json || {};
const source = $('H Normalizar IA').first().json;
const wa_id = source.wa_id;
const sender_name = source.sender_name || 'Huésped';

let parsed = {};
try {
    const rawText = geminiRes.candidates?.[0]?.content?.parts?.[0]?.text || '{}';
    parsed = JSON.parse(rawText.replace(/^```json\\s*|```$/g, '').trim());
} catch (e) {
    parsed = {};
}

const checkIn = parsed.checkIn;
const checkOut = parsed.checkOut;
const adults = Number(parsed.adults || 1);
const children = Number(parsed.children || 0);
const hasPet = Boolean(parsed.hasPet);
const guestName = parsed.guestName || sender_name;
const guestDocument = parsed.guestDocument || '';
const companions = parsed.companions || '';

if (!checkIn || !checkOut || checkIn >= checkOut) {
    const msg = `*Entendí parte de tu mensaje:*\\n` +
                `${parsed.summary || 'Necesito que me indiques las fechas de estadía.'}\\n\\n` +
                `*Me faltan las fechas de entrada y salida.*\\n` +
                `Por favor indícalas con formato AAAA-MM-DD (ej: *2026-11-20 al 2026-11-23*) o escribe *menú* para ir al inicio.`;
    return [{
        json: {
            wa_id,
            sender_name,
            response_text: msg,
            session: { state: 'ia_reserva', step: 'esperando_datos', agent_active: false, wa_id, sender_name, ia_draft: Object.assign({}, parsed, { guestName, guestDocument }) }
        }
    }];
}

const nights = Math.max(1, Math.round((new Date(checkOut) - new Date(checkIn)) / 86400000));
const draft = {
    checkIn,
    checkOut,
    nights,
    adults,
    children,
    hasPet,
    guestName,
    guestDocument,
    companions
};

const compMsg = companions ? companions : 'Ninguno';
const petMsg = hasPet ? 'Sí' : 'No';
const docMsg = guestDocument ? guestDocument : 'Pendiente';

const msg = `*He interpretado los siguientes datos para tu reserva:*\\n\\n` +
            `*Fechas:* del ${checkIn} al ${checkOut} (${nights} ${nights === 1 ? 'noche' : 'noches'})\\n` +
            `*Huéspedes:* ${adults} ${adults === 1 ? 'adulto' : 'adultos'}${children > 0 ? ` y ${children} ${children === 1 ? 'niño' : 'niños'}` : ''}\\n` +
            `*Mascota:* ${petMsg}\\n` +
            `*Titular:* ${guestName} (Cédula: ${docMsg})\\n` +
            `*Acompañantes:* ${compMsg}\\n\\n` +
            `¿Esta información es correcta?\\n` +
            `Responde *Sí* para ver las habitaciones disponibles, o escribe las correcciones si deseas cambiar algo.`;

return [{
    json: {
        wa_id,
        sender_name,
        response_text: msg,
        session: { state: 'ia_reserva', step: 'confirmar_datos', agent_active: false, wa_id, sender_name, ia_draft: draft }
    }
}];"""

    # 5. Update H Mostrar Habitaciones IA
    nodes_dict['H Mostrar Habitaciones IA']['parameters']['jsCode'] = """const source = $('H Normalizar IA').first().json;
const raw = $input.all().map(i => i.json);
const rooms = raw.length === 1 && Array.isArray(raw[0]) ? raw[0] : raw;
const wa_id = source.wa_id;
const sender_name = source.sender_name;
const draft = source.session.ia_draft || {};

if (!rooms.length || (rooms.length === 1 && !rooms[0].id)) {
    return [{
        json: {
            wa_id,
            sender_name,
            response_text: `No encontré habitaciones disponibles del *${draft.checkIn}* al *${draft.checkOut}* para esa cantidad de huéspedes. Escribe *menú* para intentar con otras fechas.`,
            session: { state: 'menu', step: 'esperando_opcion', agent_active: false, wa_id, sender_name, reservation_draft: {} }
        }
    }];
}

const choices = rooms.slice(0, 8);
const lines = choices.map((r, i) => {
    const max = Number(r.maxAdultsCapacity || 0) + Number(r.childrenCapacity || 0);
    return `${i + 1}. *${r.name || r.type} #${r.number}* — $${Number(r.pricePerNight).toLocaleString('es-CO')}/noche (Hasta ${max} personas)`;
});

const msg = `*Encontré habitaciones disponibles del ${draft.checkIn} al ${draft.checkOut}:*\\n\\n` +
            `${lines.join('\\n')}\\n\\n` +
            `Por favor escribe el número de la habitación que deseas reservar (si necesitas más de una, puedes escribir los números separados por coma, ej: *1, 2*):`;

const newDraft = Object.assign({}, draft, { availableRooms: choices });

return [{
    json: {
        wa_id,
        sender_name,
        response_text: msg,
        session: { state: 'ia_reserva', step: 'ia_seleccion_habitacion', agent_active: false, wa_id, sender_name, ia_draft: newDraft }
    }
}];"""

    # 6. Update H Resumen y Pago IA
    nodes_dict['H Resumen y Pago IA']['parameters']['jsCode'] = """const requests = $('H Normalizar IA').all().map(item => item.json);
const results = $input.all().map(item => item.json);
const successful = requests.map((req, idx) => ({ req, res: results[idx] || {} })).filter(e => e.res.lockToken);

const source = requests[0];
const wa_id = source.wa_id;
const sender_name = source.sender_name;
const draft = source.session.ia_draft || {};

if (!successful.length) {
    return [{
        json: {
            wa_id,
            sender_name,
            response_text: 'No pudimos bloquear las habitaciones seleccionadas. Puede que otro huésped las haya tomado. Escribe *menú* para intentar de nuevo.',
            session: { state: 'menu', step: 'esperando_opcion', agent_active: false, wa_id, sender_name, reservation_draft: {} }
        }
    }];
}

const nights = Math.max(1, Math.round((new Date(draft.checkOut) - new Date(draft.checkIn)) / 86400000));
let baseStayTotal = 0;
let totalBaseCap = 0;
const roomNames = [];
const lockTokens = [];

successful.forEach(entry => {
    const r = entry.req.lockRoom || {};
    const nightly = Number(r.pricePerNight || 0);
    baseStayTotal += nightly * nights;
    totalBaseCap += Number(r.baseAdultsCapacity || 2);
    roomNames.push(`${r.name || r.type} #${r.number}`);
    lockTokens.push({ roomId: entry.req.roomId, lockToken: entry.res.lockToken });
});

const totalGuests = Number(draft.adults || 1) + Number(draft.children || 0);
const extraGuests = Math.max(0, totalGuests - totalBaseCap);
// Usar recargo de la primera habitación o tarifa estándar (ej: $35.000)
const extraGuestPrice = Number(successful[0].req.lockRoom?.extraGuestPrice || 35000);
const extraTotal = extraGuests * extraGuestPrice * nights;
const total = baseStayTotal + extraTotal;
const half = total / 2;

draft.lockTokens = lockTokens;
draft.baseStay = baseStayTotal;
draft.extraGuests = extraGuests;
draft.extraTotal = extraTotal;
draft.total = total;

const extraDesc = extraGuests > 0 ? `(${extraGuests} pers. x $${extraGuestPrice.toLocaleString('es-CO')} x ${nights}n = $${extraTotal.toLocaleString('es-CO')})` : 'Sin recargo';

const msg = `*Resumen de Reserva:*\\n` +
            `• *Habitación(es):* ${roomNames.join(', ')}\\n` +
            `• *Fechas:* del ${draft.checkIn} al ${draft.checkOut} (${nights} ${nights === 1 ? 'noche' : 'noches'})\\n` +
            `• *Titular:* ${draft.guestName} (Cédula: ${draft.guestDocument || 'Pendiente'})\\n` +
            `• *Huéspedes:* ${draft.adults} adultos${draft.children > 0 ? `, ${draft.children} niños` : ''}\\n` +
            `• *Tarifa base estadía:* $${baseStayTotal.toLocaleString('es-CO')}\\n` +
            `• *Recargo personas adicionales:* ${extraDesc}\\n` +
            `• *TOTAL ESTADÍA:* $${total.toLocaleString('es-CO')}\\n\\n` +
            `*Tus habitaciones están bloqueadas por 15 minutos.*\\n\\n` +
            `Selecciona cómo deseas proceder:\\n` +
            `1. *Pagar el 100% ahora:* $${total.toLocaleString('es-CO')}\\n` +
            `2. *Pagar el 50% de anticipo:* $${half.toLocaleString('es-CO')}\\n` +
            `3. *Cancelar reserva*`;

return [{
    json: {
        wa_id,
        sender_name,
        response_text: msg,
        session: { state: 'ia_reserva', step: 'ia_pago', agent_active: false, wa_id, sender_name, ia_draft: draft }
    }
}];"""

    # 7. Update ¿Acción IA? Switch rules
    nodes_dict['¿Acción IA?']['parameters']['rules']['values'] = [
        {
            "conditions": {
                "options": { "caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 3 },
                "conditions": [{ "id": "ia_g", "leftValue": "={{ $json.api_action }}", "rightValue": "gemini_ia", "operator": { "type": "string", "operation": "equals" } }],
                "combinator": "and"
            },
            "renameOutput": True,
            "outputKey": "Gemini IA"
        },
        {
            "conditions": {
                "options": { "caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 3 },
                "conditions": [{ "id": "ia_avail", "leftValue": "={{ $json.api_action }}", "rightValue": "availability", "operator": { "type": "string", "operation": "equals" } }],
                "combinator": "and"
            },
            "renameOutput": True,
            "outputKey": "Disponibilidad IA"
        },
        {
            "conditions": {
                "options": { "caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 3 },
                "conditions": [{ "id": "ia_l", "leftValue": "={{ $json.api_action }}", "rightValue": "lock", "operator": { "type": "string", "operation": "equals" } }],
                "combinator": "and"
            },
            "renameOutput": True,
            "outputKey": "Bloquear Habitación IA"
        },
        {
            "conditions": {
                "options": { "caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 3 },
                "conditions": [{ "id": "ia_c", "leftValue": "={{ $json.api_action }}", "rightValue": "confirm", "operator": { "type": "string", "operation": "equals" } }],
                "combinator": "and"
            },
            "renameOutput": True,
            "outputKey": "Confirmar Reserva"
        }
    ]

    # Connections for IA flow
    connections["H F1 Inicio IA"] = {
        "main": [
            [{"node": "Preparar Salida", "type": "main", "index": 0}]
        ]
    }
    connections["H Normalizar IA"] = {
        "main": [
            [{"node": "¿Acción IA?", "type": "main", "index": 0}]
        ]
    }
    connections["¿Acción IA?"] = {
        "main": [
            [{"node": "Gemini Asistente IA", "type": "main", "index": 0}],
            [{"node": "API Disponibilidad IA", "type": "main", "index": 0}],
            [{"node": "API Bloquear Habitación IA", "type": "main", "index": 0}],
            [{"node": "API Confirmar Reserva", "type": "main", "index": 0}],
            [{"node": "Preparar Salida", "type": "main", "index": 0}]
        ]
    }
    connections["Gemini Asistente IA"] = {
        "main": [
            [{"node": "H Procesar Gemini IA", "type": "main", "index": 0}]
        ]
    }
    connections["H Procesar Gemini IA"] = {
        "main": [
            [{"node": "Preparar Salida", "type": "main", "index": 0}]
        ]
    }
    connections["API Disponibilidad IA"] = {
        "main": [
            [{"node": "H Mostrar Habitaciones IA", "type": "main", "index": 0}]
        ]
    }
    connections["H Mostrar Habitaciones IA"] = {
        "main": [
            [{"node": "Preparar Salida", "type": "main", "index": 0}]
        ]
    }
    connections["API Bloquear Habitación IA"] = {
        "main": [
            [{"node": "H Resumen y Pago IA", "type": "main", "index": 0}]
        ]
    }
    connections["H Resumen y Pago IA"] = {
        "main": [
            [{"node": "Preparar Salida", "type": "main", "index": 0}]
        ]
    }

    # 8. Re-position ALL nodes cleanly into organized, non-overlapping lanes
    #
    # Layout Map:
    # Lane -400: Handshake Webhook GET
    # Lane 0: Webhook POST, Session & Main Pipeline
    # Lane 600: Menu Options Evaluator & Fallbacks
    # Lane -1200: Revisar / Pagar Saldo / Cancelar (Opción 5)
    # Lane -600: Reseñas (Opciones 3 y 4)
    # Lane 1200: Escalamiento a Secretaria (Opción 6)
    # Lane 2000: Reserva con IA (Opción 2)
    # Lane 3300: Reserva Normal Paso a Paso (Opción 1)
    # Lane 1000 (X >= 5000): Salida, Redis, WhatsApp, Inactividad
    
    positions = {
        # Trigger & Handshake
        'Webhook GET Verificación': [0, -400],
        'Responder Desafío GET': [280, -400],

        # Main Entry & Dispatcher
        'Webhook POST Mensajes': [0, 0],
        'Parsear Mensaje Meta': [280, 0],
        '¿Mensaje Válido?': [560, 0],
        'Redis Obtener Sesión': [840, 0],
        'Cargar Sesión y Detectar Ruta': [1120, 0],
        '¿Agente Activo?': [1400, 0],
        'Pausa (Agente Atendiendo)': [1680, -180],
        '¿Usar Gemini en Reserva?': [1680, 180],
        'H Preparar Contexto Gemini': [1960, 180],
        'Gemini Interpretar Respuesta': [2240, 180],
        'H Aplicar Interpretación Gemini': [2520, 180],
        'H Normalizar Respuesta': [2800, 180],
        'Enrutar por Estado1': [3080, 0],

        # Menu Evaluator & Generic Outputs
        'H Menú Evaluador Opción': [3400, 500],
        'Switch Opción Seleccionada': [3680, 500],
        'H Menú Principal': [3400, 750],
        'H No Texto': [3400, 950],
        'H Opción Inválida1': [3960, 650],

        # Flujo 5: Revisar / Pagar Saldo / Cancelar Reserva (Y = -1200)
        'H F1 Inicio Revisar Reserva': [3400, -1200],
        'H Normalizar Revisar Reserva': [3680, -1200],
        '¿Acción Revisar Reserva?': [3960, -1200],
        'API Consultar Reserva': [4240, -1400],
        'H Formatear Consulta Reserva': [4520, -1400],
        'API Cancelar Reserva': [4240, -1200],
        'H Formatear Cancelación Exitosa': [4520, -1200],
        'API Pagar Saldo': [4240, -1000],
        'H Formatear Pago Exitoso': [4520, -1000],

        # Flujo 3 & 4: Reseñas (Y = -600)
        'API Obtener Reseñas': [3400, -700],
        'H Formatear Reseñas': [3680, -700],
        'H F1 Inicio Escribir Reseña': [3400, -450],
        'H Normalizar Escribir Reseña': [3680, -450],
        '¿Acción Escribir Reseña?': [3960, -450],
        'API Guardar Reseña': [4240, -450],
        'H Reseña Guardada': [4520, -450],

        # Flujo 6: Escalamiento a Secretaria (Y = 1200)
        'H Escalar a Agente': [3400, 1200],
        '¿Recepción Disponible?': [3680, 1200],
        'Notificar Agente (API)': [3960, 1200],

        # Flujo 2: Reserva con IA (Y = 1800 a 2400)
        'H F1 Inicio IA': [3400, 1800],
        'H Normalizar IA': [3400, 2050],
        '¿Acción IA?': [3680, 2050],
        'Gemini Asistente IA': [3960, 1750],
        'H Procesar Gemini IA': [4240, 1750],
        'API Disponibilidad IA': [3960, 2000],
        'H Mostrar Habitaciones IA': [4240, 2000],
        'API Bloquear Habitación IA': [3960, 2250],
        'H Resumen y Pago IA': [4240, 2250],

        # Flujo 1: Reserva Guiada Paso a Paso (Y = 3000 a 4100)
        'H F1 Inicio Reserva': [3400, 3000],
        'H F1 CheckIn': [3400, 3250],
        'H F1 CheckOut': [3400, 3500],
        'API Habitaciones Disponibles': [3680, 3500],
        'H Mostrar Habitaciones': [3960, 3500],
        'H Normalizar Paso Reserva': [3400, 3750],
        'H Validar y Seleccionar Habitaciones': [3680, 3750],
        '¿Acción Reserva?': [3960, 3750],
        'API Bloquear Habitación 15 min': [4240, 3750],
        'H Confirmar Bloqueos': [4520, 3750],
        'H Normalizar Huespedes e Identidad': [3400, 4100],
        'H Procesar Reserva Paso': [3680, 4100],
        '¿Confirmar en BD?': [3960, 4100],
        'API Confirmar Reserva': [4240, 2700],
        'H Reserva Exitosa': [4520, 2700],

        # Salida, Sesión, WhatsApp e Inactividad (X >= 5000)
        'Preparar Salida': [5000, 1000],
        'Redis Guardar Sesión': [5300, 900],
        '¿Liberar Bloqueo Temporal?': [5300, 1150],
        'API Liberar Bloqueo Temporal': [5600, 1150],
        'Enviar Mensaje WhatsApp1': [5600, 900],
        'Esperar 10 min Inactividad': [5900, 900],
        'Redis Revisar Inactividad': [6200, 900],
        '¿Sesión Inactiva 10 min?': [6500, 900],
        '¿Avisar Inactividad?': [6800, 900],
        'H Aviso Inactividad': [7100, 900],
        'Enviar Aviso Inactividad': [7400, 900],
        'Esperar 1 min para Limpiar': [7700, 900],
        'Redis Confirmar Limpieza': [8000, 900],
        '¿Limpiar Sesión?': [8300, 900],
        '¿Borrar Redis?': [8600, 900],
        'Redis Borrar Sesión Inactiva': [8900, 900],
        'API Liberar Bloqueo Inactivo': [9200, 900]
    }

    # Apply positions
    for n in nodes:
        name = n['name']
        if name in positions:
            n['position'] = positions[name]

    flow['nodes'] = nodes
    flow['connections'] = connections

    with open('flows/n8n/V8_ChatbotReservas.json', 'w', encoding='utf-8') as f:
        json.dump(flow, f, indent=2, ensure_ascii=False)

    print(f"Successfully reorganized V8_ChatbotReservas.json with {len(nodes)} nodes.")

if __name__ == '__main__':
    reorganize()
