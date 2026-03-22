import os
import pandas as pd

from pathlib import Path
from typing import Optional, Union

def concat_path_file(strPathFile: str, strFile: str, strExtFile: str) -> str:
    """
    Função..: concat_path_file
    Objetivo: Concatena o Caminho e o Nome do arquivo em uma única variável
            Caso o diretório não exista, ele será criado.
    """
    if not strPathFile:
        raise ValueError("O caminho base não pode ser vazio.")

    if not strFile:
        raise ValueError("O nome do arquivo não pode ser vazio.")

    # Cria o diretório caso não exista
    os.makedirs(strPathFile, exist_ok=True)

    # Garante extensão do arquivo
    if strExtFile and not strFile.lower().endswith(f".{strExtFile}"):
        strFile = f"{strFile}.{strExtFile}"

    return os.path.join(strPathFile, strFile)

# def save_file_parquet(
#     df: pd.DataFrame,
#     caminho: Union[str, Path],
#     verificar_integridade: bool = True,
#     comprimir: Optional[str] = 'snappy'
# ) -> bool:
#     """
#     Função..: save_file_parquet
#     Objetivo: Salva um DataFrame em formato Parquet e verifica a gravação.
#     Args....:
#         df: DataFrame a ser salvo
#         caminho: Caminho completo do arquivo (incluindo .parquet)
#         verificar_integridade: Se True, valida a gravação lendo o arquivo
#         comprimir: Tipo de compressão ('snappy', 'gzip', 'brotli' ou None)

#     Returns:
#         bool: True se gravação bem-sucedida, False caso contrário
#     """
#     # Validação inicial: DataFrame não pode estar vazio
#     if df.empty:
#         raise ValueError("DataFrame não pode estar vazio")

#     # Converte para Path para manipulação consistente de caminhos
#     caminho_arquivo = Path(caminho)

#     # Garante que o arquivo tenha extensão .parquet
#     if caminho_arquivo.suffix != '.parquet':
#         caminho_arquivo = caminho_arquivo.with_suffix('.parquet')

#     try:
#         # Cria diretórios intermediários se não existirem
#         caminho_arquivo.parent.mkdir(parents=True, exist_ok=True)

#         # Salva o DataFrame em formato Parquet
#         df.to_parquet(
#             caminho_arquivo,
#             compression=comprimir,
#             index=False,
#             engine='pyarrow'  # Engine padrão no Colab
#         )

#         # Verifica se o arquivo foi realmente criado no sistema
#         if not caminho_arquivo.exists():
#             log.error(f"Arquivo não foi criado: {caminho_arquivo}")
#             return False

#         # Validação de integridade: lê o arquivo e compara com original
#         if verificar_integridade:
#             df_validacao = pd.read_parquet(caminho_arquivo)

#             # Verifica se dimensões (linhas x colunas) são iguais
#             if df.shape != df_validacao.shape:
#                 log.error("Dimensões do arquivo salvo diferem do original")
#                 return False

#             # Verifica se os nomes das colunas correspondem
#             if not df.columns.equals(df_validacao.columns):
#                 log.error("Colunas do arquivo salvo diferem do original")
#                 return False

#         # Exibe tamanho do arquivo salvo
#         tamanho_mb = caminho_arquivo.stat().st_size / (1024 * 1024)
#         log.info(f"✓ Arquivo salvo: {caminho_arquivo} ({tamanho_mb:.2f} MB)")

#         return True

#     except PermissionError:
#         log.error(f"Sem permissão para escrever em: {caminho_arquivo}")
#         return False

#     except Exception as e:
#         log.error(f"Erro ao salvar arquivo: {str(e)}")
#         return False

# def fxSaveDownload(
#     df: pd.DataFrame,
#     nome_arquivo: str = 'dados.parquet',
#     baixar: bool = True
# ) -> bool:
#     """
#     Salva Parquet e oferece download automático no Colab.

#     Args:
#         df: DataFrame a ser salvo
#         nome_arquivo: Nome do arquivo (sem necessidade de caminho)
#         baixar: Se True, inicia download automaticamente

#     Returns:
#         bool: True se operação bem-sucedida
#     """
#     # Salva o arquivo no diretório temporário do Colab
#     sucesso = fxSaveParquet(df, nome_arquivo)

#     if sucesso and baixar:
#         try:
#             # Faz download do arquivo para máquina local
#             files.download(nome_arquivo)
#             log.info(f"Download iniciado: {nome_arquivo}")
#         except Exception as e:
#             log.error(f"Erro ao fazer download: {str(e)}")
#             return False

#     return sucesso


def fxRemoveFileIfExists(strPathFile: str) -> None:
    """
    Função..: fxRemoveFileIfExists
    Objetivo: Remover o arquivo caso ele exista.
    """
    if os.path.isfile(strPathFile):
        os.remove(strPathFile)

def fxAcertaDataHora(df, strNomeColuna):
    """
    Função - fxAcertaDataHora
    Objetivo.: Transformar as colunas: [data_emprestimo, data_devolucao, data_renovacao'] que possuem o
            formato: YYYY-mm-dd HH:MM:SS.ffffffff para o formato: YYYY-mm-dd HH:MM
    """
    intContReg  = 1
    lstDataHora = []
    #
    for conteudo in df[strNomeColuna]:
        if str(conteudo) == 'nan':
            conteudo = ''
        elif len(conteudo) > 16:
            conteudo = conteudo[:16]
        #
        lstDataHora.append(conteudo)
        print(f'Registro: {str(intContReg)}, Data Devolucao: {conteudo}')
        intContReg += 1
    #
    df[strNomeColuna] = lstDataHora
    return None

"""
# Função: Converte os valores de uma coluna STRING de um DataFrame para Data
"""
fxConvParaData = lambda df, strNomeColuna : pd.to_datetime(df[strNomeColuna])

"""
# Função: Converte o valor de uma Variável STRING para Data
"""
fxConvStrParaData = lambda strNomeColuna : pd.to_datetime(strNomeColuna, dayfirst=True)
