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
        <div class="field"><label>Data de Nascimento: <input type="date" name="dependente_nasc_${index}" required></label></div>
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
