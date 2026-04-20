# 📖 Complete Setup Guide

This guide walks you through setting up the CEO Data Agent demo from scratch.

**Estimated time:** 2-3 hours  
**Difficulty:** Intermediate

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Azure Resources Deployment](#step-1-azure-resources-deployment)
3. [Fabric Workspace Setup](#step-2-fabric-workspace-setup)
4. [Data Loading](#step-3-data-loading)
5. [Semantic Model Creation](#step-4-semantic-model-creation)
6. [Power BI Reports](#step-5-power-bi-reports)
7. [Copilot Studio Agent](#step-6-copilot-studio-agent)
8. [Azure AI Integration](#step-7-azure-ai-integration-optional)
9. [Testing & Validation](#step-8-testing--validation)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### 1. Licenses Required

| License | Purpose | How to Get |
|---------|---------|------------|
| Microsoft Fabric | Data platform | [Fabric Trial](https://app.fabric.microsoft.com) |
| Copilot Studio | Agent creation | Included in Power Platform or standalone |
| Azure Subscription | AI services | [Azure Free Account](https://azure.microsoft.com/free) |
| M365 E5 | Copilot in Excel/PPT | For IQ1 demo only |

### 2. Tools to Install

```bash
# Required
- VS Code (https://code.visualstudio.com)
- Python 3.10+ (https://python.org)
- Azure CLI (https://docs.microsoft.com/cli/azure/install-azure-cli)
- Power BI Desktop (https://powerbi.microsoft.com/desktop)

# VS Code Extensions
- Fabric Extension
- Python Extension
- Bicep Extension
```

### 3. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/ceo-data-agent.git
cd ceo-data-agent
```

### 4. Python Environment Setup

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Mac/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Step 1: Azure Resources Deployment

### Option A: One-Click Deploy

1. Click the **Deploy to Azure** button in the README
2. Fill in parameters:
   - **Resource Group:** `rg-ceo-agent-demo`
   - **Location:** `France Central` (or your preferred region)
   - **Project Name:** `ceoagent`
3. Click **Review + Create**
4. Wait for deployment (~5 minutes)

### Option B: Azure CLI

```bash
# Login to Azure
az login

# Create resource group
az group create \
  --name rg-ceo-agent-demo \
  --location francecentral

# Deploy infrastructure
az deployment group create \
  --resource-group rg-ceo-agent-demo \
  --template-file infra/main.bicep \
  --parameters projectName=ceoagent
```

### Option C: Bicep with Parameters File

```bash
# Edit parameters file first
code infra/azuredeploy.parameters.json

# Deploy
az deployment group create \
  --resource-group rg-ceo-agent-demo \
  --template-file infra/main.bicep \
  --parameters @infra/azuredeploy.parameters.json
```

### Deployed Resources

After deployment, you'll have:
- ✅ Azure AI Services (for GPT-4)
- ✅ Key Vault (for secrets)
- ✅ Storage Account (for data files)

---

## Step 2: Fabric Workspace Setup

### 2.1 Create Workspace

1. Go to [app.fabric.microsoft.com](https://app.fabric.microsoft.com)
2. Click **Workspaces** → **+ New workspace**
3. Configure:
   - **Name:** `CEO-Demo-StreamFlow`
   - **Description:** `CEO Data Agent Demo - StreamFlow`
   - **License mode:** Fabric capacity (or Trial)
4. Click **Apply**

### 2.2 Create Lakehouse

1. In your workspace, click **+ New** → **Lakehouse**
2. Name: `StreamFlow_Lakehouse`
3. Click **Create**

### 2.3 Create Folder Structure

In the Lakehouse Files explorer:

```
Files/
├── bronze/           # Raw data
├── silver/           # Cleaned data (optional, we use Tables)
├── reference/        # Dimension CSVs
└── scripts/          # Utility scripts
```

**To create folders:**
1. Click **Files** in Lakehouse
2. Click **...** → **New subfolder**
3. Create each folder

---

## Step 3: Data Loading

### 3.1 Generate Demo Data

```bash
# From repo root
cd data
python generate_data.py

# This creates CSV files in data/output/
```

**Generated files:**
- `dim_date.csv` (~760 rows)
- `dim_geography.csv` (5 rows)
- `dim_offer.csv` (4 rows)
- `dim_content.csv` (100 rows)
- `dim_customer.csv` (50,000 rows)
- `fact_subscriptions.csv` (50,000 rows)
- `fact_content_views.csv` (~2M rows)
- `fact_marketing.csv` (~1,000 rows)
- `fact_surveys.csv` (~10,000 rows)

### 3.2 Upload to Lakehouse

**Option A: Manual Upload**
1. In Lakehouse, go to **Files/bronze/**
2. Click **Upload** → **Upload files**
3. Select all CSV files from `data/output/`

**Option B: Using OneLake File Explorer**
1. Install [OneLake File Explorer](https://www.microsoft.com/store/productId/9P8G0QNK8N7V)
2. Navigate to your Lakehouse in Windows Explorer
3. Copy files directly

### 3.3 Run Loading Notebooks

1. In workspace, click **+ New** → **Import notebook**
2. Import notebooks from `fabric/notebooks/` in order:

#### Notebook 1: Load Bronze

```python
# 01_load_bronze.ipynb
# This notebook loads CSVs into Delta tables

# Load dimension tables
for dim in ['date', 'geography', 'offer', 'content', 'customer']:
    df = spark.read.csv(f"Files/bronze/dim_{dim}.csv", header=True, inferSchema=True)
    df.write.mode("overwrite").format("delta").saveAsTable(f"bronze_dim_{dim}")
    print(f"✅ Loaded bronze_dim_{dim}: {df.count()} rows")

# Load fact tables
for fact in ['subscriptions', 'content_views', 'marketing', 'surveys']:
    df = spark.read.csv(f"Files/bronze/fact_{fact}.csv", header=True, inferSchema=True)
    df.write.mode("overwrite").format("delta").saveAsTable(f"bronze_fact_{fact}")
    print(f"✅ Loaded bronze_fact_{fact}: {df.count()} rows")
```

#### Notebook 2: Transform to Silver

```python
# 02_transform_silver.ipynb
# Data cleaning and validation

from pyspark.sql.functions import *

# Clean subscriptions
df_subs = spark.table("bronze_fact_subscriptions")
df_subs_clean = df_subs \
    .withColumn("monthly_fee", col("monthly_fee").cast("decimal(10,2)")) \
    .withColumn("tenure_months", col("tenure_months").cast("int")) \
    .filter(col("customer_key").isNotNull())

df_subs_clean.write.mode("overwrite").format("delta").saveAsTable("silver_fact_subscriptions")

# Repeat for other tables...
```

#### Notebook 3: Create Gold Aggregates

```python
# 03_create_gold.ipynb
# Business-ready aggregations

# Daily KPIs
spark.sql("""
    CREATE OR REPLACE TABLE gold_daily_kpis AS
    SELECT 
        d.date,
        d.month,
        d.year,
        g.region,
        COUNT(DISTINCT s.customer_key) as active_subscribers,
        SUM(s.monthly_fee) as daily_mrr,
        AVG(s.tenure_months) as avg_tenure
    FROM silver_fact_subscriptions s
    JOIN bronze_dim_date d ON s.date_key = d.date_key
    JOIN bronze_dim_geography g ON s.geo_key = g.geo_key
    WHERE s.status = 'Active'
    GROUP BY d.date, d.month, d.year, g.region
""")

# Content Performance
spark.sql("""
    CREATE OR REPLACE TABLE gold_content_performance AS
    SELECT 
        c.title,
        c.type,
        c.genre,
        SUM(v.views) as total_views,
        SUM(v.watch_time_minutes) as total_watch_time,
        AVG(v.completion_rate) as avg_completion
    FROM silver_fact_content_views v
    JOIN bronze_dim_content c ON v.content_key = c.content_key
    GROUP BY c.content_key, c.title, c.type, c.genre
""")
```

### 3.4 Verify Data

```sql
-- Run in Lakehouse SQL endpoint
SELECT 'dim_date' as table_name, COUNT(*) as row_count FROM bronze_dim_date
UNION ALL
SELECT 'dim_geography', COUNT(*) FROM bronze_dim_geography
UNION ALL
SELECT 'fact_subscriptions', COUNT(*) FROM silver_fact_subscriptions
UNION ALL
SELECT 'gold_daily_kpis', COUNT(*) FROM gold_daily_kpis;
```

---

## Step 4: Semantic Model Creation

### 4.1 Create New Semantic Model

1. In Lakehouse, click **New semantic model**
2. Name: `StreamFlow_CEO_Model`
3. Select tables:
   - All `bronze_dim_*` tables
   - `silver_fact_subscriptions`
   - `silver_fact_content_views`
   - `gold_*` tables

### 4.2 Configure Relationships

Open Model view and create relationships:

```
bronze_dim_date.date_key → silver_fact_subscriptions.date_key (1:N)
bronze_dim_date.date_key → silver_fact_content_views.date_key (1:N)
bronze_dim_geography.geo_key → silver_fact_subscriptions.geo_key (1:N)
bronze_dim_offer.offer_key → silver_fact_subscriptions.offer_key (1:N)
bronze_dim_content.content_key → silver_fact_content_views.content_key (1:N)
bronze_dim_customer.customer_key → silver_fact_subscriptions.customer_key (1:N)
```

### 4.3 Add DAX Measures

In Data view, create a measures table and add:

```dax
-- Copy from fabric/semantic-model/measures.dax

-- ════════════════════════════════════════
-- REVENUE METRICS
-- ════════════════════════════════════════

MRR = 
SUMX(
    FILTER(silver_fact_subscriptions, silver_fact_subscriptions[status] = "Active"),
    silver_fact_subscriptions[monthly_fee]
)

ARR = [MRR] * 12

MRR Growth MoM = 
VAR CurrentMRR = [MRR]
VAR PreviousMRR = CALCULATE([MRR], DATEADD(bronze_dim_date[date], -1, MONTH))
RETURN DIVIDE(CurrentMRR - PreviousMRR, PreviousMRR, 0)

-- ════════════════════════════════════════
-- SUBSCRIBER METRICS
-- ════════════════════════════════════════

Active Subscribers = 
CALCULATE(
    DISTINCTCOUNT(silver_fact_subscriptions[customer_key]),
    silver_fact_subscriptions[status] = "Active"
)

Churn Rate = 
VAR Churned = CALCULATE(COUNTROWS(silver_fact_subscriptions), silver_fact_subscriptions[status] = "Churned")
VAR Total = COUNTROWS(silver_fact_subscriptions)
RETURN DIVIDE(Churned, Total, 0)

-- Add all other measures from measures.dax...
```

### 4.4 Enable Copilot & Q&A

1. Open Semantic Model settings
2. Enable **Q&A** feature
3. Enable **Copilot** (if available)
4. Add synonyms for business terms:
   - "revenue" → MRR, ARR
   - "customers" → Subscribers
   - "loss rate" → Churn

---

## Step 5: Power BI Reports

### 5.1 Open Reports in Power BI Desktop

1. Open `powerbi/CEO_Dashboard.pbix`
2. When prompted, update data source:
   - **Workspace:** Your Fabric workspace
   - **Semantic Model:** `StreamFlow_CEO_Model`

### 5.2 Apply Custom Theme

1. In Power BI Desktop: **View** → **Themes** → **Browse for themes**
2. Select `powerbi/theme/streamflow-theme.json`

### 5.3 Publish to Fabric

1. **Home** → **Publish**
2. Select your `CEO-Demo-StreamFlow` workspace
3. Repeat for all 6 reports

### 5.4 Create Power BI App

1. In workspace, click **Create app**
2. Configure:
   - **Name:** StreamFlow CEO Dashboard
   - **Navigation:** Custom order
3. Add reports in order:
   1. Executive Summary
   2. Subscriptions Analysis
   3. Content Performance
   4. Financial Overview
   5. Marketing ROI
   6. Forecasting
4. Publish app

---

## Step 6: Copilot Studio Agent

### 6.1 Create New Copilot

1. Go to [copilotstudio.microsoft.com](https://copilotstudio.microsoft.com)
2. Select your environment
3. Click **+ Create** → **New copilot**
4. Configure:
   - **Name:** CEO Assistant - StreamFlow
   - **Language:** English (or French)
   - **Icon:** Upload custom icon

### 6.2 Import Topics

For each file in `copilot-studio/topics/`:

1. **Topics** → **+ New topic** → **Create from blank**
2. Configure trigger phrases
3. Add actions and responses
4. Save and test

**Example: Daily KPIs Topic**

```yaml
Name: Daily KPIs
Trigger phrases:
  - "KPIs today"
  - "daily dashboard"
  - "how are we doing"
  - "today's numbers"

Response:
  - Call Fabric connector to get KPIs
  - Format response with:
    📊 **Today's KPIs - {date}**
    
    💰 **MRR:** {mrr} €
    👥 **Subscribers:** {subscribers}
    📉 **Churn:** {churn}%
    
    Want more details?
```

### 6.3 Configure Fabric Connector

1. **Settings** → **Generative AI**
2. Enable **Knowledge sources**
3. Add **Power BI dataset** connector:
   - Workspace: `CEO-Demo-StreamFlow`
   - Dataset: `StreamFlow_CEO_Model`
4. Test with: "What's our MRR?"

### 6.4 Deploy to Teams

1. **Publish** → **Microsoft Teams**
2. Configure app manifest
3. Submit for admin approval
4. Once approved, add to Teams

---

## Step 7: Azure AI Integration (Optional)

### 7.1 Create Azure AI Project

1. Go to [ai.azure.com](https://ai.azure.com)
2. **+ New project**
3. Configure:
   - **Name:** `CEO-Agent-StreamFlow`
   - **Hub:** Create new or use existing
   - **Region:** Same as your resources

### 7.2 Deploy GPT-4 Model

1. **Deployments** → **+ Deploy model**
2. Select: `gpt-4o` or `gpt-4`
3. Configure:
   - **Name:** `gpt-4o-ceo`
   - **TPM:** 80,000

### 7.3 Import Prompt Flow

1. **Prompt flow** → **+ Create**
2. **Import** → Upload `azure-ai/prompt-flows/ceo-orchestrator/`
3. Configure connections:
   - Azure OpenAI connection
   - Fabric connector (custom)

### 7.4 Deploy as Endpoint

1. **Deploy** → **Deploy to endpoint**
2. Configure:
   - **Endpoint name:** `ceo-agent-endpoint`
   - **VM:** Standard_DS3_v2
3. Note the endpoint URL and key

### 7.5 Integrate with Copilot Studio

1. In Copilot Studio, create **Custom connector**
2. Configure with Azure AI endpoint
3. Create topic that calls advanced AI for complex queries

---

## Step 8: Testing & Validation

### 8.1 Test Checklist

#### Fabric
- [ ] All tables loaded successfully
- [ ] Relationships working in model
- [ ] Measures calculating correctly
- [ ] Copilot in Fabric responds to queries

#### Power BI
- [ ] All reports display data
- [ ] Slicers work correctly
- [ ] Cards show correct values
- [ ] App published and accessible

#### Copilot Studio
- [ ] Agent responds to greetings
- [ ] KPI queries return data
- [ ] Comparison queries work
- [ ] Deployed to Teams

#### Azure AI (if configured)
- [ ] Prompt flow runs successfully
- [ ] Endpoint responds
- [ ] Integration with Copilot Studio works

### 8.2 Sample Test Queries

| Query | Expected Result |
|-------|-----------------|
| "What's our MRR?" | ~€45M |
| "How many active subscribers?" | ~2.85M |
| "What's our churn rate?" | ~2.1% |
| "Top 5 content this month" | List with views |
| "Compare Europe vs Americas" | Side-by-side metrics |

### 8.3 Run Automated Tests

```bash
cd scripts
python test-agent.py --endpoint YOUR_ENDPOINT
```

---

## Troubleshooting

### Common Issues

#### "Semantic model not found"
- Verify workspace name matches exactly
- Check permissions on workspace
- Refresh Copilot Studio connections

#### "No data returned"
- Verify tables have data: `SELECT COUNT(*) FROM table`
- Check relationship cardinality
- Verify filter context in measures

#### "Copilot Studio errors"
- Check connector authentication
- Verify API limits not exceeded
- Review error logs in Copilot Studio

#### "Power BI reports blank"
- Update data source connections
- Refresh dataset
- Check RLS if configured

### Getting Help

- [Microsoft Fabric Documentation](https://learn.microsoft.com/fabric/)
- [Copilot Studio Documentation](https://learn.microsoft.com/microsoft-copilot-studio/)
- [Azure AI Documentation](https://learn.microsoft.com/azure/ai-services/)
- [GitHub Issues](https://github.com/YOUR_USERNAME/ceo-data-agent/issues)

---

## Next Steps

Once setup is complete:

1. 📖 Read the [Demo Script](./DEMO_SCRIPT.md)
2. 🎯 Practice the demo flow
3. 🎨 Customize branding for your audience
4. 📊 Add your own data (optional)

---

**Setup complete! You're ready to demo the CEO Data Agent. 🚀**
