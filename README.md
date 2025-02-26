# Formulário de Declaração de Conteúdo - Preenchimento Automático # 

Este script foi desenvolvido para facilitar o preenchimento do [Formulário de Declaração de Conteúdo dos Correios](https://www.correios.com.br/enviar/encomendas/arquivo/nacional/formulario-declaracao-de-conteudo-a5). Ele gera um PDF preenchido automaticamente a partir dos dados fornecidos no arquivo `input.json` e insere os dados no formulário, tanto na versão original quanto em sua duplicata.

## Como Usar ##

### Pré-requisitos ###

- Python 3 instalado.
- Instalar as dependências necessárias utilizando o pip:

```
pip install reportlab PyPDF2 pdf2image Pillow
```

- No Ubuntu, certifique-se de que o pacote poppler-utils esteja instalado:

```
sudo apt-get install poppler-utils
```

- O script utiliza a fonte "DejaVuSans", que já vem instalada por padrão no Ubuntu.

### Preencha o arquivo "input.json" ###

O arquivo "input.json" deve conter os dados do remetente, destinatário e itens,
conforme o exemplo abaixo:

```
{
 "Sender": {
   "Name": "Nome do Remetente",
   "Address": "Endereço do Remetente",
   "City": "Cidade do Remetente",
   "State": "Estado",
   "Zip": "CEP",
   "Tax_id": "CPF/CNPJ"
 },
 "Receiver": {
   "Name": "Nome do Destinatário",
   "Address": "Endereço do Destinatário",
   "City": "Cidade do Destinatário",
   "State": "Estado",
   "Zip": "CEP",
   "Tax_id": "CPF/CNPJ"
 },
 "Itens": [
   {
     "Name": "Nome do Item 1",
     "Qty": 2,
     "Price": 45.50
   },
   {
     "Name": "Nome do Item 2",
     "Qty": 1,
     "Price": 30.00
   }
 ]
}
```

### Executando o Script: ###

Após preencher o "input.json" com os dados desejados, execute o script:

```
python fill_form.py
```

O script irá gerar um PDF chamado "output.pdf" com os dados preenchidos.
O PDF também será exibido em uma janela gráfica. Para sair da janela, basta pressionar "Q" no teclado (na GUI ou no terminal).

## Nota de Confiabilidade ##

Este software é fornecido "no estado em que se encontra" ("as-is"), sem garantias de qualquer tipo, expressas ou implícitas, incluindo, mas não se limitando a, garantias de comercialização ou adequação a um propósito específico. O desenvolvedor não se responsabiliza por quaisquer informações contidas no formulário gerado ou por eventuais alterações futuras no layout ou no conteúdo do formulário dos Correios. O usuário é responsável por verificar a conformidade dos dados e a validade do formulário utilizado.

## Licença ##

Este script é licenciado sob a Licença MIT. Você é livre para utilizar, modificar e distribuir este código, desde que mantenha o aviso de copyright e a licença em todas as cópias ou partes substanciais do software.