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


if __name__ == '__main__':
    import unicodedata

    def remover_acentuacao(texto):
        # Normaliza o texto para decompor caracteres acentuados
        texto_normalizado = unicodedata.normalize('NFKD', texto)
        # Filtra apenas caracteres ASCII (sem acentuação)
        texto_sem_acentos = ''.join(c for c in texto_normalizado if not unicodedata.combining(c))
        return texto_sem_acentos

    # Exemplo de uso
    texto = "Elisângela"
    texto_sem_acentos = remover_acentuacao(texto)
    print(texto_sem_acentos)
