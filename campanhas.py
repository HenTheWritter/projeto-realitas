# ENTREGA 11: CAMPANHAS (criar, listar, editar, excluir)
# ENTREGA 12: VINCULAÇÃO AGENTE <-> CAMPANHA (N:N)
#
# Regras:
# - Quem cria a campanha é o Mestre e recebe um código de convite.
# - Qualquer usuário que digitar o código entra como Jogador e adiciona seus agentes.
# - Cada jogador remove os próprios agentes (ou sai da campanha).
# - O Mestre remove qualquer agente ou jogador, edita e exclui a campanha.

import random
import string
from datetime import date
import pandas as pd
from persistencia import (
    ARQUIVO_USUARIOS,
    ARQUIVO_PERSONAGENS,
    ARQUIVO_CAMPANHAS,
    ARQUIVO_CAMPANHA_MEMBROS,
    ARQUIVO_CAMPANHA_AGENTES,
    carregar_tabela,
    salvar_tabela,
)
from prestigio import obter_pp, obter_patente, definir_pp


# ======================================================
# AUXILIARES
# ======================================================

def _txt(valor, padrao="-"):
    if valor is None or pd.isna(valor):
        return padrao
    s = str(valor).strip()
    return s if s and s.lower() != "nan" else padrao


def _colunas_texto(df, colunas):
    """Evita erro de tipo ao gravar texto em colunas lidas como vazias (float)."""
    for c in colunas:
        if c in df.columns:
            df[c] = df[c].astype(object)
    return df


def gerar_codigo(df_campanhas):
    existentes = set(df_campanhas["codigo"].astype(str).str.upper()) if not df_campanhas.empty else set()
    alfabeto = string.ascii_uppercase + string.digits
    while True:
        codigo = "OP-" + "".join(random.choices(alfabeto, k=5))
        if codigo not in existentes:
            return codigo


def obter_campanha(id_campanha):
    df = carregar_tabela(ARQUIVO_CAMPANHAS)
    if df.empty:
        return None
    linha = df[df["id"].astype(int) == int(id_campanha)]
    return None if linha.empty else linha.iloc[0].to_dict()


def eh_membro(id_campanha, id_usuario):
    df = carregar_tabela(ARQUIVO_CAMPANHA_MEMBROS)
    if df.empty:
        return False
    achou = (df["id_campanha"].astype(int) == int(id_campanha)) & (df["id_usuario"].astype(int) == int(id_usuario))
    return bool(achou.any())


def campanhas_do_usuario(id_usuario):
    """Campanhas em que o usuário é mestre OU jogador."""
    df_c = carregar_tabela(ARQUIVO_CAMPANHAS)
    if df_c.empty:
        return df_c
    df_m = carregar_tabela(ARQUIVO_CAMPANHA_MEMBROS)
    ids_membro = set()
    if not df_m.empty:
        ids_membro = set(df_m[df_m["id_usuario"].astype(int) == int(id_usuario)]["id_campanha"].astype(int))
    mask = (df_c["id_mestre"].astype(int) == int(id_usuario)) | (df_c["id"].astype(int).isin(ids_membro))
    return df_c[mask].sort_values("id").reset_index(drop=True)


def jogadores_da_campanha(id_campanha):
    df_m = carregar_tabela(ARQUIVO_CAMPANHA_MEMBROS)
    df_u = carregar_tabela(ARQUIVO_USUARIOS)
    if df_m.empty or df_u.empty:
        return pd.DataFrame(columns=["id", "nome"])
    ids = df_m[df_m["id_campanha"].astype(int) == int(id_campanha)]["id_usuario"].astype(int).tolist()
    res = df_u[df_u["id"].astype(int).isin(ids)][["id", "nome"]].copy()
    res["id"] = res["id"].astype(int)
    return res.sort_values("nome").reset_index(drop=True)


