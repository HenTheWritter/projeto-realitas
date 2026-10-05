# ENTREGA 2: ATRIBUTOS
# ENTREGA 3: CLASSES, NEX, RECURSOS AUTOMÁTICOS E AFINIDADE
# ENTREGA 4: PERICIAS
# ENTREGA 5: DEFESA, LIMITE DE ITENS E INVENTÁRIO
# ENTREGA 6: RITUAIS
# ENTREGA 7: ROLAGEM DE DADOS

import os
import random
from datetime import date
import pandas as pd
from persistencia import (
    ARQUIVO_PERSONAGENS,
    ARQUIVO_USUARIOS,
    ARQUIVO_ITENS,
    ARQUIVO_INVENTARIO,
    ARQUIVO_RITUAIS,
    ARQUIVO_RITUAIS_AGENTE,
    carregar_tabela,
    inicializar_banco,
    salvar_tabela,
    salvar_sessao,
    ler_sessao,
    encerrar_sessao
)

# Arquivo para manter o usuário logado entre execuções do código
ARQUIVO_SESSAO = "sessao.txt"

# Cores ANSI para o Terminal
CORES_AFINIDADE = {
    "Sangue": "\033[91m",       # Vermelho
    "Conhecimento": "\033[93m", # Amarelo 
    "Energia": "\033[95m",      # Roxo 
    "Morte": "\033[97m",        # Branco
    "Nenhuma": "\033[0m"        # Padrão
}
RESET_COR = "\033[0m"

# Lista de NEX Válidos
NEX_VALIDOS = [0] + list(range(5, 96, 5)) + [99]

# Lista Global de Perícias
LISTA_PERICIAS = [
    "acrobacia", "adestramento", "artes", "atletismo", "atualidades", 
    "ciencias", "crime", "diplomacia", "enganacao", "fortitude", 
    "furtividade", "iniciativa", "intimidacao", "intuicao", "investigacao", 
    "luta", "medicina", "ocultismo", "percepcao", "pilotagem", 
    "pontaria", "profissao", "reflexos", "religiao", "sobrevivencia", 
    "tatica", "tecnologia", "vontade"
]

PERICIA_ATRIBUTO = {
    "acrobacia": "AGI", "adestramento": "PRE", "artes": "PRE", "atletismo": "FOR",
    "atualidades": "INT", "ciencias": "INT", "crime": "AGI", "diplomacia": "PRE",
    "enganacao": "PRE", "fortitude": "VIG", "furtividade": "AGI", "iniciativa": "AGI",
    "intimidacao": "PRE", "intuicao": "PRE", "investigacao": "INT", "luta": "FOR",
    "medicina": "INT", "ocultismo": "INT", "percepcao": "PRE", "pilotagem": "AGI",
    "pontaria": "AGI", "profissao": "INT", "reflexos": "AGI", "religiao": "PRE",
    "sobrevivencia": "INT", "tatica": "INT", "tecnologia": "INT", "vontade": "PRE"
}

DADOS_VALIDOS = [4, 6, 8, 10, 12, 20]


# ======================================================
# GERENCIAMENTO DE SESSÃO / LOGIN
# ======================================================

def obter_usuario_logado():
    if not os.path.exists(ARQUIVO_SESSAO):
        return None
    try:
        with open(ARQUIVO_SESSAO, "r", encoding="utf-8") as f:
            user_id_str = f.read().strip()
            if not user_id_str:
                return None
            user_id = int(user_id_str)
            df_u = carregar_tabela(ARQUIVO_USUARIOS)
            if df_u.empty:
                return None
            
            user_row = df_u[df_u["id"].astype(int) == user_id]
            if not user_row.empty:
                return user_row.iloc[0].to_dict()
    except Exception:
        pass
    return None

def deslogar_usuario():
    encerrar_sessao()
    print("[OK] Sessão encerrada. Você foi deslogado.")


# ======================================================
# CÁLCULOS E REGRAS DO SISTEMA
# ======================================================

