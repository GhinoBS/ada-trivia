-- ADA WEB ONLINE · Ejecutar UNA VEZ en Supabase > SQL Editor.
-- Recomendado: crear un proyecto Supabase exclusivo para Ada.
-- Crea tablas con RLS y solo funciones accesibles mediante la clave secreta del servidor.

create table if not exists public.ada_rooms (
    id uuid primary key default gen_random_uuid(),
    code text not null unique check (code ~ '^[A-F0-9]{8}$'),
    phase text not null default 'waiting'
        check (phase in ('waiting', 'countdown', 'question', 'reveal', 'finished')),
    round_no integer not null default 0,
    deadline timestamptz,
    created_at timestamptz not null default clock_timestamp()
);

create table if not exists public.ada_players (
    id uuid primary key default gen_random_uuid(),
    room_id uuid not null references public.ada_rooms(id) on delete cascade,
    name text not null check (char_length(name) between 1 and 18),
    token uuid not null unique,
    created_at timestamptz not null default clock_timestamp()
);
create unique index if not exists ada_player_name_room_unique
    on public.ada_players (room_id, lower(name));

create table if not exists public.ada_questions (
    id bigint generated always as identity primary key,
    category text not null,
    prompt text not null unique,
    choices text[] not null check (array_length(choices, 1) = 4),
    correct_index integer not null check (correct_index between 0 and 3),
    explanation text not null
);

create table if not exists public.ada_room_questions (
    room_id uuid not null references public.ada_rooms(id) on delete cascade,
    round_no integer not null check (round_no between 1 and 10),
    question_id bigint not null references public.ada_questions(id),
    primary key (room_id, round_no),
    unique (room_id, question_id)
);

create table if not exists public.ada_answers (
    room_id uuid not null references public.ada_rooms(id) on delete cascade,
    round_no integer not null,
    player_id uuid not null references public.ada_players(id) on delete cascade,
    choice_index integer not null check (choice_index between 0 and 3),
    submitted_at timestamptz not null default clock_timestamp(),
    primary key (room_id, round_no, player_id),
    foreign key (room_id, round_no) references public.ada_room_questions(room_id, round_no)
);

alter table public.ada_rooms enable row level security;
alter table public.ada_players enable row level security;
alter table public.ada_questions enable row level security;
alter table public.ada_room_questions enable row level security;
alter table public.ada_answers enable row level security;
-- Sin políticas para anon/authenticated. Solo el servidor, usando sb_secret_, puede operar.
revoke all on public.ada_rooms, public.ada_players, public.ada_questions,
    public.ada_room_questions, public.ada_answers from anon, authenticated;

