function mostrarDependentes() {
    const valor = document.getElementById('tem_dependente').value;
    document.getElementById('dependentes_container').style.display = valor === 'sim' ? 'block' : 'none';
}

function atualizaTitularNosDependentes() {
    const nomeTitular = document.getElementById('titular').value;
    const campos = document.querySelectorAll('.campo-titular-dependente');
    campos.forEach(campo => campo.value = nomeTitular);
}

function atualizaContratoNosDependentes() {
    const codContrato = document.getElementById('cod_contrato').value;
    const campos = document.querySelectorAll('.campo-contrato-dependente');
    campos.forEach(campo => campo.value = codContrato);
}

function adicionarDependente() {
    const container = document.getElementById('lista_dependentes');
    const index = container.children.length + 1;
    const nomeTitular = document.getElementById('titular').value;
    const codContrato = document.getElementById('cod_contrato').value;

    const html = `
    <div class="dependente">
        <strong>Dependente ${index}</strong><br>
        <div class="field"><label>Nome do Titular: <input type="text" class="campo-titular-dependente" value="${nomeTitular}" readonly></label></div>
        <div class="field"><label>Código do Contrato: <input type="text" class="campo-contrato-dependente" value="${codContrato}" readonly></label></div>
        <div class="field"><label>Código do Beneficiário: <input type="text" name="dependente_cod_benef_${index}"></label></div>
        <div class="field"><label>Nome: <input type="text" name="dependente_nome_${index}" required></label></div>
        <div class="field"><label>Sexo do Dependente: <select name="sexo_dependente_${index}">
            <option value="">Selecione</option>
            <option value="masculino">Masculino</option>
            <option value="feminino">Feminino</option>
            <option value="outro">Outro</option>
        </select></label></div>
        <div class="field"><label>CPF/CNPJ: <input type="text" name="dependente_cpf_${index}"></label></div>
        <div class="field"><label>Data de Nascimento: <input type="date" name="dependente_nasc_${index}" class="data-input" required></label></div>
        <div class="field">
            <label>Parentesco:
                <select name="dependente_parentesco_${index}">
                    <option value="">Selecione</option>
                    <option value="Filho(a)">Filho(a)</option>
                    <option value="Cônjuge">Cônjuge</option>
                    <option value="Enteado(a)">Enteado(a)</option>
                    <option value="Outros">Outros</option>
                </select>
            </label>
        </div>
    </div>
    `;
    container.insertAdjacentHTML('beforeend', html);
}

function formatarDataParaExibir(dataISO) {
    if (!dataISO) return "";
    const data = new Date(dataISO);
    const dia = String(data.getDate()).padStart(2, '0');
    const mes = String(data.getMonth() + 1).padStart(2, '0'); // Meses começam em 0
    const ano = data.getFullYear();
    return `${dia}/${mes}/${ano}`;
}

function aplicarFormatoDataExibicao() {
    document.addEventListener('DOMContentLoaded', function() {
        const elementosComData = document.querySelectorAll('[data-date-iso]');
        elementosComData.forEach(elemento => {
            const dataISO = elemento.getAttribute('data-date-iso');
            elemento.textContent = formatarDataParaExibir(dataISO);
        });

        // Aplica a classe 'data-input' a todos os campos de data gerados dinamicamente
        const camposData = document.querySelectorAll('#lista_dependentes input[type="date"]');
        camposData.forEach(campo => campo.classList.add('data-input'));
    });
}

function formatarDataParaEnviar(dataISO) {
    if (!dataISO) return "";
    return dataISO; // Mantém no formato ISO para o backend
}

function formatarDatasNosInputs(formId) {
    const form = document.getElementById(formId);
    if (!form) return;
    const inputs = form.querySelectorAll('input[type="hidden"]');

    inputs.forEach(input => {
        if (input.name.includes('dt_nascimento') || input.name.includes('dt_contrato') || input.name.includes('dependente_nasc')) {
            input.value = formatarDataParaEnviar(input.value);
        }
    });
}

function formatarDatasSalvarExcel() {
    formatarDatasNosInputs('form_salvar_excel');
    document.getElementById('form_salvar_excel').submit();
}

function formatarDatasSalvarCSV() {
    formatarDatasNosInputs('form_salvar_csv');
    document.getElementById('form_salvar_csv').submit();
}