def agentes_da_campanha(id_campanha):
    """Agentes da mesa (merge: campanha_agentes + personagens + nome do jogador)."""
    df_ca = carregar_tabela(ARQUIVO_CAMPANHA_AGENTES)
    df_p = carregar_tabela(ARQUIVO_PERSONAGENS)
    if df_ca.empty or df_p.empty:
        return pd.DataFrame()

    ids = df_ca[df_ca["id_campanha"].astype(int) == int(id_campanha)]["id_personagem"].astype(int)
    agentes = df_p[df_p["id"].astype(int).isin(ids)].copy()
    if agentes.empty:
        return pd.DataFrame()

    agentes["id_usuario"] = agentes["id_usuario"].astype(int)
    df_u = carregar_tabela(ARQUIVO_USUARIOS)[["id", "nome"]].copy()
    df_u["id"] = df_u["id"].astype(int)
    df_u = df_u.rename(columns={"id": "id_usuario", "nome": "jogador"})

    agentes = agentes.merge(df_u, on="id_usuario", how="left")
    agentes["jogador"] = agentes["jogador"].fillna("?")
    return agentes.sort_values(["jogador", "nome"]).reset_index(drop=True)


def _listar_agentes_numerados(agentes):
    for i, a in agentes.iterrows():
        print(f"[{i + 1:>2}] {a['nome']} ({a['jogador']}) | {a['classe']} NEX {a['NEX']}%")


def _escolher_numero(total, mensagem):
    escolha = input(mensagem).strip()
    if escolha == "0":
        return None
    if not escolha.isdigit() or not (1 <= int(escolha) <= total):
        print("[ERRO] Número inválido.")
        return None
    return int(escolha) - 1


# ======================================================
# LIMPEZA / SINCRONIA (usadas também pelo main)
# ======================================================

def _remover_vinculo_agente(id_campanha, id_personagem):
    df_ca = carregar_tabela(ARQUIVO_CAMPANHA_AGENTES)
    if df_ca.empty:
        return
    rem = (df_ca["id_campanha"].astype(int) == int(id_campanha)) & (df_ca["id_personagem"].astype(int) == int(id_personagem))
    salvar_tabela(df_ca[~rem], ARQUIVO_CAMPANHA_AGENTES)


def _remover_membro(id_campanha, id_usuario):
    """Tira o jogador da campanha e todos os agentes dele da mesa."""
    df_p = carregar_tabela(ARQUIVO_PERSONAGENS)
    ids_agentes = []
    if not df_p.empty:
        ids_agentes = df_p[df_p["id_usuario"].astype(int) == int(id_usuario)]["id"].astype(int).tolist()

    df_ca = carregar_tabela(ARQUIVO_CAMPANHA_AGENTES)
    if not df_ca.empty:
        rem = (df_ca["id_campanha"].astype(int) == int(id_campanha)) & (df_ca["id_personagem"].astype(int).isin(ids_agentes))
        salvar_tabela(df_ca[~rem], ARQUIVO_CAMPANHA_AGENTES)

    df_m = carregar_tabela(ARQUIVO_CAMPANHA_MEMBROS)
    if not df_m.empty:
        rem = (df_m["id_campanha"].astype(int) == int(id_campanha)) & (df_m["id_usuario"].astype(int) == int(id_usuario))
        salvar_tabela(df_m[~rem], ARQUIVO_CAMPANHA_MEMBROS)


def excluir_campanha_por_id(id_campanha):
    id_c = int(id_campanha)
    for arquivo in (ARQUIVO_CAMPANHAS, ARQUIVO_CAMPANHA_MEMBROS, ARQUIVO_CAMPANHA_AGENTES):
        df = carregar_tabela(arquivo)
        if df.empty:
            continue
        coluna = "id" if arquivo == ARQUIVO_CAMPANHAS else "id_campanha"
        salvar_tabela(df[df[coluna].astype(int) != id_c], arquivo)


def limpar_usuario_campanhas(id_usuario):
    """Usada ao excluir uma conta: apaga as campanhas que ele mestra e tira ele das demais."""
    df_c = carregar_tabela(ARQUIVO_CAMPANHAS)
    if not df_c.empty:
        for id_c in df_c[df_c["id_mestre"].astype(int) == int(id_usuario)]["id"].astype(int).tolist():
            excluir_campanha_por_id(id_c)

    df_m = carregar_tabela(ARQUIVO_CAMPANHA_MEMBROS)
    if not df_m.empty:
        salvar_tabela(df_m[df_m["id_usuario"].astype(int) != int(id_usuario)], ARQUIVO_CAMPANHA_MEMBROS)


