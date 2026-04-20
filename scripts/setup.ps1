# ═══════════════════════════════════════════════════════════════
# CEO Data Agent - Quick Setup Script (PowerShell)
# ═══════════════════════════════════════════════════════════════

<#
.SYNOPSIS
    Sets up the CEO Data Agent demo environment

.DESCRIPTION
    This script:
    1. Deploys Azure resources (AI Services, Storage, Key Vault)
    2. Generates demo data
    3. Uploads data to storage
    4. Provides next steps for Fabric configuration

.PARAMETER ResourceGroupName
    Name of the Azure resource group (will be created)

.PARAMETER Location
    Azure region (default: westeurope)

.EXAMPLE
    .\setup.ps1 -ResourceGroupName "rg-ceo-demo" -Location "westeurope"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroupName,
    
    [string]$Location = "westeurope",
    
    [switch]$SkipAzureDeployment,
    
    [switch]$SkipDataGeneration
)

$ErrorActionPreference = "Stop"
$scriptRoot = $PSScriptRoot

Write-Host @"
═══════════════════════════════════════════════════════════════
  CEO Data Agent - Quick Setup
═══════════════════════════════════════════════════════════════
"@ -ForegroundColor Cyan

# ═══════════════════════════════════════
# Prerequisites Check
# ═══════════════════════════════════════

Write-Host "`n📋 Checking prerequisites..." -ForegroundColor Yellow

# Check Azure CLI
try {
    $azVersion = az version | ConvertFrom-Json
    Write-Host "  ✅ Azure CLI: $($azVersion.'azure-cli')" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Azure CLI not found. Install from: https://aka.ms/installazurecliwindows" -ForegroundColor Red
    exit 1
}

# Check Python
try {
    $pyVersion = python --version 2>&1
    Write-Host "  ✅ Python: $pyVersion" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Python not found. Install from: https://python.org" -ForegroundColor Red
    exit 1
}

# Check Azure login
$account = az account show 2>&1 | ConvertFrom-Json
if ($LASTEXITCODE -ne 0) {
    Write-Host "`n🔐 Please log in to Azure..." -ForegroundColor Yellow
    az login
    $account = az account show | ConvertFrom-Json
}

Write-Host "  ✅ Azure Account: $($account.name)" -ForegroundColor Green

# ═══════════════════════════════════════
# Step 1: Deploy Azure Resources
# ═══════════════════════════════════════

if (-not $SkipAzureDeployment) {
    Write-Host "`n🚀 Step 1: Deploying Azure resources..." -ForegroundColor Yellow
    
    # Create resource group
    Write-Host "  Creating resource group: $ResourceGroupName"
    az group create --name $ResourceGroupName --location $Location | Out-Null
    
    # Deploy template
    $templatePath = Join-Path $scriptRoot "..\infra\azuredeploy.json"
    
    Write-Host "  Deploying ARM template (this may take 3-5 minutes)..."
    $deployment = az deployment group create `
        --resource-group $ResourceGroupName `
        --template-file $templatePath `
        --query "properties.outputs" | ConvertFrom-Json
    
    Write-Host "  ✅ Azure resources deployed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Resources created:" -ForegroundColor Cyan
    Write-Host "    • Storage Account: $($deployment.storageAccountName.value)"
    Write-Host "    • Key Vault: $($deployment.keyVaultName.value)"
    Write-Host "    • AI Services: $($deployment.aiServicesName.value)"
    
    # Store outputs for later use
    $storageAccountName = $deployment.storageAccountName.value
    $aiEndpoint = $deployment.aiServicesEndpoint.value
} else {
    Write-Host "`n⏭️ Step 1: Skipping Azure deployment" -ForegroundColor Yellow
}

# ═══════════════════════════════════════
# Step 2: Generate Demo Data
# ═══════════════════════════════════════

if (-not $SkipDataGeneration) {
    Write-Host "`n📊 Step 2: Generating demo data..." -ForegroundColor Yellow
    
    # Install Python dependencies
    Write-Host "  Installing Python dependencies..."
    pip install pandas numpy -q
    
    # Run data generator
    $dataScript = Join-Path $scriptRoot "..\data\generate_data.py"
    Write-Host "  Running data generator..."
    python $dataScript
    
    Write-Host "  ✅ Demo data generated!" -ForegroundColor Green
} else {
    Write-Host "`n⏭️ Step 2: Skipping data generation" -ForegroundColor Yellow
}

# ═══════════════════════════════════════
# Step 3: Upload Data to Storage
# ═══════════════════════════════════════

if (-not $SkipAzureDeployment) {
    Write-Host "`n☁️ Step 3: Uploading data to Azure Storage..." -ForegroundColor Yellow
    
    $outputDir = Join-Path $scriptRoot "..\data\output"
    
    $csvFiles = Get-ChildItem -Path $outputDir -Filter "*.csv"
    foreach ($file in $csvFiles) {
        Write-Host "  Uploading $($file.Name)..."
        az storage blob upload `
            --account-name $storageAccountName `
            --container-name "demo-data" `
            --name $file.Name `
            --file $file.FullName `
            --auth-mode login | Out-Null
    }
    
    Write-Host "  ✅ Data uploaded!" -ForegroundColor Green
}

# ═══════════════════════════════════════
# Summary & Next Steps
# ═══════════════════════════════════════

Write-Host @"

═══════════════════════════════════════════════════════════════
  ✅ SETUP COMPLETE
═══════════════════════════════════════════════════════════════

📋 Next Steps:

1. FABRIC WORKSPACE
   - Go to: https://app.fabric.microsoft.com
   - Create workspace: CEO-Demo-StreamFlow
   - Enable Fabric trial if needed

2. LAKEHOUSE
   - Create Lakehouse: lh_streamflow
   - Upload CSV files from: data/output/

3. SEMANTIC MODEL
   - Create Direct Lake semantic model
   - Copy DAX measures from: fabric/semantic-model/measures.dax

4. POWER BI
   - Create reports connected to semantic model
   - Apply theme: powerbi/theme/streamflow-theme.json

5. COPILOT STUDIO
   - Create new agent: CEO Data Agent
   - Connect to Fabric semantic model
   - Import topics from: copilot-studio/agent-topics.yaml

📚 Full documentation: docs/SETUP.md

"@ -ForegroundColor Cyan

Write-Host "🎉 Ready to build your CEO Data Agent!" -ForegroundColor Green
