"""Ada — trivia para dos personas, 100 % web y con estado compartido."""

from __future__ import annotations

import html
import re
import uuid
from urllib.parse import quote, urlencode

import requests
import streamlit as st

st.set_page_config(
    page_title="Ada 💜 | Trivia para dos",
    page_icon="💜",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(ellipse at 15% 0%, #25204d 0%, #0b1020 55%, #080d18 100%);
    }
    .block-container { max-width: 700px; padding-top: 1.1rem; padding-bottom: 3rem; }
    [data-testid="stHeader"] { background: transparent; }
    #MainMenu, footer { visibility: hidden; }
    .ada-logo { font-size: 3rem; font-weight: 900; line-height: 1.05;
        letter-spacing: -.07em; text-align: center; margin: 0.3rem 0 0; }
    .ada-logo span { color: #c3a6ff; }
    .ada-sub { text-align: center; color: #b1b9d4; margin-bottom: 1.5rem; }
    .ada-card { border: 1px solid #4b4669; border-radius: 22px;
        padding: 1.15rem; background: rgba(255,255,255,.045); margin: 0.7rem 0 1rem; }
    .ada-eyebrow { color: #c7b3ff; font-weight: 750; font-size: .8rem;
        letter-spacing: .1em; text-transform: uppercase; }
    .ada-question { font-size: clamp(1.25rem, 5vw, 1.8rem);
        font-weight: 800; letter-spacing: -.02em; line-height: 1.3; margin-top: .6rem; }
    .ada-status { font-size: 1rem; color: #c8cdeb; margin-top: .45rem; }
    .ada-clock { font-variant-numeric: tabular-nums; color: #eecbff;
        font-size: 2.2rem; font-weight: 900; }
    .stButton > button { min-height: 3.25rem; border-radius: 15px; font-weight: 700; }
    div[data-testid="stMetric"] { border: 1px solid #44435e;
        border-radius: 16px; background: #14172b; padding: .85rem; }
    [data-testid="stTextInput"] input { border-radius: 12px; }
    @media(max-width: 600px) {
      .block-container {padding-left: 1rem; padding-right: 1rem;}
      .ada-logo {font-size: 2.8rem;}
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
                "apikey": key,  # sb_secret_..., NO es un Bearer JWT
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
        # Nunca incluir la clave o los headers en el mensaje de error.
        raise BackendError(str(detail)[:240])
    try:
        return response.json()
    except ValueError:
        raise BackendError("Respuesta inesperada de la base de datos.") from None


def title():
    st.markdown('<div class="ada-logo">ada<span>♡</span></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="ada-sub">Un duelo de preguntas para dos personas, estén donde estén.</div>',
        unsafe_allow_html=True,
    )


def invite_url(code: str) -> str:
    # Devuelve exclusivamente el código de sala; JAMÁS comparte el token personal ?me=.
    return f"{st.context.url}?{urlencode({'room': code})}"


def enter_room(code: str, token: str):
    st.query_params["room"] = code
    st.query_params["me"] = token
    st.rerun()


def landing(room_code: str):
    title()
    if room_code:
        st.markdown("### 💌 Te invitaron a jugar")
        st.info(f"Sala: {room_code}. Solo necesitas escribir tu nombre para entrar.")
    else:
        st.markdown("### 🎮 Una partida, dos celulares")
        st.caption("Sin cuentas · Sin descargas · 10 preguntas · Resultados sincronizados")

    with st.form("enter", clear_on_submit=False):
        name = st.text_input("¿Cómo te llamas?", max_chars=18, placeholder="Escribe tu nombre")
        submitted = st.form_submit_button(
            "Unirme a la sala 💜" if room_code else "Crear sala e invitar 💜",
            use_container_width=True,
            type="primary",
        )

    if submitted:
        name = " ".join(name.split())
        if len(name) < 1 or len(name) > 18:
            st.warning("Escribe un nombre de entre 1 y 18 caracteres.")
            return
        token = str(uuid.uuid4())
        try:
            if room_code:
                rpc("ada_join_room", {"p_code": room_code, "p_name": name, "p_token": token})
                enter_room(room_code, token)
            else:
                code = rpc("ada_create_room", {"p_name": name, "p_token": token})
                enter_room(str(code), token)
        except BackendError as ex:
            st.error(str(ex))

    st.markdown(
        '<div class="ada-card">📱 Abre Ada desde Safari, Chrome u otro navegador. '
        'Ambos juegan al mismo tiempo desde sus propios teléfonos.</div>',
        unsafe_allow_html=True,
    )


def scoreboard(players):
    cols = st.columns(2, gap="small")
    for i, player in enumerate(players[:2]):
        with cols[i]:
            st.metric(str(player["name"]), f'{int(player["score"])} pts')


def render_invite(code: str):
    link = invite_url(code)
    st.markdown("**💌 Enlace para invitar**")
    st.code(link, language=None)
    message = f"¡Juguemos Ada! 💜 Entra aquí: {link}"
    st.link_button("Enviar por WhatsApp", f"https://wa.me/?text={quote(message)}", use_container_width=True)
    st.caption("Copia el enlace para mandarlo también por Instagram u otro chat.")


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

    if phase == "waiting":
        st.markdown(
            '<div class="ada-card"><div class="ada-eyebrow">Esperando jugador</div>'
            '<div class="ada-question">✨ Comparte el enlace con tu persona favorita.</div>'
            '<div class="ada-status">La partida comenzará automáticamente cuando los dos entren.</div></div>',
            unsafe_allow_html=True,
        )
        render_invite(code)
        return

    remaining = int(data.get("remaining_seconds") or 0)
    if phase == "countdown":
        st.markdown("### ¡Ya están los dos! 🎉")
        st.markdown(f'<div class="ada-clock">{remaining}s</div>', unsafe_allow_html=True)
        st.info("Preparen sus dedos. La primera pregunta aparece automáticamente.")
        return

    if phase == "finished":
        st.markdown("## 🏆 ¡Partida terminada!")
        sorted_players = sorted(players, key=lambda p: int(p["score"]), reverse=True)
        if len(sorted_players) == 2 and sorted_players[0]["score"] == sorted_players[1]["score"]:
            st.success("¡Empataron! 💜")
        elif sorted_players:
            st.success(f'🥇 Ganó {sorted_players[0]["name"]}. ¡Felicidades!')
        if not st.session_state.get(f"celebrated_{code}", False):
            st.session_state[f"celebrated_{code}"] = True
            st.balloons()
        st.caption("Para jugar otra partida, abre la página de inicio y crea otra sala.")
        if st.button("Crear otra sala", use_container_width=True, type="primary"):
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
                    rpc(
                        "ada_submit_answer",
                        {"p_code": code, "p_token": token, "p_choice": i},
                    )
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
            st.success("¡Acertaste! +100 puntos 🎯")
        else:
            st.caption("Esta vez no sumaste puntos. ¡Vamos por la siguiente!")
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
