from thefuzz import fuzz



def comparar_nomes(baseAnalise, baseCorreta):

    parNomes = {}
    for nomeBaseAnalise in baseAnalise:
        similaridadesLista = [] # Lista da similaridade de "nomeBaseAnalise" com todos os nomes em "BaseCorreta"
        nomesSimilares = [] # Lista com os nomes mais similares
        
        for nomeBaseCorreta in baseCorreta:
            similaridade = fuzz.ratio(nomeBaseAnalise, nomeBaseCorreta)
            similaridadesLista.append(similaridade)
            nomesSimilares.append(nomeBaseCorreta)
        
        maiorSimilaridade = max(similaridadesLista)

        for nome in nomesSimilares:
            similaridade = fuzz.ratio(nomeBaseAnalise, nome)
            if similaridade == maiorSimilaridade:
                nomeMaisSimilar = nome

        parNomes[nomeBaseAnalise] = nomeMaisSimilar
    return parNomes


if __name__ == '__main__':
    print(fuzz.ratio('ROSELAINE SANTOS', 'JOSELAINE DOS SANTOS'))
    print(fuzz.ratio('JOSELAINE DOS SANTOS', 'ROSELAINE SANTOS'))
    print(fuzz.ratio('ROSELAINE SANTOS', 'ROSELAINE SANTOS AGUIRRE'))

    # print(fuzz.partial_ratio('ROSELAINE SANTOS', 'JOSELAINE DOS SANTOS'))
    # print(fuzz.partial_ratio('ROSELAINE SANTOS', 'ROSELAINE SANTOS AGUIRRE'))