def calcular_recursos(classe, nex, vig, pre):
    nivel = 20 if nex == 99 else max(1, nex // 5)
    
    if classe == "Combatente":
        pv = (20 + vig) + ((nivel - 1) * (4 + vig))
        san = 12 + ((nivel - 1) * 3)
        pe = (2 + pre) + ((nivel - 1) * (2 + pre))
    elif classe == "Especialista":
        pv = (16 + vig) + ((nivel - 1) * (3 + vig))
        san = 16 + ((nivel - 1) * 4)
        pe = (3 + pre) + ((nivel - 1) * (3 + pre))
    elif classe == "Ocultista":
        pv = (12 + vig) + ((nivel - 1) * (2 + vig))
        san = 20 + ((nivel - 1) * 5)
        pe = (4 + pre) + ((nivel - 1) * (4 + pre))
    elif classe == "Mundano":
        pv = (12 + vig) + ((nivel - 1) * (2 + vig))
        san = 12 + ((nivel - 1) * 2)
        pe = (1 + pre) + ((nivel - 1) * (1 + pre))
    else:
        pv, san, pe = 10, 10, 10
        
    return pv, san, pe


def calcular_defesa_limite(agi, forca):
    defesa = 10 + agi
    limite_itens = forca * 5
    return defesa, limite_itens


def validar_atributos_ordem(nex):
    pontos_totais = 9
    if nex >= 20: pontos_totais += 1
    if nex >= 50: pontos_totais += 1
    if nex >= 80: pontos_totais += 1
    if nex >= 95: pontos_totais += 1

    limite_max = 3
    if nex >= 50: limite_max = 5
    elif nex >= 20: limite_max = 4

    print(f"\n--- DISTRIBUIÇÃO DE ATRIBUTOS (NEX {nex}%) ---")
    print(f"Regras: Máximo {limite_max}, Mínimo 0. A soma exata deve ser {pontos_totais}.")
    if pontos_totais > 9:
        print(f"Você tem {pontos_totais - 9} ponto(s) extra(s) devido ao seu NEX!")
    
    while True:
        try:
            agi = int(input("  AGI (Agilidade): "))
            forca = int(input("  FOR (Força): "))
            inte = int(input("  INT (Intelecto): "))
            pre = int(input("  PRE (Presença): "))
            vig = int(input("  VIG (Vigor): "))

            atributos = [agi, forca, inte, pre, vig]

            if any(attr < 0 or attr > limite_max for attr in atributos):
                print(f"[ERRO] Valores devem ser entre 0 e {limite_max}.\n")
                continue

            if sum(atributos) != pontos_totais:
                print(f"[ERRO] A soma deve ser {pontos_totais} (Sua soma: {sum(atributos)}).\n")
                continue

            return agi, forca, inte, pre, vig
        except ValueError:
            print("[ERRO] Digite apenas números inteiros.\n")


def imprimir_lista_numerada(pericias, elegiveis):
    linhas = []
    for i, p in enumerate(elegiveis, start=1):
        valor = pericias[p]
        nome_fmt = p.capitalize().ljust(14)
        texto_valor = f"+{valor}" if valor > 0 else "0"
        linhas.append(f"[{i:>2}] {nome_fmt}{texto_valor.rjust(3)}")

    colunas = 3
    for i in range(0, len(linhas), colunas):
        print(" | ".join(linhas[i:i + colunas]))


def distribuir_pericias(classe, nex, inte):
    pericias = {p: 0 for p in LISTA_PERICIAS}
    
    print(f"\n--- TREINAMENTO DE PERÍCIAS (INT: {inte}) ---")
    
    qtd_escolhas = 0
    
    if classe == "Ocultista":
        print("Ocultistas recebem +5 em Ocultismo e Vontade automaticamente.")
        pericias["ocultismo"] = 5
        pericias["vontade"] = 5
        qtd_escolhas = 3 + inte
        
    elif classe == "Combatente":
        print("Combatentes devem escolher suas perícias iniciais:")
        while True:
            esc1 = input("Escolha [1] Luta ou [2] Pontaria: ").strip()
            if esc1 == "1": pericias["luta"] = 5; break
            elif esc1 == "2": pericias["pontaria"] = 5; break
            else: print("[ERRO] Opção inválida.")
            
        while True:
            esc2 = input("Escolha [1] Fortitude ou [2] Reflexos: ").strip()
            if esc2 == "1": pericias["fortitude"] = 5; break
            elif esc2 == "2": pericias["reflexos"] = 5; break
            else: print("[ERRO] Opção inválida.")
            
        qtd_escolhas = 1 + inte
        
    elif classe == "Especialista":
        qtd_escolhas = 7 + inte
        
    elif classe == "Mundano":
        qtd_escolhas = 2 + inte

    def escolher_da_lista(quantidade, valor_alvo, mensagem):
        escolhidas = 0

        validas = [p for p, v in pericias.items() if (valor_alvo == 5 and v == 0) or (valor_alvo == 10 and v == 5) or (valor_alvo == 15 and v == 10)]

        if len(validas) < quantidade:
            print(f"Aviso: Você tem {quantidade} opções para melhorar, mas só {len(validas)} perícias estão disponíveis nesse grau!")
            quantidade = len(validas)

        while escolhidas < quantidade:
            validas_agora = [p for p, v in pericias.items() if (valor_alvo == 5 and v == 0) or (valor_alvo == 10 and v == 5) or (valor_alvo == 15 and v == 10)]

            print(f"\n{mensagem} ({quantidade - escolhidas} restantes):")
            imprimir_lista_numerada(pericias, validas_agora)

            escolha = input("Digite o NÚMERO da perícia: ").strip()

            if not escolha.isdigit() or not (1 <= int(escolha) <= len(validas_agora)):
                print(f"[ERRO] Número inválido. Escolha um valor entre 1 e {len(validas_agora)}.")
                continue

            nome_pericia = validas_agora[int(escolha) - 1]
            pericias[nome_pericia] = valor_alvo
            escolhidas += 1
            print(f"{nome_pericia.capitalize()} evoluída para +{valor_alvo}!")

    def escolher_evolucao_flexivel(quantidade, teto, mensagem):
        escolhidas = 0
        while escolhidas < quantidade:
            elegiveis = [p for p, v in pericias.items() if v < teto]

            if not elegiveis:
                print("Não há mais perícias elegíveis para evoluir nesse marco.")
                break

            print(f"\n{mensagem} ({quantidade - escolhidas} restantes):")
            imprimir_lista_numerada(pericias, elegiveis)
            print(" -> Escolha uma perícia no grau 0 para TREINAR, ou uma já treinada para EVOLUIR (+5 no grau atual).")

            escolha = input("Digite o NÚMERO da perícia: ").strip()

            if not escolha.isdigit() or not (1 <= int(escolha) <= len(elegiveis)):
                print(f"[ERRO] Número inválido. Escolha um valor entre 1 e {len(elegiveis)}.")
                continue

            nome_pericia = elegiveis[int(escolha) - 1]
            novo_valor = pericias[nome_pericia] + 5
            pericias[nome_pericia] = novo_valor
            escolhidas += 1
            print(f"{nome_pericia.capitalize()} evoluída para +{novo_valor}!")

    if qtd_escolhas > 0:
        escolher_da_lista(qtd_escolhas, 5, "Escolha perícias para ficar Treinado (+5)")

    qtd_evolucao = 0
    if classe == "Combatente":
        qtd_evolucao = 2 + inte
    elif classe == "Ocultista":
        qtd_evolucao = 3 + inte
    elif classe == "Especialista":
        qtd_evolucao = 5 + inte

    if nex >= 35 and qtd_evolucao > 0:
        print(f"\nNEX {nex}%: Você tem {qtd_evolucao} ponto(s) para treinar perícias novas ou evoluir para Veterano (+10).")
        escolher_evolucao_flexivel(qtd_evolucao, 10, "Escolha uma perícia para treinar ou evoluir")

    if nex >= 70 and qtd_evolucao > 0:
        print(f"\nNEX {nex}%: Você tem {qtd_evolucao} ponto(s) para treinar perícias novas ou evoluir até Expert (+15).")
        escolher_evolucao_flexivel(qtd_evolucao, 15, "Escolha uma perícia para treinar ou evoluir")

    print("\nPerícias distribuídas com sucesso!")
    return pericias


# ======================================================
# FUNÇÕES DE ROLAGEM DE DADOS
# ======================================================

def rolar_dado(lados, quantidade=1):
    return [random.randint(1, lados) for _ in range(quantidade)]


def menu_rolar_dados_livre():
    print("\n--- ROLAGEM LIVRE ---")
    print("[1] d4 | [2] d6 | [3] d8 | [4] d10 | [5] d12 | [6] d20")
    opcoes = {str(i): lados for i, lados in enumerate(DADOS_VALIDOS, start=1)}

    op = input("Escolha o dado: ").strip()
    if op not in opcoes:
        print("[ERRO] Opção inválida.")
        return
    lados = opcoes[op]

    try:
        qtd = int(input("Quantidade de dados: ").strip())
        if qtd <= 0:
            print("[ERRO] A quantidade deve ser maior que zero.")
            return
    except ValueError:
        print("[ERRO] Digite um número válido.")
        return

    resultados = rolar_dado(lados, qtd)
    print(f"\nRolando {qtd}d{lados}: {resultados}")
    print(f"Soma total: {sum(resultados)}")
    if qtd > 1:
        print(f"Maior valor: {max(resultados)}")


def selecionar_personagem_para_teste(usuario_logado):
    df = carregar_tabela(ARQUIVO_PERSONAGENS)
    meus = df[df["id_usuario"].astype(int) == int(usuario_logado["id"])] if not df.empty else df

    if meus.empty:
        print("[ERRO] Você não possui agentes cadastrados.")
        return None

    meus = meus.reset_index(drop=True)
    print("\n--- ESCOLHA O AGENTE ---")
    for i, row in meus.iterrows():
        print(f"[{i + 1:>2}] {row['nome']} (NEX {row['NEX']}%)")

    escolha = input("Número do agente (ou 0 para cancelar): ").strip()
    if escolha == "0":
        return None
    if not escolha.isdigit() or not (1 <= int(escolha) <= len(meus)):
        print("[ERRO] Número inválido.")
        return None

    return meus.iloc[int(escolha) - 1].to_dict()


def rolar_teste_atributo(personagem):
    atributos = ["AGI", "FOR", "INT", "PRE", "VIG"]

    print(f"\n--- TESTE DE ATRIBUTO ({personagem['nome']}) ---")
    for i, a in enumerate(atributos, start=1):
        print(f"[{i}] {a} ({int(personagem[a])})")

    escolha = input("Escolha o atributo: ").strip()
    if not escolha.isdigit() or not (1 <= int(escolha) <= len(atributos)):
        print("[ERRO] Número inválido.")
        return

    atributo = atributos[int(escolha) - 1]
    valor = int(personagem[atributo])
    qtd_dados = max(1, valor)

    resultados = rolar_dado(20, qtd_dados)
    maior = max(resultados)

    print(f"\n🎲 Teste de {atributo} ({valor}): rolando {qtd_dados}d20 -> {resultados}")
    print(f"Maior resultado: {maior}")


def rolar_teste_pericia(personagem):
    pericias_vals = {p: int(float(personagem.get(p, 0))) for p in LISTA_PERICIAS}

    print(f"\n--- TESTE DE PERÍCIA ({personagem['nome']}) ---")
    imprimir_lista_numerada(pericias_vals, LISTA_PERICIAS)

    escolha = input("Digite o NÚMERO da perícia: ").strip()
    if not escolha.isdigit() or not (1 <= int(escolha) <= len(LISTA_PERICIAS)):
        print("[ERRO] Número inválido.")
        return

    pericia = LISTA_PERICIAS[int(escolha) - 1]
    atributo = PERICIA_ATRIBUTO[pericia]
    valor_atributo = int(personagem[atributo])
    bonus_pericia = pericias_vals[pericia]
    qtd_dados = max(1, valor_atributo)

    resultados = rolar_dado(20, qtd_dados)
    maior = max(resultados)
    total = maior + bonus_pericia

    print(f"\nTeste de {pericia.capitalize()} ({atributo} {valor_atributo} + Perícia +{bonus_pericia}):")
    print(f"   Dados: {qtd_dados}d20 -> {resultados}")
    print(f"   Maior: {maior} + Perícia: {bonus_pericia} = TOTAL: {total}")


def menu_rolagem_dados(usuario_logado=None):
    while True:
        print("\n--- ROLAGEM DE DADOS ---")
        print("[1] Rolagem Livre (escolher dado e quantidade)")
        if usuario_logado:
            print("[2] Teste de Atributo")
            print("[3] Teste de Perícia")
        print("[0] Voltar")

        op = input("Opção: ").strip()

        if op == "0":
            break
        elif op == "1":
            menu_rolar_dados_livre()
        elif op == "2" and usuario_logado:
            personagem = selecionar_personagem_para_teste(usuario_logado)
            if personagem:
                rolar_teste_atributo(personagem)
        elif op == "3" and usuario_logado:
            personagem = selecionar_personagem_para_teste(usuario_logado)
            if personagem:
                rolar_teste_pericia(personagem)
        else:
            print("[ERRO] Opção inválida.")


# ======================================================
# FUNÇÕES DE USUÁRIO E AUTENTICAÇÃO
# ======================================================

def cadastrar_usuario():
    print("\n--- CADASTRO DE NOVO USUÁRIO ---")
    df = carregar_tabela(ARQUIVO_USUARIOS)
    
    nome = input("Nome: ").strip()
    senha = input("Senha: ").strip()
    email = input("Email: ").strip()
    
    if not df.empty and "email" in df.columns:
        emails_existentes = df["email"].astype(str).str.strip().str.lower().values
        if email.lower() in emails_existentes:
            print(f"[ERRO] O email '{email}' já existe! Cancelado.")
            return
    
    try:
        idade = int(input("Idade: "))
    except ValueError:
        print("[ERRO] A idade precisa ser um número! Cancelado.")
        return

    novo_id = 1 if df.empty else int(df["id"].max()) + 1
    novo_usuario = {
        "id": novo_id, "nome": nome, "senha": str(senha),
        "email": email, "idade": idade, "dataCadastro": str(date.today())
    }
    
    df = pd.concat([df, pd.DataFrame([novo_usuario])], ignore_index=True)
    if salvar_tabela(df, ARQUIVO_USUARIOS):
        salvar_sessao(novo_id) 
        print(f"[OK] Usuário '{nome}' cadastrado e logado com sucesso! (ID: {novo_id})")

def fazer_login():
    print("\n--- LOGIN DE USUÁRIO ---")
    df = carregar_tabela(ARQUIVO_USUARIOS)
    if df.empty:
        print("[ERRO] Nenhum usuário cadastrado no sistema! Cadastre um usuário primeiro.")
        return None

    email = input("Email: ").strip()
    senha = input("Senha: ").strip()

    email_clean = df["email"].astype(str).str.strip().str.lower()
    senha_clean = df["senha"].astype(str).str.strip()

    usuario = df[(email_clean == email.lower()) & (senha_clean == senha)]
    
    if usuario.empty:
        print("[ERRO] Email ou senha incorretos!")
        return None
    
    user_dict = usuario.iloc[0].to_dict()
    salvar_sessao(int(user_dict["id"]))
    print(f"[OK] Login realizado! Bem-vindo(a) de volta, {user_dict['nome']}.")
    return user_dict

def editar_perfil_logado(usuario_logado):
    print(f"\n--- EDITAR MEU PERFIL ({usuario_logado['nome']}) ---")
    df = carregar_tabela(ARQUIVO_USUARIOS)
    id_alvo = int(usuario_logado["id"])

    if not df.empty:
        df["nome"] = df["nome"].astype(str)
        df["senha"] = df["senha"].astype(str)
        df["email"] = df["email"].astype(str)
        df["idade"] = df["idade"].astype(int)

    novo_nome = input(f"Novo nome (Atual: {usuario_logado['nome']}): ").strip() or usuario_logado['nome']
    nova_senha = input("Nova senha (deixe em branco para manter): ").strip() or usuario_logado['senha']
    novo_email = input(f"Novo email (Atual: {usuario_logado['email']}): ").strip() or usuario_logado['email']

    if novo_email.lower() != str(usuario_logado["email"]).lower():
        if not df.empty and novo_email.lower() in df["email"].astype(str).str.strip().str.lower().values:
            print(f"[ERRO] O email '{novo_email}' já pertence a outro usuário!")
            return

    nova_idade_str = input(f"Nova idade (Atual: {usuario_logado['idade']}): ").strip()
    nova_idade = int(nova_idade_str) if nova_idade_str.isdigit() else usuario_logado['idade']

    mask = df["id"].astype(int) == id_alvo
    df.loc[mask, "nome"] = novo_nome
    df.loc[mask, "senha"] = str(nova_senha)
    df.loc[mask, "email"] = novo_email
    df.loc[mask, "idade"] = nova_idade

    if salvar_tabela(df, ARQUIVO_USUARIOS):
        print("[OK] Perfil atualizado com sucesso!")
        usuario_logado['nome'] = novo_nome
        usuario_logado['senha'] = str(nova_senha)
        usuario_logado['email'] = novo_email
        usuario_logado['idade'] = nova_idade

def excluir_conta_logada(usuario_logado):
    df_usuarios = carregar_tabela(ARQUIVO_USUARIOS)
    id_alvo = int(usuario_logado["id"])

    if input(f"Tem certeza que deseja APAGAR sua conta ({usuario_logado['nome']}) e TODOS os seus agentes? (S/N): ").strip().upper() == "S":
        df_usuarios = df_usuarios[df_usuarios["id"].astype(int) != id_alvo]
        df_pers = carregar_tabela(ARQUIVO_PERSONAGENS)
        
        if not df_pers.empty:
            ids_dos_agentes = df_pers[df_pers["id_usuario"].astype(int) == id_alvo]["id"].astype(int).tolist()
            limpar_dados_agentes(ids_dos_agentes)
            df_pers = df_pers[df_pers["id_usuario"].astype(int) != id_alvo]
            salvar_tabela(df_pers, ARQUIVO_PERSONAGENS)

        salvar_tabela(df_usuarios, ARQUIVO_USUARIOS)
        encerrar_sessao()
        print("[OK] Sua conta e todos os seus agentes foram excluídos!")


# ======================================================
# FUNÇÕES DE PERSONAGEM / AGENTE
# ======================================================

def escolher_classe():
    classes = {"1": "Combatente", "2": "Especialista", "3": "Ocultista", "4": "Mundano"}
    while True:
        print("\nEscolha a Classe:")
        print("[1] Combatente | [2] Especialista | [3] Ocultista | [4] Mundano")
        op = input("Opção: ").strip()
        if op in classes: return classes[op]
        print("[ERRO] Opção inválida!")

def escolher_nex():
    while True:
        try:
            nex = int(input("NEX (%) (0, 5, 10, 15... até 95, ou 99): "))
            if nex in NEX_VALIDOS: return nex
            print("[ERRO] NEX inválido! Deve ser 0, múltiplo de 5 (até 95), ou 99.")
        except ValueError:
            print("[ERRO] Digite apenas números inteiros.")

def escolher_afinidade():
    afinidades = {"1": "Sangue", "2": "Conhecimento", "3": "Energia", "4": "Morte", "5": "Nenhuma"}
    while True:
        print("\nSeu agente atingiu 50% de NEX! Escolha uma Afinidade:")
        print("[1] Sangue | [2] Conhecimento | [3] Energia | [4] Morte | [5] Nenhuma")
        op = input("Opção: ").strip()
        if op in afinidades: return afinidades[op]
        print("[ERRO] Opção inválida!")

def cadastrar_personagem(usuario_logado):
    if not usuario_logado:
        print("[ERRO] Você precisa estar logado para criar um agente!")
        return

    print(f"\n--- CRIAÇÃO DE AGENTE (Usuário: {usuario_logado['nome']}) ---")
    id_usuario = int(usuario_logado["id"])

    nome = input("Nome do Agente: ").strip()
    classe = escolher_classe()
    nex = escolher_nex()
    
    afinidade = "Nenhuma"
    if nex >= 50: afinidade = escolher_afinidade()

    agi, forca, inte, pre, vig = validar_atributos_ordem(nex)
    pv, san, pe = calcular_recursos(classe, nex, vig, pre)
    defesa, limite_itens = calcular_defesa_limite(agi, forca)
    
    pericias_dict = distribuir_pericias(classe, nex, inte)

    df_pers = carregar_tabela(ARQUIVO_PERSONAGENS)
    novo_id = 1 if df_pers.empty else int(df_pers["id"].max()) + 1

    novo_pers = {
        "id": novo_id, "id_usuario": id_usuario, "nome": nome, "dataCriacao": str(date.today()),
        "classe": classe, "NEX": nex, "afinidade": afinidade,
        "AGI": agi, "FOR": forca, "INT": inte, "PRE": pre, "VIG": vig,
        "pvATUAL": pv, "pvMAX": pv, "sanATUAL": san, "sanMAX": san, "peATUAL": pe, "peMAX": pe,
        "defesa": defesa, "limiteItens": limite_itens,
        **pericias_dict 
    }

    df_pers = pd.concat([df_pers, pd.DataFrame([novo_pers])], ignore_index=True)
    if salvar_tabela(df_pers, ARQUIVO_PERSONAGENS):
        print(f"\n[OK] Agente '{nome}' salvo com sucesso! (PV: {pv} | SAN: {san} | PE: {pe} | Defesa: {defesa} | Limite de Itens: {limite_itens})")


# ======================================================
# FUNÇÕES DE ITENS / INVENTÁRIO
# ======================================================

def calcular_peso_total(id_personagem):
    df_inv = carregar_tabela(ARQUIVO_INVENTARIO)
    df_itens = carregar_tabela(ARQUIVO_ITENS)

    if df_inv.empty or df_itens.empty:
        return 0.0

    inv_pers = df_inv[df_inv["id_personagem"].astype(int) == int(id_personagem)]
    if inv_pers.empty:
        return 0.0

    total = 0.0
    for _, linha in inv_pers.iterrows():
        item_row = df_itens[df_itens["id"].astype(int) == int(linha["id_item"])]
        if not item_row.empty:
            peso_unit = float(item_row.iloc[0]["peso"])
            total += peso_unit * float(linha["quantidade"])
    return total


def exibir_inventario(id_personagem, limite_itens):
    df_inv = carregar_tabela(ARQUIVO_INVENTARIO)
    df_itens = carregar_tabela(ARQUIVO_ITENS)

    peso_total = calcular_peso_total(id_personagem)
    print("-" * 70)
    print(f" INVENTÁRIO (Carga: {peso_total:g} / {limite_itens}):")

    if df_inv.empty or df_itens.empty:
        print("   (Mochila vazia)")
        return

    inv_pers = df_inv[df_inv["id_personagem"].astype(int) == int(id_personagem)]
    if inv_pers.empty:
        print("   (Mochila vazia)")
        return

    for _, linha in inv_pers.iterrows():
        item_row = df_itens[df_itens["id"].astype(int) == int(linha["id_item"])]
        if item_row.empty:
            continue
        item = item_row.iloc[0]
        qtd = float(linha["quantidade"])
        peso_unit = float(item["peso"])
        print(f"   - {item['nome']} (x{qtd:g}) | Peso unit.: {peso_unit:g} | Subtotal: {qtd * peso_unit:g}")


def adicionar_item_inventario(id_personagem, limite_itens):
    df_itens = carregar_tabela(ARQUIVO_ITENS)
    if df_itens.empty:
        print("[ERRO] O catálogo de itens ainda está vazio.")
        return

    df_itens = df_itens.reset_index(drop=True)

    print("\n--- CATÁLOGO DE ITENS ---")
    for i, linha in df_itens.iterrows():
        nome_fmt = str(linha["nome"]).ljust(26)
        tipo = str(linha.get("tipoItem", "-")).ljust(11)
        peso_txt = f"Peso:{linha['peso']}".ljust(8)

        extra = ""
        dano = linha.get("dano")
        if pd.notna(dano) and str(dano).strip() not in ("", "-", "nan"):
            extra += f" Dano:{dano}"
            critico = linha.get("critico")
            if pd.notna(critico) and str(critico).strip() not in ("", "-", "nan"):
                extra += f" Crít:{critico}"
            alcance = linha.get("alcance")
            if pd.notna(alcance) and str(alcance).strip() not in ("", "-", "nan"):
                extra += f" Alc:{alcance}"
        defesa = linha.get("defesa")
        if pd.notna(defesa) and str(defesa).strip() not in ("", "-", "nan"):
            extra += f" Defesa:{defesa}"

        print(f"[{i + 1:>2}] {nome_fmt}{tipo}{peso_txt}{extra}")

    escolha = input("\nDigite o NÚMERO do item (ou 0 para cancelar): ").strip()
    if escolha == "0":
        return
    if not escolha.isdigit() or not (1 <= int(escolha) <= len(df_itens)):
        print("[ERRO] Número inválido.")
        return

    item = df_itens.iloc[int(escolha) - 1]
    peso_unit = float(item["peso"])

    try:
        qtd = float(input(f"Quantidade de '{item['nome']}' a adicionar: ").strip())
        if qtd <= 0:
            print("[ERRO] A quantidade deve ser maior que zero.")
            return
    except ValueError:
        print("[ERRO] Digite um número válido.")
        return

    peso_atual = calcular_peso_total(id_personagem)
    peso_novo = peso_atual + (qtd * peso_unit)

    if peso_novo > limite_itens:
        print(f"[ERRO] Isso ultrapassa seu Limite de Itens! (Carga resultante: {peso_novo:g} / {limite_itens})")
        return

    df_inv = carregar_tabela(ARQUIVO_INVENTARIO)
    if not df_inv.empty:
        mask = (df_inv["id_personagem"].astype(int) == int(id_personagem)) & (df_inv["id_item"].astype(int) == int(item["id"]))
    else:
        mask = pd.Series([], dtype=bool)

    if not df_inv.empty and mask.any():
        df_inv.loc[mask, "quantidade"] = df_inv.loc[mask, "quantidade"].astype(float) + qtd
    else:
        novo_id = 1 if df_inv.empty else int(df_inv["id"].max()) + 1
        novo_reg = {"id": novo_id, "id_personagem": int(id_personagem), "id_item": int(item["id"]), "quantidade": qtd}
        df_inv = pd.concat([df_inv, pd.DataFrame([novo_reg])], ignore_index=True)

    if salvar_tabela(df_inv, ARQUIVO_INVENTARIO):
        print(f"[OK] {qtd:g}x '{item['nome']}' adicionado(s)! (Carga: {peso_novo:g} / {limite_itens})")


def remover_item_inventario(id_personagem):
    df_inv = carregar_tabela(ARQUIVO_INVENTARIO)
    df_itens = carregar_tabela(ARQUIVO_ITENS)

    if df_inv.empty:
        print("[ERRO] Mochila vazia.")
        return

    inv_pers = df_inv[df_inv["id_personagem"].astype(int) == int(id_personagem)].reset_index(drop=True)
    if inv_pers.empty:
        print("[ERRO] Mochila vazia.")
        return

    print("\n--- ITENS NA MOCHILA ---")
    for i, linha in inv_pers.iterrows():
        item_row = df_itens[df_itens["id"].astype(int) == int(linha["id_item"])] if not df_itens.empty else pd.DataFrame()
        nome = item_row.iloc[0]["nome"] if not item_row.empty else f"Item #{linha['id_item']}"
        print(f"[{i + 1:>2}] {nome} (x{float(linha['quantidade']):g})")

    escolha = input("\nDigite o NÚMERO do item a remover (ou 0 para cancelar): ").strip()
    if escolha == "0":
        return
    if not escolha.isdigit() or not (1 <= int(escolha) <= len(inv_pers)):
        print("[ERRO] Número inválido.")
        return

    linha_escolhida = inv_pers.iloc[int(escolha) - 1]
    qtd_atual = float(linha_escolhida["quantidade"])

    entrada = input(f"Quantidade a remover (atual: {qtd_atual:g}, ENTER = remover tudo): ").strip()
    try:
        qtd_remover = float(entrada) if entrada else qtd_atual
    except ValueError:
        print("[ERRO] Digite um número válido.")
        return

    if qtd_remover <= 0:
        print("[ERRO] Quantidade inválida.")
        return

    if qtd_remover >= qtd_atual:
        df_inv = df_inv[df_inv["id"].astype(int) != int(linha_escolhida["id"])]
        print("[OK] Item removido da mochila.")
    else:
        mask = df_inv["id"].astype(int) == int(linha_escolhida["id"])
        df_inv.loc[mask, "quantidade"] = qtd_atual - qtd_remover
        print(f"[OK] Quantidade atualizada para {qtd_atual - qtd_remover:g}.")

    salvar_tabela(df_inv, ARQUIVO_INVENTARIO)


def gerenciar_inventario(id_personagem):
    while True:
        df_pers = carregar_tabela(ARQUIVO_PERSONAGENS)
        linha_pers = df_pers[df_pers["id"].astype(int) == int(id_personagem)]
        if linha_pers.empty:
            break
        personagem = linha_pers.iloc[0].to_dict()

        try:
            limite_itens = int(float(personagem.get("limiteItens")))
        except (TypeError, ValueError):
            limite_itens = int(personagem["FOR"]) * 5

        print(f"\n--- INVENTÁRIO DE {str(personagem['nome']).upper()} ---")
        exibir_inventario(id_personagem, limite_itens)

        print("\n[1] Adicionar Item do Catálogo")
        print("[2] Remover / Diminuir Item")
        print("[0] Voltar")
        op = input("Opção: ").strip()

        if op == "0":
            break
        elif op == "1":
            adicionar_item_inventario(id_personagem, limite_itens)
        elif op == "2":
            remover_item_inventario(id_personagem)
        else:
            print("[ERRO] Opção inválida.")


# ======================================================
# FUNÇÕES DE RITUAIS
# ======================================================

# NEX mínimo para liberar cada círculo de ritual 
CIRCULOS_POR_NEX = [(85, 4), (55, 3), (25, 2)]

def circulo_maximo(nex):
    for nex_minimo, circulo in CIRCULOS_POR_NEX:
        if nex >= nex_minimo:
            return circulo
    return 1


def _txt(valor, padrao="-"):
    if valor is None or pd.isna(valor):
        return padrao
    s = str(valor).strip()
    return s if s and s.lower() != "nan" else padrao


def _elemento_curto(elemento):
    e = _txt(elemento)
    return "Vários" if "/" in e else e


def _custo_texto(pe, circulo, afinidade):
    if pe is None or pd.isna(pe):
        return "-"
    partes = [f"+{int(float(pe))} PE"]
    if circulo is not None and pd.notna(circulo):
        partes.append(f"{int(float(circulo))}º círculo")
    if afinidade is True or str(afinidade).strip().lower() == "true":
        partes.append("afinidade")
    return ", ".join(partes)


def obter_rituais_agente(id_personagem):
    df_ra = carregar_tabela(ARQUIVO_RITUAIS_AGENTE)
    df_r = carregar_tabela(ARQUIVO_RITUAIS)
    if df_ra.empty or df_r.empty:
        return pd.DataFrame()
    ids = df_ra[df_ra["id_personagem"].astype(int) == int(id_personagem)]["id_ritual"].astype(int).tolist()
    return df_r[df_r["id"].astype(int).isin(ids)].sort_values(["circulo", "nome"]).reset_index(drop=True)


def exibir_rituais_ficha(id_personagem):
    rituais = obter_rituais_agente(id_personagem)
    print("-" * 70)
    print(f" RITUAIS ({len(rituais)}):")
    if rituais.empty:
        print("   (Nenhum ritual aprendido)")
        return
    for _, r in rituais.iterrows():
        print(f"   - {str(r['nome']).ljust(26)} {_elemento_curto(r['elemento'])} {int(r['circulo'])}º | "
              f"Exec: {_txt(r['execucao'])} | Alc: {_txt(r['alcance'])} | Dur: {_txt(r['duracao'])}")


def exibir_detalhes_ritual(r):
    print("\n" + "-" * 70)
    print(f" {str(r['nome']).upper()}  ({_txt(r['elemento'])} - {int(r['circulo'])}º círculo)")
    print(f" Resumo: {_txt(r.get('resumo'))}")
    print(f" Execução: {_txt(r['execucao'])} | Alcance: {_txt(r['alcance'])}")
    print(f" Alvo/Área: {_txt(r['alvoArea'])}")
    print(f" Duração: {_txt(r['duracao'])} | Resistência: {_txt(r['resistencia'])}")
    print(f" Discente:   {_custo_texto(r.get('peDiscente'), r.get('circuloReqDiscente'), r.get('afinidadeReqDiscente'))}")
    print(f" Verdadeiro: {_custo_texto(r.get('peVerdadeiro'), r.get('circuloReqVerdadeiro'), r.get('afinidadeReqVerdadeiro'))}")
    obs = _txt(r.get("observacoes"), "")
    if obs:
        print(f" Obs.: {obs}")
    print("-" * 70)


def ver_ritual_agente(id_personagem):
    rituais = obter_rituais_agente(id_personagem)
    if rituais.empty:
        print("[ERRO] Este agente ainda não aprendeu nenhum ritual.")
        return

    print("\n--- RITUAIS DO AGENTE ---")
    for i, r in rituais.iterrows():
        print(f"[{i + 1:>2}] {str(r['nome']).ljust(26)}{_elemento_curto(r['elemento'])} {int(r['circulo'])}º")

    escolha = input("\nDigite o NÚMERO do ritual para ver detalhes (ou 0 para voltar): ").strip()
    if escolha == "0":
        return
    if not escolha.isdigit() or not (1 <= int(escolha) <= len(rituais)):
        print("[ERRO] Número inválido.")
        return
    exibir_detalhes_ritual(rituais.iloc[int(escolha) - 1])


def adicionar_ritual(id_personagem, personagem):
    df_r = carregar_tabela(ARQUIVO_RITUAIS)
    if df_r.empty:
        print("[ERRO] O catálogo de rituais (rituais.csv) está vazio ou não foi encontrado.")
        return

    nex = int(personagem["NEX"])
    circ_max = circulo_maximo(nex)

    conhecidos = obter_rituais_agente(id_personagem)
    ids_conhecidos = set(conhecidos["id"].astype(int)) if not conhecidos.empty else set()

    elementos = sorted(df_r["elemento"].dropna().astype(str).unique())
    print(f"\n--- APRENDER RITUAL (NEX {nex}% -> até {circ_max}º círculo) ---")
    print("Filtrar por elemento:")
    print("[0] Todos")
    for i, el in enumerate(elementos, start=1):
        print(f"[{i}] {el}")

    filtro = input("Opção: ").strip()
    if not filtro.isdigit() or int(filtro) > len(elementos):
        print("[ERRO] Opção inválida.")
        return

    df_f = df_r[(df_r["circulo"].astype(int) <= circ_max) & (~df_r["id"].astype(int).isin(ids_conhecidos))]
    if int(filtro) > 0:
        df_f = df_f[df_f["elemento"].astype(str) == elementos[int(filtro) - 1]]
    df_f = df_f.sort_values(["circulo", "nome"]).reset_index(drop=True)

    if df_f.empty:
        print("[ERRO] Nenhum ritual disponível com esse filtro (círculo liberado ou já aprendidos).")
        return

    print("\n--- RITUAIS DISPONÍVEIS ---")
    for i, r in df_f.iterrows():
        print(f"[{i + 1:>2}] {str(r['nome']).ljust(26)}{_elemento_curto(r['elemento']).ljust(13)} {int(r['circulo'])}º | {_txt(r.get('resumo'))}")

    escolha = input("\nDigite o NÚMERO do ritual (ou 0 para cancelar): ").strip()
    if escolha == "0":
        return
    if not escolha.isdigit() or not (1 <= int(escolha) <= len(df_f)):
        print("[ERRO] Número inválido.")
        return

    ritual = df_f.iloc[int(escolha) - 1]
    exibir_detalhes_ritual(ritual)

    if input(f"Aprender '{ritual['nome']}'? (S/N): ").strip().upper() != "S":
        print("Cancelado.")
        return

    df_ra = carregar_tabela(ARQUIVO_RITUAIS_AGENTE)
    novo_id = 1 if df_ra.empty else int(df_ra["id"].max()) + 1
    novo_reg = {"id": novo_id, "id_personagem": int(id_personagem), "id_ritual": int(ritual["id"])}
    df_ra = pd.concat([df_ra, pd.DataFrame([novo_reg])], ignore_index=True)

    if salvar_tabela(df_ra, ARQUIVO_RITUAIS_AGENTE):
        print(f"[OK] Ritual '{ritual['nome']}' adicionado ao agente!")


def remover_ritual(id_personagem):
    rituais = obter_rituais_agente(id_personagem)
    if rituais.empty:
        print("[ERRO] Este agente ainda não aprendeu nenhum ritual.")
        return

    print("\n--- RITUAIS DO AGENTE ---")
    for i, r in rituais.iterrows():
        print(f"[{i + 1:>2}] {str(r['nome']).ljust(26)}{_elemento_curto(r['elemento'])} {int(r['circulo'])}º")

    escolha = input("\nDigite o NÚMERO do ritual a esquecer (ou 0 para cancelar): ").strip()
    if escolha == "0":
        return
    if not escolha.isdigit() or not (1 <= int(escolha) <= len(rituais)):
        print("[ERRO] Número inválido.")
        return

    ritual = rituais.iloc[int(escolha) - 1]
    if input(f"Remover '{ritual['nome']}' deste agente? (S/N): ").strip().upper() != "S":
        print("Cancelado.")
        return

    df_ra = carregar_tabela(ARQUIVO_RITUAIS_AGENTE)
    remover = (df_ra["id_personagem"].astype(int) == int(id_personagem)) & (df_ra["id_ritual"].astype(int) == int(ritual["id"]))
    df_ra = df_ra[~remover]
    if salvar_tabela(df_ra, ARQUIVO_RITUAIS_AGENTE):
        print(f"[OK] Ritual '{ritual['nome']}' removido.")


def gerenciar_rituais(id_personagem):
    while True:
        df_pers = carregar_tabela(ARQUIVO_PERSONAGENS)
        linha_pers = df_pers[df_pers["id"].astype(int) == int(id_personagem)]
        if linha_pers.empty:
            break
        personagem = linha_pers.iloc[0].to_dict()

        print(f"\n--- RITUAIS DE {str(personagem['nome']).upper()} (NEX {personagem['NEX']}% | até {circulo_maximo(int(personagem['NEX']))}º círculo) ---")
        exibir_rituais_ficha(id_personagem)

        print("\n[1] Ver detalhes de um ritual")
        print("[2] Aprender novo ritual")
        print("[3] Esquecer ritual")
        print("[0] Voltar")
        op = input("Opção: ").strip()

        if op == "0":
            break
        elif op == "1":
            ver_ritual_agente(id_personagem)
        elif op == "2":
            adicionar_ritual(id_personagem, personagem)
        elif op == "3":
            remover_ritual(id_personagem)
        else:
            print("[ERRO] Opção inválida.")


def limpar_dados_agentes(ids_personagens):
    ids = [int(i) for i in ids_personagens]
    if not ids:
        return
    for arquivo in (ARQUIVO_INVENTARIO, ARQUIVO_RITUAIS_AGENTE):
        df = carregar_tabela(arquivo)
        if not df.empty:
            df = df[~df["id_personagem"].astype(int).isin(ids)]
            salvar_tabela(df, arquivo)


def exibir_ficha(personagem):
    afinidade = personagem.get('afinidade', 'Nenhuma')
    cor = CORES_AFINIDADE.get(afinidade, RESET_COR)
    
    print("\n" + "="*70)
    print(f" NOME: {cor}{str(personagem['nome']).upper()}{RESET_COR}")
    print(f" CLASSE: {personagem.get('classe', 'Desconhecida')} | NEX: {personagem['NEX']}% | AFINIDADE: {afinidade}")
    print("-" * 70)
    print(f" RECURSOS: PV: {personagem['pvMAX']} | SAN: {personagem['sanMAX']} | PE: {personagem['peMAX']}")
    print("-" * 70)
    print(f" ATRIBUTOS: AGI:{personagem['AGI']} FOR:{personagem['FOR']} INT:{personagem['INT']} PRE:{personagem['PRE']} VIG:{personagem['VIG']}")
    print("-" * 70)

    try:
        defesa = int(float(personagem.get('defesa')))
    except (TypeError, ValueError):
        defesa = 10 + int(personagem['AGI'])
    try:
        limite_itens = int(float(personagem.get('limiteItens')))
    except (TypeError, ValueError):
        limite_itens = int(personagem['FOR']) * 5

    print(f" DEFESA: {defesa} | LIMITE DE ITENS: {limite_itens}")
    print("-" * 70)
    
    print(" PERÍCIAS (0 = Destreinado | +5 = Treinado | +10 = Veterano | +15 = Expert):")
    
    pericias_formatadas = []
    for p in LISTA_PERICIAS:
        valor = personagem.get(p, 0)
        nome_formatado = p.capitalize().ljust(15) 
        try:
            val_int = int(float(valor))
            if val_int > 0:
                texto_valor = f"+{val_int}"
            else:
                texto_valor = "0 "
        except (ValueError, TypeError):
            texto_valor = "0 "
            
        pericias_formatadas.append(f"{nome_formatado}: {texto_valor.ljust(3)}")

    colunas = 4
    for i in range(0, len(pericias_formatadas), colunas):
        linha = pericias_formatadas[i:i+colunas]
        print(" | ".join(linha))

    exibir_inventario(personagem["id"], limite_itens)
    exibir_rituais_ficha(personagem["id"])
    print("="*70)

def submenu_editar_agente(id_pers):
    while True:
        df = carregar_tabela(ARQUIVO_PERSONAGENS)
        mask = df["id"].astype(int) == int(id_pers)
        personagem = df.loc[mask].iloc[0].to_dict()

        print(f"\n--- EDITANDO: {str(personagem['nome']).upper()} ---")
        print("[1] Nome")
        print("[2] Classe ")
        print("[3] NEX ")
        print("[4] Afinidade")
        print("[5] Atributos ")
        print("[6] Refazer Perícias")
        print("[7] Refazer Ficha Completa")
        print("[8] Itens / Inventário")
        print("[9] Rituais")
        print("[0] Voltar para a Ficha")
        
        op = input("Opção: ").strip()

        if op == "0":
            break
            
        elif op == "1":
            novo_nome = input(f"Novo nome ({personagem['nome']}): ").strip()
            if novo_nome:
                df.loc[mask, "nome"] = novo_nome
                salvar_tabela(df, ARQUIVO_PERSONAGENS)
                print("[OK] Nome atualizado!")
                
        elif op == "2":
            nova_classe = escolher_classe()
            pv, san, pe = calcular_recursos(nova_classe, personagem["NEX"], personagem["VIG"], personagem["PRE"])
            print("A mudança de Classe alterou suas perícias base. Redistribua:")
            pericias_dict = distribuir_pericias(nova_classe, personagem["NEX"], personagem["INT"])
            
            df.loc[mask, "classe"] = nova_classe
            df.loc[mask, ["pvMAX", "pvATUAL", "sanMAX", "sanATUAL", "peMAX", "peATUAL"]] = [pv, pv, san, san, pe, pe]
            for p_nome, p_valor in pericias_dict.items():
                df.loc[mask, p_nome] = p_valor
                
            salvar_tabela(df, ARQUIVO_PERSONAGENS)
            print("[OK] Classe, Recursos e Perícias atualizados!")
            
        elif op == "3":
            novo_nex = escolher_nex()
            print("O seu NEX mudou! Você precisa redistribuir os Atributos e Perícias para se adequar ao novo nível.")
            agi, forca, inte, pre, vig = validar_atributos_ordem(novo_nex)
            pv, san, pe = calcular_recursos(personagem["classe"], novo_nex, vig, pre)
            defesa, limite_itens = calcular_defesa_limite(agi, forca)
            pericias_dict = distribuir_pericias(personagem["classe"], novo_nex, inte)
            
            nova_afinidade = personagem.get("afinidade", "Nenhuma")
            if novo_nex >= 50 and nova_afinidade == "Nenhuma":
                print("Seu agente alcançou 50%! Escolha uma afinidade:")
                nova_afinidade = escolher_afinidade()
            elif novo_nex < 50:
                nova_afinidade = "Nenhuma"

            df.loc[mask, "NEX"] = novo_nex
            df.loc[mask, "afinidade"] = nova_afinidade
            df.loc[mask, ["AGI", "FOR", "INT", "PRE", "VIG"]] = [agi, forca, inte, pre, vig]
            df.loc[mask, ["pvMAX", "pvATUAL", "sanMAX", "sanATUAL", "peMAX", "peATUAL"]] = [pv, pv, san, san, pe, pe]
            df.loc[mask, ["defesa", "limiteItens"]] = [defesa, limite_itens]
            for p_nome, p_valor in pericias_dict.items():
                df.loc[mask, p_nome] = p_valor
                
            salvar_tabela(df, ARQUIVO_PERSONAGENS)
            print("[OK] NEX atualizado com sucesso!")
            
        elif op == "4":
            if personagem["NEX"] >= 50:
                nova_afinidade = escolher_afinidade()
                df.loc[mask, "afinidade"] = nova_afinidade
                salvar_tabela(df, ARQUIVO_PERSONAGENS)
                print("[OK] Afinidade atualizada!")
            else:
                print("[ERRO] Agentes precisam ter NEX 50% ou mais para ter Afinidade.")
                
        elif op == "5":
            agi, forca, inte, pre, vig = validar_atributos_ordem(personagem["NEX"])
            pv, san, pe = calcular_recursos(personagem["classe"], personagem["NEX"], vig, pre)
            defesa, limite_itens = calcular_defesa_limite(agi, forca)
            
            df.loc[mask, ["AGI", "FOR", "INT", "PRE", "VIG"]] = [agi, forca, inte, pre, vig]
            df.loc[mask, ["pvMAX", "pvATUAL", "sanMAX", "sanATUAL", "peMAX", "peATUAL"]] = [pv, pv, san, san, pe, pe]
            df.loc[mask, ["defesa", "limiteItens"]] = [defesa, limite_itens]
            
            if inte != personagem["INT"]:
                print("Você alterou seu Intelecto (INT). Isso afeta sua quantidade de perícias! Redistribua:")
                pericias_dict = distribuir_pericias(personagem["classe"], personagem["NEX"], inte)
                for p_nome, p_valor in pericias_dict.items():
                    df.loc[mask, p_nome] = p_valor
                    
            salvar_tabela(df, ARQUIVO_PERSONAGENS)
            print("[OK] Atributos (e PV/PE) atualizados!")
            
        elif op == "6":
            pericias_dict = distribuir_pericias(personagem["classe"], personagem["NEX"], personagem["INT"])
            for p_nome, p_valor in pericias_dict.items():
                df.loc[mask, p_nome] = p_valor
            salvar_tabela(df, ARQUIVO_PERSONAGENS)
            print("[OK] Perícias atualizadas!")
            
        elif op == "7":
            novo_nome = input(f"Nome ({personagem['nome']}): ").strip() or personagem['nome']
            nova_classe = escolher_classe()
            novo_nex = escolher_nex()
            nova_afinidade = "Nenhuma"
            if novo_nex >= 50: nova_afinidade = escolher_afinidade()
            
            agi, forca, inte, pre, vig = validar_atributos_ordem(novo_nex)
            pv, san, pe = calcular_recursos(nova_classe, novo_nex, vig, pre)
            defesa, limite_itens = calcular_defesa_limite(agi, forca)
            pericias_dict = distribuir_pericias(nova_classe, novo_nex, inte)

            df.loc[mask, "nome"] = novo_nome
            df.loc[mask, "classe"] = nova_classe
            df.loc[mask, "NEX"] = novo_nex
            df.loc[mask, "afinidade"] = nova_afinidade
            df.loc[mask, ["AGI", "FOR", "INT", "PRE", "VIG"]] = [agi, forca, inte, pre, vig]
            df.loc[mask, ["pvMAX", "pvATUAL", "sanMAX", "sanATUAL", "peMAX", "peATUAL"]] = [pv, pv, san, san, pe, pe]
            df.loc[mask, ["defesa", "limiteItens"]] = [defesa, limite_itens]
            for p_nome, p_valor in pericias_dict.items():
                df.loc[mask, p_nome] = p_valor

            salvar_tabela(df, ARQUIVO_PERSONAGENS)
            print("[OK] Ficha refeita completamente!")
            break

        elif op == "8":
            gerenciar_inventario(id_pers)

        elif op == "9":
            gerenciar_rituais(id_pers)

        else:
            print("[ERRO] Opção inválida.")


def menu_personagem(id_pers):
    while True:
        df = carregar_tabela(ARQUIVO_PERSONAGENS)
        
        linha = df[df["id"].astype(int) == int(id_pers)]
        if linha.empty: break
        
        personagem = linha.iloc[0].to_dict()
        exibir_ficha(personagem)

        print("\nO que deseja fazer com este agente?")
        print("[1] Editar Agente")
        print("[2] Excluir Agente")
        print("[0] Voltar para a lista")
        op = input("Opção: ").strip()

        if op == "0":
            break
        elif op == "2":
            if input("Deseja mesmo DELETAR este agente? (S/N): ").strip().upper() == "S":
                df = df[df["id"].astype(int) != int(id_pers)]
                salvar_tabela(df, ARQUIVO_PERSONAGENS)
                limpar_dados_agentes([id_pers])
                print("[OK] Agente apagado no fluxo paranormal.")
                break
        elif op == "1":
            submenu_editar_agente(id_pers)
        else:
            print("[ERRO] Opção inválida.")

def listar_personagens(usuario_logado):
    if not usuario_logado:
        print("[ERRO] Você precisa estar logado para ver seus agentes!")
        return

    id_usuario = int(usuario_logado["id"])

    while True:
        df = carregar_tabela(ARQUIVO_PERSONAGENS)
        if df.empty:
            print("\nNenhum agente cadastrado no sistema.")
            return

        seus_personagens = df[df["id_usuario"].astype(int) == id_usuario]

        if seus_personagens.empty:
            print("\nVocê não possui agentes cadastrados.")
            return

        print(f"\n--- AGENTES DE {str(usuario_logado['nome']).upper()} ---")
        for _, row in seus_personagens.iterrows():
            print(f"ID: {row['id']} | NOME: {row['nome']} | CLASSE: {row.get('classe', 'Mundano')} | NEX: {row['NEX']}%")
            
        print("\nDigite o ID do Agente para ABRIR A FICHA, ou 0 para voltar ao menu.")
        try:
            escolha = int(input("ID: "))
            if escolha == 0: break
            if escolha in seus_personagens["id"].astype(int).values:
                menu_personagem(escolha)
            else:
                print("[ERRO] ID inválido ou o agente não pertence a você.")
        except ValueError:
            print("[ERRO] Digite apenas números.")


# ======================================================
# MENU PRINCIPAL
# ======================================================

def menu():
    inicializar_banco()
    
    while True:
        usuario_logado = obter_usuario_logado()
        
        print("\n========================================")
        print("   SISTEMA RPG - ORDEM PARANORMAL")
        print("========================================")
        
        if usuario_logado:
            print(f" CONECTADO COMO: {str(usuario_logado['nome']).upper()} (ID: {usuario_logado['id']})")
            print("----------------------------------------")
            print("[1] Criar Novo Agente")
            print("[2] Meus Agentes (Ver / Editar / Excluir)")
            print("[3] Editar Meu Perfil de Usuário")
            print("[4] Excluir Minha Conta")
            print("[5] Trocar de Usuário (Fazer Login)")
            print("[6] Deslogar")
            print("[7] Rolar Dados")
            print("[0] Sair do Sistema")
        else:
            print(" NENHUM USUÁRIO LOGADO")
            print("----------------------------------------")
            print("[1] Fazer Login")
            print("[2] Cadastrar Novo Usuário")
            print("[3] Rolar Dados (livre)")
            print("[0] Sair do Sistema")

        opcao = input("\nOpção: ").strip()

        if usuario_logado:
            if opcao == "1": cadastrar_personagem(usuario_logado)
            elif opcao == "2": listar_personagens(usuario_logado)
            elif opcao == "3": editar_perfil_logado(usuario_logado)
            elif opcao == "4": excluir_conta_logada(usuario_logado)
            elif opcao == "5": fazer_login()
            elif opcao == "6": deslogar_usuario()
            elif opcao == "7": menu_rolagem_dados(usuario_logado)
            elif opcao == "0":
                print("Desconectando da Ordo Realitas... Até logo!")
                break
            else:
                print("[ERRO] Opção inválida!")
        else:
            if opcao == "1": fazer_login()
            elif opcao == "2": cadastrar_usuario()
            elif opcao == "3": menu_rolagem_dados()
            elif opcao == "0":
                print("Desconectando da Ordo Realitas... Até logo!")
                break
            else:
                print("[ERRO] Opção inválida!")

if __name__ == "__main__":
    menu()