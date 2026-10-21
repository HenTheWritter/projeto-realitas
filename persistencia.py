# ENTREGA 1: INÍCIO 
# ENTREGA 3: CLASSES, NEX, RECURSOS AUTOMÁTICOS E AFINIDADE
# ENTREGA 4: PERICIAS
# ENTREGA 5: ITENS E INVENTÁRIO
# ENTREGA 6: RITUAIS
# ENTREGA 9: PATENTES E PRESTÍGIO 
# ENTREGA 10: TABELA DE AMEAÇAS PARANORMAIS (BESTIÁRIO)
# ENTREGA 11: CAMPANHAS
# ENTREGA 12: VINCULAÇÃO AGENTE <-> CAMPANHA

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
ARQUIVO_AMEACAS = "ameacas.csv"
ARQUIVO_CAMPANHAS = "campanhas.csv"
ARQUIVO_CAMPANHA_MEMBROS = "campanha_membros.csv"
ARQUIVO_CAMPANHA_AGENTES = "campanha_agentes.csv"
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
    "pp",  # Pontos de Prestígio (a patente é calculada a partir dele)
    
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
# categoria = 0, I, II, III ou IV (é o que conta para o limite por patente)
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

# Bestiário: criaturas e ameaças paranormais
COLUNAS_AMEACAS = [
    "id", "nome", "VD", "elemento", "PV", "defesa", "deslocamento",
    "AGI", "FOR", "INT", "PRE", "VIG",
    "pericias", "resistencias", "ataques", "habilidades", "descricao"
]

# Campanhas (o mestre é um usuário; "codigo" é o código de convite)
COLUNAS_CAMPANHAS = [
    "id", "nome", "id_mestre", "nomeMestre", "descricao", "dataCriacao", "codigo"
]

# Usuários que entraram em uma campanha usando o código (jogadores)
COLUNAS_CAMPANHA_MEMBROS = [
    "id", "id_campanha", "id_usuario"
]

# Agentes que cada jogador colocou em uma campanha (relação N:N)
COLUNAS_CAMPANHA_AGENTES = [
    "id", "id_campanha", "id_personagem"
]

# Criaturas iniciais do bestiário (valores RESUMIDOS/ESTIMADOS para uso no sistema).
# Ordem dos campos = COLUNAS_AMEACAS. Edite ameacas.csv à vontade para ajustar.
AMEACAS_INICIAIS = [
    (1, "Cultista Fanático", 20, "Nenhum", 30, 14, "9m",
     2, 2, 1, 2, 2,
     "Luta +10, Ocultismo +5, Vontade +10", "Nenhuma",
     "Adaga ritual +10 (1d4+2 perfuração, crít 19); Pistola +10 (1d12 perfuração, crít 18, alc 15m)",
     "Fanatismo: +5 em testes de Vontade; Último Ritual: ao chegar a 0 PV, causa 1d6 de dano mental em quem estiver adjacente (Vontade DT 15 reduz à metade)",
     "Seguidor devoto de um culto do Outro Lado. Perigoso em grupo."),
    (2, "Zumbi de Sangue", 40, "Sangue", 60, 13, "6m",
     1, 3, 0, 0, 3,
     "Luta +10, Fortitude +10", "Balístico 5; imune a efeitos de medo",
     "Pancada +14 (2d6+4 impacto); Mordida +14 (1d8+4 perfuração, apenas contra alvo agarrado)",
     "Sede de Sangue: +1d6 de dano contra alvos com menos da metade dos PV; Agarrar: ação padrão, Luta oposta para segurar o alvo",
     "Cadáver reanimado por Sangue, movido por fome incessante."),
    (3, "Sombra Rastejante", 50, "Morte", 55, 20, "12m (escalada 12m)",
     4, 1, 0, 2, 1,
     "Furtividade +20, Percepção +10", "Metade do dano de armas mundanas",
     "Toque gélido +16 (2d6+2 morte)",
     "Emboscada: +2d6 de dano contra alvos desprevenidos; Esvair-se: ação de movimento para se fundir à escuridão (+10 em Furtividade)",
     "Mancha de escuridão viva que se esgueira por paredes e tetos."),
    (4, "Marionete", 60, "Energia", 80, 18, "12m",
     3, 2, 1, 1, 3,
     "Furtividade +10, Luta +15", "Imune a eletricidade; corte 5",
     "Garra de fios +18 (2d8+3 corte, alcance 3m); Descarga +18 (3d6 eletricidade, alc 9m)",
     "Fios Elétricos: seu corpo a corpo alcança 3m; Marionetista: ação de movimento para empurrar ou puxar um alvo 3m",
     "Boneco articulado movido por fios de energia instável."),
    (5, "Fulgor Errante", 70, "Energia", 70, 21, "18m (voo)",
     5, 0, 2, 3, 2,
     "Reflexos +20, Pontaria +20", "Imune a eletricidade",
     "Raio +20 (3d8 eletricidade, alc 18m)",
     "Salto Elétrico: teletransporta 9m como ação de movimento; Sobrecarga: aparelhos eletrônicos em 9m param de funcionar por 1 rodada",
     "Esfera de energia pura que vaga em busca de aparelhos para consumir."),
    (6, "Devorador de Mentes", 80, "Conhecimento", 90, 20, "9m",
     2, 1, 5, 4, 2,
     "Ocultismo +20, Vontade +20, Percepção +15", "Imune a efeitos mentais",
     "Tentáculo psíquico +20 (3d8 mental, alc 12m)",
     "Sussurros: ação padrão, alvo em 30m faz Vontade (DT 25) ou fica confuso por 1 rodada; Absorver: recupera PV igual à metade do dano mental causado",
     "Entidade que se alimenta de pensamentos e memórias de suas vítimas."),
    (7, "Aberração Carnal", 100, "Sangue", 150, 22, "9m",
     1, 5, 0, 1, 5,
     "Luta +25, Fortitude +20", "Corte 10; impacto 10; perfuração 10",
     "Garras +25 (2d10+8 corte, 2 ataques); Esmagar +25 (4d8+10 impacto)",
     "Regeneração 5; Fúria Sangrenta: abaixo da metade dos PV, recebe +2 em ataques e dano",
     "Massa de carne retorcida e pulsante, resultado de um ritual de Sangue fora de controle."),
    (8, "Espectro Cinzento", 120, "Morte", 110, 25, "12m (voo)",
     3, 0, 3, 5, 3,
     "Intimidação +25, Vontade +25", "Incorpóreo; imune a dano mundano",
     "Dreno vital +25 (4d8 morte, toque)",
     "Aura de Pavor: inimigos em 9m fazem Vontade (DT 25) ou ficam abalados e perdem 1d6 SAN; Atravessar Paredes: pode se mover através de objetos sólidos",
     "Alma aprisionada entre a vida e a morte, que arrasta os vivos para o Outro Lado."),
]


