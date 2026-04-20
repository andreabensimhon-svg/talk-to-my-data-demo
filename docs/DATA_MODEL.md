# StreamFlow Demo - Data Model

## Overview

The demo uses a **star schema** optimized for analytical queries. The model represents a streaming platform with subscription-based revenue.

## Entity Relationship Diagram

```
                              ┌─────────────────┐
                              │   dim_date      │
                              │─────────────────│
                              │ date_key (PK)   │
                              │ date            │
                              │ month           │
                              │ quarter         │
                              │ year            │
                              └────────┬────────┘
                                       │
     ┌─────────────────┐               │               ┌─────────────────┐
     │  dim_geography  │               │               │   dim_offer     │
     │─────────────────│               │               │─────────────────│
     │ geo_key (PK)    │               │               │ offer_key (PK)  │
     │ region          │               │               │ offer_name      │
     │ country_code    │               │               │ monthly_price   │
     │ currency        │               │               │ annual_price    │
     └────────┬────────┘               │               └────────┬────────┘
              │                        │                        │
              │         ┌──────────────┴──────────────┐         │
              │         │                             │         │
              │         ▼                             ▼         │
              │  ┌─────────────────┐         ┌─────────────────┐│
              │  │fact_subscriptions│        │fact_content_views││
              │  │─────────────────│         │─────────────────││
              └─▶│ subscription_id │         │ view_id         │◀┘
                 │ date_key (FK)   │         │ date_key (FK)   │
                 │ customer_key(FK)│         │ customer_key(FK)│
                 │ geo_key (FK)    │         │ content_key (FK)│
                 │ offer_key (FK)  │         │ geo_key (FK)    │
                 │ monthly_fee     │         │ views           │
                 │ status          │         │ watch_time_min  │
                 └────────┬────────┘         └────────┬────────┘
                          │                           │
                          │    ┌─────────────────┐    │
                          │    │  dim_customer   │    │
                          │    │─────────────────│    │
                          └───▶│ customer_key(PK)│◀───┘
                               │ acquisition_ch. │
                               │ segment         │
                               │ age_group       │
                               └─────────────────┘
                                       ▲
                                       │
     ┌─────────────────┐               │               ┌─────────────────┐
     │  dim_content    │               │               │  fact_surveys   │
     │─────────────────│               │               │─────────────────│
     │ content_key(PK) │               │               │ survey_id       │
     │ title           │               │               │ date_key (FK)   │
     │ type            │               └───────────────│ customer_key(FK)│
     │ genre           │                               │ score           │
     │ duration_min    │               ┌───────────────│ category        │
     │ production_cost │               │               └─────────────────┘
     │ is_original     │               │
     └─────────────────┘               │
                                       │
                          ┌────────────┴────────────┐
                          │    fact_marketing       │
                          │─────────────────────────│
                          │ campaign_id             │
                          │ date_key (FK)           │
                          │ geo_key (FK)            │
                          │ channel                 │
                          │ spend                   │
                          │ impressions             │
                          │ clicks                  │
                          │ acquisitions            │
                          └─────────────────────────┘
```

## Dimension Tables

### dim_date
| Column | Type | Description |
|--------|------|-------------|
| date_key | INT | Primary key (YYYYMMDD format) |
| date | DATE | Full date |
| day_of_week | STRING | Monday, Tuesday, etc. |
| day_of_week_num | INT | 0-6 |
| week_number | INT | ISO week number |
| month | INT | 1-12 |
| month_name | STRING | January, February, etc. |
| quarter | INT | 1-4 |
| year | INT | Calendar year |
| is_weekend | BOOLEAN | True if Saturday/Sunday |
| fiscal_year | INT | Fiscal year (April start) |

### dim_geography
| Column | Type | Description |
|--------|------|-------------|
| geo_key | INT | Primary key |
| region | STRING | Europe West, Americas, etc. |
| country_code | STRING | Short code |
| currency | STRING | EUR, USD |
| timezone | STRING | IANA timezone |
| market_weight | DECIMAL | Distribution weight for generation |

### dim_offer
| Column | Type | Description |
|--------|------|-------------|
| offer_key | INT | Primary key |
| offer_name | STRING | Basic, Standard, Premium, Ultimate |
| monthly_price | DECIMAL | Monthly subscription price |
| annual_price | DECIMAL | Annual subscription price |
| max_screens | INT | Simultaneous streams allowed |
| has_4k | BOOLEAN | 4K streaming included |
| has_download | BOOLEAN | Offline download included |
| offer_weight | DECIMAL | Distribution weight for generation |

### dim_customer
| Column | Type | Description |
|--------|------|-------------|
| customer_key | INT | Primary key (1000+) |
| acquisition_channel | STRING | How customer was acquired |
| acquisition_date | DATE | When customer signed up |
| segment | STRING | Customer segment |
| age_group | STRING | Age bracket |
| device_preference | STRING | Primary device used |

