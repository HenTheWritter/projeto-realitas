# ENTREGA 9: PATENTES E PRESTÍGIO
# - Pontos de Prestígio (PP) -> Patente
# - Limite de itens por CATEGORIA de acordo com a patente

import pandas as pd
from persistencia import (
    ARQUIVO_PERSONAGENS,
    ARQUIVO_ITENS,
    ARQUIVO_INVENTARIO,
    carregar_tabela,
    salvar_tabela,
)

# Tabela de patentes (livro base). "limites" = quantos itens de cada categoria
# o agente pode ter. Itens de categoria 0 não têm limite.
PATENTES = [
    {"nome": "Recruta",              "pp": 0,   "credito": "Baixo",     "limites": {1: 2, 2: 0, 3: 0, 4: 0}},
    {"nome": "Operador",             "pp": 20,  "credito": "Médio",     "limites": {1: 3, 2: 1, 3: 0, 4: 0}},
    {"nome": "Agente Especial",      "pp": 50,  "credito": "Médio",     "limites": {1: 3, 2: 2, 3: 1, 4: 0}},
    {"nome": "Oficial de Operações", "pp": 100, "credito": "Alto",      "limites": {1: 3, 2: 3, 3: 2, 4: 1}},
    {"nome": "Agente de Elite",      "pp": 200, "credito": "Ilimitado", "limites": {1: 3, 2: 3, 3: 3, 4: 2}},
]

ROMANOS = {0: "0", 1: "I", 2: "II", 3: "III", 4: "IV"}
_TEXTO_PARA_CATEGORIA = {"0": 0, "I": 1, "II": 2, "III": 3, "IV": 4}


# ======================================================
# PATENTE / PP
# ======================================================

def obter_pp(personagem):
    """Lê os PP de um dict/Series de personagem (0 se vazio ou inválido)."""
    try:
        return max(0, int(float(personagem.get("pp", 0))))
    except (TypeError, ValueError):
        return 0


def obter_patente(pp):
    atual = PATENTES[0]
    for patente in PATENTES:
        if pp >= patente["pp"]:
            atual = patente
    return atual


def proxima_patente(pp):
    for patente in PATENTES:
        if patente["pp"] > pp:
            return patente
    return None


def definir_pp(id_personagem, novo_pp):
    """Grava o total de PP de um personagem. Retorna True se salvou."""
    df = carregar_tabela(ARQUIVO_PERSONAGENS)
    if df.empty:
        return False
    if "pp" not in df.columns:
        df["pp"] = 0
    df["pp"] = df["pp"].fillna(0).astype(int)
    mask = df["id"].astype(int) == int(id_personagem)
    if not mask.any():
        return False
    df.loc[mask, "pp"] = max(0, int(novo_pp))
    return salvar_tabela(df, ARQUIVO_PERSONAGENS)


# ======================================================
# LIMITE DE ITENS POR CATEGORIA
# ======================================================

def normalizar_categoria(valor):
    """Converte '0', 'I', 'II', 'III', 'IV', 'Categoria II', 2, 2.0... em um inteiro 0-4.
    Valores vazios ou desconhecidos contam como categoria 0 (sem limite)."""
    if valor is None or pd.isna(valor):
        return 0
    s = str(valor).strip().upper()
    for lixo in ("CATEGORIA", "CAT."):
        s = s.replace(lixo, "")
    s = s.strip()
    if s in _TEXTO_PARA_CATEGORIA:
        return _TEXTO_PARA_CATEGORIA[s]
    try:
        n = int(float(s))
        return n if 0 <= n <= 4 else 0
    except ValueError:
        return 0


def rotulo_categoria(valor):
    return ROMANOS[normalizar_categoria(valor)]


def contar_itens_por_categoria(id_personagem):
    contagem = {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0}
    df_inv = carregar_tabela(ARQUIVO_INVENTARIO)
    df_itens = carregar_tabela(ARQUIVO_ITENS)
    if df_inv.empty or df_itens.empty:
        return contagem

    inv = df_inv[df_inv["id_personagem"].astype(int) == int(id_personagem)]
    for _, linha in inv.iterrows():
        item = df_itens[df_itens["id"].astype(int) == int(linha["id_item"])]
        if item.empty:
            continue
        cat = normalizar_categoria(item.iloc[0].get("categoria"))
        contagem[cat] += float(linha["quantidade"])
    return contagem


