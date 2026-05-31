const projectId = new URLSearchParams(window.location.search).get('project_id');

const workspace = Blockly.inject('blocklyDiv', {
    toolbox: document.getElementById('toolbox'),
    renderer: 'zelos',
    trashcan: true,
    scrollbars: true
});

const pythonCodeField = document.getElementById('pythonCode');

function getWorkspaceXml() {
    return Blockly.Xml.domToText(Blockly.Xml.workspaceToDom(workspace));
}

function updateGeneratedCode() {
    pythonCodeField.value = Blockly.Python.workspaceToCode(workspace) || '# Connect blocks to generate code...';
}

function markProjectSaved() {
    if (!projectId) return Promise.resolve();

    return fetch(`/projects/mark-saved/${projectId}`, {
        method: 'POST'
    });
}

function saveWorkspace(silent = false) {
    fetch('/blockly/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ workspace_xml: getWorkspaceXml() })
    })
    .then(r => r.json())
    .then(d => markProjectSaved().then(() => d))
    .then(d => { if (!silent) alert(d.message); })
    .catch(e => { if (!silent) alert('Opslaan mislukt: ' + e.message); });
}

function loadWorkspace() {
    fetch('/blockly/load')
        .then(r => r.json())
        .then(d => {
            workspace.clear();
            if (d.workspace_xml) {
                Blockly.Xml.domToWorkspace(Blockly.utils.xml.textToDom(d.workspace_xml), workspace);
            }
            updateGeneratedCode();
        })
        .catch(e => alert('Fout bij laden: ' + e.message));
}

function clearWorkspace() {
    if (!confirm("Weet je zeker dat je alle blokken wilt verwijderen?")) return;
    workspace.clear();
    saveWorkspace(true);
}

function runTest() {
    const runBtn = document.getElementById('runBtn');
    runBtn.disabled = true;
    showResult({ message: 'Test loopt...' });

    fetch('/blockly/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ workspace_xml: getWorkspaceXml(), project_id: projectId })
    })
    .then(r => r.json())
    .then(data => {
        runBtn.disabled = false;
        showResult({
            status: data.return_code === 0 ? 'Geslaagd' : 'Gefaald',
            success: data.return_code === 0,
            output: data.output || data.fout || ''
        });
    })
    .catch(e => {
        runBtn.disabled = false;
        showResult({ status: 'Fout', success: false, output: e.message });
    });
}

function showResult({ message, status, success, output } = {}) {
    const panel = document.getElementById('testResults');
    if (message) {
        panel.innerHTML = `<p class="result-placeholder">${message}</p>`;
        return;
    }
    panel.innerHTML = `
        ${status ? `<p class="result-status ${success ? 'success' : 'error'}">${status}</p>` : ''}
        ${output ? `<textarea id="testResultsOutput" readonly>${output}</textarea>` : '<p class="result-placeholder">Geen uitvoer beschikbaar</p>'}
    `;
}

function copyCode() {
    const code = pythonCodeField.value;
    if (!code || code.includes('Connect blocks')) {
        alert('Geen code om te kopiëren. Voeg eerst blokken toe.');
        return;
    }
    navigator.clipboard.writeText(code).then(() => {
        const btn = document.getElementById('copyCodeBtn');
        btn.style.opacity = '0.5';
        setTimeout(() => btn.style.opacity = '1', 2000);
    });
}

let saveTimeout;
workspace.addChangeListener(event => {
    if (event.isUiEvent) return;
    updateGeneratedCode();
    clearTimeout(saveTimeout);
    saveTimeout = setTimeout(() => saveWorkspace(true), 2000);
});

updateGeneratedCode();
document.getElementById("clearWorkspaceBtn")?.addEventListener("click", clearWorkspace);
