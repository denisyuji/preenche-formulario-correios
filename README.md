# Formulário de Declaração de Conteúdo - Preenchimento Automático # 

Este script foi desenvolvido para facilitar o preenchimento do [Formulário de Declaração de Conteúdo dos Correios](https://www.correios.com.br/enviar/encomendas/arquivo/nacional/formulario-declaracao-de-conteudo-a5). Ele gera um PDF preenchido automaticamente a partir dos dados fornecidos no arquivo `input.json` e insere os dados no formulário, tanto na versão original quanto em sua duplicata.

## Como Usar ##

### Pré-requisitos ###

- Python 3 instalado.
- Instalar as dependências necessárias utilizando o pip:

```
pip install -r requirements.txt
```

### Preencha o arquivo "dados.json" ###

O arquivo "dados.json" deve conter os dados do remetente, destinatário e itens,
conforme o exemplo abaixo:

```
{
	"Remetente": {
		"Nome": "Vinicius de Moraes",
		"Endereco": "R. Flamengo - Itapuã",
		"Cidade": "Salvador",
		"Estado": "BA",
		"CEP": "41635-480",
		"CPF_CNPJ": "986.543.210-00"
	},
	"Destinatario": {
		"Nome": "Tom Jobim",
		"Endereco": "Rua Nascimento e Silva 107",
		"Cidade": "Rio de Janeiro",
		"Estado": "RJ",
		"CEP": "22421-025",
		"CPF_CNPJ": "123.456.789-00"
	},
	"Itens": [
		{
			"Nome": "Livros",
			"Quantidade": 3,
			"Preco": 42.10
		},
		{
			"Nome": "Discos",
			"Quantidade": 2,
			"Preco": 10.00
		}
	]
}
```

### Executando o Script: ###

Após preencher o "dados.json" com os dados desejados, execute o script:

```
python preenche_formulario.py
```

O script irá gerar um PDF chamado "formulario_preenchido.pdf" com os dados preenchidos.

## Nota de Confiabilidade ##

Este software é fornecido "no estado em que se encontra" ("as-is"), sem garantias de qualquer tipo, expressas ou implícitas, incluindo, mas não se limitando a, garantias de comercialização ou adequação a um propósito específico. O desenvolvedor não se responsabiliza por quaisquer informações contidas no formulário gerado ou por eventuais alterações futuras no layout ou no conteúdo do formulário dos Correios. O usuário é responsável por verificar a conformidade dos dados e a validade do formulário utilizado.

## Licença ##

Este script é licenciado sob a Licença MIT. Você é livre para utilizar, modificar e distribuir este código, desde que mantenha o aviso de copyright e a licença em todas as cópias ou partes substanciais do software.