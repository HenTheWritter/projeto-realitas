# ENTREGA 2: ATRIBUTOS
# ENTREGA 3: CLASSES, NEX, RECURSOS AUTOMÁTICOS E AFINIDADE
# ENTREGA 4: PERICIAS

import os
from datetime import date
import pandas as pd
from persistencia import (
    ARQUIVO_PERSONAGENS,
    ARQUIVO_USUARIOS,
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

def distribuir_pericias(classe, nex, inte):
    """ Gerencia a distribuição das perícias (+5, +10, +15) """
    pericias = {p: 0 for p in LISTA_PERICIAS}
    
    print(f"\n--- TREINAMENTO DE PERÍCIAS (INT: {inte}) ---")
    
    qtd_escolhas = 0
    
    # 1. PERÍCIAS INICIAIS (Treinadas: +5)
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
        
        # Filtra apenas as perícias válidas para este grau
        validas = [p for p, v in pericias.items() if (valor_alvo == 5 and v == 0) or (valor_alvo == 10 and v == 5) or (valor_alvo == 15 and v == 10)]
        
        # Trava de segurança: Se a quantidade de opções que ele pode melhorar for menor que a quantidade de pontos
        if len(validas) < quantidade:
            print(f"Aviso: Você tem {quantidade} opções para melhorar, mas só {len(validas)} perícias estão disponíveis nesse grau!")
            quantidade = len(validas) # Limita a quantidade

        while escolhidas < quantidade:
            print(f"\n{mensagem} ({quantidade - escolhidas} restantes):")
            
            # Recalcula as válidas para tirar da lista o que já foi escolhido no loop atual
            validas_agora = [p for p, v in pericias.items() if (valor_alvo == 5 and v == 0) or (valor_alvo == 10 and v == 5) or (valor_alvo == 15 and v == 10)]
            print("Opções: " + ", ".join(validas_agora[:10]) + ("..." if len(validas_agora) > 10 else ""))
            
            escolha = input("Digite o nome exato da perícia: ").strip().lower()
            
            if escolha in validas_agora:
                pericias[escolha] = valor_alvo
                escolhidas += 1
                print(f"{escolha.capitalize()} evoluída para +{valor_alvo}!")
            else:
                print(f"[ERRO] Perícia '{escolha}' inválida ou já foi treinada nesse grau.")

    # Distribui +5
    if qtd_escolhas > 0:
        escolher_da_lista(qtd_escolhas, 5, "Escolha perícias para ficar Treinado (+5)")

    # Calcula quantas perícias a classe pode evoluir (Veterano/Expert)
    qtd_evolucao = 0
    if classe == "Combatente":
        qtd_evolucao = 2 + inte
    elif classe == "Ocultista":
        qtd_evolucao = 3 + inte
    elif classe == "Especialista":
        qtd_evolucao = 5 + inte

    # Distribui +10 (Veterano)
    if nex >= 35 and qtd_evolucao > 0:
        print(f"\nNEX {nex}%: Você pode escolher {qtd_evolucao} perícias Treinadas para virar Veterano (+10).")
        escolher_da_lista(qtd_evolucao, 10, "Escolha perícias para ficar Veterano (+10)")
        
    # Distribui +15 (Expert)
    if nex >= 70 and qtd_evolucao > 0:
        print(f"\nNEX {nex}%: Você pode escolher {qtd_evolucao} perícias Veteranas para virar Expert (+15).")
        escolher_da_lista(qtd_evolucao, 15, "Escolha perícias para ficar Expert (+15)")

    print("\nPerícias distribuídas com sucesso!")
    return pericias


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
    
    # Chama a função de perícias
    pericias_dict = distribuir_pericias(classe, nex, inte)

    df_pers = carregar_tabela(ARQUIVO_PERSONAGENS)
    novo_id = 1 if df_pers.empty else int(df_pers["id"].max()) + 1

    novo_pers = {
        "id": novo_id, "id_usuario": id_usuario, "nome": nome, "dataCriacao": str(date.today()),
        "classe": classe, "NEX": nex, "afinidade": afinidade,
        "AGI": agi, "FOR": forca, "INT": inte, "PRE": pre, "VIG": vig,
        "pvATUAL": pv, "pvMAX": pv, "sanATUAL": san, "sanMAX": san, "peATUAL": pe, "peMAX": pe,
        **pericias_dict # Desempacota o dicionário de perícias direto aqui
    }

    df_pers = pd.concat([df_pers, pd.DataFrame([novo_pers])], ignore_index=True)
    if salvar_tabela(df_pers, ARQUIVO_PERSONAGENS):
        print(f"\n[OK] Agente '{nome}' salvo com sucesso! (PV: {pv} | SAN: {san} | PE: {pe})")


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
    
    print(" PERÍCIAS (0 = Destreinado | +5 = Treinado | +10 = Veterano | +15 = Expert):")
    
    # Criar uma cópia formatada das perícias para exibição
    pericias_formatadas = []
    for p in LISTA_PERICIAS:
        valor = personagem.get(p, 0)
        # Formata o nome para ter sempre o mesmo tamanho 
        nome_formatado = p.capitalize().ljust(15) 
        try:
            # Converte com float antes para evitar crash caso o pandas leia como decimal 
            val_int = int(float(valor))
            if val_int > 0:
                texto_valor = f"+{val_int}"
            else:
                texto_valor = "0 "
        except (ValueError, TypeError):
            texto_valor = "0 "
            
        # Adiciona na lista com o valor também alinhado
        pericias_formatadas.append(f"{nome_formatado}: {texto_valor.ljust(3)}")

    # Imprimir em 4 colunas para caber bonitinho e economizar espaço vertical
    colunas = 4
    for i in range(0, len(pericias_formatadas), colunas):
        linha = pericias_formatadas[i:i+colunas]
        print(" | ".join(linha))
        
    print("="*70)

def submenu_editar_agente(id_pers):
    """ Menu detalhado para alterar partes específicas da ficha do agente """
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
            
            df.loc[mask, ["AGI", "FOR", "INT", "PRE", "VIG"]] = [agi, forca, inte, pre, vig]
            df.loc[mask, ["pvMAX", "pvATUAL", "sanMAX", "sanATUAL", "peMAX", "peATUAL"]] = [pv, pv, san, san, pe, pe]
            
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
            # Refazer ficha completa (a lógica original que você já tinha)
            novo_nome = input(f"Nome ({personagem['nome']}): ").strip() or personagem['nome']
            nova_classe = escolher_classe()
            novo_nex = escolher_nex()
            nova_afinidade = "Nenhuma"
            if novo_nex >= 50: nova_afinidade = escolher_afinidade()
            
            agi, forca, inte, pre, vig = validar_atributos_ordem(novo_nex)
            pv, san, pe = calcular_recursos(nova_classe, novo_nex, vig, pre)
            pericias_dict = distribuir_pericias(nova_classe, novo_nex, inte)

            df.loc[mask, "nome"] = novo_nome
            df.loc[mask, "classe"] = nova_classe
            df.loc[mask, "NEX"] = novo_nex
            df.loc[mask, "afinidade"] = nova_afinidade
            df.loc[mask, ["AGI", "FOR", "INT", "PRE", "VIG"]] = [agi, forca, inte, pre, vig]
            df.loc[mask, ["pvMAX", "pvATUAL", "sanMAX", "sanATUAL", "peMAX", "peATUAL"]] = [pv, pv, san, san, pe, pe]
            for p_nome, p_valor in pericias_dict.items():
                df.loc[mask, p_nome] = p_valor

            salvar_tabela(df, ARQUIVO_PERSONAGENS)
            print("[OK] Ficha refeita completamente!")
            break
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
                print("[OK] Agente apagado no fluxo paranormal.")
                break
        elif op == "1":
            # Aqui ele puxa o submenu que acabamos de criar!
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
            print("[0] Sair do Sistema")
        else:
            print(" NENHUM USUÁRIO LOGADO")
            print("----------------------------------------")
            print("[1] Fazer Login")
            print("[2] Cadastrar Novo Usuário")
            print("[0] Sair do Sistema")

        opcao = input("\nOpção: ").strip()

        if usuario_logado:
            if opcao == "1": cadastrar_personagem(usuario_logado)
            elif opcao == "2": listar_personagens(usuario_logado)
            elif opcao == "3": editar_perfil_logado(usuario_logado)
            elif opcao == "4": excluir_conta_logada(usuario_logado)
            elif opcao == "5": fazer_login()
            elif opcao == "6": deslogar_usuario()
            elif opcao == "0":
                print("Desconectando da Ordo Realitas... Até logo!")
                break
            else:
                print("[ERRO] Opção inválida!")
        else:
            if opcao == "1": fazer_login()
            elif opcao == "2": cadastrar_usuario()
            elif opcao == "0":
                print("Desconectando da Ordo Realitas... Até logo!")
                break
            else:
                print("[ERRO] Opção inválida!")

if __name__ == "__main__":
    menu()