-- Banco de 24 preguntas. Las partidas eligen 10 sin repetirse.
insert into public.ada_questions(category, prompt, choices, correct_index, explanation) values
('Ciencia', '¿Cuál es el planeta más cercano al Sol?', array['Marte','Venus','Mercurio','Júpiter'], 2, 'Mercurio es el primer planeta del Sistema Solar.'),
('Geografía', '¿En qué continente está Perú?', array['Asia','América del Sur','Europa','África'], 1, 'Perú se encuentra en la costa occidental de América del Sur.'),
('Animales', '¿Cuántos corazones tiene un pulpo?', array['Uno','Dos','Tres','Cuatro'], 2, 'Los pulpos tienen tres corazones.'),
('Cine', '¿Cómo se llama el vaquero de Toy Story?', array['Buzz','Woody','Andy','Rex'], 1, 'Woody es el sheriff de juguete de Toy Story.'),
('Cultura general', '¿Cuántos lados tiene un hexágono?', array['Cinco','Seis','Siete','Ocho'], 1, 'Hexa significa seis.'),
('Naturaleza', '¿Cuál es el océano más grande?', array['Atlántico','Índico','Pacífico','Ártico'], 2, 'El océano Pacífico ocupa la mayor superficie.'),
('Ciencia', '¿Qué gas necesitamos principalmente para respirar?', array['Helio','Oxígeno','Neón','Argón'], 1, 'Las células utilizan el oxígeno para obtener energía.'),
('Música', '¿Cuántas cuerdas tiene una guitarra clásica?', array['Cuatro','Cinco','Seis','Ocho'], 2, 'Una guitarra clásica estándar tiene seis cuerdas.'),
('Espacio', '¿Cómo se llama nuestra galaxia?', array['Andrómeda','Vía Láctea','Triángulo','Centauro'], 1, 'Nuestro Sistema Solar pertenece a la Vía Láctea.'),
('Historia', '¿Qué civilización construyó Machu Picchu?', array['Romana','Maya','Inca','Griega'], 2, 'Machu Picchu fue construido durante el Imperio inca.'),
('Comida', '¿Cuál de estos ingredientes es habitual en el guacamole?', array['Palta','Papa','Coco','Arroz'], 0, 'El guacamole se prepara principalmente con palta o aguacate.'),
('Geografía', '¿Cuál es la capital de Francia?', array['Madrid','Roma','París','Berlín'], 2, 'París es la capital francesa.'),
('Animales', '¿Qué animal es un mamífero marino?', array['Tiburón','Delfín','Atún','Pulpo'], 1, 'Los delfines respiran aire y amamantan a sus crías.'),
('Matemáticas', '¿Cuánto es 9 × 7?', array['56','63','72','81'], 1, 'Nueve multiplicado por siete es sesenta y tres.'),
('Ciencia', '¿A qué temperatura se congela el agua pura a presión normal?', array['0 °C','10 °C','50 °C','100 °C'], 0, 'El punto de congelación es 0 °C a presión atmosférica normal.'),
('Arte', '¿Quién pintó La noche estrellada?', array['Picasso','Van Gogh','Dalí','Monet'], 1, 'Vincent van Gogh pintó La noche estrellada en 1889.'),
('Lenguaje', '¿Cuál es el antónimo de «valiente»?', array['Audaz','Temeroso','Firme','Decidido'], 1, 'Temeroso describe a alguien que siente miedo.'),
('Naturaleza', '¿Qué proceso usan las plantas para producir alimento con luz?', array['Evaporación','Fotosíntesis','Fermentación','Digestión'], 1, 'La fotosíntesis transforma energía luminosa en energía química.'),
('Deportes', '¿Cuántos jugadores de un equipo hay en cancha en fútbol tradicional?', array['Cinco','Siete','Nueve','Once'], 3, 'Cada equipo juega con once futbolistas, incluido el arquero.'),
('Tecnología', '¿Qué significa la sigla GPS?', array['Sistema de Posicionamiento Global','Programa General Seguro','Guía Postal Satelital','Grupo de Procesos Simples'], 0, 'GPS significa Global Positioning System.'),
('Comida', '¿Qué bebida se obtiene a partir de granos tostados y molidos?', array['Té','Café','Limonada','Chicha'], 1, 'El café se elabora con granos de café tostados y molidos.'),
('Cultura general', '¿Cuántos minutos tiene una hora?', array['30','45','60','90'], 2, 'Una hora equivale a sesenta minutos.'),
('Geografía', '¿Qué país tiene forma de bota en el mapa?', array['Portugal','Noruega','Italia','Canadá'], 2, 'La península italiana se representa comúnmente con forma de bota.'),
('Animales', '¿Cuál de estos animales puede volar?', array['Pingüino','Avestruz','Murciélago','Kiwi'], 2, 'El murciélago es un mamífero capaz de vuelo activo.')
on conflict (prompt) do nothing;

-- Avanza fases solo con el reloj de la base de datos: ambos móviles comparten el mismo estado.
create or replace function public.ada_step_room(p_room_id uuid)
returns void language plpgsql security definer set search_path = public, pg_temp as $$
declare
    v_room public.ada_rooms%rowtype;
    v_now timestamptz := clock_timestamp();
    v_answered integer;
    v_total integer;
