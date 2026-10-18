import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
  context.subscriptions.push(
    vscode.commands.registerCommand('equilex.generatePrivacyPolicy', async () => {
      const company = await vscode.window.showInputBox({ prompt: 'Company name for the privacy policy' });
      const product = await vscode.window.showInputBox({ prompt: 'Product name' });
      const jurisdiction = await vscode.window.showInputBox({ prompt: 'Jurisdiction (e.g. Global)' });
      if (!company || !product) {
        vscode.window.showWarningMessage('Company and product names are required.');
        return;
      }
      const template = `# Privacy Policy\n\n${company} respects your privacy...`;
      const editor = vscode.window.activeTextEditor;
      if (editor) {
        editor.edit((editBuilder) => editBuilder.insert(editor.selection.active, template));
        vscode.window.showInformationMessage('EquiLex privacy policy template inserted.');
      } else {
        vscode.window.showInformationMessage('No active editor open to insert the policy.');
      }
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('equilex.validateTOS', async () => {
      const editor = vscode.window.activeTextEditor;
      if (!editor) {
        vscode.window.showWarningMessage('Open a TOS file in the editor first.');
        return;
      }
      const content = editor.document.getText(editor.selection.isEmpty ? undefined : editor.selection);
      if (!content) {
        vscode.window.showWarningMessage('No content selected or available.');
        return;
      }
      vscode.window.showInformationMessage('EquiLex TOS validator would analyze the current content.');
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('equilex.openCopilotGuide', async () => {
      const uri = vscode.Uri.file(vscode.workspace.workspaceFolders?.[0].uri.fsPath + '/copilot_integration.md');
      vscode.window.showTextDocument(uri);
    })
  );
}

export function deactivate() {}
