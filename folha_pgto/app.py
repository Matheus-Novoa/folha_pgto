import streamlit as st
import tempfile
from io import BytesIO
from ler_folha_pgto import process_pdf
from pathlib import Path
import pandas as pd
import logging


file_handler = logging.FileHandler('folha_pgto_intempo.log', encoding='utf-8')
file_handler.setLevel(logging.INFO)

out_handler = logging.StreamHandler()
out_handler.setLevel(logging.INFO)

debug_handler = logging.FileHandler('folha_debug.log', encoding='utf-8')
debug_handler.setLevel(logging.DEBUG)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8',
    handlers=[
        out_handler,
        file_handler,
        debug_handler
    ]
)
logger = logging.getLogger(__name__)

st.title("Processador de Folha de Pagamento")

uploaded_pdf = st.file_uploader("Upload do arquivo PDF", type="pdf")

if uploaded_pdf:
    logger.info(f"Arquivo PDF carregado: {uploaded_pdf.name}")
    file_id = f"{uploaded_pdf.name}-{uploaded_pdf.size}"

    if st.session_state.get("last_file_id") != file_id:
        logger.debug(f"Novo arquivo detectado com ID: {file_id}")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_pdf.read())
            pdf_path = Path(tmp_file.name)
            created_tmp = True
            logger.debug(f"Arquivo temporário criado em: {pdf_path}")

        try:
            logger.info("Iniciando processamento do PDF...")
            with st.spinner("Processando PDF..."):
                tabela_final, tabela_distincao = process_pdf(pdf_path)
            logger.info("PDF processado com sucesso")
            
            logger.debug("Gerando arquivo Excel...")
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                tabela_final.to_excel(writer, index=False, sheet_name='lista')
                tabela_distincao.to_excel(writer, sheet_name='distinção')
            output.seek(0)

            st.session_state["output_bytes"] = output.getvalue()
            st.session_state["last_file_id"] = file_id
            logger.info("Arquivo Excel gerado com sucesso")

            st.success("Processamento concluído!")
        except Exception as e:
            logger.error(f"Erro durante o processamento: {str(e)}", exc_info=True)
            st.error(f"Erro ao processar: {str(e)}")
        finally:
            if 'created_tmp' in locals() and created_tmp:
                logger.debug(f"Removendo arquivo temporário: {pdf_path}")
                pdf_path.unlink()
    else:
        logger.debug("Arquivo já processado anteriormente")
        st.success("Resultado pronto para download")

    if st.session_state.get("output_bytes"):
        logger.debug("Preparando botão de download")
        st.download_button(
            label="Baixar resultados",
            data=st.session_state["output_bytes"],
            file_name="Resultado.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        logger.info("Arquivo pronto para download")