begin
    select * into v_room from public.ada_rooms where id = p_room_id for update;
    if not found then return; end if;

    if v_room.phase = 'countdown' and v_room.deadline <= v_now then
        update public.ada_rooms
           set phase = 'question', round_no = 1,
               deadline = clock_timestamp() + interval '20 seconds'
         where id = p_room_id;
    elsif v_room.phase = 'question' then
        select count(*) into v_answered from public.ada_answers
         where room_id = p_room_id and round_no = v_room.round_no;
        if v_room.deadline <= v_now or v_answered >= 2 then
            update public.ada_rooms
               set phase = 'reveal', deadline = clock_timestamp() + interval '5 seconds'
             where id = p_room_id;
        end if;
    elsif v_room.phase = 'reveal' and v_room.deadline <= v_now then
        select count(*) into v_total from public.ada_room_questions where room_id = p_room_id;
        if v_room.round_no >= v_total then
            update public.ada_rooms set phase = 'finished', deadline = null where id = p_room_id;
        else
            update public.ada_rooms
               set phase = 'question', round_no = round_no + 1,
                   deadline = clock_timestamp() + interval '20 seconds'
             where id = p_room_id;
        end if;
    end if;
end;
$$;

create or replace function public.ada_create_room(p_name text, p_token uuid)
returns text language plpgsql security definer set search_path = public, pg_temp as $$
declare
    v_id uuid;
    v_code text;
    v_name text := btrim(p_name);
begin
    if char_length(v_name) not between 1 and 18 then
        raise exception 'Escribe un nombre entre 1 y 18 caracteres.';
    end if;
    if (select count(*) from public.ada_questions) < 10 then
        raise exception 'Faltan preguntas. Ejecuta todo el archivo database.sql.';
    end if;
    v_code := upper(substring(replace(gen_random_uuid()::text, '-', ''), 1, 8));
    insert into public.ada_rooms(code) values (v_code) returning id into v_id;
    insert into public.ada_players(room_id, name, token) values (v_id, v_name, p_token);
    insert into public.ada_room_questions(room_id, round_no, question_id)
        select v_id, row_number() over (order by random())::integer, q.id
        from (select id from public.ada_questions order by random() limit 10) as q;
    return v_code;
end;
$$;

create or replace function public.ada_join_room(p_code text, p_name text, p_token uuid)
returns boolean language plpgsql security definer set search_path = public, pg_temp as $$
declare
    v_room public.ada_rooms%rowtype;
    v_name text := btrim(p_name);
begin
    if char_length(v_name) not between 1 and 18 then
        raise exception 'Escribe un nombre entre 1 y 18 caracteres.';
    end if;
    select * into v_room from public.ada_rooms where code = upper(btrim(p_code)) for update;
    if not found then raise exception 'Esta sala no existe. Pide un enlace nuevo.'; end if;
    if exists (select 1 from public.ada_players where room_id = v_room.id and token = p_token) then
        return true;
    end if;
    if v_room.phase <> 'waiting' then
        raise exception 'Esta partida ya comenzó o terminó. Crea otra sala.';
    end if;
    if (select count(*) from public.ada_players where room_id = v_room.id) >= 2 then
        raise exception 'La sala ya tiene dos personas.';
    end if;
    if exists (select 1 from public.ada_players where room_id = v_room.id and lower(name) = lower(v_name)) then
        raise exception 'Ese nombre ya está usado en la sala. Elige otro.';
    end if;
    insert into public.ada_players(room_id, name, token) values (v_room.id, v_name, p_token);
    if (select count(*) from public.ada_players where room_id = v_room.id) = 2 then
        update public.ada_rooms
           set phase = 'countdown', deadline = clock_timestamp() + interval '5 seconds'
         where id = v_room.id;
    end if;
    return true;
end;
$$;

create or replace function public.ada_submit_answer(p_code text, p_token uuid, p_choice integer)
returns boolean language plpgsql security definer set search_path = public, pg_temp as $$
declare
    v_room public.ada_rooms%rowtype;
    v_player_id uuid;
begin
    if p_choice not between 0 and 3 then raise exception 'Respuesta inválida.'; end if;
    select * into v_room from public.ada_rooms where code = upper(btrim(p_code)) for update;
    if not found then raise exception 'Sala no encontrada.'; end if;
    select id into v_player_id from public.ada_players
     where room_id = v_room.id and token = p_token;
    if not found then raise exception 'Tu acceso a esta sala no es válido.'; end if;
    perform public.ada_step_room(v_room.id);
    select * into v_room from public.ada_rooms where id = v_room.id;
    if v_room.phase <> 'question' or v_room.deadline <= clock_timestamp() then
        raise exception 'Se agotó el tiempo. Espera la siguiente pregunta.';
    end if;
    insert into public.ada_answers(room_id, round_no, player_id, choice_index)
        values (v_room.id, v_room.round_no, v_player_id, p_choice)
        on conflict (room_id, round_no, player_id) do nothing;
    perform public.ada_step_room(v_room.id);
    return true;