def atualizar_nome_mestre(id_usuario, novo_nome):
    """Usada ao editar o perfil: mantém o nome do mestre atualizado nas campanhas."""
    df = carregar_tabela(ARQUIVO_CAMPANHAS)
    if df.empty:
        return
    mask = df["id_mestre"].astype(int) == int(id_usuario)
    if mask.any():
        df = _colunas_texto(df, ["nomeMestre"])
        df.loc[mask, "nomeMestre"] = novo_nome
        salvar_tabela(df, ARQUIVO_CAMPANHAS)


# ======================================================
# EXIBIÇÃO
# ======================================================

def exibir_cabecalho(camp, mestre):
    print("\n" + "=" * 70)
    print(f" CAMPANHA: {str(camp['nome']).upper()}")
    print(f" Mestre: {_txt(camp.get('nomeMestre'))} | Criada em: {_txt(camp.get('dataCriacao'))}")
    if mestre:
        print(f" Código de convite: {camp['codigo']}  (compartilhe com seus jogadores)")
    print(f" Descrição: {_txt(camp.get('descricao'))}")
    print("-" * 70)


def exibir_mesa(id_campanha):
    agentes = agentes_da_campanha(id_campanha)
    jogadores = jogadores_da_campanha(id_campanha)

    print(f" MESA ({len(agentes)} agente(s) | {len(jogadores)} jogador(es)):")
    if agentes.empty:
        print("   (Nenhum agente na mesa ainda)")
    else:
        for i, a in agentes.iterrows():
            pp = obter_pp(a.to_dict())
            patente = obter_patente(pp)["nome"]
            print(f" [{i + 1:>2}] {str(a['nome']).ljust(18)} ({a['jogador']}) | {a['classe']} NEX {a['NEX']}% | "
                  f"{patente} ({pp} PP) | PV {a['pvMAX']} SAN {a['sanMAX']} PE {a['peMAX']}")

    if not jogadores.empty:
        com_agente = set(agentes["id_usuario"]) if not agentes.empty else set()
        sem = [str(r["nome"]) for _, r in jogadores.iterrows() if int(r["id"]) not in com_agente]
        if sem:
            print(f"   Jogadores sem agente: {', '.join(sem)}")
    print("-" * 70)
    return agentes


# ======================================================
# CRIAR / ENTRAR
# ======================================================

def criar_campanha(usuario):
    print("\n--- CRIAR CAMPANHA ---")
    nome = input("Nome da campanha: ").strip()
    if not nome:
        print("[ERRO] O nome não pode ficar vazio. Cancelado.")
        return
    descricao = input("Descrição: ").strip()

    df = carregar_tabela(ARQUIVO_CAMPANHAS)
    novo_id = 1 if df.empty else int(df["id"].max()) + 1
    codigo = gerar_codigo(df)

    registro = {
        "id": novo_id, "nome": nome, "id_mestre": int(usuario["id"]),
        "nomeMestre": str(usuario["nome"]), "descricao": descricao,
        "dataCriacao": str(date.today()), "codigo": codigo,
    }
    df = pd.concat([df, pd.DataFrame([registro])], ignore_index=True)
    if salvar_tabela(df, ARQUIVO_CAMPANHAS):
        print(f"[OK] Campanha '{nome}' criada! Código de convite: {codigo}")


def entrar_campanha(usuario, exibir_ficha):
    print("\n--- ENTRAR EM UMA CAMPANHA ---")
    codigo = input("Código de convite (ex.: OP-AB12C): ").strip().upper()

    df = carregar_tabela(ARQUIVO_CAMPANHAS)
    if df.empty:
        print("[ERRO] Nenhuma campanha existe ainda.")
        return
    achou = df[df["codigo"].astype(str).str.upper() == codigo]
    if achou.empty:
        print("[ERRO] Código inválido.")
        return

    camp = achou.iloc[0].to_dict()
    id_c = int(camp["id"])
    uid = int(usuario["id"])

    if int(camp["id_mestre"]) == uid:
        print("[ERRO] Você é o mestre desta campanha.")
        return

    if eh_membro(id_c, uid):
        print(f"Você já faz parte de '{camp['nome']}'.")
    else:
        df_m = carregar_tabela(ARQUIVO_CAMPANHA_MEMBROS)
        novo_id = 1 if df_m.empty else int(df_m["id"].max()) + 1
        reg = {"id": novo_id, "id_campanha": id_c, "id_usuario": uid}
        df_m = pd.concat([df_m, pd.DataFrame([reg])], ignore_index=True)
        if not salvar_tabela(df_m, ARQUIVO_CAMPANHA_MEMBROS):
            return
        print(f"[OK] Você entrou na campanha '{camp['nome']}' (Mestre: {_txt(camp.get('nomeMestre'))})!")

    if input("Deseja adicionar um agente seu agora? (S/N): ").strip().upper() == "S":
        adicionar_agente_campanha(camp, usuario)

    menu_campanha(id_c, usuario, exibir_ficha)


