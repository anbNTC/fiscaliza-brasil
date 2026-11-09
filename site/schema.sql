-- Fiscaliza Brasil · banco de dados (Supabase)
-- Rode este arquivo inteiro em Supabase > SQL Editor > New query > Run,
-- DEPOIS de criar o seu usuário em Authentication > Users > Add user.
-- Pode rodar de novo sem problema: ele não apaga nada.

-- 1) Administradores: só quem está nesta lista edita o site.
create table if not exists public.admins (
  user_id uuid primary key references auth.users(id) on delete cascade,
  created_at timestamptz not null default now()
);
alter table public.admins enable row level security;
drop policy if exists "admin lê a si mesmo" on public.admins;
create policy "admin lê a si mesmo" on public.admins for select using (user_id = auth.uid());

-- Coloca na lista todos os usuários que já existem (só você, se seguiu o guia).
insert into public.admins (user_id) select id from auth.users on conflict do nothing;

create or replace function public.is_admin() returns boolean
language sql stable security definer set search_path = public as
$$ select exists (select 1 from public.admins where user_id = auth.uid()) $$;

-- 2) Perfil da página de links (uma linha só, id = 1).
create table if not exists public.links_profile (
  id int primary key default 1 check (id = 1),
  name text not null default 'Abraão Nery',
  handle text default '@oabraaonery',
  bio text default 'Vamos fiscalizar tudo.',
  theme text not null default 'claro' check (theme in ('claro','escuro')),
  avatar_path text,
  style jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);
insert into public.links_profile (id) values (1) on conflict do nothing;

-- 3) Botões da página de links.
create table if not exists public.links (
  id uuid primary key default gen_random_uuid(),
  label text not null,
  url text not null,
  position int not null default 0,
  active boolean not null default true,
  clicks int not null default 0,
  created_at timestamptz not null default now()
);
create index if not exists links_position_idx on public.links(position);

-- Botões iniciais (só se a tabela estiver vazia).
insert into public.links (label, url, position)
select * from (values
  ('Fiscaliza Brasil', '/', 0),
  ('Fiscalize os políticos', '/fiscalize', 1),
  ('Simulador do voto distrital', '/distrital', 2),
  ('Instagram', 'https://instagram.com/oabraaonery', 3)
) v(label, url, position)
where not exists (select 1 from public.links);

-- 4) Permissões: o público só lê; só administradores mudam.
alter table public.links_profile enable row level security;
alter table public.links enable row level security;

drop policy if exists "público lê perfil" on public.links_profile;
create policy "público lê perfil" on public.links_profile for select using (true);
drop policy if exists "admin edita perfil" on public.links_profile;
create policy "admin edita perfil" on public.links_profile for all using (public.is_admin()) with check (public.is_admin());

drop policy if exists "público lê links ativos" on public.links;
create policy "público lê links ativos" on public.links for select using (active or public.is_admin());
drop policy if exists "admin edita links" on public.links;
create policy "admin edita links" on public.links for all using (public.is_admin()) with check (public.is_admin());

-- 5) Contador de cliques (qualquer visitante soma 1, e só isso).
create or replace function public.link_click(p_id uuid) returns void
language sql security definer set search_path = public as
$$ update public.links set clicks = clicks + 1 where id = p_id and active $$;
grant execute on function public.link_click(uuid) to anon, authenticated;

-- 6) Armazenamento de imagens (foto do perfil e, no futuro, outras mídias).
insert into storage.buckets (id, name, public) values ('midia', 'midia', true)
on conflict (id) do update set public = true;

drop policy if exists "público vê mídia" on storage.objects;
create policy "público vê mídia" on storage.objects for select using (bucket_id = 'midia');
drop policy if exists "admin envia mídia" on storage.objects;
create policy "admin envia mídia" on storage.objects for insert with check (bucket_id = 'midia' and public.is_admin());
drop policy if exists "admin altera mídia" on storage.objects;
create policy "admin altera mídia" on storage.objects for update using (bucket_id = 'midia' and public.is_admin());
drop policy if exists "admin apaga mídia" on storage.objects;
create policy "admin apaga mídia" on storage.objects for delete using (bucket_id = 'midia' and public.is_admin());

