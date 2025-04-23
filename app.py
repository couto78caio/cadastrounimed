from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
from datetime import datetime

app = Flask(__name__)

TABELA_PRECOS_PATH = 'tabela_precos.csv'
ARQUIVO_CSV_FINAL = 'cadastro_planos_saude.csv'

def calcular_idade(data_nascimento):
    if not data_nascimento:
        return None
    try:
        data_nascimento = datetime.strptime(data_nascimento, '%Y-%m-%d')
        hoje = datetime.now()
        idade = hoje.year - data_nascimento.year - ((hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day))
        return idade
    except ValueError:
        return None

def obter_preco(codigo_contrato, idade):
    try:
        tabela_precos = pd.read_csv(TABELA_PRECOS_PATH)
        faixa = tabela_precos[(tabela_precos['codigo_contrato'] == codigo_contrato) & (tabela_precos['idade_min'] <= idade) & (tabela_precos['idade_max'] >= idade)]
        if not faixa.empty:
            return faixa['valor_mensal'].iloc[0], faixa['descricao'].iloc[0]
        return None, None
    except FileNotFoundError:
        return None, None

@app.route('/', methods=['GET', 'POST'])
def formulario_inicial():
    if request.method == 'POST':
        titular_data = {
            'cod_contrato': request.form['cod_contrato'],
            'cod_beneficiario': request.form['cod_beneficiario'],
            'titular': request.form['titular'],
            'sexo_titular': request.form['sexo_titular'],
            'cpf_cnpj': request.form['cpf_cnpj'],
            'dt_nascimento': request.form['dt_nascimento'],
            'num_conta_corrente': request.form['num_conta_corrente'],
            'num_telefone': request.form['num_telefone'],
            'uf': request.form['uf'],
            'cidade': request.form['cidade'],
            'endereco': request.form['endereco'],
            'dt_contrato': request.form['dt_contrato']
        }
        dependentes_data = []
        i = 1
        while True:
            nome_dependente = request.form.get(f'dependente_nome_{i}')
            if nome_dependente:
                dependente = {
                    'nome': nome_dependente,
                    'sexo': request.form.get(f'sexo_dependente_{i}'),
                    'cpf': request.form.get(f'dependente_cpf_{i}'),
                    'dt_nascimento': request.form.get(f'dependente_nasc_{i}'),
                    'parentesco': request.form.get(f'dependente_parentesco_{i}')
                }
                dependentes_data.append(dependente)
                i += 1
            else:
                break
        return redirect(url_for('exibir_idades', titular_data=titular_data, dependentes_data=dependentes_data))
    return render_template('formulario_inicial.html')

@app.route('/idades', methods=['GET'])
def exibir_idades():
    titular_data = request.args.get('titular_data')
    dependentes_data = request.args.get('dependentes_data')

    if titular_data:
        import json
        titular_data = json.loads(titular_data.replace("'", "\""))
        idade_titular = calcular_idade(titular_data['dt_nascimento'])

        idades_dependentes = []
        if dependentes_data:
            dependentes_data = json.loads(dependentes_data.replace("'", "\""))
            for dependente in dependentes_data:
                idade_dependente = calcular_idade(dependente['dt_nascimento'])
                idades_dependentes.append({'nome': dependente['nome'], 'idade': idade_dependente})

        return render_template('exibir_idades.html', titular=titular_data, idade_titular=idade_titular, dependentes=idades_dependentes)
    else:
        return "Erro: Dados do titular não encontrados."