### dim_content
| Column | Type | Description |
|--------|------|-------------|
| content_key | INT | Primary key (500+) |
| title | STRING | Content title |
| type | STRING | Movie, Series, Sports, etc. |
| genre | STRING | Action, Comedy, Drama, etc. |
| duration_minutes | INT | Runtime |
| production_cost | DECIMAL | Investment if original |
| release_date | DATE | When added to platform |
| is_original | BOOLEAN | StreamFlow original content |

## Fact Tables

### fact_subscriptions
| Column | Type | Description |
|--------|------|-------------|
| subscription_id | INT | Primary key |
| date_key | INT | FK to dim_date |
| customer_key | INT | FK to dim_customer |
| geo_key | INT | FK to dim_geography |
| offer_key | INT | FK to dim_offer |
| billing_type | STRING | Monthly or Annual |
| tenure_months | INT | Months subscribed |
| monthly_fee | DECIMAL | Current monthly charge |
| status | STRING | Active or Churned |

### fact_content_views
| Column | Type | Description |
|--------|------|-------------|
| view_id | INT | Primary key |
| date_key | INT | FK to dim_date (monthly) |
| customer_key | INT | FK to dim_customer |
| content_key | INT | FK to dim_content |
| geo_key | INT | FK to dim_geography |
| views | INT | Number of views |
| watch_time_minutes | INT | Time watched |
| completion_rate | DECIMAL | % of content watched |
| device | STRING | Device used |

### fact_marketing
| Column | Type | Description |
|--------|------|-------------|
| campaign_id | INT | Primary key |
| date_key | INT | FK to dim_date (monthly) |
| geo_key | INT | FK to dim_geography |
| channel | STRING | Marketing channel |
| spend | DECIMAL | Marketing spend |
| impressions | INT | Ad impressions |
| clicks | INT | Ad clicks |
| acquisitions | INT | New customers acquired |
| conversion_rate | DECIMAL | Acquisitions / Clicks |

### fact_surveys
| Column | Type | Description |
|--------|------|-------------|
| survey_id | INT | Primary key |
| date_key | INT | FK to dim_date (quarterly) |
| customer_key | INT | FK to dim_customer |
| score | INT | NPS score (0-10) |
| category | STRING | Survey category |

## Data Volume

| Table | Records | Notes |
|-------|---------|-------|
| dim_date | ~760 | 24 months of dates |
| dim_geography | 5 | 5 regions |
| dim_offer | 4 | 4 subscription tiers |
| dim_content | 100 | 10 featured + 90 catalog |
| dim_customer | 50,000 | Customer base |
| fact_subscriptions | 50,000 | Snapshot per customer |
| fact_content_views | ~2M | Monthly aggregates |
| fact_marketing | ~720 | Channel × region × month |
| fact_surveys | ~50,000 | Quarterly samples |

## Key Relationships

```sql
-- Fabric Semantic Model relationships
fact_subscriptions[date_key] → dim_date[date_key] (M:1)
fact_subscriptions[customer_key] → dim_customer[customer_key] (M:1)
fact_subscriptions[geo_key] → dim_geography[geo_key] (M:1)
fact_subscriptions[offer_key] → dim_offer[offer_key] (M:1)

fact_content_views[date_key] → dim_date[date_key] (M:1)
fact_content_views[customer_key] → dim_customer[customer_key] (M:1)
fact_content_views[content_key] → dim_content[content_key] (M:1)
fact_content_views[geo_key] → dim_geography[geo_key] (M:1)

fact_marketing[date_key] → dim_date[date_key] (M:1)
fact_marketing[geo_key] → dim_geography[geo_key] (M:1)

fact_surveys[date_key] → dim_date[date_key] (M:1)
fact_surveys[customer_key] → dim_customer[customer_key] (M:1)
```

## Sample Queries

### MRR by Region
```dax
EVALUATE
SUMMARIZE(
    fact_subscriptions,
    dim_geography[region],
    "MRR", SUMX(FILTER(fact_subscriptions, fact_subscriptions[status] = "Active"), fact_subscriptions[monthly_fee])
)
```

### Content Performance
```dax
EVALUATE
TOPN(
    10,
    SUMMARIZE(
        fact_content_views,
        dim_content[title],
        "Total Views", SUM(fact_content_views[views]),
        "Avg Completion", AVERAGE(fact_content_views[completion_rate])
    ),
    [Total Views],
    DESC
)
```

### Churn Analysis
```dax
EVALUATE
SUMMARIZE(
    fact_subscriptions,
    dim_geography[region],
    "Churn Rate", DIVIDE(
        CALCULATE(COUNTROWS(fact_subscriptions), fact_subscriptions[status] = "Churned"),
        COUNTROWS(fact_subscriptions)
    )
)
```
