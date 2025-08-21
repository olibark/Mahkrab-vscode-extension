//makes sure that user has these "requirements"
const vscode = require('vscode'); 
const cp = require('child_process');
const path = require('path');

function activate(context) {
  console.log("MahkrabMaker activated");
  // Reconfigures when focus is switched to a C file
  context.subscriptions.push(
    vscode.window.onDidChangeActiveTextEditor(activeFile => {
      if (isC(activeFile?.document)) { // uses isC function to fdind whether current file is c
        console.log("MahkrabMaker: active editor changed to C file");
        void configure();
      }
    })
  );

  // Reconfigure when saving a cfile to local
  context.subscriptions.push(
    vscode.workspace.onDidSaveTextDocument(doc => {
      if (isC(doc)) {
        console.log("MahkrabMaker: C file saved");
        void configure();
      }
    })
  );

  // Configure immediately if the current editor is a C file
  if (isC(vscode.window.activeTextEditor?.document)) {
    console.log("MahkrabMaker: initial configure on activation (C file already active)");
    void configure();
  }
}
//returns a bool if file is c and has .c extension from the doc
function isC(doc) {
  if (!doc) return false;
  return doc.languageId === 'c' || doc.fileName?.endsWith('.c');
}
//uses async (and await) to allow btoh processes to run simultanously(asyncronous)
async function configure() {
  const activeFile = vscode.window.activeTextEditor;
  //if file is not c then configure is not called for this cycle
  if (!activeFile || !isC(activeFile.document)) {
    console.log("MahkrabMaker: configure skipped (no active C editor)");
    return;
  }

  const doc = activeFile.document;
  const ws = vscode.workspace.getWorkspaceFolder(doc.uri);
  const cwd = ws ? ws.uri.fsPath : path.dirname(doc.fileName);

  //reads the setting in the extension for where python is installed/or command to access(e.g. python, python3, users/bin/python)
  const cfg = vscode.workspace.getConfiguration('mahkrab');
  const python = cfg.get('pythonPath') || 'python';

  //finds where to run the "main.py" file from
  const scriptPath = path.join(__dirname, 'main.py');

  //debugging locatinos necessary for extension
  console.log("MahkrabMaker: preparing to call Python: ");
  console.log("  python     =", python);
  console.log("  scriptPath =", scriptPath);
  console.log("  activeFile =", doc.fileName);
  console.log("  cwd        =", cwd);
  let out;
  try {
    out = cp.spawnSync(python, [scriptPath, '--file', doc.fileName, '--cwd', cwd], {
      cwd,
      encoding: 'utf8'
    });

    //shows the returned output, error, and status
    console.log("MahkrabMaker: python stdout:\n\n\n", out.stdout);
    console.log("\n\nMahkrabMaker: python stderr:", out.stderr);
    if (out.status == 0) {
      console.log("MahkrabMaker: python status: good")
    }
    else {
      console.log("MahkrabMaker: python status: error")
    }
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
    vscode.window.showErrorMessage(
      `MahkrabMaker: main.py did not return valid JSON: ${e.message}`
    );
    vscode.window.showInformationMessage('MahkrabMaker: check "Extension Host" output for stdout/stderr details.');
    return;
  }

  const full = String(payload?.full || '').trim();
  if (!full) {
    return vscode.window.showErrorMessage('MahkrabMaker: main.py did not include a "full" command.');
  }

  //update code runner settings
  const codeRunner = vscode.workspace.getConfiguration('code-runner');
  const current = codeRunner.get('executorMap') || {};
  const updated = { ...current, c: full };

  const target = vscode.workspace.workspaceFolders?.length
    ? vscode.ConfigurationTarget.Workspace
    : vscode.ConfigurationTarget.Global;

  try {
    await codeRunner.update('executorMap', updated, target);
    await codeRunner.update('runInTerminal', true, target);
    console.log("MahkrabMaker: Code Runner executorMap.c updated");
    vscode.window.showInformationMessage('MahkrabMaker: Code Runner command updated for C.');
  } catch (e) {
    vscode.window.showErrorMessage(`MahkrabMaker: failed to update Code Runner settings: ${e.message}`);
  }
}

function deactivate() {}

module.exports = { activate, deactivate };
