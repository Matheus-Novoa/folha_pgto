import unicodedata
from dotenv import load_dotenv
from thefuzz import fuzz  # Se não disponível, use difflib para similaridade
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
import pandas as pd
import logging

load_dotenv()


file_handler = logging.FileHandler('folha_pgto_intempo.log')
out_handler = logging.StreamHandler()
out_handler.setLevel(logging.INFO)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8',
    handlers=[file_handler, out_handler]
)


def normalize_name(name):
    """Normaliza o nome: minúsculas, remove acentos."""
    normalized = unicodedata.normalize('NFKD', name.lower())
    return ''.join(c for c in normalized if not unicodedata.combining(c))


def comparar_nomes(baseAnalise, baseCorreta):
    parNomes = {}
    casos_para_IA = []

    for nomeBaseAnalise in baseAnalise:
        logging.info(f'\nAnalisando: {nomeBaseAnalise}')

        similaridadesBaseAnalise = []
        norm_analise = normalize_name(nomeBaseAnalise)
        norm_first_analise = normalize_name(nomeBaseAnalise.split(' ')[0]) if ' ' in nomeBaseAnalise else norm_analise

        for nomeBaseCorreta in baseCorreta:
            norm_correta = normalize_name(nomeBaseCorreta)
            similaridade = max(fuzz.token_sort_ratio(norm_analise, norm_correta),
                               fuzz.partial_token_sort_ratio(norm_analise, norm_correta))
            similaridadesBaseAnalise.append((nomeBaseCorreta, similaridade, norm_correta))

        # Ordena e pega apenas o top 1
        top_candidates = sorted(similaridadesBaseAnalise, key=lambda item: item[1], reverse=True)
        
        logging.info(f'\nTop candidatos:\n{top_candidates}')

        MIN_SIM = 70
        LOW_CONFIDENCE = 85

        maisSimilares = top_candidates[0] if top_candidates else None

        selected = None
        if maisSimilares and (maisSimilares[1] >= MIN_SIM and norm_first_analise in maisSimilares[2]):
            selected = maisSimilares[0]
            logging.info(f'Nome selecionado pelo algoritmo: {selected}')
    
        else:
            logging.info('O algoritmo não obteve uma resposta confiável. Delegando para a IA.')
            casos_para_IA.append((nomeBaseAnalise, top_candidates[:10] if top_candidates else []))

        if selected and maisSimilares[1] < LOW_CONFIDENCE:
            logging.info('O algoritmo não obteve uma resposta confiável. Delegando para a IA.')
            casos_para_IA.append((nomeBaseAnalise, top_candidates[:10]))

        parNomes[nomeBaseAnalise] = selected

    # Processa casos para IA via LangChain + Groq
    llm = ChatGroq(temperature=0.1, model_name="llama-3.3-70b-versatile")

    prompt_template = PromptTemplate(
        input_variables=["nome_analise", "top_candidates", "baseCorreta"],
        template="""
        Você é um especialista em matching de nomes. Analise o nome da baseAnalise: "{nome_analise}".

        Top candidatos do algoritmo (com similaridade aproximada):
        {top_candidates}

        Baseado na lista acima, busque o nome que seja mais compatível com "{nome_analise}".

        Regras:
        - Priorize o primeiro nome exato ou similar.
        - Tolere truncamentos (ex.: 'ARAU' = 'ARAUJO') e adicione partes faltantes se plausível.
        - Escolha o nome da baseCorreta mais próximo semanticamente e unicidade.
        - Responda APENAS com o nome exato da baseCorreta, sem explicações. Se nenhum match, responda 'None'.
        """
    )

    chain = RunnableSequence(prompt_template | llm)

    for nome_analise, candidates in casos_para_IA:
        # Formata inputs para a chain
        inputs = {
            "nome_analise": nome_analise,
            "top_candidates": "\n".join([f'- {cand[0]} (sim: {cand[1]:.0f}%)' for cand in candidates]) if candidates else 'Nenhum candidato encontrado',
            # "baseCorreta": "\n".join(baseCorreta[:5]) + "\n..." if len(baseCorreta) > 5 else "\n".join(baseCorreta)
        }
        try:
            response = chain.invoke(inputs)
            ia_match = response.content.strip()

            logging.info(f'Nome selecionado pela IA: {ia_match}')
            print(f'Nome selecionado pela IA: {ia_match}')

            parNomes[nome_analise] = ia_match if ia_match != 'None' else None
        except Exception as e:
            print(f"Erro na chain LangChain/Groq: {e}")
            parNomes[nome_analise] = None

    return parNomes


def montar_tabela_final(dadosFuncionarios, folhaPgto, pasta):
    tabelaFinal = pd.merge(dadosFuncionarios, folhaPgto, on='Nome')
    tabelaFinal.drop_duplicates(inplace=True)
    tabelaFinal.reset_index(drop=True,inplace=True)

    tabelaFinal['Valor'] = (tabelaFinal['Valor']
                            .str.replace('.','')
                            .str.replace(',', '.')
                            .astype('float32')
                            .apply(round, args=(2,))
                            )
    tabelaFinal.to_excel(pasta / 'Resultado.xlsx', index=False)

    return tabelaFinal