# ======================================================
# AGENTES NA CAMPANHA
# ======================================================

def adicionar_agente_campanha(camp, usuario):
    id_c = int(camp["id"])
    uid = int(usuario["id"])

    if int(camp["id_mestre"]) == uid:
        print("[ERRO] O mestre não adiciona agentes à própria mesa.")
        return
    if not eh_membro(id_c, uid):
        print("[ERRO] Você precisa entrar na campanha pelo código primeiro.")
        return

    df_p = carregar_tabela(ARQUIVO_PERSONAGENS)
    meus = df_p[df_p["id_usuario"].astype(int) == uid] if not df_p.empty else df_p
    if meus.empty:
        print("[ERRO] Você ainda não possui agentes. Crie um no menu principal.")
        return

    df_ca = carregar_tabela(ARQUIVO_CAMPANHA_AGENTES)
    ja_na_mesa = set()
    if not df_ca.empty:
        ja_na_mesa = set(df_ca[df_ca["id_campanha"].astype(int) == id_c]["id_personagem"].astype(int))

    disponiveis = meus[~meus["id"].astype(int).isin(ja_na_mesa)].reset_index(drop=True)
    if disponiveis.empty:
        print("[ERRO] Todos os seus agentes já estão nesta campanha.")
        return

    print("\n--- SEUS AGENTES DISPONÍVEIS ---")
    for i, a in disponiveis.iterrows():
        print(f"[{i + 1:>2}] {a['nome']} | {a['classe']} NEX {a['NEX']}%")

    idx = _escolher_numero(len(disponiveis), "\nNúmero do agente (ou 0 para cancelar): ")
    if idx is None:
        return
    agente = disponiveis.iloc[idx]

    novo_id = 1 if df_ca.empty else int(df_ca["id"].max()) + 1
    reg = {"id": novo_id, "id_campanha": id_c, "id_personagem": int(agente["id"])}
    df_ca = pd.concat([df_ca, pd.DataFrame([reg])], ignore_index=True)
    if salvar_tabela(df_ca, ARQUIVO_CAMPANHA_AGENTES):
        print(f"[OK] '{agente['nome']}' agora faz parte da campanha '{camp['nome']}'!")


def remover_agente_campanha(camp, usuario, mestre):
    """Jogador remove só os próprios agentes; o mestre remove qualquer um."""
    id_c = int(camp["id"])
    agentes = agentes_da_campanha(id_c)

    if not agentes.empty and not mestre:
        agentes = agentes[agentes["id_usuario"] == int(usuario["id"])].reset_index(drop=True)

    if agentes.empty:
        print("[ERRO] Não há agentes seus para remover nesta campanha." if not mestre
              else "[ERRO] Não há agentes nesta campanha.")
        return

    print("\n--- REMOVER AGENTE DA CAMPANHA ---")
    _listar_agentes_numerados(agentes)
    idx = _escolher_numero(len(agentes), "\nNúmero do agente a remover (ou 0 para cancelar): ")
    if idx is None:
        return

    agente = agentes.iloc[idx]
    if input(f"Remover '{agente['nome']}' da campanha? (S/N): ").strip().upper() != "S":
        print("Cancelado.")
        return

    _remover_vinculo_agente(id_c, int(agente["id"]))
    print(f"[OK] '{agente['nome']}' foi removido da campanha.")


def remover_jogador(camp):
    """Somente o mestre: remove um jogador inteiro (e todos os agentes dele)."""
    id_c = int(camp["id"])
    jogadores = jogadores_da_campanha(id_c)
    if jogadores.empty:
        print("[ERRO] Nenhum jogador na campanha.")
        return

    print("\n--- REMOVER JOGADOR ---")
    for i, j in jogadores.iterrows():
        print(f"[{i + 1:>2}] {j['nome']}")

    idx = _escolher_numero(len(jogadores), "\nNúmero do jogador a remover (ou 0 para cancelar): ")
    if idx is None:
        return

    jogador = jogadores.iloc[idx]
    if input(f"Remover '{jogador['nome']}' e todos os agentes dele da campanha? (S/N): ").strip().upper() != "S":
        print("Cancelado.")
        return

    _remover_membro(id_c, int(jogador["id"]))
    print(f"[OK] '{jogador['nome']}' foi removido da campanha.")


