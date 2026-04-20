// ═══════════════════════════════════════════════════════════════
// CEO Data Agent - Infrastructure as Code (Bicep)
// ═══════════════════════════════════════════════════════════════
// This template deploys the Azure resources needed for the demo:
// - Azure AI Services (for GPT-4)
// - Key Vault (for secrets)
// - Storage Account (for data)
// ═══════════════════════════════════════════════════════════════

@description('Name prefix for all resources')
param projectName string = 'ceoagent'

@description('Azure region for resources')
param location string = resourceGroup().location

@description('Tags to apply to all resources')
param tags object = {
  project: 'CEO Data Agent Demo'
  environment: 'demo'
}

// ═══════════════════════════════════════
// VARIABLES
// ═══════════════════════════════════════

var uniqueSuffix = uniqueString(resourceGroup().id)
var storageAccountName = '${projectName}${uniqueSuffix}'
var keyVaultName = 'kv-${projectName}-${uniqueSuffix}'
var aiServicesName = 'ai-${projectName}-${uniqueSuffix}'
var logAnalyticsName = 'log-${projectName}'

// ═══════════════════════════════════════
// LOG ANALYTICS WORKSPACE
// ═══════════════════════════════════════

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: logAnalyticsName
  location: location
  tags: tags
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

// ═══════════════════════════════════════
// STORAGE ACCOUNT
// ═══════════════════════════════════════

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageAccountName
  location: location
  tags: tags
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
  }
}

resource blobServices 'Microsoft.Storage/storageAccounts/blobServices@2023-01-01' = {
  parent: storageAccount
  name: 'default'
}

resource dataContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  parent: blobServices
  name: 'demo-data'
  properties: {
    publicAccess: 'None'
  }
}

resource docsContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  parent: blobServices
  name: 'strategic-docs'
  properties: {
    publicAccess: 'None'
  }
}

// ═══════════════════════════════════════
// KEY VAULT
// ═══════════════════════════════════════

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  tags: tags
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    enabledForDeployment: true
    enabledForTemplateDeployment: true
    enableRbacAuthorization: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 7
  }
}

// ═══════════════════════════════════════
// AZURE AI SERVICES
// ═══════════════════════════════════════

resource aiServices 'Microsoft.CognitiveServices/accounts@2023-10-01-preview' = {
  name: aiServicesName
  location: location
  tags: tags
  kind: 'OpenAI'
  sku: {
    name: 'S0'
  }
  properties: {
    customSubDomainName: aiServicesName
    publicNetworkAccess: 'Enabled'
  }
}

// Deploy GPT-4o model
resource gpt4oDeployment 'Microsoft.CognitiveServices/accounts/deployments@2023-10-01-preview' = {
  parent: aiServices
  name: 'gpt-4o'
  properties: {
    model: {
      format: 'OpenAI'
      name: 'gpt-4o'
      version: '2024-05-13'
    }
  }
  sku: {
    name: 'Standard'
    capacity: 80
  }
}

// Deploy text-embedding model
resource embeddingDeployment 'Microsoft.CognitiveServices/accounts/deployments@2023-10-01-preview' = {
  parent: aiServices
  name: 'text-embedding-ada-002'
  dependsOn: [gpt4oDeployment]
  properties: {
    model: {
      format: 'OpenAI'
      name: 'text-embedding-ada-002'
      version: '2'
    }
  }
  sku: {
    name: 'Standard'
    capacity: 120
  }
}

// ═══════════════════════════════════════
// STORE SECRETS IN KEY VAULT
// ═══════════════════════════════════════

resource aiServicesKeySecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: keyVault
  name: 'ai-services-key'
  properties: {
    value: aiServices.listKeys().key1
  }
}

resource storageKeySecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: keyVault
  name: 'storage-key'
  properties: {
    value: storageAccount.listKeys().keys[0].value
  }
}

// ═══════════════════════════════════════
// OUTPUTS
// ═══════════════════════════════════════

output storageAccountName string = storageAccount.name
output storageAccountEndpoint string = storageAccount.properties.primaryEndpoints.blob
output keyVaultName string = keyVault.name
output keyVaultUri string = keyVault.properties.vaultUri
output aiServicesName string = aiServices.name
output aiServicesEndpoint string = aiServices.properties.endpoint
output logAnalyticsWorkspaceId string = logAnalytics.id
