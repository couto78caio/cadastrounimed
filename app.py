from flask import Flask, render_template, request, send_file
import pandas as pd
from datetime import datetime
import io
import re

app = Flask(__name__)

TABELA_PRECOS_PATH = 'tabela_precos.csv'

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
        tabela_precos = pd.read_csv(TABELA_PRECOS_PATH, dtype={'codigo_contrato': str})
        faixa = tabela_precos[(tabela_precos['codigo_contrato'].str.strip() == codigo_contrato.strip()) & (tabela_precos['idade_min'] <= idade) & (tabela_precos['idade_max'] >= idade)]
        if not faixa.empty:
            return faixa['valor_mensal'].iloc[0], faixa['descricao'].iloc[0]
        return None, None
    except FileNotFoundError:
        return None, None

@app.route('/', methods=['GET', 'POST'])
def formulario_inicial():
    return render_template('formulario_inicial.html')

@app.route('/idades', methods=['POST'])
def exibir_idades():
    titular_data = {
        'cod_contrato': request.form['cod_contrato'],
        'cod_beneficiario': request.form.get('cod_beneficiario', ''),
        'titular': request.form['titular'],
        'sexo_titular': request.form.get('sexo_titular', ''),
        'cpf_cnpj': request.form['cpf_cnpj'],
        'dt_nascimento': request.form['dt_nascimento'],
        'num_conta_corrente': request.form.get('num_conta_corrente', ''),
        'num_telefone': request.form.get('num_telefone', ''),
        'uf': request.form.get('uf', ''),
        'cidade': request.form.get('cidade', ''),
        'endereco': request.form.get('endereco', ''),
        'dt_contrato': request.form['dt_contrato']
    }
    dependentes_data = []
    i = 1
    while True:
        nome_dependente = request.form.get(f'dependente_nome_{i}')
        if nome_dependente:
            dependente = {
                'nome': nome_dependente,
                'cod_beneficiario': request.form.get(f'dependente_cod_beneficiario_{i}', ''),
                'sexo_dependente': request.form.get(f'dependente_sexo_{i}'),
                'cpf': request.form.get(f'dependente_cpf_{i}'),
                'dt_nascimento': request.form.get(f'dependente_nasc_{i}'),
                'parentesco': request.form.get(f'dependente_parentesco_{i}')
            }
            dependentes_data.append(dependente)
            i += 1
        else:
            break

    idade_titular = calcular_idade(titular_data['dt_nascimento'])
    valor_titular, descricao_titular = obter_preco(titular_data['cod_contrato'], idade_titular)

    idades_dependentes = []
    valores_dependentes_list = []
    for index, dependente in enumerate(dependentes_data):
        idade_dependente = calcular_idade(dependente['dt_nascimento'])
        valor_dependente, descricao_dependente = obter_preco(titular_data['cod_contrato'], idade_dependente)
        idades_dependentes.append({
            'nome': dependente['nome'],
            'idade': idade_dependente,
            'index': index + 1,
            'dt_nascimento': dependente['dt_nascimento'],
            'cod_beneficiario': dependente['cod_beneficiario'],
            'cpf': dependente['cpf'],
            'parentesco': dependente['parentesco'],
            'sexo_dependente': dependente['sexo_dependente']
        })
        valores_dependentes_list.append({'nome': dependente['nome'], 'valor': valor_dependente, 'descricao': descricao_dependente, 'index': index + 1})

    return render_template('exibir_idades.html',
                           titular=titular_data,
                           idade_titular=idade_titular,
                           valor_titular=valor_titular,
                           descricao_titular=descricao_titular,
                           dependentes=idades_dependentes,
                           valores_dependentes=valores_dependentes_list,
                           tabela_precos_json=pd.read_csv(TABELA_PRECOS_PATH, dtype={'codigo_contrato': str}).to_dict(orient='records'))

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
                'cod_beneficiario': request.form.get(f'dependente_cod_beneficiario_{i}', ''),
                'sexo': request.form.get(f'sexo_dependente_{i}'), # CORREÇÃO ANTERIOR
                'cpf': request.form.get(f'dependente_cpf_{i}'),
                'dt_nascimento': request.form.get(f'dependente_nasc_{i}'),
                'parentesco': request.form.get(f'dependente_parentesco_{i}'),
                'idade': request.form.get(f'idade_dependente_{i}')
            }
            dependentes.append(dependente)
            i += 1
        else:
            break

    print("Conteúdo da variável 'dependentes' em /resumo:", dependentes) # Mantenha esta linha para debug

    idade_titular = int(request.form['idade_titular'])
    codigo_contrato = titular['cod_contrato']

    valor_titular, descricao_titular = obter_preco(codigo_contrato, idade_titular)
    valores_dependentes = []
    for dependente in dependentes:
        idade_dependente = int(dependente['idade'])
        valor_dependente, descricao_dependente = obter_preco(codigo_contrato, idade_dependente)
        valores_dependentes.append({'nome': dependente['nome'], 'valor': valor_dependente, 'descricao': descricao_dependente, 'sexo': dependente['sexo']}) # Adicionando o sexo aqui
        print(f"Dados do dependente {dependente['nome']} em /resumo:", valores_dependentes[-1]) # Debug para o sexo
    total = valor_titular if valor_titular else 0
    for valor_dep in [dep['valor'] for dep in valores_dependentes if dep['valor'] is not None]:
        total += valor_dep

    return render_template('resumo_cadastro.html', titular=titular, idade_titular=idade_titular, valor_titular=valor_titular, descricao_titular=descricao_titular, dependentes=dependentes, valores_dependentes=valores_dependentes, total=total)

