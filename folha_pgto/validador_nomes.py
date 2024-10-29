from thefuzz import fuzz



def comparar_nomes(baseAnalise, baseCorreta):

    parNomes = {}
    for nomeBaseAnalise in baseAnalise:
        # Dicionário com as similaridades entre os nomes da baseAnalise em relação a baseCorreta
        similaridadesBaseAnalise = []
        
        for nomeBaseCorreta in baseCorreta:
            similaridade = fuzz.ratio(nomeBaseAnalise, nomeBaseCorreta)
            similaridadePartial = fuzz.partial_ratio(nomeBaseAnalise, nomeBaseCorreta)
            similaridadesBaseAnalise.append((nomeBaseCorreta, (similaridade, similaridadePartial)))
        
        doisMaisSimilares = sorted(similaridadesBaseAnalise,
                               key=lambda item: item[1][0],
                               reverse=True)[:2]
        
        nomeMaisSimilar, _ = sorted(doisMaisSimilares,
                               key=lambda item: item[1][1],
                               reverse=True)[0]

        # for nome in nomesSimilares:
        #     similaridade = fuzz.ratio(nomeBaseAnalise, nome)
        #     if similaridade == maiorSimilaridade:
        #         nomeMaisSimilar = nome

        parNomes[nomeBaseAnalise] = nomeMaisSimilar
    return parNomes


if __name__ == '__main__':
    # print(fuzz.ratio('ROSELAINE SANTOS', 'JOSELAINE DOS SANTOS'))
    # print(fuzz.ratio('JOSELAINE DOS SANTOS', 'ROSELAINE SANTOS'))
    # print(fuzz.ratio('ROSELAINE SANTOS', 'ROSELAINE SANTOS AGUIRRE'))

    # Dicionário de exemplo
    dicionario = {
        "a": (10, 5),
        "b": (15, 8),
        "c": (7, 3),
        "d": (20, 9),
        "e": (25, 4)
    }

    # Ordena os itens com base no índice 0 da tupla em ordem decrescente e pega os dois primeiros
    maiores = sorted(dicionario.items(), key=lambda item: item[1][0], reverse=True)[:2]
    # maiores = sorted(dicionario.items(), key=lambda item: item[1][0], reverse=True)
    print(maiores)
    # Exibe o resultado
    # for chave, valor in maiores:
    #     print(f"Chave: {chave}, Valor: {valor}")


