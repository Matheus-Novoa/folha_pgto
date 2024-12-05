# Robô para Leitura de PDF de Folha de Pagamento

* O robô utiliza OCR (pytesseract) para realizar a leitura de uma folha de pagamentos, que é fornecida através de um documento em PDF.
* Após a leitura, expressões regulares são aplicadas para obter os dados de interesse.
* Por fim, os dados são tratados, validados e organizados em um dataframe do Pandas. 