# PowerShell script to copy project to WSL and set up the environment

Write-Host "=== Copying Project to WSL ===" -ForegroundColor Green

# Copy project files to WSL
$sourceDir = "C:\Users\Philip.Rubbo\prodeng-md-to-confluence-2"
$wslHomeDir = wsl pwd
$targetDir = "$wslHomeDir/prodeng-md-to-confluence-2"

Write-Host "Copying files from Windows to WSL..." -ForegroundColor Yellow
wsl mkdir -p prodeng-md-to-confluence-2
wsl cp -r /mnt/c/Users/Philip.Rubbo/prodeng-md-to-confluence-2/* ./prodeng-md-to-confluence-2/

Write-Host "Making shell scripts executable..." -ForegroundColor Yellow
wsl chmod +x ./prodeng-md-to-confluence-2/setup-linux.sh
wsl chmod +x ./prodeng-md-to-confluence-2/test-linux.sh
wsl chmod +x ./prodeng-md-to-confluence-2/wsl-setup.sh

Write-Host "Project copied successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Open WSL terminal in VS Code (Ctrl+Shift+P -> 'Remote-WSL: New WSL Window')" -ForegroundColor White
Write-Host "2. Navigate to project: cd ~/prodeng-md-to-confluence-2" -ForegroundColor White
Write-Host "3. Run setup script: ./wsl-setup.sh" -ForegroundColor White
Write-Host "4. Or run the Linux setup: ./setup-linux.sh" -ForegroundColor White
