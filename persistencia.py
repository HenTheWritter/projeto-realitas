# ENTREGA 1: INÍCIO 
# ENTREGA 3: CLASSES, NEX, RECURSOS AUTOMÁTICOS E AFINIDADE
# ENTREGA 4: PERICIAS
# ENTREGA 5: ITENS E INVENTÁRIO
# ENTREGA 6: RITUAIS

import os
import pandas as pd

# Define os nomes dos arquivos
ARQUIVO_USUARIOS = "usuarios.csv"
ARQUIVO_PERSONAGENS = "personagens.csv"
ARQUIVO_MESAS = "mesas.csv"
ARQUIVO_ITENS = "itens.csv"
ARQUIVO_INVENTARIO = "inventario.csv"
ARQUIVO_RITUAIS = "rituais.csv"
ARQUIVO_RITUAIS_AGENTE = "rituais_agente.csv"
ARQUIVO_SESSAO = "sessao.txt" 

# Estrutura das tabelas
COLUNAS_USUARIOS = [
    "id", "nome", "senha", "email", "idade", "dataCadastro"
]

COLUNAS_PERSONAGENS = [
    "id", "id_usuario", "nome", "dataCriacao", "classe", "NEX", "afinidade",
    "AGI", "FOR", "INT", "PRE", "VIG",
    "pvATUAL", "pvMAX", "sanATUAL", "sanMAX", "peATUAL", "peMAX",
    "defesa", "limiteItens",
    
    # === PERÍCIAS (28 Perícias Oficiais de Ordem Paranormal) ===
    "acrobacia", "adestramento", "artes", "atletismo", "atualidades", 
    "ciencias", "crime", "diplomacia", "enganacao", "fortitude", 
    "furtividade", "iniciativa", "intimidacao", "intuicao", "investigacao", 
    "luta", "medicina", "ocultismo", "percepcao", "pilotagem", 
    "pontaria", "profissao", "reflexos", "religiao", "sobrevivencia", 
    "tatica", "tecnologia", "vontade"
]

COLUNAS_MESAS = [
    "id", "nomeDaMesa", "maxJogadores", 
    "codigoConvite", "anotacoes"
]

# Catálogo de itens do jogo (referência, não pertence a nenhum agente)
# peso = "Espaços" do livro (é o que conta para o Limite de Itens do agente)
COLUNAS_ITENS = [
    "id", "nome", "tipoItem", "subtipo", "categoria", "peso",
    "dano", "critico", "alcance", "tipoDano", "defesa", "descricao"
]

# Inventário: liga um item do catálogo a um personagem, com quantidade
COLUNAS_INVENTARIO = [
    "id", "id_personagem", "id_item", "quantidade"
]

# Catálogo de rituais do jogo (referência)
COLUNAS_RITUAIS = [
    "id", "nome", "resumo", "elemento", "circulo", "execucao", "alcance", "alvoArea",
    "duracao", "resistencia", "peDiscente", "circuloReqDiscente", "afinidadeReqDiscente",
    "peVerdadeiro", "circuloReqVerdadeiro", "afinidadeReqVerdadeiro", "observacoes"
]

# Rituais que cada agente conhece (liga personagem -> ritual do catálogo)
COLUNAS_RITUAIS_AGENTE = [
    "id", "id_personagem", "id_ritual"
]

def inicializar_banco():
    """Verifica e cria os arquivos CSV caso não existam."""
    print("=== INICIALIZANDO BANCO DE DADOS ===")
    
    if not os.path.exists(ARQUIVO_USUARIOS):
        pd.DataFrame(columns=COLUNAS_USUARIOS).to_csv(ARQUIVO_USUARIOS, index=False)
        print(f"Arquivo '{ARQUIVO_USUARIOS}' criado!")
        
    if not os.path.exists(ARQUIVO_PERSONAGENS):
        pd.DataFrame(columns=COLUNAS_PERSONAGENS).to_csv(ARQUIVO_PERSONAGENS, index=False)
        print(f"Arquivo '{ARQUIVO_PERSONAGENS}' criado!")

    if not os.path.exists(ARQUIVO_MESAS):
        pd.DataFrame(columns=COLUNAS_MESAS).to_csv(ARQUIVO_MESAS, index=False)
        print(f"Arquivo '{ARQUIVO_MESAS}' criado!")

    if not os.path.exists(ARQUIVO_ITENS):
        pd.DataFrame(columns=COLUNAS_ITENS).to_csv(ARQUIVO_ITENS, index=False)
        print(f"Arquivo '{ARQUIVO_ITENS}' criado!")

    if not os.path.exists(ARQUIVO_INVENTARIO):
        pd.DataFrame(columns=COLUNAS_INVENTARIO).to_csv(ARQUIVO_INVENTARIO, index=False)
        print(f"Arquivo '{ARQUIVO_INVENTARIO}' criado!")

    if not os.path.exists(ARQUIVO_RITUAIS):
        pd.DataFrame(columns=COLUNAS_RITUAIS).to_csv(ARQUIVO_RITUAIS, index=False)
        print(f"Arquivo '{ARQUIVO_RITUAIS}' criado (vazio)!")

    if not os.path.exists(ARQUIVO_RITUAIS_AGENTE):
        pd.DataFrame(columns=COLUNAS_RITUAIS_AGENTE).to_csv(ARQUIVO_RITUAIS_AGENTE, index=False)
        print(f"Arquivo '{ARQUIVO_RITUAIS_AGENTE}' criado!")


def carregar_tabela(nome_arquivo):
    try:
        return pd.read_csv(nome_arquivo)
    except Exception as e:
        print(f"Erro ao ler '{nome_arquivo}': {e}")
        return pd.DataFrame()


def salvar_tabela(df, nome_arquivo):
    try:
        df.to_csv(nome_arquivo, index=False)
        return True
    except Exception as e:
        print(f"Erro ao salvar dados: {e}")
        return False

def salvar_sessao(id_usuario):
    with open(ARQUIVO_SESSAO, "w", encoding="utf-8") as f:
        f.write(str(id_usuario))

def ler_sessao():
    if not os.path.exists(ARQUIVO_SESSAO):
        return None
    try:
        with open(ARQUIVO_SESSAO, "r", encoding="utf-8") as f:
            conteudo = f.read().strip()
            return int(conteudo) if conteudo else None
    except Exception:
        return None

def encerrar_sessao():
    """ Deleta o arquivo de sessão """
    if os.path.exists(ARQUIVO_SESSAO):
        os.remove(ARQUIVO_SESSAO)