-- 7) Reportes de erro enviados pelo público na ficha dos políticos.
create table if not exists public.reportes (
  id uuid primary key default gen_random_uuid(),
  pagina text, sobre text, texto text not null check (char_length(texto) between 3 and 2000), contato text,
  resolvido boolean not null default false,
  created_at timestamptz not null default now()
);
alter table public.reportes enable row level security;
drop policy if exists "público envia reporte" on public.reportes;
create policy "público envia reporte" on public.reportes for insert to anon, authenticated with check (not resolvido);
drop policy if exists "admin lê reportes" on public.reportes;
create policy "admin lê reportes" on public.reportes for select using (public.is_admin());
drop policy if exists "admin altera reportes" on public.reportes;
create policy "admin altera reportes" on public.reportes for update using (public.is_admin()) with check (public.is_admin());
drop policy if exists "admin apaga reportes" on public.reportes;
create policy "admin apaga reportes" on public.reportes for delete using (public.is_admin());

-- 8) Cliques nas manchetes do ACONTECE AGORA (para "Mais clicadas no Fiscaliza").
create table if not exists public.noticias_cliques (
  url text not null, dia date not null default current_date, titulo text, fonte text, cliques int not null default 0,
  primary key (url, dia)
);
alter table public.noticias_cliques enable row level security;
drop policy if exists "público lê cliques" on public.noticias_cliques;
create policy "público lê cliques" on public.noticias_cliques for select using (true);
create or replace function public.noticia_clique(p_url text, p_titulo text, p_fonte text) returns void
language sql security definer set search_path = public as $$
  insert into public.noticias_cliques (url, titulo, fonte, cliques) values (left(p_url, 500), left(p_titulo, 300), left(p_fonte, 40), 1)
  on conflict (url, dia) do update set cliques = noticias_cliques.cliques + 1
$$;
grant execute on function public.noticia_clique(text, text, text) to anon, authenticated;

-- 9) Contador de acessos e "no site agora" (página inicial).
create table if not exists public.acessos (id int primary key default 1 check (id = 1), total bigint not null default 0);
insert into public.acessos (id) values (1) on conflict do nothing;
create table if not exists public.sessoes (id text primary key, visto timestamptz not null default now());
alter table public.acessos enable row level security;
alter table public.sessoes enable row level security;
drop policy if exists "público lê acessos" on public.acessos;
create policy "público lê acessos" on public.acessos for select using (true);
create or replace function public.registrar_acesso(p_sessao text, p_conta boolean default true) returns json
language plpgsql security definer set search_path = public as $$
declare v_total bigint; v_agora int;
begin
  if p_conta then update public.acessos set total = total + 1 where id = 1; end if;
  if p_sessao is not null and length(p_sessao) between 8 and 64 then
    insert into public.sessoes (id, visto) values (p_sessao, now()) on conflict (id) do update set visto = now();
  end if;
  delete from public.sessoes where visto < now() - interval '15 minutes';
  select total into v_total from public.acessos where id = 1;
  select count(*) into v_agora from public.sessoes where visto > now() - interval '5 minutes';
  return json_build_object('total', v_total, 'agora', v_agora);
end $$;
grant execute on function public.registrar_acesso(text, boolean) to anon, authenticated;

-- 10) Ajustes do site editáveis no painel (ex.: lista do X na lateral do ACONTECE AGORA).
create table if not exists public.site_config (chave text primary key, valor text, atualizado timestamptz not null default now());
alter table public.site_config enable row level security;
drop policy if exists "público lê ajustes" on public.site_config;
create policy "público lê ajustes" on public.site_config for select using (true);
drop policy if exists "admin edita ajustes" on public.site_config;
create policy "admin edita ajustes" on public.site_config for all using (public.is_admin()) with check (public.is_admin());

