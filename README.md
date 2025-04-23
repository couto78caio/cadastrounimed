# Projeto Cadastro de Plano de Saúde

Este projeto consiste em uma aplicação web desenvolvida em Python utilizando o framework Flask. Ele permite o cadastro de titulares e seus dependentes em um plano de saúde, coletando informações detalhadas, calculando os valores dos planos com base na idade e em uma tabela de preços, exibindo um resumo do cadastro e, finalmente, salvando os dados em um arquivo CSV.


## Funcionalidades Detalhadas

1.  **Formulário Inicial de Cadastro (`templates/formulario_inicial.html`):**

      * **Dados do Titular:**
          * **Código do Contrato:** Campo de texto (`cod_contrato`) obrigatório. Utilizado para buscar os preços na tabela. Possui a função JavaScript `atualizaContratoNosDependentes()` para preencher automaticamente este campo nos formulários de dependentes.
          * **Código do Beneficiário:** Campo de texto (`cod_beneficiario`).
          * **Titular:** Campo de texto (`titular`) obrigatório. Nome completo do titular. Possui a função JavaScript `atualizaTitularNosDependentes()` para preencher automaticamente este campo nos formulários de dependentes.
          * **Sexo do Titular:** Dropdown (`sexo_titular`) com opções "Selecione", "Masculino", "Feminino", "Outro".
          * **CPF/CNPJ:** Campo de texto (`cpf_cnpj`) obrigatório.
          * **Data de Nascimento:** Campo de data (`dt_nascimento`) obrigatório. Usada para calcular a idade do titular.
          * **Número da Conta Corrente:** Campo de texto (`num_conta_corrente`).
          * **Número de Telefone:** Campo de telefone (`num_telefone`).
          * **UF:** Campo de texto (`uf`) para a Unidade Federativa (máximo 2 caracteres).
          * **Cidade:** Campo de texto (`cidade`).
          * **Endereço:** Campo de texto (`endereco`).
          * **Data do Contrato:** Campo de data (`dt_contrato`) obrigatório.

      * **Dependentes:**
          * **Possui Dependentes?** Dropdown (`tem_dependente`) com opções "Não" e "Sim". A seleção "Sim" torna visível a seção de dependentes através da função JavaScript `mostrarDependentes()`.
          * **Lista de Dependentes (`#lista_dependentes`):** Container dinâmico onde os formulários de cada dependente são adicionados.
          * **Botão "+ Adicionar Dependente":** Ao clicar, a função JavaScript `adicionarDependente()` cria e adiciona um novo conjunto de campos para um dependente. Os campos incluem:
              * Nome do Titular (readonly, preenchido automaticamente)
              * Código do Contrato (readonly, preenchido automaticamente)
              * Código do Beneficiário do Dependente (`dependente_cod_benef_${index}`)
              * Nome do Dependente (`dependente_nome_${index}`, obrigatório)
              * Sexo do Dependente (`sexo_dependente_${index}`)
              * CPF/CNPJ do Dependente (`dependente_cpf_${index}`)
              * Data de Nascimento do Dependente (`dependente_nasc_${index}`, obrigatório)
              * Parentesco do Dependente (`dependente_parentesco_${index}`)
          * As funções JavaScript `atualizaTitularNosDependentes()` e `atualizaContratoNosDependentes()` atualizam os campos readonly nos formulários de dependentes quando os campos correspondentes do titular são modificados.

      * **Botão "Próximo":** Submete o formulário via método POST para a rota `/` no `app.py`, que redireciona para a rota `/idades`.

2.  **Exibição de Idades (`templates/exibir_idades.html`):**

      * Recebe os dados do formulário inicial via parâmetros na URL (`request.args`).
      * Exibe o nome e a data de nascimento do titular, juntamente com a idade calculada usando a função `calcular_idade` no `app.py`.
      * Se houver dependentes, exibe uma lista com o nome, data de nascimento e idade de cada um.
      * Um formulário POST envia os dados (incluindo as idades calculadas como campos hidden) para a rota `/resumo` no `app.py` ao clicar no botão "Ver Resumo e Calcular Valores".
      * Um link "Voltar ao Formulário" redireciona para a página inicial (`/`).

