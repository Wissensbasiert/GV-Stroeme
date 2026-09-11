param([switch]$CheckOnly)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Security
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$settingsFolder = Join-Path $env:LOCALAPPDATA 'WBP-Solutions\Gueterstroeme\Requesty'
if ($CheckOnly) {
    Write-Output ('Konfiguration vorhanden: ' + (Test-Path -LiteralPath (Join-Path $settingsFolder 'config.json')))
    Write-Output ('Verschlüsselter Schlüssel vorhanden: ' + (Test-Path -LiteralPath (Join-Path $settingsFolder 'key.dpapi')))
    exit
}
$form = New-Object System.Windows.Forms.Form
$form.Text = 'Güterströme – Requesty sicher einrichten'
$form.Size = New-Object System.Drawing.Size(660, 385)
$form.StartPosition = 'CenterScreen'
$form.FormBorderStyle = 'FixedDialog'
$form.MaximizeBox = $false
$form.MinimizeBox = $false
$form.TopMost = $true
function Add-TextField([string]$label, [int]$y, [string]$value) {
    $caption = New-Object System.Windows.Forms.Label
    $caption.Text = $label
    $caption.Location = New-Object System.Drawing.Point(20, $y)
    $caption.Size = New-Object System.Drawing.Size(180, 25)
    $form.Controls.Add($caption)
    $box = New-Object System.Windows.Forms.TextBox
    $box.Location = New-Object System.Drawing.Point(205, $y)
    $box.Size = New-Object System.Drawing.Size(410, 25)
    $box.Text = $value
    $form.Controls.Add($box)
    return $box
}
$intro = New-Object System.Windows.Forms.Label
$intro.Text = 'Der Schlüssel wird nur für dieses Windows-Konto verschlüsselt gespeichert. Es wird jetzt keine Modellanfrage gesendet.'
$intro.Location = New-Object System.Drawing.Point(20, 18)
$intro.Size = New-Object System.Drawing.Size(605, 45)
$form.Controls.Add($intro)
$keyBox = Add-TextField 'API-Schlüssel' 80 ''
$keyBox.UseSystemPasswordChar = $true
$modelBox = Add-TextField 'Modellkennung' 120 ''
$urlBox = Add-TextField 'Requesty-Basisadresse' 160 'https://router.eu.requesty.ai/v1'
$routingBox = New-Object System.Windows.Forms.CheckBox
$routingBox.Text = 'EU-Routing und Datenverarbeitung sind in Requesty für dieses Modell eingerichtet.'
$routingBox.Location = New-Object System.Drawing.Point(20, 205)
$routingBox.Size = New-Object System.Drawing.Size(605, 40)
$form.Controls.Add($routingBox)
$save = New-Object System.Windows.Forms.Button
$save.Text = 'Verschlüsselt speichern'
$save.Location = New-Object System.Drawing.Point(380, 275)
$save.Size = New-Object System.Drawing.Size(235, 35)
$form.Controls.Add($save)
$save.Add_Click({
    try {
        $base = $urlBox.Text.Trim().TrimEnd('/')
        if ($base -ne 'https://router.eu.requesty.ai/v1') {
            throw 'Bitte die dokumentierte EU-Adresse https://router.eu.requesty.ai/v1 verwenden.'
        }
        if ([string]::IsNullOrWhiteSpace($keyBox.Text) -or [string]::IsNullOrWhiteSpace($modelBox.Text)) {
            throw 'Bitte Schlüssel und die genaue Modellkennung eintragen.'
        }
        if (-not $routingBox.Checked) { throw 'Bitte die vorhandene EU-Konfiguration bestätigen.' }
        [System.IO.Directory]::CreateDirectory($settingsFolder) | Out-Null
        $acl = New-Object System.Security.AccessControl.DirectorySecurity
        $acl.SetAccessRuleProtection($true, $false)
        $currentSid = [System.Security.Principal.WindowsIdentity]::GetCurrent().User
        foreach ($sid in @($currentSid, (New-Object System.Security.Principal.SecurityIdentifier('S-1-5-18')))) {
            $rule = New-Object System.Security.AccessControl.FileSystemAccessRule($sid, 'FullControl', 'ContainerInherit,ObjectInherit', 'None', 'Allow')
            $acl.AddAccessRule($rule)
        }
        Set-Acl -LiteralPath $settingsFolder -AclObject $acl
        $keyBytes = [System.Text.Encoding]::UTF8.GetBytes($keyBox.Text.Trim())
        try {
            $encrypted = [System.Security.Cryptography.ProtectedData]::Protect($keyBytes, $null, [System.Security.Cryptography.DataProtectionScope]::CurrentUser)
            [System.IO.File]::WriteAllBytes((Join-Path $settingsFolder 'key.dpapi'), $encrypted)
        } finally {
            [Array]::Clear($keyBytes, 0, $keyBytes.Length)
            $keyBox.Clear()
        }
        $config = @{model=$modelBox.Text.Trim(); base_url=$base; eu_routing_confirmed=$true; timeout_seconds=180; max_tokens=1500}
        $utf8 = New-Object System.Text.UTF8Encoding($false)
        [System.IO.File]::WriteAllText((Join-Path $settingsFolder 'config.json'), ($config | ConvertTo-Json), $utf8)
        [System.Windows.Forms.MessageBox]::Show('Gespeichert. Codex kann den Schlüssel für den lokalen Test einlesen. Bitte im Chat kurz Bescheid geben.', 'Requesty', 'OK', 'Information') | Out-Null
        $form.Close()
    } catch {
        [System.Windows.Forms.MessageBox]::Show($_.Exception.Message, 'Einrichtung nicht abgeschlossen', 'OK', 'Error') | Out-Null
    }
})
[void]$form.ShowDialog()
$keyBox.Clear()
$form.Dispose()
