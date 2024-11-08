import pdfplumber
import re
import pandas as pd
from validador_nomes import comparar_nomes



padraoNome = r"(Nome\s+do\s+Destinatário:)(\s.*)"
padraoValor = r'(Valor:.*)(R\$\s+)(\d+\,\d+)'

arquivo = 'folha_pgto/CCO_000002.pdf'
with pdfplumber.open(arquivo) as pdf:
    paginas = [page.extract_text() for page in pdf.pages]     

nomes = []
valores = []
for pagina in paginas:
    buscaNome = re.search(padraoNome, pagina)
    buscaValor = re.search(padraoValor, pagina)
    nomeDestinatario = buscaNome.group(2).strip()
    valor = buscaValor.group(3).strip()

    nomes.append(nomeDestinatario)
    valores.append(valor)

dados = {'Nome': nomes, 'Valor': valores}
tabela = pd.DataFrame(dados)

dadosFuncionarios = pd.read_excel('folha_pgto/Empregados.xls', 'dados')

validacao = comparar_nomes(tabela['Nome'], dadosFuncionarios['Nome'])
tabela['Nome'] = tabela['Nome'].map(validacao)

tabelaFinal = pd.merge(dadosFuncionarios, tabela, on='Nome')

tabelaFinal.drop_duplicates(inplace=True)
tabelaFinal.reset_index(drop=True,inplace=True)

tabelaFinal['Valor'] = (tabelaFinal['Valor'].str
                        .replace(',', '.')
                        .astype('float32')
                        .apply(round, args=(2,)))

tabelaDistincao = tabelaFinal.groupby('Centro de Custo')['Valor'].sum()
print(tabelaDistincao)