3.  **Resumo do Cadastro (`templates/resumo_cadastro.html`):**

      * Recebe os dados via método POST do formulário de confirmação de idades.
      * Exibe todas as informações do titular e dos dependentes.
      * Para o titular e cada dependente, a função `obter_preco` no `app.py` é chamada para buscar o valor do plano e a descrição (plano e acomodação) na `tabela_precos.csv` com base no `Código do Contrato` e na `idade`.
      * Os valores individuais e a descrição do plano para cada pessoa são exibidos.
      * O valor total do plano (soma dos valores individuais) é calculado e mostrado.
      * Um formulário POST envia todos os dados (incluindo os valores e a descrição do plano como campos hidden) para a rota `/salvar_csv` no `app.py` ao clicar no botão "Salvar em CSV".
      * Um link "Voltar para Editar Idades" redireciona para a página de exibição de idades (`/idades`), reenviando os dados do formulário inicial.

4.  **Salvar em Arquivo CSV (`/salvar_csv` no `app.py`):**

      * Recebe os dados via método POST do formulário de resumo.
      * Organiza os dados do titular e de todos os dependentes em uma lista de dicionários.
      * Utiliza a biblioteca Pandas para criar um DataFrame com esses dados.
      * Salva o DataFrame em um arquivo CSV chamado `cadastro_planos_saude.csv` na raiz do projeto, com codificação UTF-8 e sem incluir o índice do DataFrame.
      * Retorna uma mensagem de sucesso indicando que os dados foram salvos.

## Arquivos de Configuração

1.  **`tabela_precos.csv`:**
    * Arquivo de texto com valores separados por vírgula (CSV).
    * Contém as colunas: `codigo_contrato`, `descricao`, `idade_min`, `idade_max`, `valor_mensal`.
    * Deve ser populado com os dados de preços dos planos, seguindo a estrutura especificada.

2.  **`pyproject.toml`:**
    * Arquivo de configuração do Poetry para gerenciamento de dependências.
    * Define o nome do projeto, versão, descrição, autor e as dependências necessárias (`flask` e `pandas`).
    * Especifica o sistema de construção do projeto.

## Como Executar (Reiterando)**

1.  **Certifique-se de ter Python e Poetry instalados.**
2.  **Navegue até o diretório do projeto no terminal.**
3.  **Instale as dependências:** `poetry install`
4.  **Execute a aplicação:** `poetry run python app.py`
5.  **Acesse a aplicação no navegador:** `http://127.0.0.1:5000/`

## Próximos Passos e Melhorias (Reiterando)**

  * **Validação de Dados:** Implementar validação no backend usando Flask-WTF ou similar.
  * **Persistência de Dados:** Integrar um banco de dados (SQLite, PostgreSQL, MySQL, etc.) usando SQLAlchemy ou outra ORM.
  * **Interface do Usuário:** Melhorar o design e a usabilidade com um framework CSS como Bootstrap ou Tailwind CSS.
  * **Tratamento de Erros:** Implementar páginas de erro personalizadas e tratamento de exceções mais robusto.
  * **Testes:** Escrever testes unitários e de integração usando `pytest`.
  * **Segurança:** Implementar medidas de segurança contra ataques CSRF, XSS, etc.
  * **Autenticação e Autorização:** Adicionar um sistema de login para gerenciar usuários que podem cadastrar planos.
  * **Internacionalização (i18n):** Permitir que a aplicação seja utilizada em diferentes idiomas.
  * **Implantação:** Preparar a aplicação para ser implantada em um servidor web real (usando WSGI como Gunicorn ou uWSGI).
