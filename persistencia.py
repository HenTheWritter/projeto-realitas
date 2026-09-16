# ENTREGA 1: INÍCIO 
# ENTREGA 3: CLASSES, NEX, RECURSOS AUTOMÁTICOS E AFINIDADE
# ENTREGA 4: PERICIAS

import os
import pandas as pd

# Define os nomes dos arquivos
ARQUIVO_USUARIOS = "usuarios.csv"
ARQUIVO_PERSONAGENS = "personagens.csv"
ARQUIVO_MESAS = "mesas.csv"
ARQUIVO_SESSAO = "sessao.txt" 

# Estrutura das tabelas
COLUNAS_USUARIOS = [
    "id", "nome", "senha", "email", "idade", "dataCadastro"
]

COLUNAS_PERSONAGENS = [
    "id", "id_usuario", "nome", "dataCriacao", "classe", "NEX", "afinidade",
    "AGI", "FOR", "INT", "PRE", "VIG",
    "pvATUAL", "pvMAX", "sanATUAL", "sanMAX", "peATUAL", "peMAX",
    
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
    """ Grava o ID do usuário logado no arquivo de sessão """
    with open(ARQUIVO_SESSAO, "w", encoding="utf-8") as f:
        f.write(str(id_usuario))

def ler_sessao():
    """ Retorna o ID do usuário logado se o arquivo existir """
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