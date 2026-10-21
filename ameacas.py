# ENTREGA 10: TABELA DE AMEAÇAS PARANORMAIS (BESTIÁRIO)

import pandas as pd
from persistencia import ARQUIVO_AMEACAS, carregar_tabela


def _txt(valor, padrao="-"):
    if valor is None or pd.isna(valor):
        return padrao
    s = str(valor).strip()
    return s if s and s.lower() != "nan" else padrao


def carregar_ameacas():
    df = carregar_tabela(ARQUIVO_AMEACAS)
    if df.empty:
        return df
    df["VD"] = pd.to_numeric(df["VD"], errors="coerce").fillna(0).astype(int)
    return df.sort_values(["VD", "nome"]).reset_index(drop=True)


# ---------- Filtros (Pandas) ----------

def filtrar_por_vd(df, vd_min, vd_max):
    return df[(df["VD"] >= vd_min) & (df["VD"] <= vd_max)].reset_index(drop=True)


def filtrar_por_elemento(df, elemento):
    return df[df["elemento"].astype(str).str.lower() == elemento.lower()].reset_index(drop=True)


def buscar_por_nome(df, trecho):
    return df[df["nome"].astype(str).str.contains(trecho, case=False, regex=False)].reset_index(drop=True)


# ---------- Exibição ----------

def listar_ameacas(df):
    if df.empty:
        print("   (Nenhuma criatura encontrada)")
        return
    print(f"   {'Nome'.ljust(22)}{'VD'.rjust(4)}  {'Elemento'.ljust(13)}{'PV'.rjust(4)}  Def")
    for i, a in df.iterrows():
        print(f"[{i + 1:>2}] {str(a['nome']).ljust(22)}{str(a['VD']).rjust(4)}  "
              f"{_txt(a['elemento']).ljust(13)}{str(a['PV']).rjust(4)}  {a['defesa']}")


def exibir_ameaca(a):
    print("\n" + "=" * 70)
    print(f" {str(a['nome']).upper()}  (VD {a['VD']} | {_txt(a['elemento'])})")
    print("-" * 70)
    print(f" PV: {a['PV']} | Defesa: {a['defesa']} | Deslocamento: {_txt(a['deslocamento'])}")
    print(f" AGI:{a['AGI']} FOR:{a['FOR']} INT:{a['INT']} PRE:{a['PRE']} VIG:{a['VIG']}")
    print(f" Perícias: {_txt(a['pericias'])}")
    print(f" Resistências: {_txt(a['resistencias'])}")
    print(f" Ataques: {_txt(a['ataques'])}")
    print(f" Habilidades: {_txt(a['habilidades'])}")
    print(f" Descrição: {_txt(a['descricao'])}")
    print("=" * 70)


def _escolher_para_detalhar(df):
    if df.empty:
        return
    escolha = input("\nDigite o NÚMERO da criatura para ver os detalhes (ou 0 para voltar): ").strip()
    if escolha == "0":
        return
    if not escolha.isdigit() or not (1 <= int(escolha) <= len(df)):
        print("[ERRO] Número inválido.")
        return
    exibir_ameaca(df.iloc[int(escolha) - 1])
    input("\nENTER para continuar...")


# ---------- Menu ----------

def menu_ameacas():
    while True:
        df = carregar_ameacas()
        print("\n--- BESTIÁRIO: AMEAÇAS PARANORMAIS ---")
        if df.empty:
            print("[ERRO] Nenhuma criatura cadastrada (verifique o arquivo ameacas.csv).")
            return

        print(f"{len(df)} criatura(s) cadastrada(s).")
        print("[1] Listar todas")
        print("[2] Filtrar por VD (faixa)")
        print("[3] Filtrar por Elemento")
        print("[4] Buscar por nome")
        print("[0] Voltar")
        op = input("Opção: ").strip()

        if op == "0":
            break

        elif op == "1":
            print()
            listar_ameacas(df)
            _escolher_para_detalhar(df)

        elif op == "2":
            try:
                vd_min = int(input("VD mínimo: ").strip())
                vd_max = int(input("VD máximo: ").strip())
            except ValueError:
                print("[ERRO] Digite números inteiros.")
                continue
            if vd_min > vd_max:
                vd_min, vd_max = vd_max, vd_min
            resultado = filtrar_por_vd(df, vd_min, vd_max)
            print(f"\nCriaturas com VD entre {vd_min} e {vd_max}:")
            listar_ameacas(resultado)
            _escolher_para_detalhar(resultado)

        elif op == "3":
            elementos = sorted(df["elemento"].dropna().astype(str).unique())
            print("\nElementos:")
            for i, el in enumerate(elementos, start=1):
                print(f"[{i}] {el}")
            escolha = input("Opção: ").strip()
            if not escolha.isdigit() or not (1 <= int(escolha) <= len(elementos)):
                print("[ERRO] Opção inválida.")
                continue
            elemento = elementos[int(escolha) - 1]
            resultado = filtrar_por_elemento(df, elemento)
            print(f"\nCriaturas do elemento {elemento}:")
            listar_ameacas(resultado)
            _escolher_para_detalhar(resultado)

        elif op == "4":
            trecho = input("Parte do nome: ").strip()
            if not trecho:
                print("[ERRO] Digite algo para buscar.")
                continue
            resultado = buscar_por_nome(df, trecho)
            print(f"\nResultados para '{trecho}':")
            listar_ameacas(resultado)
            _escolher_para_detalhar(resultado)

        else:
            print("[ERRO] Opção inválida.")