def sair_da_campanha(camp, usuario):
    """Retorna True se o jogador saiu."""
    if input(f"Sair da campanha '{camp['nome']}'? Seus agentes serão removidos dela. (S/N): ").strip().upper() != "S":
        print("Cancelado.")
        return False
    _remover_membro(int(camp["id"]), int(usuario["id"]))
    print("[OK] Você saiu da campanha.")
    return True


def ver_ficha_agente(id_campanha, usuario, mestre, exibir_ficha):
    """Mestre abre a ficha de qualquer agente; jogador só dos próprios."""
    agentes = agentes_da_campanha(id_campanha)
    if not agentes.empty and not mestre:
        agentes = agentes[agentes["id_usuario"] == int(usuario["id"])].reset_index(drop=True)

    if agentes.empty:
        print("[ERRO] Nenhum agente disponível para visualizar.")
        return

    print("\n--- VER FICHA ---")
    _listar_agentes_numerados(agentes)
    idx = _escolher_numero(len(agentes), "\nNúmero do agente (ou 0 para cancelar): ")
    if idx is None:
        return

    df_p = carregar_tabela(ARQUIVO_PERSONAGENS)
    linha = df_p[df_p["id"].astype(int) == int(agentes.iloc[idx]["id"])]
    if linha.empty:
        print("[ERRO] Agente não encontrado.")
        return
    exibir_ficha(linha.iloc[0].to_dict())
    input("\nENTER para continuar...")


# ======================================================
# AÇÕES EXCLUSIVAS DO MESTRE
# ======================================================

def conceder_pp(id_campanha):
    agentes = agentes_da_campanha(id_campanha)
    if agentes.empty:
        print("[ERRO] Não há agentes na mesa.")
        return

    print("\n--- CONCEDER PONTOS DE PRESTÍGIO ---")
    _listar_agentes_numerados(agentes)
    idx = _escolher_numero(len(agentes), "\nNúmero do agente (ou 0 para cancelar): ")
    if idx is None:
        return

    agente = agentes.iloc[idx]
    pp_atual = obter_pp(agente.to_dict())
    try:
        qtd = int(input(f"PP a conceder a {agente['nome']} (atual: {pp_atual}; use negativo para remover): ").strip())
    except ValueError:
        print("[ERRO] Digite um número inteiro.")
        return

    novo = max(0, pp_atual + qtd)
    if definir_pp(int(agente["id"]), novo):
        antiga = obter_patente(pp_atual)["nome"]
        nova = obter_patente(novo)["nome"]
        print(f"[OK] {agente['nome']}: {pp_atual} -> {novo} PP.")
        if nova != antiga:
            verbo = "promovido" if novo > pp_atual else "rebaixado"
            print(f" *** {agente['nome']} foi {verbo} para {nova}! ***")


def editar_campanha(camp):
    id_c = int(camp["id"])
    while True:
        atual = obter_campanha(id_c)
        if atual is None:
            return

        print(f"\n--- EDITAR CAMPANHA: {str(atual['nome']).upper()} ---")
        print("[1] Nome")
        print("[2] Descrição")
        print("[3] Gerar novo código de convite")
        print("[0] Voltar")
        op = input("Opção: ").strip()

        if op == "0":
            return

        df = carregar_tabela(ARQUIVO_CAMPANHAS)
        df = _colunas_texto(df, ["nome", "descricao", "codigo"])
        mask = df["id"].astype(int) == id_c

        if op == "1":
            novo = input(f"Novo nome ({atual['nome']}): ").strip()
            if not novo:
                print("Nada alterado.")
                continue
            df.loc[mask, "nome"] = novo
        elif op == "2":
            novo = input("Nova descrição: ").strip()
            df.loc[mask, "descricao"] = novo
        elif op == "3":
            novo_codigo = gerar_codigo(df)
            df.loc[mask, "codigo"] = novo_codigo
            print(f"Novo código: {novo_codigo} (o código antigo deixa de funcionar; quem já entrou continua na campanha).")
        else:
            print("[ERRO] Opção inválida.")
            continue

        if salvar_tabela(df, ARQUIVO_CAMPANHAS):
            print("[OK] Campanha atualizada!")