def verificar_limite_categoria(id_personagem, pp, categoria, quantidade):
    """Retorna (ok, mensagem). Só categorias I a IV têm limite."""
    cat = normalizar_categoria(categoria)
    if cat == 0:
        return True, ""

    patente = obter_patente(pp)
    limite = patente["limites"].get(cat, 0)
    usados = contar_itens_por_categoria(id_personagem)[cat]

    if usados + quantidade > limite:
        return False, (
            f"Sua patente ({patente['nome']}) permite {limite} item(ns) de categoria {ROMANOS[cat]}. "
            f"Você já tem {usados:g} e tentou adicionar {quantidade:g}."
        )
    return True, ""


def resumo_categorias(id_personagem, pp):
    """Ex.: 'I: 2/3 | II: 0/2 | III: 0/1 | IV: 0/0'. Marca com (!) se passou do limite."""
    patente = obter_patente(pp)
    usados = contar_itens_por_categoria(id_personagem)
    partes = []
    for cat in (1, 2, 3, 4):
        limite = patente["limites"][cat]
        marca = " (!)" if usados[cat] > limite else ""
        partes.append(f"{ROMANOS[cat]}: {usados[cat]:g}/{limite}{marca}")
    return " | ".join(partes)


def avisos_excesso(id_personagem, pp):
    """Lista de avisos para quando a patente caiu e o inventário passou do limite."""
    patente = obter_patente(pp)
    usados = contar_itens_por_categoria(id_personagem)
    avisos = []
    for cat in (1, 2, 3, 4):
        limite = patente["limites"][cat]
        if usados[cat] > limite:
            avisos.append(f"Categoria {ROMANOS[cat]}: {usados[cat]:g} item(ns) para um limite de {limite}. "
                          f"Remova {usados[cat] - limite:g} do inventário.")
    return avisos


# ======================================================
# TELAS
# ======================================================

def exibir_tabela_patentes(pp_atual):
    nome_atual = obter_patente(pp_atual)["nome"]
    print(f"   {'Patente'.ljust(22)}{'PP'.rjust(4)}  {'Crédito'.ljust(10)}  Cat.I  II  III  IV")
    for p in PATENTES:
        l = p["limites"]
        marca = ">>" if p["nome"] == nome_atual else "  "
        print(f" {marca} {p['nome'].ljust(22)}{str(p['pp']).rjust(4)}  {p['credito'].ljust(10)}  "
              f"{str(l[1]).rjust(5)}  {str(l[2]).rjust(2)}  {str(l[3]).rjust(3)}  {str(l[4]).rjust(2)}")


def menu_prestigio(id_personagem):
    while True:
        df = carregar_tabela(ARQUIVO_PERSONAGENS)
        linha = df[df["id"].astype(int) == int(id_personagem)]
        if linha.empty:
            break
        personagem = linha.iloc[0].to_dict()
        pp = obter_pp(personagem)
        patente = obter_patente(pp)
        proxima = proxima_patente(pp)

        print(f"\n--- PRESTÍGIO DE {str(personagem['nome']).upper()} ---")
        print(f" PP: {pp} | Patente: {patente['nome']} | Crédito: {patente['credito']}")
        if proxima:
            print(f" Próxima patente: {proxima['nome']} (faltam {proxima['pp'] - pp} PP)")
        else:
            print(" Patente máxima alcançada!")
        print(f" Itens por categoria: {resumo_categorias(id_personagem, pp)}")
        print()
        exibir_tabela_patentes(pp)

        for aviso in avisos_excesso(id_personagem, pp):
            print(f" [AVISO] {aviso}")

        print("\n[1] Adicionar PP")
        print("[2] Definir total de PP")
        print("[0] Voltar")
        op = input("Opção: ").strip()

        if op == "0":
            break
        elif op in ("1", "2"):
            try:
                valor = int(input("Quantidade de PP: ").strip())
            except ValueError:
                print("[ERRO] Digite um número inteiro.")
                continue
            novo = pp + valor if op == "1" else valor
            if novo < 0:
                print("[ERRO] O total de PP não pode ser negativo.")
                continue
            if definir_pp(id_personagem, novo):
                nova_patente = obter_patente(novo)
                print(f"[OK] PP: {pp} -> {novo}.")
                if nova_patente["nome"] != patente["nome"]:
                    print(f" *** Patente alterada: {patente['nome']} -> {nova_patente['nome']} ***")
        else:
            print("[ERRO] Opção inválida.")