def _migrar_personagens():
    """Garante que personagens.csv antigos ganhem a coluna 'pp' (Pontos de Prestígio)."""
    if not os.path.exists(ARQUIVO_PERSONAGENS):
        return
    try:
        df = pd.read_csv(ARQUIVO_PERSONAGENS)
    except Exception:
        return
    if "pp" not in df.columns:
        df["pp"] = 0
        df.to_csv(ARQUIVO_PERSONAGENS, index=False)
        print(f"Coluna 'pp' (Prestígio) adicionada em '{ARQUIVO_PERSONAGENS}'!")


def inicializar_banco():
    """Verifica e cria os arquivos CSV caso não existam."""
    print("=== INICIALIZANDO BANCO DE DADOS ===")
    
    if not os.path.exists(ARQUIVO_USUARIOS):
        pd.DataFrame(columns=COLUNAS_USUARIOS).to_csv(ARQUIVO_USUARIOS, index=False)
        print(f"Arquivo '{ARQUIVO_USUARIOS}' criado!")
        
    if not os.path.exists(ARQUIVO_PERSONAGENS):
        pd.DataFrame(columns=COLUNAS_PERSONAGENS).to_csv(ARQUIVO_PERSONAGENS, index=False)
        print(f"Arquivo '{ARQUIVO_PERSONAGENS}' criado!")
    else:
        _migrar_personagens()

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

    if not os.path.exists(ARQUIVO_AMEACAS):
        pd.DataFrame(AMEACAS_INICIAIS, columns=COLUNAS_AMEACAS).to_csv(ARQUIVO_AMEACAS, index=False)
        print(f"Arquivo '{ARQUIVO_AMEACAS}' criado com {len(AMEACAS_INICIAIS)} criaturas!")

    if not os.path.exists(ARQUIVO_CAMPANHAS):
        pd.DataFrame(columns=COLUNAS_CAMPANHAS).to_csv(ARQUIVO_CAMPANHAS, index=False)
        print(f"Arquivo '{ARQUIVO_CAMPANHAS}' criado!")

    if not os.path.exists(ARQUIVO_CAMPANHA_MEMBROS):
        pd.DataFrame(columns=COLUNAS_CAMPANHA_MEMBROS).to_csv(ARQUIVO_CAMPANHA_MEMBROS, index=False)
        print(f"Arquivo '{ARQUIVO_CAMPANHA_MEMBROS}' criado!")

    if not os.path.exists(ARQUIVO_CAMPANHA_AGENTES):
        pd.DataFrame(columns=COLUNAS_CAMPANHA_AGENTES).to_csv(ARQUIVO_CAMPANHA_AGENTES, index=False)
        print(f"Arquivo '{ARQUIVO_CAMPANHA_AGENTES}' criado!")


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