def excluir_campanha(camp):
    """Retorna True se excluiu."""
    if input(f"Tem certeza que deseja EXCLUIR a campanha '{camp['nome']}'? Jogadores e vínculos serão removidos. (S/N): ").strip().upper() != "S":
        print("Cancelado.")
        return False
    excluir_campanha_por_id(int(camp["id"]))
    print("[OK] Campanha excluída.")
    return True


# ======================================================
# MENUS
# ======================================================

def menu_campanha(id_campanha, usuario, exibir_ficha):
    while True:
        camp = obter_campanha(id_campanha)
        if camp is None:
            print("[AVISO] Esta campanha não existe mais.")
            break

        uid = int(usuario["id"])
        mestre = int(camp["id_mestre"]) == uid
        if not mestre and not eh_membro(id_campanha, uid):
            print("[AVISO] Você não faz mais parte desta campanha.")
            break

        exibir_cabecalho(camp, mestre)
        exibir_mesa(id_campanha)

        if mestre:
            print("[1] Ver ficha de um agente da mesa")
            print("[2] Conceder Pontos de Prestígio (PP)")
            print("[3] Editar campanha")
            print("[4] Remover agente da mesa")
            print("[5] Remover jogador da campanha")
            print("[6] Excluir campanha")
            print("[0] Voltar")
            op = input("Opção: ").strip()

            if op == "0": break
            elif op == "1": ver_ficha_agente(id_campanha, usuario, True, exibir_ficha)
            elif op == "2": conceder_pp(id_campanha)
            elif op == "3": editar_campanha(camp)
            elif op == "4": remover_agente_campanha(camp, usuario, True)
            elif op == "5": remover_jogador(camp)
            elif op == "6":
                if excluir_campanha(camp):
                    break
            else: print("[ERRO] Opção inválida.")
        else:
            print("[1] Adicionar meu agente")
            print("[2] Remover meu agente")
            print("[3] Ver ficha de um dos meus agentes")
            print("[4] Sair da campanha")
            print("[0] Voltar")
            op = input("Opção: ").strip()

            if op == "0": break
            elif op == "1": adicionar_agente_campanha(camp, usuario)
            elif op == "2": remover_agente_campanha(camp, usuario, False)
            elif op == "3": ver_ficha_agente(id_campanha, usuario, False, exibir_ficha)
            elif op == "4":
                if sair_da_campanha(camp, usuario):
                    break
            else: print("[ERRO] Opção inválida.")


def listar_campanhas(usuario, exibir_ficha):
    uid = int(usuario["id"])
    while True:
        minhas = campanhas_do_usuario(uid)
        if minhas.empty:
            print("\nVocê não participa de nenhuma campanha. Crie uma ou entre com um código.")
            return

        print(f"\n--- CAMPANHAS DE {str(usuario['nome']).upper()} ---")
        for i, c in minhas.iterrows():
            papel = "Mestre" if int(c["id_mestre"]) == uid else "Jogador"
            print(f"[{i + 1:>2}] {str(c['nome']).ljust(26)} Mestre: {_txt(c.get('nomeMestre')).ljust(15)} | Você: {papel}")

        escolha = input("\nNúmero da campanha para abrir (ou 0 para voltar): ").strip()
        if escolha == "0":
            return
        if not escolha.isdigit() or not (1 <= int(escolha) <= len(minhas)):
            print("[ERRO] Número inválido.")
            continue
        menu_campanha(int(minhas.iloc[int(escolha) - 1]["id"]), usuario, exibir_ficha)


def menu_campanhas(usuario, exibir_ficha):
    while True:
        print("\n--- CAMPANHAS ---")
        print("[1] Minhas Campanhas (abrir / editar / excluir)")
        print("[2] Criar Nova Campanha (você será o Mestre)")
        print("[3] Entrar em uma Campanha (código de convite)")
        print("[0] Voltar")
        op = input("Opção: ").strip()

        if op == "0": break
        elif op == "1": listar_campanhas(usuario, exibir_ficha)
        elif op == "2": criar_campanha(usuario)
        elif op == "3": entrar_campanha(usuario, exibir_ficha)
        else: print("[ERRO] Opção inválida.")
