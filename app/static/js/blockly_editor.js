// Blockly editor - hoofd functies

const workspace = Blockly.inject('blocklyDiv', { 
    toolbox: document.getElementById('toolbox') 
});
const pythonCodeField = document.getElementById('pythonCode');

// Get workspace XML als string
function getWorkspaceXml() {
    const xml = Blockly.Xml.workspaceToDom(workspace);
    return Blockly.Xml.domToText(xml);
}

// Update gegenereerde code display
function updateGeneratedCode() {
    const code = Blockly.Python.workspaceToCode(workspace);
    pythonCodeField.value = code || '# Connect blocks to generate code...';
}

// Luister naar workspace wijzigingen en update code
workspace.addChangeListener(function(event) {
    if (event.isUiEvent) return;
    updateGeneratedCode();
});

// Initial code generation
updateGeneratedCode();

// ===== Opslaan & Laden Workspace =====

// Save workspace naar database
function saveWorkspace() {
    fetch('/blockly/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ workspace_xml: getWorkspaceXml() })
    })
        .then(r => r.json())
        .then(d => alert(d.message))
        .catch(e => alert('Fout bij opslaan: ' + e.message));
}

// Load workspace van database
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

// ===== Test Uitvoering =====

// Voer test uit - stuur workspace naar backend
function runTest() {
    const runBtn = document.getElementById('runBtn');
    
    runBtn.disabled = true;
    runBtn.classList.add('loading');
    renderResultsPanel({ message: 'Test loopt...' });
    
    fetch('/blockly/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ workspace_xml: getWorkspaceXml() })
    })
        .then(r => r.json())
        .then(data => {
            runBtn.classList.remove('loading');
            runBtn.disabled = false;
            
            if (data.fout) {
                renderResultsPanel({
                    statusText: 'Fout',
                    statusClass: 'error',
                    output: data.fout
                });
            } else {
                const statusClass = data.return_code === 0 ? 'success' : 'error';
                const statusText = data.return_code === 0 ? 'Geslaagd' : 'Gefaald';
                renderResultsPanel({
                    statusText,
                    statusClass,
                    output: data.output
                });
            }
        })
        .catch(e => {
            runBtn.classList.remove('loading');
            runBtn.disabled = false;
            renderResultsPanel({
                statusText: 'Fout',
                statusClass: 'error',
                output: e.message
            });
        });
}


// Escape HTML special characters for safe display
function escapeHtml(value) {
    return String(value ?? '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

// Render test resultaten paneel met status en output
function renderResultsPanel({ message = '', statusText = '', statusClass = '', output = '' } = {}) {
    const resultsPanel = document.getElementById('testResults');

    if (message) {
        resultsPanel.innerHTML = `<p class="result-placeholder">${escapeHtml(message)}</p>`;
        return;
    }

    const statusMarkup = statusText
        ? `<p class="result-status ${statusClass}">${escapeHtml(statusText)}</p>`
        : '';
    const outputMarkup = output
        ? `<textarea id="testResultsOutput" readonly>${escapeHtml(output)}</textarea>`
        : '<p class="result-placeholder">Geen uitvoer beschikbaar</p>';

    resultsPanel.innerHTML = `${statusMarkup}${outputMarkup}`;
}

//  Code Copy to Clipboard

// Copy generated code to clipboard
function copyCode() {
    const code = pythonCodeField.value;
    const btn = document.getElementById('copyCodeBtn');
    
    if (!code || code.includes('Connect blocks to generate code')) {
        alert('Er is geen code om te kopieëren. Voeg blokken toe en probeer opnieuw.');
        return;
    }
    
    navigator.clipboard.writeText(code)
        .then(() => {
            btn.style.opacity = '0.5';
            
            setTimeout(() => {
                btn.style.opacity = '1';
            }, 2000);
        })
        .catch(err => {
            alert('Kan niet naar klembord kopieëren: ' + err);
        });
}
