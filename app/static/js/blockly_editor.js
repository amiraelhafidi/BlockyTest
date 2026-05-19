// Blockly editor - alle functies voor workspace, opslaan, laden en test uitvoering

const urlParams = new URLSearchParams(window.location.search);
const projectId = urlParams.get('project_id');

const workspace = Blockly.inject('blocklyDiv', {
    toolbox: document.getElementById('toolbox'),
    renderer: 'zelos',
    trashcan: true,
    scrollbars: true
});

const pythonCodeField = document.getElementById('pythonCode');

// Update gegenereerde code display
function updateGeneratedCode() {
    const code = Blockly.Python.workspaceToCode(workspace);
    pythonCodeField.value = code || '# Connect blocks to generate code...';
}

// Luister naar workspace wijzigingen
let saveTimeout;
workspace.addChangeListener(function(event) {
    if (event.isUiEvent) return;
    updateGeneratedCode();
    clearTimeout(saveTimeout);
    saveTimeout = setTimeout(autoSaveWorkspace, 2000);
});

updateGeneratedCode();

// Haal workspace XML op als string
function getWorkspaceXml() {
    const xml = Blockly.Xml.workspaceToDom(workspace);
    return Blockly.Xml.domToText(xml);
}

// Sla workspace op in database
function saveWorkspace() {
    fetch('/blockly/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ workspace_xml: getWorkspaceXml() })
    })
    .then(r => r.json())
    .then(d => alert(d.message))
    .catch(e => alert('Opslaan mislukt: ' + e.message));
}

// Sla automatisch op na wijziging
function autoSaveWorkspace() {
    fetch('/blockly/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ workspace_xml: getWorkspaceXml(), source: 'autosave' })
    })
    .then(r => r.json())
    .then(d => console.log(d.message))
    .catch(e => console.error('Autosave fout:', e));
}

// Laad workspace vanuit database
function loadWorkspace() {
    fetch('/blockly/load')
        .then(r => r.json())
        .then(d => {
            workspace.clear();
            if (d.workspace_xml) {
                const xml = Blockly.utils.xml.textToDom(d.workspace_xml);
                Blockly.Xml.domToWorkspace(xml, workspace);
            }
            updateGeneratedCode();
        })
        .catch(e => alert('Fout bij laden: ' + e.message));
}

// Wis de workspace en sla lege state op
function clearWorkspace() {
    if (!confirm("Weet je zeker dat je alle blokken wilt verwijderen?")) return;
    workspace.clear();
    fetch('/blockly/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ workspace_xml: getWorkspaceXml() })
    })
    .then(r => r.json())
    .then(() => alert("Alle blokken zijn verwijderd en opgeslagen."))
    .catch(e => console.error(e));
}

// Voer test uit - stuur workspace en project_id naar backend
function runTest() {
    const runBtn = document.getElementById('runBtn');
    runBtn.disabled = true;
    runBtn.classList.add('loading');
    renderResultsPanel({ message: 'Test loopt...' });

    const payload = { workspace_xml: getWorkspaceXml() };
    if (projectId) payload.project_id = projectId;

    fetch('/blockly/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(r => r.json())
    .then(data => {
        runBtn.classList.remove('loading');
        runBtn.disabled = false;
        if (data.fout) {
            renderResultsPanel({ statusText: 'Fout', statusClass: 'error', output: data.fout });
        } else {
            renderResultsPanel({
                statusText: data.return_code === 0 ? 'Geslaagd' : 'Gefaald',
                statusClass: data.return_code === 0 ? 'success' : 'error',
                output: data.output
            });
        }
    })
    .catch(e => {
        runBtn.classList.remove('loading');
        runBtn.disabled = false;
        renderResultsPanel({ statusText: 'Fout', statusClass: 'error', output: e.message });
    });
}

// Escape HTML voor veilige weergave
function escapeHtml(value) {
    return String(value ?? '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

// Render testresultaten paneel
function renderResultsPanel({ message = '', statusText = '', statusClass = '', output = '' } = {}) {
    const resultsPanel = document.getElementById('testResults');
    if (message) {
        resultsPanel.innerHTML = `<p class="result-placeholder">${escapeHtml(message)}</p>`;
        return;
    }
    const statusMarkup = statusText ? `<p class="result-status ${statusClass}">${escapeHtml(statusText)}</p>` : '';
    const outputMarkup = output
        ? `<textarea id="testResultsOutput" readonly>${escapeHtml(output)}</textarea>`
        : '<p class="result-placeholder">Geen uitvoer beschikbaar</p>';
    resultsPanel.innerHTML = `${statusMarkup}${outputMarkup}`;
}

// Kopieer gegenereerde code naar klembord
function copyCode() {
    const code = pythonCodeField.value;
    if (!code || code.includes('Connect blocks to generate code')) {
        alert('Er is geen code om te kopieëren. Voeg blokken toe en probeer opnieuw.');
        return;
    }
    navigator.clipboard.writeText(code)
        .then(() => {
            const btn = document.getElementById('copyCodeBtn');
            btn.style.opacity = '0.5';
            setTimeout(() => btn.style.opacity = '1', 2000);
        })
        .catch(err => alert('Kan niet naar klembord kopieëren: ' + err));
}

// Clear knop event listener
document.getElementById("clearWorkspaceBtn")?.addEventListener("click", clearWorkspace);