@app.route('/resumo', methods=['POST'])
def resumo_cadastro():
    titular = request.form.to_dict()
    dependentes = []
    i = 1
    while True:
        nome_dependente = request.form.get(f'dependente_nome_{i}')
        if nome_dependente:
            dependente = {
                'nome': nome_dependente,
                'sexo': request.form.get(f'sexo_dependente_{i}'),
                'cpf': request.form.get(f'dependente_cpf_{i}'),
                'dt_nascimento': request.form.get(f'dependente_nasc_{i}'),
                'parentesco': request.form.get(f'dependente_parentesco_{i}'),
                'idade': int(request.form.get(f'idade_dependente_{i}'))
            }
            dependentes.append(dependente)
            i += 1
        else:
            break

    idade_titular = int(request.form['idade_titular'])
    codigo_contrato = titular['cod_contrato']

    valor_titular, descricao_titular = obter_preco(codigo_contrato, idade_titular)
    valores_dependentes = []
    total = valor_titular if valor_titular else 0

    for dependente in dependentes:
        valor_dependente, descricao_dependente = obter_preco(codigo_contrato, dependente['idade'])
        valores_dependentes.append({'nome': dependente['nome'], 'valor': valor_dependente, 'descricao': descricao_dependente})
        if valor_dependente:
            total += valor_dependente

    return render_template('resumo_cadastro.html', titular=titular, idade_titular=idade_titular, valor_titular=valor_titular, descricao_titular=descricao_titular, dependentes=dependentes, valores_dependentes=valores_dependentes, total=total)

@app.route('/salvar_csv', methods=['POST'])
def salvar_csv():
    titular = request.form.to_dict()
    dependentes_data = []
    i = 1
    while True:
        nome_dependente = request.form.get(f'dependente_nome_{i}')
        if nome_dependente:
            dependente = {
                'Nome Dependente': nome_dependente,
                'Sexo Dependente': request.form.get(f'sexo_dependente_{i}'),
                'CPF Dependente': request.form.get(f'dependente_cpf_{i}'),
                'Data de Nascimento Dependente': request.form.get(f'dependente_nasc_{i}'),
                'Parentesco': request.form.get(f'dependente_parentesco_{i}'),
                'Idade Dependente': request.form.get(f'idade_dependente_{i}'),
                'Valor Dependente': request.form.get(f'valor_dependente_{i}'),
                'Descricao Dependente': request.form.get(f'descricao_dependente_{i}')
            }
            dependentes_data.append(dependente)
            i += 1
        else:
            break

    dados_para_csv = [
        {
            'Código do Contrato': titular['cod_contrato'],
            'Código do Beneficiário': titular['cod_beneficiario'],
            'Titular': titular['titular'],
            'Sexo Titular': titular['sexo_titular'],
            'CPF/CNPJ': titular['cpf_cnpj'],
            'Data de Nascimento': titular['dt_nascimento'],
            'Número da Conta Corrente': titular['num_conta_corrente'],
            'Número de Telefone': titular['num_telefone'],
            'UF': titular['uf'],
            'Cidade': titular['cidade'],
            'Endereço': titular['endereco'],
            'Data do Contrato': titular['dt_contrato'],
            'Idade Titular': request.form['idade_titular'],
            'Valor Titular': request.form['valor_titular'],
            'Descricao Titular': request.form['descricao_titular'],
            'Total': request.form['total']
        }
    ]

    for dep in dependentes_data:
        dados_para_csv.append({
            'Código do Contrato': titular['cod_contrato'],
            'Código do Beneficiário': '',
            'Titular': titular['titular'],
            'Sexo Titular': '',
            'CPF/CNPJ': dep['CPF Dependente'],
            'Data de Nascimento': dep['Data de Nascimento Dependente'],
            'Número da Conta Corrente': '',
            'Número de Telefone': '',
            'UF': '',
            'Cidade': '',
            'Endereço': '',
            'Data do Contrato': titular['dt_contrato'],
            'Idade Titular': dep['Idade Dependente'],
            'Valor Titular': dep['Valor Dependente'],
            'Descricao Titular': dep['Descricao Dependente'],
            'Total': ''
        })

    df = pd.DataFrame(dados_para_csv)
    df.to_csv(ARQUIVO_CSV_FINAL, index=False, encoding='utf-8')
    return "Dados salvos com sucesso no arquivo CSV!"

if __name__ == '__main__':
    app.run(debug=True)