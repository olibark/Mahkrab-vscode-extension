// extension.js
const vscode = require('vscode');
const cp = require('child_process');
const path = require('path');

function activate(context) {
  console.log("MahkrabMaker activated");
  // Reconfigure when you switch to a C file
  context.subscriptions.push(
    vscode.window.onDidChangeActiveTextEditor(ed => {
      if (isC(ed?.document)) { void configure(); }
    })
  );

  // Reconfigure when you save a C file
  context.subscriptions.push(
    vscode.workspace.onDidSaveTextDocument(doc => {
      if (isC(doc)) { void configure(); }
    })
  );

  // Configure immediately if the current editor is a C file
  if (isC(vscode.window.activeTextEditor?.document)) {
    void configure();
  }
}

function isC(doc) {
  if (!doc) return false;
  return doc.languageId === 'c' || doc.fileName?.endsWith('.c');
}

async function configure() {
  const ed = vscode.window.activeTextEditor;
  if (!ed || !isC(ed.document)) return;

  const doc = ed.document;
  const ws = vscode.workspace.getWorkspaceFolder(doc.uri);
  const cwd = ws ? ws.uri.fsPath : path.dirname(doc.fileName);

  // Read interpreter setting
  const cfg = vscode.workspace.getConfiguration('mahkrab');
  const python = cfg.get('pythonPath') || 'python';

  // main.py sits next to this file
  const scriptPath = path.join(__dirname, 'main.py');

  // Run Python to get { full: "compile && run" }
  let out;
  try {
    out = cp.spawnSync(python, [scriptPath, '--file', doc.fileName, '--cwd', cwd], {
      cwd,
      encoding: 'utf8'
    });
  } catch (e) {
    return vscode.window.showErrorMessage(`MahkrabMaker: failed to start Python (${python}): ${e.message}`);
  }

  if (out.error) {
    return vscode.window.showErrorMessage(`MahkrabMaker: Python error: ${out.error.message}`);
  }
  if (out.status !== 0) {
    const stderr = (out.stderr || '').trim();
    return vscode.window.showErrorMessage(`MahkrabMaker: main.py exited with ${out.status}${stderr ? `\n${stderr}` : ''}`);
  }

  let payload;
  try {
    payload = JSON.parse(out.stdout);
  } catch (e) {
    return vscode.window.showErrorMessage(
      `MahkrabMaker: main.py did not return valid JSON: ${e.message}\nSTDOUT:\n${out.stdout}`
    );
  }

  const full = String(payload?.full || '').trim();
  if (!full) {
    return vscode.window.showErrorMessage('MahkrabMaker: main.py did not include a "full" command.');
  }

  // Update Code Runner settings
  const codeRunner = vscode.workspace.getConfiguration('code-runner');
  const current = codeRunner.get('executorMap') || {};
  const updated = { ...current, c: full };

  const target = vscode.workspace.workspaceFolders?.length
    ? vscode.ConfigurationTarget.Workspace
    : vscode.ConfigurationTarget.Global;

  try {
    await codeRunner.update('executorMap', updated, target);
    await codeRunner.update('runInTerminal', true, target);
    vscode.window.showInformationMessage('MahkrabMaker: Code Runner command updated for C.');
  } catch (e) {
    vscode.window.showErrorMessage(`MahkrabMaker: failed to update Code Runner settings: ${e.message}`);
  }
}

function deactivate() {}

module.exports = { activate, deactivate };
