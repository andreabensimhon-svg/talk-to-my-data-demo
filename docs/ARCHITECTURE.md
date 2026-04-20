# StreamFlow CEO Data Agent - Architecture

## Overview

This document describes the technical architecture of the CEO Data Agent demo, showcasing Microsoft's "3 IQs" approach:

- **IQ1**: M365 Copilot (Excel, PowerPoint integration)
- **IQ2**: Copilot Studio (Custom agent with Fabric connector)
- **IQ3**: Azure AI Foundry (Advanced orchestration with RAG)

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          USER INTERACTION LAYER                         │
├────────────────┬──────────────────────────┬────────────────────────────┤
│   M365 Copilot │      Copilot Studio      │      Teams / Web App       │
│     (IQ1)      │         (IQ2)            │                            │
│                │                          │                            │
│  Excel Plugin  │    CEO Data Agent        │     Embedded Chat          │
│  PPT Copilot   │    Custom Topics         │                            │
└───────┬────────┴────────────┬─────────────┴─────────────┬──────────────┘
        │                     │                           │
        │                     │                           │
        ▼                     ▼                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      INTELLIGENCE ORCHESTRATION                         │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │                    Azure AI Foundry (IQ3)                        │  │
│  │                                                                   │  │
│  │   ┌───────────────┐   ┌───────────────┐   ┌─────────────────┐   │  │
│  │   │    Intent     │──▶│    Router     │──▶│   Response      │   │  │
│  │   │  Classifier   │   │               │   │   Generator     │   │  │
│  │   └───────────────┘   └───────┬───────┘   └─────────────────┘   │  │
│  │                               │                                   │  │
│  │                       ┌───────┴───────┐                          │  │
│  │                       ▼               ▼                          │  │
│  │               ┌───────────────┐ ┌───────────────┐                │  │
│  │               │  Fabric Query │ │  RAG Search   │                │  │
│  │               │    Engine     │ │    Engine     │                │  │
│  │               └───────────────┘ └───────────────┘                │  │
│  │                                                                   │  │
│  └─────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           DATA PLATFORM                                 │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │                   Microsoft Fabric                               │  │
│  │                                                                   │  │
│  │   ┌─────────────┐   ┌─────────────┐   ┌─────────────────────┐   │  │
│  │   │  Lakehouse  │──▶│  Warehouse  │──▶│   Semantic Model    │   │  │
│  │   │   Bronze    │   │   Silver    │   │   (Direct Lake)     │   │  │
│  │   │   Silver    │   │   Gold      │   │                     │   │  │
│  │   │   Gold      │   │             │   │   DAX Measures      │   │  │
│  │   └─────────────┘   └─────────────┘   └──────────┬──────────┘   │  │
│  │                                                   │              │  │
│  │                                                   ▼              │  │
│  │                                          ┌───────────────┐       │  │
│  │                                          │   Power BI    │       │  │
│  │                                          │   Reports     │       │  │
│  │                                          └───────────────┘       │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │                   Azure AI Search                                │  │
│  │                   (Strategic Documents Index)                    │  │
│  └─────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Microsoft Fabric

**Lakehouse Architecture (Medallion)**

| Layer | Purpose | Tables |
|-------|---------|--------|
| Bronze | Raw data ingestion | All dimension and fact tables (raw CSV) |
| Silver | Cleaned, validated data | Standardized schemas, data quality checks |
| Gold | Business-ready aggregates | Pre-calculated KPIs, summary tables |

**Semantic Model**

- **Mode**: Direct Lake (live connection to Lakehouse)
- **Refresh**: Real-time with incremental refresh
- **Measures**: 40+ DAX measures (see `fabric/semantic-model/measures.dax`)

### 2. Copilot Studio (IQ2)

**Agent Configuration**
- **Name**: CEO Data Agent
- **Channel**: Teams, Web
- **Connector**: Fabric Semantic Model

**Topic Categories**
- Revenue (MRR, ARR, growth)
- Subscribers (count, churn, retention)
- Content (views, engagement, ROI)
- Marketing (spend, CAC, ROAS)
- Executive Summary (holistic view)

### 3. Azure AI Foundry (IQ3)

**Prompt Flow Components**
1. **Intent Classifier**: Routes questions to appropriate handler
2. **Fabric Query Engine**: Translates natural language to DAX
3. **RAG Engine**: Searches strategic documents
4. **Response Generator**: Combines data with context

**Models Used**
- GPT-4o: Main reasoning and generation
- text-embedding-ada-002: Document embeddings

### 4. Data Flow

```
Source Data → Lakehouse (Bronze) → Transform (Silver) → Aggregate (Gold)
                                                              │
                                                              ▼
                                                      Semantic Model
                                                              │
              ┌───────────────────────────────────────────────┼──────┐
              │                       │                       │      │
              ▼                       ▼                       ▼      ▼
         Power BI              Copilot Studio           M365 Copilot │
                                     │                              │
                                     └──────────Azure AI ◄──────────┘
```

## Security & Governance

### Authentication
- Azure AD / Entra ID for all services
- Managed Identity where possible
- Key Vault for secrets

### Data Access
- Row-Level Security (RLS) in Semantic Model
- Workspace roles in Fabric
- API permissions scoped to minimum required

### Compliance
- All data stays within Fabric/Azure boundary
- No PII in demo data
- Audit logging enabled

## Deployment Options

| Option | Complexity | Best For |
|--------|------------|----------|
| Manual | Low | Learning, understanding components |
| PowerShell Script | Medium | Repeatable demos |
| Deploy to Azure Button | Low | Quick setup |
| Bicep/ARM Templates | High | Production, automation |

## Performance Considerations

- **Direct Lake**: Near-real-time queries without data movement
- **Caching**: Copilot Studio caches recent responses
- **Token Limits**: GPT-4o context managed by Prompt Flow
- **Query Optimization**: Pre-aggregated Gold layer for common queries

## Monitoring

- Application Insights for API calls
- Fabric monitoring for query performance
- Copilot Studio analytics for usage patterns
