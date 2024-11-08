from thefuzz import fuzz
import unicodedata
import pandas as pd



def comparar_nomes(baseAnalise, baseCorreta):

    parNomes = {}
    for nomeBaseAnalise in baseAnalise:
        # Dicionário com as similaridades entre os nomes da baseAnalise em relação a baseCorreta
        similaridadesBaseAnalise = []
        
        for nomeBaseCorreta in baseCorreta:
            similaridade = fuzz.ratio(nomeBaseAnalise, nomeBaseCorreta)
            similaridadesBaseAnalise.append((nomeBaseCorreta, similaridade))
        
        maisSimilares, segundoMaisSimilar = sorted(similaridadesBaseAnalise,
                               key=lambda item: item[1],
                               reverse=True)[:2]
        
        nomeNormalizado = unicodedata.normalize('NFKD', maisSimilares[0])
        nomeSemAcento = ''.join(c for c in nomeNormalizado if not unicodedata.combining(c))
        
        parNomes[nomeBaseAnalise] = (maisSimilares[0]
                                     if nomeBaseAnalise.split(' ')[0] in nomeSemAcento
                                     else segundoMaisSimilar[0])

    return parNomes


def montar_tabela_final(dadosFuncionarios, folhaPgto):
    tabelaFinal = pd.merge(dadosFuncionarios, folhaPgto, on='Nome')
    tabelaFinal.drop_duplicates(inplace=True)
    tabelaFinal.reset_index(drop=True,inplace=True)

    tabelaFinal['Valor'] = (tabelaFinal['Valor']
                            .str.replace('.','')
                            .str.replace(',', '.')
                            .astype('float32')
                            .apply(round, args=(2,))
                            )
    tabelaFinal.to_excel('Resultado.xlsx', index=False)

    return tabelaFinal
