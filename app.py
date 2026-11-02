"""Ada: una partida compartida, con temas y cantidad de preguntas a elección."""

from __future__ import annotations

import html
import re
import uuid
from urllib.parse import quote, urlencode

import requests
import streamlit as st

st.set_page_config(
    page_title="Ada ♡",
    page_icon="💗",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    :root {
        --rose-1: #fff7fb;
        --rose-2: #ffeaf3;
        --rose-3: #ffd6e8;
        --rose-4: #f8bdd8;
        --rose-5: #ec8fbb;
        --rose-6: #d96aa2;
        --plum-1: #7b4060;
        --plum-2: #5d3350;
        --ink-1: #4c3241;
        --ink-2: #7a6170;
        --line: rgba(217,106,162,.20);
        --card: rgba(255,255,255,.78);
        --card-strong: rgba(255,255,255,.92);
        --shadow: 0 18px 45px rgba(172, 91, 132, .12);
    }

    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(circle at top left, #fffafc 0%, #ffeef5 25%, #ffe3ef 48%, #fff6fa 75%, #fffdfd 100%);
    }
    [data-testid="stHeader"] { background: transparent; }
    #MainMenu, footer { visibility: hidden; }

    .block-container {
        max-width: 760px;
        padding-top: 1rem;
        padding-bottom: 3rem;
    }

    html, body, [class*="css"] {
        color: var(--ink-1);
    }

    .ada-top {
        text-align: center;
        margin: .35rem 0 1.15rem;
    }
    .ada-logo {
        font-size: 3.4rem;
        font-weight: 900;
        line-height: 1;
        letter-spacing: -.08em;
        margin: 0;
        color: var(--plum-2);
    }
    .ada-logo span {
        color: var(--rose-6);
    }
    .ada-mini {
        margin-top: .45rem;
        font-size: .98rem;
        color: var(--ink-2);
    }

    .ada-panel {
        background: linear-gradient(180deg, var(--card-strong) 0%, var(--card) 100%);
        border: 1px solid var(--line);
        border-radius: 26px;
        padding: 1.2rem 1.15rem;
        box-shadow: var(--shadow);
        backdrop-filter: blur(10px);
        margin: .85rem 0 1rem;
    }

    /* La tarjeta es el formulario nativo de Streamlit, no un div suelto. */
    [data-testid="stForm"] {
        border: 1px solid rgba(217,106,162,.16) !important;
        border-radius: 24px !important;
        background: rgba(255,255,255,.62) !important;
        padding: 1rem !important;
        box-shadow: 0 12px 30px rgba(210,128,165,.10);
    }

    .ada-card {
        border: 1px solid rgba(217,106,162,.16);
        border-radius: 24px;
        padding: 1.15rem;
        background: linear-gradient(180deg, rgba(255,255,255,.82), rgba(255,247,251,.92));
        box-shadow: 0 12px 30px rgba(210, 128, 165, .10);
        margin: .85rem 0 1rem;
    }

    .ada-eyebrow {
        color: var(--rose-6);
        font-weight: 800;
        font-size: .78rem;
        letter-spacing: .12em;
        text-transform: uppercase;
    }

    .ada-section-title {
        font-size: clamp(1.5rem, 5vw, 2.45rem);
        font-weight: 850;
        line-height: 1.12;
        letter-spacing: -.04em;
        margin: .2rem 0 .25rem;
        color: var(--plum-2);
    }

    .ada-soft {
        color: var(--ink-2);
        font-size: 1rem;
        line-height: 1.55;
        margin-top: .2rem;
    }

    .ada-love-note {
        color: var(--ink-2);
        font-size: clamp(.97rem, 2.7vw, 1.07rem);
        line-height: 1.65;
        margin: .55rem 0 .15rem;
        max-width: 60ch;
    }

    .ada-question {
        font-size: clamp(1.22rem, 4.6vw, 1.75rem);
        font-weight: 800;
        letter-spacing: -.02em;
        line-height: 1.3;
        margin-top: .45rem;
        color: var(--plum-2);
    }

    .ada-clock {
        font-variant-numeric: tabular-nums;
        color: var(--rose-6);
        font-size: 2.2rem;
        font-weight: 900;
        letter-spacing: -.04em;
        margin-top: .1rem;
    }

    .ada-chip-row {
        display: flex;
        flex-wrap: wrap;
        gap: .5rem;
        margin-top: .45rem;
    }
    .ada-chip {
        background: rgba(248, 189, 216, .28);
        color: var(--plum-2);
        border: 1px solid rgba(217,106,162,.18);
        padding: .42rem .72rem;
        border-radius: 999px;
        font-size: .88rem;
        font-weight: 650;
    }

    [data-testid="stTextInput"] input,
    [data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    [data-testid="stMultiSelect"] div[data-baseweb="select"] > div {
        border-radius: 16px !important;
        border: 1px solid rgba(217,106,162,.18) !important;
        background: rgba(255,255,255,.88) !important;
        box-shadow: none !important;
    }

    div[data-testid="stMetric"] {
        border: 1px solid rgba(217,106,162,.16);
        border-radius: 20px;
        background: linear-gradient(180deg, rgba(255,255,255,.94), rgba(255,240,247,.95));
        padding: 1rem .9rem;
        box-shadow: 0 10px 24px rgba(210,128,165,.08);
    }
    div[data-testid="stMetric"] label,
    div[data-testid="stMetric"] [data-testid="stMetricLabel"] {
        color: var(--ink-2) !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: var(--plum-2) !important;
    }

    .stButton > button,
    div[data-testid="stFormSubmitButton"] > button {
        min-height: 3.3rem;
        border-radius: 16px;
        font-weight: 800;
        border: none !important;
        background: linear-gradient(135deg, #f6abc9 0%, #eb93ba 48%, #d96aa2 100%) !important;
        color: white !important;
        box-shadow: 0 12px 24px rgba(217, 106, 162, .26);
        transition: transform .12s ease, box-shadow .12s ease;
    }
    .stButton > button:hover,
    div[data-testid="stFormSubmitButton"] > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 14px 26px rgba(217, 106, 162, .30);
    }

    div[role="radiogroup"] {
        gap: .55rem;
    }
    div[role="radiogroup"] label {
        background: rgba(255,255,255,.72);
        border: 1px solid rgba(217,106,162,.16);
        border-radius: 999px;
        padding: .4rem .7rem;
    }

    [data-baseweb="tag"] {
        border-radius: 999px !important;
        background: rgba(248, 189, 216, .32) !important;
        color: var(--plum-2) !important;
    }

    [data-testid="stCodeBlock"] {
        border-radius: 18px;
        border: 1px solid rgba(217,106,162,.16);
    }

    [data-testid="stAlert"] {
        border-radius: 18px;
        border: 1px solid rgba(217,106,162,.14);
    }

    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #f8bdd8 0%, #eb93ba 55%, #d96aa2 100%);
    }

    @media (max-width: 640px) {
        .block-container { padding-left: 1rem; padding-right: 1rem; }
        .ada-logo { font-size: 3rem; }
        .ada-panel, .ada-card { border-radius: 22px; padding: 1rem; }
        .ada-chip { font-size: .84rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


class BackendError(Exception):
    """Error controlado de la API de Ada."""


def rpc(function_name: str, arguments: dict):
    """La clave secreta vive solo en Python de Streamlit Cloud, nunca en el móvil."""
    try:
        url = str(st.secrets["SUPABASE_URL"]).rstrip("/")
        key = str(st.secrets["SUPABASE_SECRET_KEY"])
    except (KeyError, FileNotFoundError):
        raise BackendError(
            "Falta configurar SUPABASE_URL y SUPABASE_SECRET_KEY en los Secrets de Streamlit."
        ) from None

    try:
        response = requests.post(
            f"{url}/rest/v1/rpc/{function_name}",
            headers={
                "apikey": key,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            json=arguments,
            timeout=12,
        )
    except requests.RequestException:
        raise BackendError("No se pudo conectar con la base de datos. Intenta de nuevo.") from None

    if not response.ok:
        try:
            detail = response.json().get("message", "Error de base de datos")
        except ValueError:
            detail = "No se pudo procesar la solicitud."
        raise BackendError(str(detail)[:240])
    try:
        return response.json()
    except ValueError:
        raise BackendError("Respuesta inesperada de la base de datos.") from None


def title():
    st.markdown(
        '<div class="ada-top"><div class="ada-logo">ada<span>♡</span></div>'
        '<div class="ada-mini">un espacio bonito para jugar un ratito</div></div>',
        unsafe_allow_html=True,
    )


def invite_url(code: str) -> str:
    return f"{st.context.url}?{urlencode({'room': code})}"


def enter_room(code: str, token: str):
    st.query_params["room"] = code
    st.query_params["me"] = token
    st.rerun()


def landing(room_code: str):
    title()
    if room_code:
        st.markdown(
            '<div class="ada-panel"><div class="ada-section-title">'
            'Qué bueno que llegaste ♡</div></div>',
            unsafe_allow_html=True,
        )
        st.caption(f"Sala {room_code}")
        with st.form("enter_invited"):
            name = st.text_input("¿Cómo te llamas?", max_chars=18, placeholder="Escribe tu nombre")
            submitted = st.form_submit_button("Entrar ♡", use_container_width=True, type="primary")
        if submitted:
            name = " ".join(name.split())
            if not (1 <= len(name) <= 18):
                st.warning("Escribe un nombre de entre 1 y 18 caracteres.")
                return
            token = str(uuid.uuid4())
            try:
                rpc("ada_join_room", {"p_code": room_code, "p_name": name, "p_token": token})
                enter_room(room_code, token)
            except BackendError as ex:
                st.error(str(ex))
    else:
        try:
            catalog = rpc("ada_topics_catalog", {})
        except BackendError as ex:
            st.error(f"No se pudo cargar el banco de preguntas: {ex}")
            st.info("Actualiza Supabase con actualizar_supabase.sql y banco_preguntas.sql.")
            return
        topics = [str(t["name"]) for t in catalog if int(t["count"]) >= 200]
        if not topics:
            st.warning("Aún no hay temas habilitados. Ejecuta primero los dos archivos SQL de la actualización.")
            return

        st.markdown(
            '<div class="ada-panel">'
            '<div class="ada-eyebrow">Crear partida</div>'
            '<div class="ada-section-title">¿Jugamos? ♡</div>'
            '<div class="ada-love-note">No me importan los kilómetros que nos separen '
            'físicamente; siempre te llevo en mi mente y en mi corazón.</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        mode = st.radio("Modo", ["Un tema", "Varios temas", "Todos los temas"], horizontal=True, label_visibility="collapsed")

        with st.form("create_game"):
            name = st.text_input("¿Cómo te llamas?", max_chars=18, placeholder="Escribe tu nombre")
            if mode == "Un tema":
                selected = [st.selectbox("Elige un tema", topics)]
            elif mode == "Varios temas":
                selected = st.multiselect("Selecciona dos o más temas", topics, default=topics[:2])
            else:
                selected = topics
                st.markdown(
                    '<div class="ada-chip-row">' + ''.join(f'<span class="ada-chip">{html.escape(t)}</span>' for t in topics) + '</div>',
                    unsafe_allow_html=True,
                )
            rounds = st.select_slider("¿Cuántas preguntas?", options=[10, 20, 40, 50], value=20)
            submitted = st.form_submit_button("Crear sala e invitar ♡", use_container_width=True, type="primary")

        if submitted:
            name = " ".join(name.split())
            if not (1 <= len(name) <= 18):
                st.warning("Escribe un nombre de entre 1 y 18 caracteres.")
                return
            if not selected or (mode == "Varios temas" and len(selected) < 2):
                st.warning("Selecciona por lo menos dos temas para jugar combinados.")
                return
            token = str(uuid.uuid4())
            try:
                code = rpc(
                    "ada_create_room",
                    {
                        "p_name": name,
                        "p_token": token,
                        "p_topics": selected,
                        "p_total": rounds,
                    },
                )
                enter_room(str(code), token)
            except BackendError as ex:
                st.error(str(ex))


def scoreboard(players):
    cols = st.columns(2, gap="small")
    for i, player in enumerate(players[:2]):
        with cols[i]:
            st.metric(str(player["name"]), f'{int(player["score"])} pts')


def render_invite(code: str):
    link = invite_url(code)
    st.markdown("**💌 Enlace para compartir**")
    st.code(link, language=None)
    message = f"¿Jugamos un ratito? ♡ {link}"
    st.link_button("Enviar por WhatsApp", f"https://wa.me/?text={quote(message)}", use_container_width=True)
    st.caption("También puedes copiarlo y mandarlo por donde prefieras.")


@st.fragment(run_every="1s")
def live_game(code: str, token: str):
    try:
        data = rpc("ada_room_state", {"p_code": code, "p_token": token})
    except BackendError as ex:
        st.error(str(ex))
        if st.button("Salir de esta sala", use_container_width=True):
            st.query_params.clear()
            st.rerun()
        return

    phase = data["phase"]
    players = data.get("players", [])
    st.caption(f"Sala {code} · {len(players)}/2 jugadores · Tú: {data['my_name']}")
    scoreboard(players)
    chosen_topics = data.get("topics", [])
    if chosen_topics:
        st.markdown(
            '<div class="ada-chip-row">' + ''.join(f'<span class="ada-chip">{html.escape(t)}</span>' for t in chosen_topics)
            + f'<span class="ada-chip">{data.get("configured_rounds", data.get("total_rounds", 10))} preguntas</span></div>',
            unsafe_allow_html=True,
        )

    if phase == "waiting":
        st.markdown(
            '<div class="ada-card"><div class="ada-eyebrow">Todo listo</div>'
            '<div class="ada-question">Ya estás aquí ♡</div>'
            '<div class="ada-soft">Solo falta que llegue la otra persona.</div></div>',
            unsafe_allow_html=True,
        )
        render_invite(code)
        return

    remaining = int(data.get("remaining_seconds") or 0)
    if phase == "countdown":
        st.markdown(
            '<div class="ada-card"><div class="ada-eyebrow">A punto de empezar</div>'
            '<div class="ada-question">Ya están aquí los dos ♡</div></div>',
            unsafe_allow_html=True,
        )
        st.markdown(f'<div class="ada-clock">{remaining}s</div>', unsafe_allow_html=True)
        st.caption("En un momento aparece la primera pregunta.")
        return

    if phase == "finished":
        st.markdown(
            '<div class="ada-card"><div class="ada-eyebrow">Final</div>'
            '<div class="ada-question">Y así terminó esta partida ♡</div></div>',
            unsafe_allow_html=True,
        )
        sorted_players = sorted(players, key=lambda p: int(p["score"]), reverse=True)
        if len(sorted_players) == 2 and sorted_players[0]["score"] == sorted_players[1]["score"]:
            st.success("Empate ♡ ¿Se animan a otra?")
        elif sorted_players:
            st.success(f'Esta vez ganó {sorted_players[0]["name"]} ♡')
        if not st.session_state.get(f"celebrated_{code}", False):
            st.session_state[f"celebrated_{code}"] = True
            st.balloons()
        if st.button("¿Otra partida? ♡", use_container_width=True, type="primary"):
            st.query_params.clear()
            st.rerun()
        return

    question = data.get("question")
    if not question:
        st.info("Preparando la siguiente pregunta...")
        return

    round_number = int(data["round"])
    total = int(data["total_rounds"])
    st.progress(round_number / max(total, 1), text=f"Pregunta {round_number} de {total}")

    st.markdown(
        '<div class="ada-card">'
        f'<div class="ada-eyebrow">{html.escape(str(question["category"]))}</div>'
        f'<div class="ada-question">{html.escape(str(question["prompt"]))}</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    caption = "⏱️ Tiempo para responder" if phase == "question" else "🔍 Respuesta revelada"
    st.caption(caption)
    st.markdown(f'<div class="ada-clock">{remaining}s</div>', unsafe_allow_html=True)

    options = question["choices"]
    if phase == "question":
        chosen = data.get("my_choice")
        if chosen is not None:
            st.success(f'Tu respuesta: {"ABCD"[int(chosen)]}. Esperando a la otra persona…')
        for i, option in enumerate(options):
            clicked = st.button(
                f'{"ABCD"[i]}.  {option}',
                key=f"choice_{code}_{round_number}_{i}",
                use_container_width=True,
                disabled=chosen is not None or remaining <= 0,
                type="primary" if chosen == i else "secondary",
            )
            if clicked:
                try:
                    rpc("ada_submit_answer", {"p_code": code, "p_token": token, "p_choice": i})
                    st.rerun(scope="fragment")
                except BackendError as ex:
                    st.warning(str(ex))
        answered = sum(bool(p.get("answered")) for p in players)
        st.caption(f"{answered}/2 respuestas recibidas")
        return

    if phase == "reveal":
        correct_index = int(question["correct_index"])
        st.success(f'✅ Respuesta correcta: {"ABCD"[correct_index]}. {options[correct_index]}')
        st.info(str(question.get("explanation") or ""))
        if data.get("my_choice") is None:
            st.warning("Se agotó tu tiempo para responder esta pregunta.")
        elif int(data["my_choice"]) == correct_index:
            st.success("¡Acertaste! +100 puntos ♡")
        else:
            st.caption("Esta vez no sumaste puntos. Vamos por la siguiente.")
        st.caption("La próxima pregunta aparecerá automáticamente.")


def main():
    code = str(st.query_params.get("room", "")).strip().upper()
    token = str(st.query_params.get("me", "")).strip()
    if code and not re.fullmatch(r"[A-F0-9]{8}", code):
        st.warning("El enlace de invitación no tiene un código de sala válido.")
        if st.button("Ir al inicio"):
            st.query_params.clear()
            st.rerun()
        return
    if token and not code:
        st.query_params.clear()
        st.rerun()
    if token and not re.fullmatch(r"[0-9a-fA-F-]{36}", token):
        st.warning("Identificador de jugador no válido.")
        if st.button("Entrar con otro nombre"):
            st.query_params.pop("me", None)
            st.rerun()
        return
    if code and token:
        title()
        live_game(code, token)
    else:
        landing(code)


if __name__ == "__main__":
    main()