-- 11) ACOMPANHAR: lista de políticos e partidos de cada pessoa que entrou com o e-mail (sem senha).
create table if not exists public.acompanha (
  user_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
  tipo text not null check (tipo in ('p', 'partido')),
  ref text not null check (char_length(ref) between 1 and 120),
  dados jsonb,
  criado timestamptz not null default now(),
  primary key (user_id, tipo, ref)
);
alter table public.acompanha enable row level security;
drop policy if exists "cada um vê a sua lista" on public.acompanha;
create policy "cada um vê a sua lista" on public.acompanha for select using (user_id = auth.uid());
drop policy if exists "cada um adiciona na sua lista" on public.acompanha;
create policy "cada um adiciona na sua lista" on public.acompanha for insert with check (user_id = auth.uid());
drop policy if exists "cada um altera a sua lista" on public.acompanha;
create policy "cada um altera a sua lista" on public.acompanha for update using (user_id = auth.uid()) with check (user_id = auth.uid());
drop policy if exists "cada um apaga da sua lista" on public.acompanha;
create policy "cada um apaga da sua lista" on public.acompanha for delete using (user_id = auth.uid());
-- botão "Apagar minha conta": apaga o usuário (e a lista, pelo "on delete cascade")
create or replace function public.apagar_minha_conta() returns void
language sql security definer set search_path = public, auth as $$
  delete from auth.users where id = auth.uid() and not exists (select 1 from public.admins a where a.user_id = auth.uid())
$$;
revoke all on function public.apagar_minha_conta() from public, anon;
grant execute on function public.apagar_minha_conta() to authenticated;

-- 12) RESUMO SEMANAL POR E-MAIL: só para quem marca a opção na página Acompanhando. Sai pelo link do próprio e-mail, sem login.
create table if not exists public.resumo_email (
  user_id uuid primary key default auth.uid() references auth.users(id) on delete cascade,
  ativo boolean not null default true,
  token uuid not null default gen_random_uuid(),
  atualizado timestamptz not null default now()
);
alter table public.resumo_email enable row level security;
drop policy if exists "cada um vê o seu resumo" on public.resumo_email;
create policy "cada um vê o seu resumo" on public.resumo_email for select using (user_id = auth.uid());
drop policy if exists "cada um ativa o seu resumo" on public.resumo_email;
create policy "cada um ativa o seu resumo" on public.resumo_email for insert with check (user_id = auth.uid());
drop policy if exists "cada um altera o seu resumo" on public.resumo_email;
create policy "cada um altera o seu resumo" on public.resumo_email for update using (user_id = auth.uid()) with check (user_id = auth.uid());
-- link "parar de receber" do e-mail: funciona sem login, só com o código secreto de cada pessoa
create or replace function public.sair_resumo(t uuid) returns boolean
language sql security definer set search_path = public as $$
  with u as (update public.resumo_email set ativo = false, atualizado = now() where token = t returning 1) select exists (select 1 from u)
$$;
revoke all on function public.sair_resumo(uuid) from public;
grant execute on function public.sair_resumo(uuid) to anon, authenticated;
-- lista de envio: só o robô do resumo (chave de serviço) consegue ler
create or replace function public.resumo_destinatarios() returns table (email text, token uuid, lista jsonb)
language sql security definer set search_path = public, auth as $$
  select u.email::text, r.token,
         coalesce((select jsonb_agg(jsonb_build_object('tipo', a.tipo, 'ref', a.ref, 'dados', a.dados)) from public.acompanha a where a.user_id = r.user_id), '[]'::jsonb)
  from public.resumo_email r join auth.users u on u.id = r.user_id where r.ativo
$$;
revoke all on function public.resumo_destinatarios() from public, anon, authenticated;
grant execute on function public.resumo_destinatarios() to service_role;
