import pdfplumber
import re
import pandas as pd
from utils import comparar_nomes, montar_tabela_final
from customtkinter import filedialog
from pathlib import Path



arquivo = Path(filedialog.askopenfilename())
dadosFuncionarios = pd.read_excel('folha_pgto/Empregados.xls', 'dados')
dadosFuncionarios['Nome'] = dadosFuncionarios['Nome'].str.strip()

padraoNome = r"(Nome\s+do\s+Destinatário:)(\s.*)"
padraoValor = r'(Valor:.*)(R\$\s+)(\d+\,\d+)'

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
tabelaDados = pd.DataFrame(dados)

validacao = comparar_nomes(tabelaDados['Nome'], dadosFuncionarios['Nome'])
tabelaDados['Nome'] = tabelaDados['Nome'].map(validacao)

tabelaFinal = montar_tabela_final(dadosFuncionarios, tabelaDados)

tabelaDistincao = tabelaFinal.groupby('Centro de Custo')['Valor'].sum()

with open(arquivo.parent / 'resultado.txt', 'w') as f:
    f.write(tabelaDistincao.to_string())

print(tabelaDistincao)