end;
$$;

create or replace function public.ada_room_state(p_code text, p_token uuid)
returns jsonb language plpgsql security definer set search_path = public, pg_temp as $$
declare
    v_room public.ada_rooms%rowtype;
    v_player public.ada_players%rowtype;
    v_question public.ada_questions%rowtype;
    v_players jsonb;
    v_own_choice integer;
    v_question_json jsonb := null;
    v_total integer;
begin
    select * into v_room from public.ada_rooms where code = upper(btrim(p_code));
    if not found then raise exception 'Sala no encontrada.'; end if;
    select * into v_player from public.ada_players
     where room_id = v_room.id and token = p_token;
    if not found then raise exception 'No tienes acceso a esta sala. Usa tu enlace original.'; end if;
    perform public.ada_step_room(v_room.id);
    select * into v_room from public.ada_rooms where id = v_room.id;

    select coalesce(jsonb_agg(jsonb_build_object(
        'name', p.name,
        'score', (select coalesce(sum(case when a.choice_index = q.correct_index then 100 else 0 end), 0)::integer
                  from public.ada_answers a
                  join public.ada_room_questions rq on rq.room_id = a.room_id and rq.round_no = a.round_no
                  join public.ada_questions q on q.id = rq.question_id
                 where a.player_id = p.id),
        'answered', exists (select 1 from public.ada_answers a
                           where a.player_id = p.id and a.room_id = v_room.id
                             and a.round_no = v_room.round_no)
    ) order by p.created_at), '[]'::jsonb)
    into v_players
    from public.ada_players p where p.room_id = v_room.id;

    select count(*) into v_total from public.ada_room_questions where room_id = v_room.id;
    if v_room.round_no > 0 then
        select q.* into v_question
        from public.ada_room_questions rq
        join public.ada_questions q on q.id = rq.question_id
        where rq.room_id = v_room.id and rq.round_no = v_room.round_no;
        if found and v_room.phase in ('question', 'reveal') then
            v_question_json := jsonb_build_object(
                'category', v_question.category,
                'prompt', v_question.prompt,
                'choices', to_jsonb(v_question.choices),
                'correct_index', case when v_room.phase = 'reveal' then v_question.correct_index else null end,
                'explanation', case when v_room.phase = 'reveal' then v_question.explanation else null end
            );
        end if;
        select choice_index into v_own_choice from public.ada_answers
        where player_id = v_player.id and room_id = v_room.id and round_no = v_room.round_no;
    end if;

    return jsonb_build_object(
        'code', v_room.code,
        'phase', v_room.phase,
        'round', v_room.round_no,
        'total_rounds', v_total,
        'my_name', v_player.name,
        'my_choice', v_own_choice,
        'players', v_players,
        'question', v_question_json,
        'remaining_seconds', case when v_room.deadline is null then null
            else greatest(0, ceil(extract(epoch from (v_room.deadline - clock_timestamp())))::integer) end
    );
end;
$$;

-- Rechaza invocaciones hechas con las claves públicas de Supabase.
revoke all on function public.ada_step_room(uuid) from public, anon, authenticated;
revoke all on function public.ada_create_room(text, uuid) from public, anon, authenticated;
revoke all on function public.ada_join_room(text, text, uuid) from public, anon, authenticated;
revoke all on function public.ada_submit_answer(text, uuid, integer) from public, anon, authenticated;
revoke all on function public.ada_room_state(text, uuid) from public, anon, authenticated;
grant execute on function public.ada_step_room(uuid) to service_role;
grant execute on function public.ada_create_room(text, uuid) to service_role;
grant execute on function public.ada_join_room(text, text, uuid) to service_role;
grant execute on function public.ada_submit_answer(text, uuid, integer) to service_role;
grant execute on function public.ada_room_state(text, uuid) to service_role;
