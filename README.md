# 🎬 CEO Data Agent - Talk to My Data Demo

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FYOUR_USERNAME%2Fceo-data-agent%2Fmain%2Finfra%2Fazuredeploy.json)

> **Demo project** showcasing Microsoft's 3 IQs (M365 Copilot, Copilot Studio, Azure AI) on Microsoft Fabric for executive data analytics.

---

## 🚀 Déploiement rapide (15 min)

### Option 1 : Quick Start (Recommandé)
👉 **[QUICK_START.md](./docs/QUICK_START.md)** - Guide pas-à-pas clic-à-clic

### Option 2 : Deploy to Azure
Cliquez le bouton ci-dessus pour déployer les ressources Azure automatiquement.

---

## 🎯 What is this?

This repository contains everything needed to deploy a **CEO Data Agent** demo that enables executives to interact with their business data using natural language.

**Fictional Company:** StreamFlow (streaming platform)  
**Use Case:** CEO asks questions like "What's our MRR?" or "Show me top content this month"

### The 3 IQs in Action

| IQ | Product | Role in Demo |
|----|---------|--------------|
| **IQ1** | Microsoft 365 Copilot | Excel/PowerPoint with live data |
| **IQ2** | Copilot Studio | Custom CEO Assistant agent |
| **IQ3** | Azure AI Foundry | RAG + advanced orchestration |

```
                         CEO
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
    ┌─────────┐     ┌─────────┐     ┌─────────┐
    │   IQ1   │     │   IQ2   │     │   IQ3   │
    │  M365   │     │ Copilot │     │ Azure   │
    │ Copilot │     │ Studio  │     │   AI    │
    └────┬────┘     └────┬────┘     └────┬────┘
         │               │               │
         └───────────────┼───────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │  MICROSOFT FABRIC   │
              │    (Single Source   │
              │     of Truth)       │
              └─────────────────────┘
```

---

## 📁 Repository Structure

```
ceo-data-agent/
├── README.md                    # This file
├── LICENSE
├── .gitignore
│
├── docs/                        # 📚 Documentation
│   ├── QUICK_START.md           # ⭐ Déploiement en 15 min
│   ├── SETUP.md                 # Guide complet
│   ├── ARCHITECTURE.md          # Architecture technique
│   ├── DATA_MODEL.md            # Schéma de données
│   ├── POWER_BI_VISUALS.md      # 🎨 Visuels premium
│   └── DEMO_SCRIPT.md           # Script de présentation
│
├── infra/                       # Infrastructure as Code
│   ├── azuredeploy.json         # ARM template for one-click deploy
│   └── main.bicep               # Bicep template
│
├── data/                        # Demo data
│   └── generate_data.py         # Script to generate fresh data
│
├── fabric/                      # Microsoft Fabric assets
│   ├── notebooks/
│   │   ├── 01_load_bronze.ipynb
│   │   ├── 02_transform_silver.ipynb
│   │   ├── 03_create_gold.ipynb
│   │   └── 04_create_semantic_model.ipynb
│   ├── dataflows/
│   │   └── df_daily_refresh.json
│   └── semantic-model/
│       ├── model.bim
│       └── measures.dax
│
├── powerbi/                     # Power BI reports
│   ├── CEO_Dashboard.pbix
│   ├── Subscriptions_Analysis.pbix
│   ├── Content_Performance.pbix
│   ├── Financial_Overview.pbix
│   ├── Marketing_ROI.pbix
│   ├── Forecasting.pbix
│   └── theme/
│       └── streamflow-theme.json
│
├── copilot-studio/              # Copilot Studio configuration
│   ├── ceo-assistant.yaml
│   ├── topics/
│   │   ├── greeting.yaml
│   │   ├── daily_kpis.yaml
│   │   ├── revenue_analysis.yaml
│   │   ├── content_performance.yaml
│   │   ├── alerts.yaml
│   │   └── comparison.yaml
│   └── connectors/
│       └── fabric-connector.json
│
├── azure-ai/                    # Azure AI Foundry assets
│   ├── prompt-flows/
│   │   └── ceo-orchestrator/
│   │       ├── flow.dag.yaml
│   │       ├── classify_intent.py
│   │       ├── query_fabric.py
│   │       └── generate_response.py
│   ├── indexes/
│   │   └── strategic-docs-index.json
│   └── prompts/
│       └── ceo_system_prompt.txt
│
├── docs/                        # Documentation
│   ├── SETUP.md                 # Detailed setup guide
│   ├── ARCHITECTURE.md          # Architecture documentation
│   ├── DATA_MODEL.md            # Data model documentation
│   ├── DEMO_SCRIPT.md           # Demo presentation script
│   └── images/
│       ├── architecture-overview.png
│       ├── fabric-workspace.png
│       └── agent-conversation.png
│
└── scripts/                     # Utility scripts
    ├── setup.ps1                # PowerShell setup script
    ├── setup.sh                 # Bash setup script
    ├── deploy-fabric.ps1        # Deploy Fabric assets
    └── test-agent.py            # Test agent responses
```

---

## 🚀 Quick Start

### Option 1: One-Click Deploy to Azure

Click the button below to deploy the Azure resources:

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FYOUR_USERNAME%2Fceo-data-agent%2Fmain%2Finfra%2Fazuredeploy.json)

This will create:
- Azure AI Services resource
- Key Vault for secrets
- Storage Account for data

> **Note:** Microsoft Fabric workspace must be created manually (see Setup Guide).

### Option 2: Manual Setup

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/ceo-data-agent.git
cd ceo-data-agent

