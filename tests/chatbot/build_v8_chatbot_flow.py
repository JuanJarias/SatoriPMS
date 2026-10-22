#!/usr/bin/env python3
import json
import uuid
import sys

def generate_v8():
    with open('flows/n8n/V6_ChatbotReservas.json', 'r', encoding='utf-8') as f:
        flow = json.load(f)

    flow['name'] = 'V8_ChatbotReservas'
    flow['versionId'] = str(uuid.uuid4())

    nodes = flow['nodes']
    nodes_dict = {n['name']: n for n in nodes}
    connections = flow['connections']

    # =========================================================================
    # 1. Update Existing Nodes
    # =========================================================================

    # Fix Gemini Interpretar Respuesta model
    if 'Gemini Interpretar Respuesta' in nodes_dict:
        nodes_dict['Gemini Interpretar Respuesta']['parameters']['url'] = (
            "={{ 'https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent?key=' + $env.GEMINI_API_KEY }}"
        )
        nodes_dict['Gemini Interpretar Respuesta']['onError'] = 'continueRegularOutput'

    # Ensure all existing HTTP nodes have onError continueRegularOutput
    for n in nodes:
        if 'httpRequest' in n['type']:
            n['onError'] = 'continueRegularOutput'

    # Update Cargar Sesión y Detectar Ruta
    nodes_dict['Cargar Sesión y Detectar Ruta']['parameters']['jsCode'] = """const p = $('Parsear Mensaje Meta').first().json;
const raw = $input.first().json.value;
let S = {};
if (typeof raw === 'string' && raw.trim()) { try { S = JSON.parse(raw); } catch (e) { S = {}; } }
else if (raw && typeof raw === 'object') { S = raw; }
if (!S || typeof S !== 'object' || Array.isArray(S)) S = {};

const norm = (s) => String(s == null ? '' : s).toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g, '').trim();
const t = norm(p.message_text);
const state = S.state || 'menu';
const step = S.step || 'inicio';

const RESTART = ['hola','menu','inicio','reiniciar','start','hi','hello','buenas','buenos dias','buenas tardes','buenas noches'];
const restartRequested = RESTART.includes(t);
const agentActive = !restartRequested && (S.agent_active === true || S.agent_active === 'true');
const AGENT = /\\b(agente|recepcionista|humano)\\b/;
const textual = ['text','interactive','button'].includes(p.message_type);

let route = state + ':' + step;
if (!textual) {
  route = 'no_texto';
} else if (restartRequested) {
  route = 'menu:inicio';
} else if (AGENT.test(t) && state !== 'escribir_resena') {
  route = 'escalamiento:inicio';
} else if (state === 'escalamiento') {
  route = 'menu:inicio';
} else if (state === 'revisar_reserva') {
  route = 'revisar_reserva';
} else if (state === 'escribir_resena') {
  route = 'escribir_resena';
} else if (state === 'ia_reserva') {
  route = 'ia_reserva';
}

return [{ json: { wa_id: p.wa_id, sender_name: p.sender_name, message_text: p.message_text, message_type: p.message_type, agent_active: agentActive, session: S, route } }];"""

    # Update H Menú Evaluador Opción
    nodes_dict['H Menú Evaluador Opción']['parameters']['jsCode'] = """const J = $input.first().json;
const text = String(J.message_text || '').trim().toLowerCase();
const ids = { 
  menu_reserva: '1', 
  menu_ia: '2', 
  menu_resenas: '3', 
  menu_escribir_resena: '4', 
  menu_agente: '5', 
  menu_cancelar: '6' 
};
const normalized = ids[text] || text;
const m = normalized.replace(/[\\uFE0F\\u20E3]/g, '').match(/^\\D*([1-6])\\D*$/);
return [{ json: Object.assign({}, J, { opcion: m ? m[1] : 'invalido' }) }];"""

    # Update H Menú Principal
    nodes_dict['H Menú Principal']['parameters']['jsCode'] = """const J = $input.first().json;
const wa_id = J.wa_id;
const sender_name = J.sender_name || 'Huésped';
const msg = '¡Hola, ' + sender_name + '! ☕\\nBienvenido al asistente de *Satori Hotel*\\n\\nSelecciona una opción para continuar:';

const rows = [
  { id: 'menu_reserva', title: 'Hacer una reserva', description: 'Reserva guiada paso a paso' },
  { id: 'menu_ia', title: 'Asistente IA', description: 'Describe tu viaje libremente' },
  { id: 'menu_resenas', title: 'Ver reseñas', description: 'Opiniones reales de huéspedes' },
  { id: 'menu_escribir_resena', title: 'Escribir reseña', description: 'Comparte tu experiencia' },
  { id: 'menu_cancelar', title: 'Revisar o Cancelar', description: 'Consulta tu reserva o saldo' },
  { id: 'menu_agente', title: 'Hablar con agente', description: 'Atención con recepción humana' }
];

return [{
  json: {
    wa_id,
    sender_name,
    response_text: msg,
    response_payload: {
      type: 'interactive',
      interactive: {
        type: 'list',
        body: { text: msg },
        action: {
          button: 'Ver opciones',
          sections: [{ title: 'Satori Hotel', rows }]
        }
      }
    },
    session: { state: 'menu', step: 'esperando_opcion', agent_active: false, wa_id, sender_name, reservation_draft: {} }
  }
}];"""

    # Update Enrutar por Estado1 router rules
    switch_node = nodes_dict['Enrutar por Estado1']
    rules = [
        ("r1", "={{ $json.route }}", "menu:esperando_opcion", "menu:esperando_opcion"),
        ("r0", "={{ $json.route }}", "menu:inicio", "menu:inicio"),
        ("r2", "={{ $json.route }}", "reserva:checkin", "reserva:checkin"),
        ("r3", "={{ $json.route }}", "reserva:checkout", "reserva:checkout"),
        ("r4", "={{ $json.route }}", "escalamiento:inicio", "escalamiento:inicio"),
        ("r5", "={{ $json.route }}", "no_texto", "no_texto"),
        ("r_rev", "={{ $json.route }}", "revisar_reserva", "revisar_reserva"),
        ("r_esc_res", "={{ $json.route }}", "escribir_resena", "escribir_resena"),
        ("r_ia", "={{ $json.route }}", "ia_reserva", "ia_reserva"),
        ("rsel", "={{ $json.route }}", "reserva:seleccion_habitacion", "reserva:seleccion_habitacion"),
        ("r_reserva_huespedes", "={{ $json.route }}", "reserva:huespedes", "reserva:huespedes"),
        ("r_reserva_nombre", "={{ $json.route }}", "reserva:nombre", "reserva:nombre"),
        ("r_reserva_identificacion", "={{ $json.route }}", "reserva:identificacion", "reserva:identificacion"),
        ("r_reserva_mascota", "={{ $json.route }}", "reserva:mascota", "reserva:mascota"),
        ("r_reserva_acompanantes", "={{ $json.route }}", "reserva:acompanantes", "reserva:acompanantes"),
        ("r_reserva_pago", "={{ $json.route }}", "reserva:pago", "reserva:pago"),
    ]
    
    switch_node['parameters']['rules']['values'] = [
        {
            "conditions": {
                "options": { "caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 3 },
                "conditions": [{ "id": rid, "leftValue": lval, "rightValue": rval, "operator": { "type": "string", "operation": "equals" } }],
                "combinator": "and"
            },
            "renameOutput": True,
            "outputKey": out_key
        }
        for (rid, lval, rval, out_key) in rules
    ]

    # Update H Validar y Seleccionar Habitaciones
    nodes_dict['H Validar y Seleccionar Habitaciones']['parameters']['jsCode'] = """const J = $input.first().json;
const D = J.session?.reservation_draft || {};
const step = J.session?.step || D.step;
const keep = (draft, nextStep) => ({ state: 'reserva', step: nextStep, agent_active: false, wa_id: J.wa_id, sender_name: J.sender_name, reservation_draft: Object.assign({}, draft, { step: nextStep }) });
const reply = (message, session) => [{ json: { wa_id: J.wa_id, sender_name: J.sender_name, response_text: message, session, api_action: 'reply' } }];

if (J.route === 'reserva:seleccion_habitacion' || step === 'seleccion_habitacion') {
  const rooms = Array.isArray(D.availableRooms) ? D.availableRooms : [];
  const input = String(J.message_text || '').toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g, '');
  const words = { uno: '1', un: '1', una: '1', dos: '2', tres: '3', cuatro: '4', cinco: '5', seis: '6', siete: '7', ocho: '8', nueve: '9', diez: '10' };
  const digits = input.replace(/\\b(uno|un|una|dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez)\\b/g, (word) => words[word]).match(/\\d+/g) || [];
  const indices = [...new Set(digits.map(Number).filter((number) => number >= 1 && number <= rooms.length))];
  const selected = indices.map((number) => rooms[number - 1]);
  if (!selected.length) return reply('⚠️ No reconocí la selección. Responde con los números de la lista, separados por coma; por ejemplo: *1, 3*.', keep(D, 'seleccion_habitacion'));
  return selected.map((room) => ({ json: Object.assign({}, J, { api_action: 'lock', roomId: room.id, checkIn: D.checkIn, checkOut: D.checkOut, selectedRooms: selected, lockRoom: room }) }));
}

if (step === 'pago') {
  const answer = String(J.message_text || '').toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g, '').trim();
  if (['1', '100', '100%', 'total', 'pago_100', 'completo'].some(k => answer.includes(k))) {
    return [{ json: Object.assign({}, J, { payment_selection: 'full' }) }];
  }
  if (['2', '50', '50%', 'mitad', 'anticipo', 'pago_50'].some(k => answer.includes(k))) {
    return [{ json: Object.assign({}, J, { payment_selection: 'deposit' }) }];
  }
  if (['3', 'cancelar', 'no', 'pago_cancelar', 'cancel'].some(k => answer.includes(k))) {
    return reply('❌ Reserva cancelada. El bloqueo de la habitación ha sido liberado. Escribe *menú* para volver al inicio.', { state: 'menu', step: 'esperando_opcion', agent_active: false, wa_id: J.wa_id, sender_name: J.sender_name, reservation_draft: {} });
  }
  return reply('⚠️ Por favor selecciona una opción válida:\\n1️⃣ Pagar el 100%\\n2️⃣ Pagar el 50% de anticipo\\n3️⃣ Cancelar reserva', keep(D, 'pago'));
}

if (step === 'acompanantes') {
  const text = String(J.message_text || '');
  const normalized = text.toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g, '').trim();
  const none = /^(ninguno|ninguna|ningun|no hay|nadie|solo yo|solo el titular)[.! ]*$/.test(normalized);
  const expected = Math.max(0, Number(D.adults || 0) + Number(D.children || 0) - 1);
  
  if (none && expected > 0) return reply('Antes indicaste que se hospedan ' + (expected + 1) + ' personas. ¿Cuáles son los nombres de tus ' + expected + ' acompañante(s)?', keep(D, 'acompanantes'));
  
  if (!none && expected === 0) return reply('Según los huéspedes registrados, solo se hospeda la persona titular. Indica *ninguno*.', keep(D, 'acompanantes'));
  
  if (!none && expected > 0) {
    const names = text.split(/,| y | e |\\n|-/).map(n => n.trim()).filter(n => n.length > 2);
    if (names.length !== expected) {
      return reply(`⚠️ Indicaste que serían ${expected + 1} huéspedes en total (tú y ${expected} acompañante(s)). Por favor, escribe los ${expected} nombres separados por coma. Si la cantidad de huéspedes es incorrecta, escribe *menú* para reiniciar.`, keep(D, 'acompanantes'));
    }
  }
}

return [{ json: J }];"""

    # Update H Normalizar Huespedes e Identidad
    nodes_dict['H Normalizar Huespedes e Identidad']['parameters']['jsCode'] = """const J = $input.first().json;
const D = J.session?.reservation_draft || {};
const step = J.session?.step || D.step;
const text = String(J.message_text || '').trim();

if (step === 'huespedes') {
  const adult = text.match(/(\\d+)\\s*(adultos?|personas?|huespedes?)/i);
  const child = text.match(/(\\d+)\\s*(niños?|ninos?|menores?)/i);
  if (adult && child) J.message_text = adult[1] + ' adultos y ' + child[1] + ' niños';
}
if (step === 'identificacion' && !/^\\d{6,10}$/.test(text.replace(/\\s+/g, ''))) {
  return [{ json: { wa_id: J.wa_id, sender_name: J.sender_name, response_text: '⚠️ La identificación debe tener solo números y entre 6 y 10 dígitos. Inténtalo de nuevo.', session: { ...J.session, step: 'identificacion' } } }];
}
return [{ json: J }];"""

    # Update H Procesar Reserva Paso
    nodes_dict['H Procesar Reserva Paso']['parameters']['jsCode'] = """const J = $input.first().json;
const D = (J.session && J.session.reservation_draft) || {};
const step = (J.session && J.session.step) || (D && D.step);
const text = String(J.message_text || '').trim();
const normalized = text.toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g, '').trim();

const keep = (draft, nextStep) => ({
  state: 'reserva',
  step: nextStep,
  agent_active: false,
  wa_id: J.wa_id,
  sender_name: J.sender_name,
  reservation_draft: Object.assign({}, draft, { step: nextStep })
});

const output = (response_text, session, extra = {}) => ({
  json: Object.assign({ wa_id: J.wa_id, sender_name: J.sender_name, response_text, session }, extra)
});

if (step === 'huespedes') {
  const numberTokens = (normalized.match(/\\d+/g) || []).map(Number);
  const adultMatches = [...normalized.matchAll(/(\\d+)\\s*(adultos?|personas?|huespedes?)/g)];
  const childMatches = [...normalized.matchAll(/(\\d+)\\s*(ninos?|niños?|menores?)/g)];
  let adults = adultMatches.length ? Number(adultMatches[0][1]) : (numberTokens[0] ?? null);
  let children = childMatches.length ? Number(childMatches[0][1]) : (numberTokens[1] ?? 0);
  if (adults == null && numberTokens.length) adults = numberTokens[0];
  if (children === 0 && numberTokens.length > 1 && !childMatches.length) children = numberTokens[1];
  const max = Number(D.room && D.room.maxAdultsCapacity || 0) + Number(D.room && D.room.childrenCapacity || 0);
  if (!adults || adults < 1 || children < 0) return [output('⚠️ Indica las personas así: *2 adultos y 1 niño*.', keep(D, 'huespedes'))];
  if (max && adults + children > max) return [output('⚠️ Esa habitación admite máximo *' + max + ' personas* según su capacidad. Regresa a la selección escribiendo *menú* o elige otra habitación.', keep(D, 'seleccion_habitacion'))];
  const base = Number(D.room && D.room.baseAdultsCapacity || 0);
  const extraPrice = Number(D.room && D.room.extraGuestPrice || 0);
  const extraGuests = Math.max(0, adults + children - base);
  const draft = Object.assign({}, D, { adults, children, extraGuests, extraGuestPrice: extraPrice, extraTotal: extraGuests * extraPrice });

  return [output(`✅ Huéspedes registrados: *${adults} adulto(s)* y *${children} niño(s)*.\\n\\nIndica el nombre completo de la persona titular de la reserva.`, keep(draft, 'nombre'))];
}

if (step === 'nombre') {
  if (text.length < 3) return [output('⚠️ Indica un nombre completo válido.', keep(D, 'nombre'))];
  return [output('Gracias. Ahora indica el número de identificación (cédula o pasaporte) del titular.', keep(Object.assign({}, D, { guestName: text }), 'identificacion'))];
}

if (step === 'identificacion') {
  const document = text.replace(/\\s+/g, '').replace(/[^0-9]/g, '');
  if (!/^\\d{6,10}$/.test(document)) return [output('⚠️ La identificación debe tener solo números y entre 6 y 10 dígitos. Inténtalo de nuevo.', keep(D, 'identificacion'))];
  return [output('¿Viajas con mascota?', keep(Object.assign({}, D, { document }), 'mascota'), { response_payload: { type: 'interactive', interactive: { type: 'button', body: { text: '¿Viajas con mascota?' }, action: { buttons: [{ type: 'reply', reply: { id: 'pet_si', title: 'Sí' } }, { type: 'reply', reply: { id: 'pet_no', title: 'No' } }] } } } })];
}

if (step === 'mascota') {
  const hasPet = ['si', 'sí', 'pet_si', 'yes'].includes(normalized);
  const noPet = ['no', 'pet_no'].includes(normalized);
  if (!hasPet && !noPet) return [output('Responde usando *Sí* o *No* para la mascota.', keep(D, 'mascota'))];
  if (hasPet && D.room && D.room.allowsPets === false) return [output('⚠️ La habitación seleccionada no permite mascotas. Responde *No* o elige otra habitación.', keep(D, 'mascota'))];
  return [output('¿Cuáles son los nombres de tus acompañantes? Si viajas solo, responde *ninguno*.', keep(Object.assign({}, D, { hasPet }), 'acompanantes'))];
}

if (step === 'acompanantes') {
  const noCompanions = ['ninguno', 'no', 'solo yo', 'nadie', 'sin acompanantes', 'no hay', 'no tengo', 'no viajan mas'].includes(normalized);
  const companions = noCompanions ? '' : text;
  const nights = Math.max(1, Math.round((new Date(D.checkOut) - new Date(D.checkIn)) / 86400000));
  const nightly = Number(D.room && D.room.pricePerNight || 0);
  const total = nights * nightly + Number(D.extraTotal || 0);
  const half = (total / 2).toFixed(2);
  const totalStr = total.toFixed(2);
  const draft = Object.assign({}, D, { companions, nights, total });

  const summary = `🧾 *Resumen de tu Reserva*\\n\\n` +
    `• Habitación: *${D.room.name || D.room.type} #${D.room.number}*\\n` +
    `• Entrada: *${D.checkIn}*\\n` +
    `• Salida: *${D.checkOut}* (${nights} noche${nights > 1 ? 's' : ''})\\n` +
    `• Huéspedes: *${D.adults} adulto(s), ${D.children} niño(s)*\\n` +
    `• Mascota: *${D.hasPet ? 'Sí' : 'No'}*\\n` +
    `• Titular: *${D.guestName}* (${D.document})\\n` +
    `• Acompañantes: *${companions || 'Ninguno'}*\\n` +
    `• Total estadía: *$${totalStr}*\\n\\n` +
    `💳 *¿Cómo deseas realizar el pago?*\\n` +
    `1️⃣ *Pagar el 100% ahora ($${totalStr})*\\n` +
    `2️⃣ *Pagar el 50% de anticipo ($${half})* (saldo al check-in)\\n` +
    `3️⃣ *Cancelar reserva*\\n\\n` +
    `_Responde 1, 2 o 3._`;

  return [output(summary, keep(draft, 'pago'), {
    response_payload: {
      type: 'interactive',
      interactive: {
        type: 'button',
        body: { text: summary },
        action: {
          buttons: [
            { type: 'reply', reply: { id: 'pago_100', title: 'Pagar 100%' } },
            { type: 'reply', reply: { id: 'pago_50', title: 'Pagar 50%' } },
            { type: 'reply', reply: { id: 'pago_cancelar', title: 'Cancelar' } }
          ]
        }
      }
    }
  })];
}

if (step === 'pago') {
  let opt = J.payment_selection;
  if (!opt) {
    if (['1', '100', '100%', 'total', 'pago_100', 'completo'].some(k => normalized.includes(k))) opt = 'full';
    else if (['2', '50', '50%', 'mitad', 'anticipo', 'pago_50'].some(k => normalized.includes(k))) opt = 'deposit';
  }

  if (opt === 'full' || opt === 'deposit') {
    const payload = {
      waId: J.wa_id,
      guestName: D.guestName,
      guestDocument: D.document,
      companions: D.companions || '',
      checkIn: D.checkIn,
      checkOut: D.checkOut,
      adults: Number(D.adults || 0),
      children: Number(D.children || 0),
      hasPet: Boolean(D.hasPet),
      rooms: Array.isArray(D.lockTokens) ? D.lockTokens.map(e => ({ roomId: e.roomId, lockToken: e.lockToken })) : [{ roomId: D.roomId, lockToken: D.lockToken }],
      paymentOption: opt
    };

    const optMsg = opt === 'deposit' ? 'el 50% de anticipo' : 'el 100% total';
    return [output(`✅ Confirmando tu reserva con pago de ${optMsg}...`, { state: 'reserva', step: 'confirmando', agent_active: false, wa_id: J.wa_id, sender_name: J.sender_name, reservation_draft: Object.assign({}, D, { payload, paymentOption: opt }) }, { api_action: 'confirm', payload })];
  }

  return [output('❌ Reserva cancelada. Escribe *menú* para volver al inicio.', { state: 'menu', step: 'esperando_opcion', agent_active: false, wa_id: J.wa_id, sender_name: J.sender_name, reservation_draft: {} })];
}

return [output('Escribe *menú* para volver al inicio.', { state: 'menu', step: 'esperando_opcion', agent_active: false, wa_id: J.wa_id, sender_name: J.sender_name, reservation_draft: {} })];"""

    # Update H Reserva Exitosa
    nodes_dict['H Reserva Exitosa']['parameters']['jsCode'] = """const apiResponse = $input.first().json || {};
const inputToApi = (() => { try { return $('API Confirmar Reserva').first().json; } catch(e) { return {}; } })();
const source = (() => {
  try { return $('H Procesar Reserva Paso').first().json; } catch(e) {}
  try { return $('H Normalizar IA').first().json; } catch(e) {}
  return {};
})();

const wa_id = source.wa_id || inputToApi.waId || (inputToApi.payload && inputToApi.payload.waId) || '';
const sender_name = source.sender_name || (inputToApi.payload && inputToApi.payload.guestName) || 'Huésped';

let text = '';

if (apiResponse.reservationGroupId) {
    const code = String(apiResponse.reservationGroupId).split('-')[0].toUpperCase();
    const paid = apiResponse.paidAmount != null ? Number(apiResponse.paidAmount).toFixed(2) : '0.00';
    const pending = apiResponse.pendingBalance != null ? Number(apiResponse.pendingBalance).toFixed(2) : '0.00';
    const total = apiResponse.totalPrice != null ? Number(apiResponse.totalPrice).toFixed(2) : paid;
    const isPartial = apiResponse.paymentStatus === 'partial';

    text = `🎉 *¡Tu reserva ha sido confirmada con éxito!*\\n\\n` +
           `• Código de reserva: *${code}*\\n` +
           `• Total de la estadía: *$${total}*\\n` +
           `• Monto pagado: *$${paid}* ${isPartial ? '_(Anticipo del 50%)_' : '_(Pago total 100%)_'}\\n`;

    if (isPartial) {
        text += `• Saldo pendiente: *$${pending}*\\n` +
                `💡 _Puedes pagar el saldo restante en cualquier momento desde la opción *Revisar o Cancelar* del menú, o al momento de tu check-in._\\n\\n`;
    } else {
        text += `• Estado de pago: *Completamente pagado (100%)*\\n\\n`;
    }

    text += `Conserva tu código *${code}* para cualquier consulta.\\n` +
            `¡Te esperamos con los brazos abiertos en *Satori Hotel*! 🌿\\n\\n` +
            `Escribe *menú* para volver al inicio.`;
} else {
    let errorMsg = apiResponse.error || apiResponse.message || apiResponse.detail;
    if (errorMsg && typeof errorMsg === 'object') errorMsg = errorMsg.message || JSON.stringify(errorMsg);
    if (!errorMsg) errorMsg = JSON.stringify(apiResponse);
    text = `⚠️ Lo sentimos, no pudimos completar tu reserva.\\nMotivo: ${errorMsg}.\\n\\nSi el tiempo de 15 minutos expiró, las habitaciones se liberaron automáticamente. Escribe *menú* para intentar de nuevo.`;
}

return [{
    json: {
        wa_id,
        sender_name,
        response_text: text,
        session: { state: 'menu', step: 'esperando_opcion', agent_active: false,
                   wa_id, sender_name, reservation_draft: {} }
    }
}];"""

    # Update H Normalizar Revisar Reserva
    nodes_dict['H Normalizar Revisar Reserva']['parameters']['jsCode'] = """const J = $input.first().json;
const S = J.session || {};
const draft = S.review_draft || {};
const text = String(J.message_text || '').trim();
const normalized = text.toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g, '').trim();

const keep = (newDraft, nextStep) => ({
    state: 'revisar_reserva',
    step: nextStep,
    agent_active: false,
    wa_id: J.wa_id,
    sender_name: J.sender_name,
    review_draft: newDraft
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

// PASO 1: Ingreso de Código
if (S.step === 'pedir_codigo') {
    const codeMatch = text.replace(/[^a-zA-Z0-9-]/g, '').toUpperCase();
    if (!codeMatch || codeMatch.length < 6) {
        return reply('⚠️ El código debe tener al menos 6 caracteres alfanuméricos (ejemplo: *41560C98*). Inténtalo de nuevo o escribe *menú* para cancelar.', S);
    }
    return [{
        json: Object.assign({}, J, {
            api_action: 'get_booking',
            search_code: codeMatch,
            session: keep(Object.assign({}, draft, { inputCode: codeMatch }), 'buscando')
        })
    }];
}

// PASO 2: Opciones sobre la Reserva
if (S.step === 'opciones_reserva') {
    const res = draft.reservation || {};
    const canPay = res.canPayRemaining === true;

    // Si tiene saldo pendiente y elige pagar (Opción 1 con canPay)
    if (canPay && ['1', 'pagar', 'pagar saldo', 'saldo', 'completar pago'].some(k => normalized.includes(k))) {
        return [{
            json: Object.assign({}, J, {
                api_action: 'pay_remaining',
                pay_code: draft.code,
                session: keep(draft, 'pagando')
            })
        }];
    }

    // Cancelar reserva: Opción 2 si canPay, u Opción 1 si no canPay
    const isCancel = (canPay && ['2', 'cancelar', 'cancelar reserva'].some(k => normalized.includes(k))) ||
                     (!canPay && ['1', 'cancelar', 'cancelar reserva'].some(k => normalized.includes(k)));

    if (isCancel) {
        const policy = res.refundPolicy || {};
        const hours = policy.hoursUntilCheckin != null ? policy.hoursUntilCheckin : 0;
        const policyDesc = policy.policyDescription || 'Políticas de Torre Satori';
        const refundAmt = policy.estimatedRefund != null ? Number(policy.estimatedRefund).toFixed(2) : '0.00';
        const paidAmt = res.paidAmount != null ? Number(res.paidAmount).toFixed(2) : '0.00';

        const msg = `⚠️ *Políticas de Cancelación (Torre Satori)*\\n\\n` +
                    `• Más de 72h antes: Reembolso del 100% de lo abonado.\\n` +
                    `• Entre 24h y 72h antes: Reembolso del 50% de lo abonado.\\n` +
                    `• Menos de 24h o no-show: Sin reembolso (0%).\\n\\n` +
                    `📊 *Detalle de tu reserva (${draft.code}):*\\n` +
                    `• Total abonado: *$${paidAmt}*\\n` +
                    `• Horas restantes: *${hours}h*\\n` +
                    `• Política aplicable: *${policyDesc}*\\n` +
                    `• Reembolso estimado: *$${refundAmt}*\\n\\n` +
                    `🔴 *¿Confirmas la cancelación definitiva de tu reserva?*\\n` +
                    `Esta acción liberará las habitaciones de inmediato y no se puede deshacer.\\n\\n` +
                    `Responde *Sí, confirmar* para cancelar o *No* para mantener tu reserva.`;

        return reply(msg, keep(draft, 'confirmar_cancelacion'));
    }

    // Volver al menú
    return reply('Operación finalizada. Tu reserva sigue activa. Escribe *menú* para ver más opciones.', reset());
}

// PASO 3: Doble Confirmación de Cancelación
if (S.step === 'confirmar_cancelacion') {
    const isAffirmative = /^(si|sí|confirmar|si confirmar|si, confirmar|cancelar|de acuerdo|afirmativo|proceder)$/i.test(normalized);
    const isNegative = /^(no|no cancelar|mantener|cancelar no|volver|menu|inicio|no gracias)$/i.test(normalized);

    if (isAffirmative) {
        return [{
            json: Object.assign({}, J, {
                api_action: 'cancel_booking',
                cancel_code: draft.code,
                session: keep(draft, 'cancelando')
            })
        }];
    }

    if (isNegative) {
        return reply(`✅ Tu reserva *${draft.code}* sigue activa y protegida. ¡Te esperamos en Satori Hotel! Escribe *menú* para volver al inicio.`, reset());
    }

    return reply('No entendí tu respuesta. Por favor responde *Sí, confirmar* para cancelar la reserva o *No* para mantenerla.', S);
}

return reply('Escribe *menú* para volver al inicio.', reset());"""

    # Update H Formatear Consulta Reserva
    nodes_dict['H Formatear Consulta Reserva']['parameters']['jsCode'] = """const apiResponse = $input.first().json || {};
const source = $('H Normalizar Revisar Reserva').first().json;
const wa_id = source.wa_id;
const sender_name = source.sender_name;

if (!apiResponse.code && !apiResponse.reservationGroupId) {
    const errorMsg = apiResponse.error || 'No se encontró ninguna reserva activa con ese código';
    return [{
        json: {
            wa_id,
            sender_name,
            response_text: `⚠️ *Reserva no encontrada*\\n\\n${errorMsg}.\\n\\nPor favor verifica el código e inténtalo de nuevo, o escribe *menú* para volver al inicio.`,
            session: {
                state: 'revisar_reserva',
                step: 'pedir_codigo',
                agent_active: false,
                wa_id,
                sender_name,
                review_draft: {}
            }
        }
    }];
}

const res = apiResponse;
const roomNames = Array.isArray(res.rooms) ? res.rooms.map(r => `#${r.number} (${r.name || r.type})`).join(', ') : 'Habitación reservada';
const total = res.totalPrice != null ? Number(res.totalPrice).toFixed(2) : '0.00';
const paid = res.paidAmount != null ? Number(res.paidAmount).toFixed(2) : '0.00';
const pending = res.pendingBalance != null ? Number(res.pendingBalance).toFixed(2) : '0.00';

let msg = `📋 *Detalles de tu Reserva*\\n\\n` +
          `• Código: *${res.code}*\\n` +
          `• Titular: *${res.guestName || sender_name}*\\n` +
          `• Estado: *${res.statusLabel || res.status}* (${res.paymentStatusLabel || res.paymentStatus})\\n` +
          `• Fechas: *${res.checkIn}* al *${res.checkOut}* (${res.nights} noche${res.nights > 1 ? 's' : ''})\\n` +
          `• Habitaciones: *${roomNames}*\\n` +
          `• Huéspedes: *${res.adults} adulto(s), ${res.children} niño(s)*\\n` +
          `• Mascota: *${res.withPet ? 'Sí' : 'No'}*\\n` +
          `• Total reserva: *$${total}*\\n` +
          `• Pagado a la fecha: *$${paid}*\\n`;

if (Number(pending) > 0) {
    msg += `• ⚠️ Saldo pendiente: *$${pending}*\\n`;
}

if (res.status === 'cancelled') {
    msg += `\\nℹ️ Esta reserva se encuentra *Cancelada*. Escribe *menú* para volver al inicio.`;
    return [{
        json: {
            wa_id,
            sender_name,
            response_text: msg,
            session: { state: 'menu', step: 'esperando_opcion', agent_active: false, wa_id, sender_name, reservation_draft: {} }
        }
    }];
}

if (res.canPayRemaining) {
    msg += `\\n¿Qué deseas hacer?\\n` +
           `1️⃣ *Pagar saldo restante ($${pending})*\\n` +
           `2️⃣ *Cancelar reserva*\\n` +
           `3️⃣ *Volver al menú*`;
} else if (res.canCancel) {
    msg += `\\n¿Qué deseas hacer?\\n` +
           `1️⃣ *Cancelar reserva*\\n` +
           `2️⃣ *Volver al menú*`;
} else {
    msg += `\\nℹ️ Esta reserva no admite cancelaciones automáticas. Escribe *menú* para volver.`;
}

return [{
    json: {
        wa_id,
        sender_name,
        response_text: msg,
        session: {
            state: 'revisar_reserva',
            step: 'opciones_reserva',
            agent_active: false,
            wa_id,
            sender_name,
            review_draft: {
                code: res.code,
                reservation: res,
                refundPolicy: res.refundPolicy
            }
        }
    }
}];"""

    # Update ¿Acción Revisar Reserva? switch
    switch_rev = nodes_dict['¿Acción Revisar Reserva?']
    switch_rev['typeVersion'] = 3.4
    switch_rev['parameters']['rules']['values'] = [
        {
            "conditions": {
                "options": { "caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 3 },
                "conditions": [{ "id": "c1", "leftValue": "={{ $json.api_action }}", "rightValue": "get_booking", "operator": { "type": "string", "operation": "equals" } }],
                "combinator": "and"
            },
            "renameOutput": True,
            "outputKey": "Consultar Reserva"
        },
        {
            "conditions": {
                "options": { "caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 3 },
                "conditions": [{ "id": "c2", "leftValue": "={{ $json.api_action }}", "rightValue": "cancel_booking", "operator": { "type": "string", "operation": "equals" } }],
                "combinator": "and"
            },
            "renameOutput": True,
            "outputKey": "Cancelar Reserva"
        },
        {
            "conditions": {
                "options": { "caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 3 },
                "conditions": [{ "id": "c3", "leftValue": "={{ $json.api_action }}", "rightValue": "pay_remaining", "operator": { "type": "string", "operation": "equals" } }],
                "combinator": "and"
            },
            "renameOutput": True,
            "outputKey": "Pagar Saldo"
        }
    ]

    # =========================================================================
    # 2. Add New Nodes
    # =========================================================================

    # Node: API Pagar Saldo
    api_pagar_saldo = {
        "parameters": {
            "method": "POST",
            "url": "={{ ($env.API_BASE_URL || 'http://api:8080') + '/api/bookings/group/' + $json.pay_code + '/pay-remaining' }}",
            "options": {
                "timeout": 15000,
                "response": {
                    "response": {
                        "neverError": True
                    }
                }
            }
        },
        "id": "e89d1001-0001-4000-8000-000000000001",
        "name": "API Pagar Saldo",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [1050, 1900],
        "onError": "continueRegularOutput"
    }

    # Node: H Formatear Pago Exitoso
    h_pago_exitoso = {
        "parameters": {
            "jsCode": """const apiResponse = $input.first().json || {};
const source = $('H Normalizar Revisar Reserva').first().json;
const wa_id = source.wa_id;
const sender_name = source.sender_name;

if (!apiResponse.reservationGroupId && !apiResponse.code) {
    const errorMsg = apiResponse.error || 'No se pudo registrar el pago del saldo';
    return [{
        json: {
            wa_id,
            sender_name,
            response_text: `⚠️ *Error al procesar el pago*\\n\\n${errorMsg}.\\n\\nEscribe *menú* para volver al inicio.`,
            session: { state: 'menu', step: 'esperando_opcion', agent_active: false, wa_id, sender_name, reservation_draft: {} }
        }
    }];
}

const code = apiResponse.code || (apiResponse.reservationGroupId ? String(apiResponse.reservationGroupId).split('-')[0].toUpperCase() : source.pay_code);
const total = apiResponse.totalPrice != null ? Number(apiResponse.totalPrice).toFixed(2) : '0.00';
const paid = apiResponse.paidAmount != null ? Number(apiResponse.paidAmount).toFixed(2) : total;

const msg = `🎉 *¡Pago de Saldo Confirmado con Éxito!*\\n\\n` +
            `• Código de reserva: *${code}*\\n` +
            `• Total cancelado: *$${paid}*\\n` +
            `• Saldo pendiente: *$0.00*\\n` +
            `• Estado de pago: *Completamente pagado (100%)*\\n\\n` +
            `Tu reserva ha quedado al día. ¡Te esperamos en Satori Hotel! ☕🌿\\n\\n` +
            `Escribe *menú* para volver al inicio.`;

return [{
    json: {
        wa_id,
        sender_name,
        response_text: msg,
        session: { state: 'menu', step: 'esperando_opcion', agent_active: false, wa_id, sender_name, reservation_draft: {} }
    }
}];"""
        },
        "id": "e89d1002-0002-4000-8000-000000000002",
        "name": "H Formatear Pago Exitoso",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [1300, 1900]
    }

    # Node: API Obtener Reseñas
    api_obtener_resenas = {
        "parameters": {
            "method": "GET",
            "url": "={{ ($env.API_BASE_URL || 'http://api:8080') + '/api/reviews?limit=5' }}",
            "options": {
                "timeout": 15000,
                "response": {
                    "response": {
                        "neverError": True
                    }
                }
            }
        },
        "id": "e89d1003-0003-4000-8000-000000000003",
        "name": "API Obtener Reseñas",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [-3504, 1008],
        "onError": "continueRegularOutput"
    }

    # Node: H Formatear Reseñas
    h_formatear_resenas = {
        "parameters": {
            "jsCode": """const source = $('Switch Opción Seleccionada').first().json;
const raw = $input.all().map(i => i.json);
const reviews = raw.length === 1 && Array.isArray(raw[0]) ? raw[0] : raw;
const wa_id = source.wa_id;
const sender_name = source.sender_name || 'Huésped';

if (!reviews.length || (reviews.length === 1 && !reviews[0].comment && !reviews[0].rating)) {
    return [{
        json: {
            wa_id,
            sender_name,
            response_text: `⭐ *Reseñas de Torre Satori*\\n\\nAún no hay reseñas registradas. ¡Sé el primero en compartir tu experiencia!\\n\\nEscribe *4* para dejar una reseña o *menú* para volver.`,
            session: { state: 'menu', step: 'esperando_opcion', agent_active: false, wa_id, sender_name, reservation_draft: {} }
        }
    }];
}

const stars = (r) => '⭐'.repeat(Math.max(1, Math.min(5, Math.round(Number(r) || 5))));
const validReviews = reviews.filter(r => r.rating || r.comment);
const avg = (validReviews.reduce((sum, r) => sum + Number(r.rating || 5), 0) / validReviews.length).toFixed(1);

const list = validReviews.slice(0, 5).map(r => {
    const author = r.authorName || 'Huésped verificado';
    const s = stars(r.rating);
    const src = r.source === 'google' ? 'Google Reviews' : 'Chatbot Satori';
    return `${s} *${author}* _(${src})_:\\n"${r.comment || 'Excelente estadía'}"`;
}).join('\\n\\n');

const msg = `🌟 *Opiniones sobre Torre Satori*\\n` +
            `Calificación promedio: *${avg} / 5.0* (${validReviews.length} opiniones recientes)\\n\\n` +
            `${list}\\n\\n` +
            `💡 _Escribe *4* para dejar tu propia reseña o escribe *menú* para regresar al inicio._`;

return [{
    json: {
        wa_id,
        sender_name,
        response_text: msg,
        session: { state: 'menu', step: 'esperando_opcion', agent_active: false, wa_id, sender_name, reservation_draft: {} }
    }
}];"""
        },
        "id": "e89d1004-0004-4000-8000-000000000004",
        "name": "H Formatear Reseñas",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [-3280, 1008]
    }

    # Node: H F1 Inicio Escribir Reseña
    h_inicio_escribir_resena = {
        "parameters": {
            "jsCode": """const J = $input.first().json;
const wa_id = J.wa_id;
const sender_name = J.sender_name || 'Huésped';

const msg = `⭐ *Tu Opinión es Muy Importante para Torre Satori*\\n\\n` +
            `Por favor califícanos del *1 al 5*, donde 1 es la menor calificación y 5 la mejor:\\n\\n` +
            `1️⃣ Muy insatisfecho\\n` +
            `2️⃣ Insatisfecho\\n` +
            `3️⃣ Neutral\\n` +
            `4️⃣ Bueno\\n` +
            `5️⃣ Excelente ⭐⭐⭐⭐⭐\\n\\n` +
            `_Escribe el número del 1 al 5 o escribe menú para cancelar._`;

return [{
    json: {
        wa_id,
        sender_name,
        response_text: msg,
        session: {
            state: 'escribir_resena',
            step: 'pedir_rating',
            agent_active: false,
            wa_id,
            sender_name,
            review_draft: {}
        }
    }
}];"""
        },
        "id": "e89d1005-0005-4000-8000-000000000005",
        "name": "H F1 Inicio Escribir Reseña",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [-3504, 1168]
    }

    # Node: H Normalizar Escribir Reseña
    h_norm_escribir_resena = {
        "parameters": {
            "jsCode": """const J = $input.first().json;
const S = J.session || {};
const draft = S.review_draft || {};
const text = String(J.message_text || '').trim();
const normalized = text.toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g, '').trim();

const keep = (newDraft, nextStep) => ({
    state: 'escribir_resena',
    step: nextStep,
    agent_active: false,
    wa_id: J.wa_id,
    sender_name: J.sender_name,
    review_draft: newDraft
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

if (S.step === 'pedir_rating') {
    let rating = null;
    const numMatch = normalized.match(/\\b([1-5])\\b/);
    if (numMatch) rating = Number(numMatch[1]);
    else if (normalized.includes('uno') || normalized.includes('pesim')) rating = 1;
    else if (normalized.includes('dos') || normalized.includes('mal')) rating = 2;
    else if (normalized.includes('tres') || normalized.includes('regular') || normalized.includes('neutral')) rating = 3;
    else if (normalized.includes('cuatro') || normalized.includes('buen')) rating = 4;
    else if (normalized.includes('cinco') || normalized.includes('excelent') || normalized.includes('genial')) rating = 5;
    else {
        const starCount = (text.match(/⭐/g) || []).length;
        if (starCount >= 1 && starCount <= 5) rating = starCount;
    }

    if (!rating) {
        return reply('⚠️ Por favor indica un número del *1* al *5* para tu calificación (o escribe *menú* para cancelar).', S);
    }

    const starsStr = '⭐'.repeat(rating);
    const newDraft = Object.assign({}, draft, { rating });
    return reply(`✅ Calificación registrada: *${starsStr} (${rating}/5)*\\n\\nAhora cuéntanos en detalle qué te pareció el hotel, la atención, las habitaciones o qué podemos mejorar:`, keep(newDraft, 'pedir_comentario'));
}

if (S.step === 'pedir_comentario') {
    if (text.length < 3) {
        return reply('Por favor escribe un breve comentario sobre tu experiencia (o escribe *menú* si prefieres cancelar).', S);
    }

    const payload = {
        waId: J.wa_id,
        authorName: J.sender_name || 'Huésped WhatsApp',
        rating: draft.rating || 5,
        comment: text,
        source: 'chatbot'
    };

    return [{
        json: Object.assign({}, J, {
            api_action: 'guardar_resena',
            payload,
            session: keep(Object.assign({}, draft, { comment: text }), 'guardando')
        })
    }];
}

return reply('Escribe *menú* para volver al inicio.', reset());"""
        },
        "id": "e89d1006-0006-4000-8000-000000000006",
        "name": "H Normalizar Escribir Reseña",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [-3300, 1168]
    }

    # Node: ¿Acción Escribir Reseña?
    switch_escribir_resena = {
        "parameters": {
            "rules": {
                "values": [
                    {
                        "conditions": {
                            "options": { "caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 3 },
                            "conditions": [{ "id": "er1", "leftValue": "={{ $json.api_action }}", "rightValue": "guardar_resena", "operator": { "type": "string", "operation": "equals" } }],
                            "combinator": "and"
                        },
                        "renameOutput": True,
                        "outputKey": "Guardar Reseña"
                    }
                ]
            },
            "options": {
                "fallbackOutput": "extra",
                "renameFallbackOutput": "Respuesta Normal"
            }
        },
        "id": "e89d1007-0007-4000-8000-000000000007",
        "name": "¿Acción Escribir Reseña?",
        "type": "n8n-nodes-base.switch",
        "typeVersion": 3.4,
        "position": [-3100, 1168]
    }

    # Node: API Guardar Reseña
    api_guardar_resena = {
        "parameters": {
            "method": "POST",
            "url": "={{ ($env.API_BASE_URL || 'http://api:8080') + '/api/reviews' }}",
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": "={{ JSON.stringify($json.payload) }}",
            "options": {
                "timeout": 15000,
                "response": {
                    "response": {
                        "neverError": True
                    }
                }
            }
        },
        "id": "e89d1008-0008-4000-8000-000000000008",
        "name": "API Guardar Reseña",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [-2880, 1168],
        "onError": "continueRegularOutput"
    }

    # Node: H Reseña Guardada
    h_resena_guardada = {
        "parameters": {
            "jsCode": """const apiResponse = $input.first().json || {};
const source = $('H Normalizar Escribir Reseña').first().json;
const wa_id = source.wa_id;
const sender_name = source.sender_name || 'Huésped';

const placeId = $env.GOOGLE_PLACE_ID || 'ChIJ_TEST_TORRE_SATORI_SEVILLA_VALLE';
const googleLink = 'https://search.google.com/local/writereview?placeid=' + placeId;

const msg = `🙏 *¡Muchas gracias por tu reseña, ${sender_name}!*\\n\\n` +
            `Tu comentario ha sido guardado exitosamente en nuestro sistema y nos motiva a seguir brindando el mejor servicio. 🌿\\n\\n` +
            `⭐ *¿Nos ayudarías compartiéndola también en Google?*\\n` +
            `Tu reseña pública en Google Maps ayuda a que más viajeros conozcan Torre Satori. Puedes publicarla con un solo clic aquí:\\n` +
            `👉 ${googleLink}\\n\\n` +
            `Escribe *menú* para continuar navegando.`;

return [{
    json: {
        wa_id,
        sender_name,
        response_text: msg,
        session: { state: 'menu', step: 'esperando_opcion', agent_active: false, wa_id, sender_name, reservation_draft: {} }
    }
}];"""
        },
        "id": "e89d1009-0009-4000-8000-000000000009",
        "name": "H Reseña Guardada",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [-2660, 1168]
    }

    # Node: H F1 Inicio IA
    h_inicio_ia = {
        "parameters": {
            "jsCode": """const J = $input.first().json;
const wa_id = J.wa_id;
const sender_name = J.sender_name || 'Huésped';

const msg = `🤖 *Asistente Inteligente de Reservas — Satori Hotel*\\n\\n` +
            `¡Hola ${sender_name}! Puedes escribir en *un solo mensaje* todos los detalles de tu viaje en tus propias palabras.\\n\\n` +
            `*Ejemplo:*\\n` +
            `_«Quiero reservar del 2026-10-20 al 2026-10-23 para 2 adultos y 1 niño, viajo con mi perrito. Mi nombre es Juan Gómez y mi cédula es 1094900111»_\\n\\n` +
            `Escribe los datos de tu reserva o escribe *menú* para regresar al menú principal.`;

return [{
    json: {
        wa_id,
        sender_name,
        response_text: msg,
        session: {
            state: 'ia_reserva',
            step: 'esperando_mensaje',
            agent_active: false,
            wa_id,
            sender_name,
            ia_draft: {}
        }
    }
}];"""
        },
        "id": "e89d1010-0010-4000-8000-000000000010",
        "name": "H F1 Inicio IA",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [-3504, 700]
    }

    # Node: H Normalizar IA
    h_norm_ia = {
        "parameters": {
            "jsCode": """const J = $input.first().json;
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

// PASO 1: Procesar mensaje libre con Gemini
if (S.step === 'esperando_mensaje' || !S.step) {
    const today = new Date(Date.now() - 5 * 3600 * 1000).toISOString().slice(0, 10);
    const prompt = `Eres un asistente de reservas de hotel. Extrae los datos de reserva del texto del usuario en formato JSON estricto.
Fecha de referencia hoy (Colombia): ${today}.
Propiedades requeridas:
- checkIn: string YYYY-MM-DD o null si no se menciona
- checkOut: string YYYY-MM-DD o null si no se menciona
- adults: número entero >= 1 (por defecto 1 si no se aclara)
- children: número entero >= 0 (por defecto 0)
- hasPet: boolean (true si menciona mascota/perro/gato, false si no)
- guestName: string con el nombre del huésped si se menciona, o null
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

// PASO 2: Selección de Habitación de las opciones mostradas
if (S.step === 'ia_seleccion_habitacion') {
    const rooms = Array.isArray(draft.availableRooms) ? draft.availableRooms : [];
    const num = Number((normalized.match(/\\d+/) || [])[0]);
    const room = rooms.find((r, idx) => idx + 1 === num || String(r.number) === normalized || String(r.id) === normalized);

    if (!room) {
        return reply('⚠️ No encontré esa opción. Por favor responde con el número de la lista (ej: *1*) o escribe *menú* para cancelar.', S);
    }

    const newDraft = Object.assign({}, draft, { selectedRoom: room, roomId: room.id });
    return [{
        json: Object.assign({}, J, {
            api_action: 'lock',
            roomId: room.id,
            checkIn: draft.checkIn,
            checkOut: draft.checkOut,
            lockRoom: room,
            session: keep(newDraft, 'bloqueando')
        })
    }];
}

// PASO 3: Selección de Modalidad de Pago
if (S.step === 'ia_pago') {
    let opt = null;
    if (['1', '100', '100%', 'total', 'pago_100', 'completo'].some(k => normalized.includes(k))) opt = 'full';
    else if (['2', '50', '50%', 'mitad', 'anticipo', 'pago_50'].some(k => normalized.includes(k))) opt = 'deposit';
    else if (['3', 'cancelar', 'no'].some(k => normalized.includes(k))) {
        return reply('❌ Reserva cancelada. El bloqueo de la habitación fue liberado. Escribe *menú* para volver al inicio.', reset());
    }

    if (!opt) {
        return reply('⚠️ Selecciona una opción válida:\\n1️⃣ Pagar 100%\\n2️⃣ Pagar 50% de anticipo\\n3️⃣ Cancelar', S);
    }

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
        rooms: [{ roomId: draft.selectedRoom.id, lockToken: draft.lockToken }],
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
        },
        "id": "e89d1011-0011-4000-8000-000000000011",
        "name": "H Normalizar IA",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [-3300, 700]
    }

    # Node: ¿Acción IA?
    switch_ia = {
        "parameters": {
            "rules": {
                "values": [
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
            },
            "options": {
                "fallbackOutput": "extra",
                "renameFallbackOutput": "Respuesta Normal"
            }
        },
        "id": "e89d1012-0012-4000-8000-000000000012",
        "name": "¿Acción IA?",
        "type": "n8n-nodes-base.switch",
        "typeVersion": 3.4,
        "position": [-3100, 700]
    }

    # Node: Gemini Asistente IA
    gemini_ia = {
        "parameters": {
            "method": "POST",
            "url": "={{ 'https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent?key=' + $env.GEMINI_API_KEY }}",
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": "={{ JSON.stringify($json.geminiRequest) }}",
            "options": {
                "timeout": 20000,
                "response": {
                    "response": {
                        "neverError": True
                    }
                }
            }
        },
        "id": "e89d1013-0013-4000-8000-000000000013",
        "name": "Gemini Asistente IA",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [-2900, 560],
        "onError": "continueRegularOutput"
    }

    # Node: H Procesar Gemini IA
    h_procesar_gemini_ia = {
        "parameters": {
            "jsCode": """const geminiRes = $input.first().json || {};
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

if (!checkIn || !checkOut || checkIn >= checkOut) {
    const msg = `🤖 *Entendí parte de tu mensaje:*\\n` +
                `${parsed.summary || 'Necesito que me indiques las fechas de estadía.'}\\n\\n` +
                `⚠️ *Me faltan las fechas de entrada y salida.*\\n` +
                `Por favor indícalas con formato AAAA-MM-DD (ej: *2026-10-20 al 2026-10-23*) o escribe *menú* para ir al inicio.`;
    return [{
        json: {
            has_dates: false,
            wa_id,
            sender_name,
            response_text: msg,
            session: { state: 'ia_reserva', step: 'esperando_mensaje', agent_active: false, wa_id, sender_name, ia_draft: Object.assign({}, parsed, { guestName, guestDocument }) }
        }
    }];
}

// Con fechas válidas, consultamos habitaciones disponibles
const draft = {
    checkIn,
    checkOut,
    adults,
    children,
    hasPet,
    guestName,
    guestDocument,
    companions: parsed.companions || ''
};

return [{
    json: {
        has_dates: true,
        wa_id,
        sender_name,
        checkIn,
        checkOut,
        adults,
        children,
        pet: hasPet,
        ia_draft: draft,
        session: { state: 'ia_reserva', step: 'buscando_disponibilidad', agent_active: false, wa_id, sender_name, ia_draft: draft }
    }
}];"""
        },
        "id": "e89d1014-0014-4000-8000-000000000014",
        "name": "H Procesar Gemini IA",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [-2680, 560]
    }

    # Node: ¿IA Fechas Válidas?
    if_ia_dates = {
        "parameters": {
            "conditions": {
                "options": {
                    "caseSensitive": True,
                    "leftValue": "",
                    "typeValidation": "strict",
                    "version": 2
                },
                "conditions": [
                    {
                        "id": "has_dates_cond",
                        "leftValue": "={{ $json.has_dates }}",
                        "rightValue": "",
                        "operator": {
                            "type": "boolean",
                            "operation": "true",
                            "singleValue": True
                        }
                    }
                ],
                "combinator": "and"
            },
            "options": {}
        },
        "id": "e89d1019-0019-4000-8000-000000000019",
        "name": "¿IA Fechas Válidas?",
        "type": "n8n-nodes-base.if",
        "typeVersion": 2.2,
        "position": [-2480, 560]
    }

    # Node: API Disponibilidad IA
    api_disp_ia = {
        "parameters": {
            "method": "GET",
            "url": "={{ ($env.API_BASE_URL || 'http://api:8080') + '/api/rooms/availability?checkIn=' + $json.checkIn + '&checkOut=' + $json.checkOut + '&adults=' + $json.adults + '&children=' + $json.children + '&pet=' + $json.pet }}",
            "options": {
                "timeout": 15000,
                "response": {
                    "response": {
                        "neverError": True
                    }
                }
            }
        },
        "id": "e89d1015-0015-4000-8000-000000000015",
        "name": "API Disponibilidad IA",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [-2260, 500],
        "onError": "continueRegularOutput"
    }

    # Node: H Mostrar Habitaciones IA
    h_mostrar_disp_ia = {
        "parameters": {
            "jsCode": """const source = $('H Procesar Gemini IA').first().json;
const raw = $input.all().map(i => i.json);
const rooms = raw.length === 1 && Array.isArray(raw[0]) ? raw[0] : raw;
const wa_id = source.wa_id;
const sender_name = source.sender_name;
const draft = source.ia_draft || {};

if (!rooms.length || (rooms.length === 1 && !rooms[0].id)) {
    return [{
        json: {
            wa_id,
            sender_name,
            response_text: `😔 No encontré habitaciones disponibles del *${draft.checkIn}* al *${draft.checkOut}* para esa cantidad de huéspedes. Escribe *menú* para intentar con otras fechas.`,
            session: { state: 'menu', step: 'esperando_opcion', agent_active: false, wa_id, sender_name, reservation_draft: {} }
        }
    }];
}

const choices = rooms.slice(0, 8);
const lines = choices.map((r, i) => {
    const max = Number(r.maxAdultsCapacity || 0) + Number(r.childrenCapacity || 0);
    return `${i + 1}. *${r.name || r.type} #${r.number}* — $${r.pricePerNight}/noche (Hasta ${max} personas)`;
});

const msg = `✅ *Encontré habitaciones disponibles del ${draft.checkIn} al ${draft.checkOut}:*\\n\\n` +
            `${lines.join('\\n')}\\n\\n` +
            `👉 Responde con el *número de la opción* que deseas reservar (ejemplo: *1*):`;

const newDraft = Object.assign({}, draft, { availableRooms: choices });

return [{
    json: {
        wa_id,
        sender_name,
        response_text: msg,
        session: { state: 'ia_reserva', step: 'ia_seleccion_habitacion', agent_active: false, wa_id, sender_name, ia_draft: newDraft }
    }
}];"""
        },
        "id": "e89d1016-0016-4000-8000-000000000016",
        "name": "H Mostrar Habitaciones IA",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [-2040, 500]
    }

    # Node: API Bloquear Habitación IA
    api_lock_ia = {
        "parameters": {
            "method": "POST",
            "url": "={{ ($env.API_BASE_URL || 'http://api:8080') + '/api/bookings/lock' }}",
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": "={{ JSON.stringify({ waId: $json.wa_id, roomId: $json.roomId, checkIn: $json.checkIn, checkOut: $json.checkOut }) }}",
            "options": {
                "timeout": 15000,
                "response": {
                    "response": {
                        "neverError": True
                    }
                }
            }
        },
        "id": "e89d1017-0017-4000-8000-000000000017",
        "name": "API Bloquear Habitación IA",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [-2900, 740],
        "onError": "continueRegularOutput"
    }

    # Node: H Resumen y Pago IA
    h_resumen_pago_ia = {
        "parameters": {
            "jsCode": """const apiResponse = $input.first().json || {};
const source = $('H Normalizar IA').first().json;
const wa_id = source.wa_id;
const sender_name = source.sender_name;
const draft = source.session.ia_draft || {};
const room = draft.selectedRoom || {};

if (!apiResponse.lockToken) {
    return [{
        json: {
            wa_id,
            sender_name,
            response_text: '⚠️ No pudimos bloquear la habitación seleccionada. Puede que otro huésped la haya tomado. Escribe *menú* para intentar de nuevo.',
            session: { state: 'menu', step: 'esperando_opcion', agent_active: false, wa_id, sender_name, reservation_draft: {} }
        }
    }];
}

draft.lockToken = apiResponse.lockToken;
const nights = Math.max(1, Math.round((new Date(draft.checkOut) - new Date(draft.checkIn)) / 86400000));
const total = Number(apiResponse.totalPrice || (nights * Number(room.pricePerNight || 0)));
const half = (total / 2).toFixed(2);
const totalStr = total.toFixed(2);

const summary = `🧾 *Resumen de Reserva Asistida por IA*\\n\\n` +
    `• Habitación: *${room.name || room.type} #${room.number}*\\n` +
    `• Fechas: *${draft.checkIn}* al *${draft.checkOut}* (${nights} noche${nights > 1 ? 's' : ''})\\n` +
    `• Huéspedes: *${draft.adults} adulto(s), ${draft.children} niño(s)*\\n` +
    `• Mascota: *${draft.hasPet ? 'Sí' : 'No'}*\\n` +
    `• Titular: *${draft.guestName}* (${draft.guestDocument || 'S/D'})\\n` +
    `• Total estadía: *$${totalStr}*\\n\\n` +
    `💳 *¿Cómo deseas abonar tu estadía?*\\n` +
    `1️⃣ *Pagar el 100% ($${totalStr})*\\n` +
    `2️⃣ *Pagar el 50% de anticipo ($${half})*\\n` +
    `3️⃣ *Cancelar*\\n\\n` +
    `_Responde 1, 2 o 3._`;

return [{
    json: {
        wa_id,
        sender_name,
        response_text: summary,
        session: { state: 'ia_reserva', step: 'ia_pago', agent_active: false, wa_id, sender_name, ia_draft: draft }
    }
}];"""
        },
        "id": "e89d1018-0018-4000-8000-000000000018",
        "name": "H Resumen y Pago IA",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [-2680, 740]
    }

    # Add all new nodes to flow['nodes']
    new_nodes = [
        api_pagar_saldo,
        h_pago_exitoso,
        api_obtener_resenas,
        h_formatear_resenas,
        h_inicio_escribir_resena,
        h_norm_escribir_resena,
        switch_escribir_resena,
        api_guardar_resena,
        h_resena_guardada,
        h_inicio_ia,
        h_norm_ia,
        switch_ia,
        gemini_ia,
        h_procesar_gemini_ia,
        if_ia_dates,
        api_disp_ia,
        h_mostrar_disp_ia,
        api_lock_ia,
        h_resumen_pago_ia
    ]

    for n in new_nodes:
        nodes.append(n)

    # =========================================================================
    # 3. Rebuild and Update Connections
    # =========================================================================

    connections["Switch Opción Seleccionada"] = {
        "main": [
            [{"node": "H F1 Inicio Reserva", "type": "main", "index": 0}],
            [{"node": "H F1 Inicio IA", "type": "main", "index": 0}],
            [{"node": "API Obtener Reseñas", "type": "main", "index": 0}],
            [{"node": "H F1 Inicio Escribir Reseña", "type": "main", "index": 0}],
            [{"node": "H F1 Inicio Revisar Reserva", "type": "main", "index": 0}],
            [{"node": "H Escalar a Agente", "type": "main", "index": 0}],
            [{"node": "H Opción Inválida1", "type": "main", "index": 0}]
        ]
    }

    connections["Enrutar por Estado1"] = {
        "main": [
            [{"node": "H Menú Evaluador Opción", "type": "main", "index": 0}],
            [{"node": "H Menú Principal", "type": "main", "index": 0}],
            [{"node": "H F1 CheckIn", "type": "main", "index": 0}],
            [{"node": "H F1 CheckOut", "type": "main", "index": 0}],
            [{"node": "H Escalar a Agente", "type": "main", "index": 0}],
            [{"node": "H No Texto", "type": "main", "index": 0}],
            [{"node": "H Normalizar Revisar Reserva", "type": "main", "index": 0}],
            [{"node": "H Normalizar Escribir Reseña", "type": "main", "index": 0}],
            [{"node": "H Normalizar IA", "type": "main", "index": 0}],
            [{"node": "H Normalizar Paso Reserva", "type": "main", "index": 0}],
            [{"node": "H Normalizar Huespedes e Identidad", "type": "main", "index": 0}],
            [{"node": "H Normalizar Huespedes e Identidad", "type": "main", "index": 0}],
            [{"node": "H Normalizar Huespedes e Identidad", "type": "main", "index": 0}],
            [{"node": "H Normalizar Huespedes e Identidad", "type": "main", "index": 0}],
            [{"node": "H Normalizar Huespedes e Identidad", "type": "main", "index": 0}],
            [{"node": "H Normalizar Huespedes e Identidad", "type": "main", "index": 0}],
            [{"node": "H En Construcción", "type": "main", "index": 0}]
        ]
    }

    connections["¿Acción Revisar Reserva?"] = {
        "main": [
            [{"node": "API Consultar Reserva", "type": "main", "index": 0}],
            [{"node": "API Cancelar Reserva", "type": "main", "index": 0}],
            [{"node": "API Pagar Saldo", "type": "main", "index": 0}],
            [{"node": "Preparar Salida", "type": "main", "index": 0}]
        ]
    }

    connections["API Pagar Saldo"] = {
        "main": [
            [{"node": "H Formatear Pago Exitoso", "type": "main", "index": 0}]
        ]
    }

    connections["H Formatear Pago Exitoso"] = {
        "main": [
            [{"node": "Preparar Salida", "type": "main", "index": 0}]
        ]
    }

    connections["API Obtener Reseñas"] = {
        "main": [
            [{"node": "H Formatear Reseñas", "type": "main", "index": 0}]
        ]
    }

    connections["H Formatear Reseñas"] = {
        "main": [
            [{"node": "Preparar Salida", "type": "main", "index": 0}]
        ]
    }

    connections["H F1 Inicio Escribir Reseña"] = {
        "main": [
            [{"node": "Preparar Salida", "type": "main", "index": 0}]
        ]
    }

    connections["H Normalizar Escribir Reseña"] = {
        "main": [
            [{"node": "¿Acción Escribir Reseña?", "type": "main", "index": 0}]
        ]
    }

    connections["¿Acción Escribir Reseña?"] = {
        "main": [
            [{"node": "API Guardar Reseña", "type": "main", "index": 0}],
            [{"node": "Preparar Salida", "type": "main", "index": 0}]
        ]
    }

    connections["API Guardar Reseña"] = {
        "main": [
            [{"node": "H Reseña Guardada", "type": "main", "index": 0}]
        ]
    }

    connections["H Reseña Guardada"] = {
        "main": [
            [{"node": "Preparar Salida", "type": "main", "index": 0}]
        ]
    }

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
            [{"node": "¿IA Fechas Válidas?", "type": "main", "index": 0}]
        ]
    }

    connections["¿IA Fechas Válidas?"] = {
        "main": [
            [{"node": "API Disponibilidad IA", "type": "main", "index": 0}],
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

    # Save to V8_ChatbotReservas.json
    output_path = 'flows/n8n/V8_ChatbotReservas.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(flow, f, indent=2, ensure_ascii=False)

    print(f"Successfully generated {output_path} with {len(nodes)} nodes.")

if __name__ == '__main__':
    generate_v8()

