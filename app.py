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
        st.caption("🎯 Temas: " + ", ".join(chosen_topics) +
                   f" · {data.get('configured_rounds', data.get('total_rounds', 10))} preguntas")

    if phase == "waiting":
        st.markdown(
            '<div class="ada-card"><div class="ada-eyebrow">Todo listo</div>'
            '<div class="ada-question">Ya estás aquí ♡</div>'
            '<div class="ada-status">Solo falta que llegue la otra persona.</div></div>',
            unsafe_allow_html=True,
        )
        render_invite(code)
        return

    remaining = int(data.get("remaining_seconds") or 0)
    if phase == "countdown":
        st.markdown("### Ya están aquí los dos ♡")
        st.markdown(f'<div class="ada-clock">{remaining}s</div>', unsafe_allow_html=True)
        st.caption("En un momento empieza la primera pregunta.")
        return

    if phase == "finished":
        st.markdown("## Y así terminó esta partida ♡")
        sorted_players = sorted(players, key=lambda p: int(p["score"]), reverse=True)
        if len(sorted_players) == 2 and sorted_players[0]["score"] == sorted_players[1]["score"]:
            st.success("¡Empate! ¿Una revancha?")
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