# Generate demo data
python data/generate_data.py

# Follow the setup guide
code docs/SETUP.md
```

---

## 📋 Prerequisites

### Required Licenses
- [ ] Microsoft Fabric capacity (F64 or Trial)
- [ ] Copilot Studio license
- [ ] Azure subscription
- [ ] Microsoft 365 E5 (for M365 Copilot demo)

### Required Permissions
- [ ] Fabric Admin or Workspace Admin
- [ ] Azure Contributor role
- [ ] Power Platform Environment Admin

### Tools
- [ ] VS Code with Fabric extension
- [ ] Python 3.10+
- [ ] Azure CLI
- [ ] Power BI Desktop

---

## 🛠️ Setup Guide (Summary)

### Step 1: Deploy Azure Resources
```bash
az deployment group create \
  --resource-group rg-ceo-agent-demo \
  --template-file infra/main.bicep \
  --parameters infra/azuredeploy.parameters.json
```

### Step 2: Create Fabric Workspace
1. Go to [app.fabric.microsoft.com](https://app.fabric.microsoft.com)
2. Create workspace: `CEO-Demo-StreamFlow`
3. Assign Fabric capacity

### Step 3: Load Data
1. Upload CSVs from `data/` to Lakehouse
2. Run notebooks in order (01 → 02 → 03 → 04)

### Step 4: Create Semantic Model
1. Import `fabric/semantic-model/model.bim`
2. Add measures from `measures.dax`

### Step 5: Deploy Power BI Reports
1. Open `.pbix` files in Power BI Desktop
2. Update data source to your Fabric workspace
3. Publish to workspace

### Step 6: Configure Copilot Studio Agent
1. Go to [copilotstudio.microsoft.com](https://copilotstudio.microsoft.com)
2. Import agent from `copilot-studio/ceo-assistant.yaml`
3. Configure Fabric connector

### Step 7: (Optional) Deploy Azure AI Flow
1. Go to [ai.azure.com](https://ai.azure.com)
2. Create project and import prompt flow
3. Deploy as endpoint

📖 **[Full Setup Guide →](./docs/SETUP.md)**

---

## 🎭 Demo Script

### Opening
> "Today, we'll show you how a CEO can talk to their data using natural language, powered by Microsoft's 3 IQs."

### Key Demo Moments

1. **Copilot in Fabric** (2 min)
   - Show native Q&A capabilities
   - "Show me MRR by region"

2. **CEO Agent in Teams** (5 min)
   - "What are today's KPIs?"
   - "Compare this month vs last year"
   - "Any alerts I should know about?"

3. **Power BI Dashboard** (3 min)
   - Executive Summary
   - Drill-down capabilities

4. **Advanced Query** (2 min)
   - Complex analysis with Azure AI
   - RAG on strategic documents

📖 **[Full Demo Script →](./docs/DEMO_SCRIPT.md)**

---

## 📊 Data Model

### Dimensions
| Table | Rows | Description |
|-------|------|-------------|
| dim_date | 760 | 24 months of dates |
| dim_geography | 5 | Regions (Europe, Americas, etc.) |
| dim_offer | 4 | Subscription tiers |
| dim_content | 100 | Movies, Series, Sports, Docs |
| dim_customer | 50,000 | Customer attributes |

### Facts
| Table | Rows | Grain |
|-------|------|-------|
| fact_subscriptions | 50,000 | One row per customer snapshot |
| fact_content_views | 2,000,000+ | One row per view event |
| fact_marketing | 1,000+ | One row per campaign/day |
| fact_surveys | 10,000+ | One row per survey response |

### Key Measures
- MRR, ARR, Revenue Growth
- Active Subscribers, Churn Rate
- LTV, CAC, LTV/CAC Ratio
- Content Views, Completion Rate, ROI
- NPS Score

📖 **[Full Data Model →](./docs/DATA_MODEL.md)**

---

## 🤖 Agent Capabilities

The CEO Assistant can answer questions like:

| Category | Example Questions |
|----------|-------------------|
| **KPIs** | "What's our current MRR?" |
| **Trends** | "How has churn evolved over 6 months?" |
| **Comparison** | "Compare Europe vs Americas performance" |
| **Content** | "What are our top 5 performing shows?" |
| **Alerts** | "Any metrics above threshold?" |
| **Forecasting** | "Project ARR for next quarter" |

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file (not committed):

```env
# Azure
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_RESOURCE_GROUP=rg-ceo-agent-demo
AZURE_LOCATION=francecentral

# Fabric
FABRIC_WORKSPACE_ID=your-workspace-id
FABRIC_LAKEHOUSE_ID=your-lakehouse-id

# Azure AI
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_KEY=your-key

# Copilot Studio
COPILOT_BOT_ID=your-bot-id
```

### Customization

To adapt for your own company:

1. **Company Name:** Search & replace "StreamFlow" in all files
2. **Data:** Modify `data/generate_data.py` parameters
3. **Branding:** Update `powerbi/theme/streamflow-theme.json`
4. **Measures:** Adjust DAX in `fabric/semantic-model/measures.dax`

---

## 📝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

---

## 🙏 Acknowledgments

- Microsoft Fabric Team
- Copilot Studio Team
- Azure AI Team
- StreamFlow (fictional company for demo purposes)

---

## 📞 Support

For questions or issues:
- Open a [GitHub Issue](https://github.com/YOUR_USERNAME/ceo-data-agent/issues)
- Contact: your-email@example.com

---

**Made with ❤️ for data-driven executives**
