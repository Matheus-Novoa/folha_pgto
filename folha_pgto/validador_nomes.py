from thefuzz import fuzz
import unicodedata



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