@app.route('/salvar_csv', methods=['POST'])
def salvar_csv():
    titular = request.form.to_dict()
    dependentes_data = []
    i = 1
    dependentes_nomes = []
    dependentes_cpfs = []
    while True:
        nome_dependente = request.form.get(f'dependente_nome_{i}')
        if nome_dependente:
            dependente = {
                'Nome Dependente': nome_dependente,
                'Código Beneficiário Dependente': request.form.get(f'dependente_cod_beneficiario_{i}', ''),
                'Sexo Dependente': request.form.get(f'sexo_dependente_{i}'),
                'CPF Dependente': request.form.get(f'dependente_cpf_{i}'),
                'Data de Nascimento Dependente': request.form.get(f'dependente_nasc_{i}'),
                'Parentesco': request.form.get(f'dependente_parentesco_{i}'),
                'Idade Dependente': request.form.get(f'idade_dependente_{i}'),
                'Valor Dependente': request.form.get(f'valor_dependente_{i}'),
                'Descricao Dependente': request.form.get(f'descricao_dependente_{i}')
            }
            dependentes_data.append(dependente)
            dependentes_nomes.append(nome_dependente)
            dependentes_cpfs.append(request.form.get(f'dependente_cpf_{i}', ''))
            i += 1
        else:
            break

    print("Conteúdo de dependentes_data em /salvar_csv:", dependentes_data)

    nome_titular = titular['titular']
    sexo_titular = titular.get('sexo_titular', '')
    cpf_titular = titular['cpf_cnpj']
    dt_nascimento_titular = titular['dt_nascimento']
    num_conta_corrente_titular = titular.get('num_conta_corrente', '')
    num_telefone_titular = titular.get('num_telefone', '')
    uf_titular = titular.get('uf', '')
    cidade_titular = titular.get('cidade', '')
    endereco_titular = titular.get('endereco', '')
    data_contrato_titular = titular['dt_contrato']
    cod_contrato = titular['cod_contrato']
    cod_beneficiario_titular = titular.get('cod_beneficiario', '')
    descricao_titular = request.form['descricao_titular']
    total_valor = request.form.get('total', '')

    dados_para_csv = [
        {
            'CATEGORIA': 'Titular',
            'TITULAR': nome_titular,
            'COD_CONTRATO': cod_contrato,
            'COD_BENEFICIARIO': cod_beneficiario_titular,
            'SEXO': sexo_titular,
            'CPF_GERAL': cpf_titular,
            'CPF_TITULAR': cpf_titular,
            'DT_NSCMT': dt_nascimento_titular,
            'N_CONTA_CORRENTE': num_conta_corrente_titular,
            'N_TEL': num_telefone_titular,
            'ENDERECO': f"{endereco_titular}-{cidade_titular}-{uf_titular}",
            'DT_INCLS': data_contrato_titular,
            'IDADE': request.form['idade_titular'],
            'VL_PLANO': request.form['valor_titular'],
            'DESC_PLANO': descricao_titular,
            'PARENTESCO': 'Titular',
            'DEPENDENTES': '-'.join(dependentes_nomes) if dependentes_nomes else '',
            'CPF_DEPEND': '-'.join(dependentes_cpfs) if dependentes_cpfs else '',
            'CIDADE': cidade_titular,
            'Total': total_valor
        }
    ]
    
    for dep in dependentes_data:
        dados_para_csv.append({
            'CATEGORIA': 'Dependente',
            'TITULAR': nome_titular,
            'COD_CONTRATO': cod_contrato,
            'COD_BENEFICIARIO': dep.get('Código Beneficiário Dependente', ''),
            'SEXO': dep.get('Sexo Dependente'),
            'CPF_GERAL': dep['CPF Dependente'],
            'CPF_TITULAR': '',
            'DT_NSCMT': dep['Data de Nascimento Dependente'],
            'N_CONTA_CORRENTE': num_conta_corrente_titular,
            'N_TEL': num_telefone_titular,
            'ENDERECO': f"{endereco_titular}-{cidade_titular}-{uf_titular}",
            'DT_INCLS': data_contrato_titular,
            'IDADE': dep['Idade Dependente'],
            'VL_PLANO': dep['Valor Dependente'],
            'DESC_PLANO': dep['Descricao Dependente'],
            'PARENTESCO': dep['Parentesco'],
            'DEPENDENTES': dep['Nome Dependente'],
            'CPF_DEPEND': dep['CPF Dependente'],
            'CIDADE': cidade_titular,
            'Total': ''
        })

    df = pd.DataFrame(dados_para_csv)

    # Limpar o nome do titular para usar no nome do arquivo (remover caracteres especiais e espaços)
    nome_titular_limpo = re.sub(r'[^a-zA-Z0-9]', '_', titular['titular']).strip('_')
    codigo_contrato = titular['cod_contrato'].strip()
    nome_arquivo = f"cadastro_{nome_titular_limpo}_contrato_{codigo_contrato}.csv"

    # Salvar o DataFrame em memória (BytesIO)
    csv_data = io.BytesIO()
    df.to_csv(csv_data, index=False, encoding='utf-8')
    csv_data.seek(0)

    # Enviar o arquivo como resposta para download com o novo nome
    return send_file(
        csv_data,
        mimetype='text/csv',
        download_name=nome_arquivo,
        as_attachment=True
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

