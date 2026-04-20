# 🚀 Quick Start - Déploiement en 15 minutes

> **Objectif** : Déployer rapidement une démo "Talk to My Data" avec des visuels Power BI exceptionnels et une expérience conversationnelle unique.

---

## 🎯 Contexte métier : Pourquoi cette démo ?

**Le problème du CEO aujourd'hui :**
- Il veut savoir "Comment va le business ?" mais doit attendre des rapports
- Il pose des questions simples mais obtient des tableaux Excel complexes
- Il n'a pas le temps d'apprendre des outils techniques

**La solution "Talk to My Data" :**
- Le CEO pose sa question en langage naturel : *"Quel est notre MRR ?"*
- L'IA interroge les données et répond instantanément
- Pas besoin de formation, pas besoin d'analyste

**Ce qu'on construit :**
```
CEO → "Comment va l'Europe ?" → Agent IA → Données Fabric → Réponse claire
```

---

## Prérequis (5 min)

- [ ] Compte Microsoft Fabric (Trial gratuit : [fabric.microsoft.com](https://fabric.microsoft.com))
- [ ] Power BI Desktop installé
- [ ] Accès à Copilot Studio

---

## Étape 1 : Créer le Workspace (2 min)

> 💡 **Pourquoi ?** Le Workspace est comme un **dossier projet** dans lequel on va ranger toutes les ressources : données, rapports, modèles. C'est l'espace de travail de l'équipe data pour ce projet.

1. Aller sur **app.fabric.microsoft.com**
2. Cliquer **Workspaces** → **New workspace**
3. Nom : `CEO-Demo-StreamFlow`
4. Activer **Fabric capacity** (Trial OK)

---

## Étape 2 : Créer le Lakehouse (2 min)

> 💡 **Pourquoi ?** Le Lakehouse est le **lac de données** de l'entreprise. C'est là qu'on stocke toutes les données brutes : abonnements, vues de contenu, marketing, etc. Pensez-y comme un **entrepôt central** où arrivent toutes les données de l'entreprise.
>
> **Analogie métier :** C'est comme le système d'information central qui reçoit les données de tous les départements (commercial, marketing, finance).

1. Dans le workspace, cliquer **+ New** → **Lakehouse**
2. Nom : `lh_streamflow`
3. Cliquer **Create**

---

## Étape 3 : Charger les données (5 min)

> 💡 **Pourquoi ?** On alimente le Lakehouse avec les données de l'entreprise. Dans cette démo, on utilise des **données fictives** qui simulent une plateforme de streaming :
>
> | Table | Ce qu'elle contient | Usage métier |
> |-------|---------------------|--------------|
> | `fact_subscriptions` | Tous les abonnements clients | Calculer le MRR, analyser le churn |
> | `fact_content_views` | Ce que les gens regardent | Mesurer l'engagement, ROI contenu |
> | `fact_marketing` | Dépenses pub par canal | Calculer le CAC, optimiser les budgets |
> | `fact_surveys` | Réponses NPS clients | Mesurer la satisfaction |
> | `dim_customer` | Profil des clients | Segmenter, personnaliser |
> | `dim_geography` | Régions (Europe, Afrique...) | Analyser par zone géographique |
> | `dim_offer` | Offres (Basic, Premium...) | Analyser par gamme de prix |
> | `dim_content` | Catalogue de contenus | Analyser les performances |

### Option A : Upload direct (Recommandé)

1. Générer les CSV localement :
   ```powershell
   cd github-repo/data
   python generate_data.py
   ```

2. Dans le Lakehouse, cliquer **Get data** → **Upload files**

3. Uploader les 9 fichiers CSV depuis `data/output/`

4. Pour chaque fichier, clic droit → **Load to Tables** → **New table**

### Option B : Notebook (si vous préférez)

1. **+ New** → **Notebook**
2. Coller le code de `fabric/notebooks/01_load_data.py`
3. Exécuter toutes les cellules

---

## Étape 4 : Créer le Semantic Model (3 min)

> 💡 **Pourquoi ?** Le Semantic Model est la **couche métier** au-dessus des données brutes. C'est là qu'on définit :
> - Les **relations** entre les tables (un client a plusieurs abonnements)
> - Les **mesures métier** (MRR, Churn Rate, LTV...) avec leurs formules
> - Le **vocabulaire business** que le CEO comprend
>
> **Analogie métier :** C'est comme un **dictionnaire de l'entreprise** qui traduit les données techniques en langage business. Quand le CEO dit "MRR", le système sait exactement comment le calculer.

1. Dans le Lakehouse, cliquer **New semantic model**
2. Nom : `sm_ceo_dashboard`
3. Sélectionner toutes les tables
4. Cliquer **Confirm**

### Créer les relations entre tables (IMPORTANT)

> ⚠️ **Si les relations ne sont pas créées automatiquement**, vous devez les créer manuellement. Sans relations, les mesures DAX ne fonctionneront pas correctement.

#### Comment fonctionnent les Keys (clés) ?

Les **keys** sont des colonnes qui permettent de **lier les tables entre elles** :

```
┌─────────────────────────────┐         ┌──────────────────────────┐
│     fact_subscriptions      │         │       dim_customer       │
├─────────────────────────────┤         ├──────────────────────────┤
│ subscription_id             │         │ customer_key (UNIQUE)    │◄── Clé primaire
│ customer_key ───────────────┼────────►│ customer_name            │
│ offer_key                   │         │ email                    │
│ monthly_fee                 │         │ segment                  │
└─────────────────────────────┘         └──────────────────────────┘
      ↑                                        ↑
   Clé étrangère                          Clé primaire
   (peut avoir des doublons)              (valeur unique)
```

**Principe :**
- **Table de dimension (dim_)** : contient une **clé primaire** unique (ex: `customer_key = 1` = "Marie Dupont")
- **Table de faits (fact_)** : contient une **clé étrangère** qui référence la dimension (ex: 10 abonnements avec `customer_key = 1`)
- La **relation** lie ces deux colonnes → permet de filtrer les faits par dimension

**Exemple concret :**
> "Combien de revenus pour les clients **Premium** ?"
> 1. Fabric filtre `dim_customer` où `segment = "Premium"` 
> 2. Via la relation `customer_key`, il trouve tous les abonnements correspondants dans `fact_subscriptions`
> 3. Il calcule la somme des `monthly_fee`

**Comment vérifier si les relations existent :**
1. Cliquer sur le semantic model dans le workspace
2. Cliquer **Open data model** (icône diagramme en haut à droite)
3. Vous voyez les tables : s'il y a des **lignes entre elles** = relations OK. Sinon, créer manuellement.

**Créer une relation manuellement :**
1. Dans la vue diagramme, **glisser** la colonne `customer_key` de `fact_subscriptions`
2. **Déposer** sur la colonne `customer_key` de `dim_customer`
3. Une fenêtre s'ouvre : vérifier que c'est **Many to One** → **OK**

**Toutes les relations à créer (12 au total) :**

#### 🔗 Relations de `fact_subscriptions` (4 relations)

| # | Table source | Colonne source | → | Table cible | Colonne cible | Cardinalité |
|---|--------------|----------------|---|-------------|---------------|-------------|
| 1 | `fact_subscriptions` | `customer_key` | → | `dim_customer` | `customer_key` | Many to One (*:1) |
| 2 | `fact_subscriptions` | `geo_key` | → | `dim_geography` | `geo_key` | Many to One (*:1) |
| 3 | `fact_subscriptions` | `offer_key` | → | `dim_offer` | `offer_key` | Many to One (*:1) |
| 4 | `fact_subscriptions` | `start_date_key` | → | `dim_date` | `date_key` | Many to One (*:1) |

#### 🔗 Relations de `fact_content_views` (4 relations)

| # | Table source | Colonne source | → | Table cible | Colonne cible | Cardinalité |
|---|--------------|----------------|---|-------------|---------------|-------------|
| 5 | `fact_content_views` | `date_key` | → | `dim_date` | `date_key` | Many to One (*:1) |
| 6 | `fact_content_views` | `customer_key` | → | `dim_customer` | `customer_key` | Many to One (*:1) |
| 7 | `fact_content_views` | `content_key` | → | `dim_content` | `content_key` | Many to One (*:1) |
| 8 | `fact_content_views` | `geo_key` | → | `dim_geography` | `geo_key` | Many to One (*:1) |

#### 🔗 Relations de `fact_marketing` (2 relations)

| # | Table source | Colonne source | → | Table cible | Colonne cible | Cardinalité |
|---|--------------|----------------|---|-------------|---------------|-------------|
| 9 | `fact_marketing` | `date_key` | → | `dim_date` | `date_key` | Many to One (*:1) |
| 10 | `fact_marketing` | `geo_key` | → | `dim_geography` | `geo_key` | Many to One (*:1) |

#### 🔗 Relations de `fact_surveys` (2 relations)

| # | Table source | Colonne source | → | Table cible | Colonne cible | Cardinalité |
|---|--------------|----------------|---|-------------|---------------|-------------|
| 11 | `fact_surveys` | `date_key` | → | `dim_date` | `date_key` | Many to One (*:1) |
| 12 | `fact_surveys` | `customer_key` | → | `dim_customer` | `customer_key` | Many to One (*:1) |

> 💡 **Astuce** : Commencez par `fact_subscriptions` (4 relations), c'est la table principale. Ensuite faites les autres tables de faits.

**Schéma en étoile final :**
```
                         dim_date
                            │
     dim_customer ──── FACT TABLES ──── dim_geography
                            │
     dim_content           │            dim_offer
         │                 │                │
         └─────────────────┴────────────────┘
```

---

## Étape 5 : Ajouter les mesures DAX (5 min)

> 💡 **Pourquoi ?** Les mesures DAX sont les **KPIs métier** que le CEO veut suivre. Ce sont des formules qui calculent automatiquement les indicateurs à partir des données brutes.
>
> **Pourquoi c'est important :** Sans ces mesures, on aurait juste des lignes de données. Avec les mesures, on a des **réponses business** : "Le MRR est de 847K€", "Le churn est de 2.1%".

### Option A : Via le portail Fabric (Recommandé)

1. Dans le workspace, cliquer sur le semantic model `sm_ceo_dashboard`
2. Cliquer **Open data model** (icône en haut à droite)
3. Dans le panneau de gauche, cliquer sur une table (ex: `fact_subscriptions`)
4. En haut, cliquer **New measure**
5. Dans la barre de formule, coller la mesure
6. Appuyer sur **Entrée** pour valider

> ⚠️ **IMPORTANT** : Les noms de tables dans Fabric peuvent être différents (underscores ou espaces). Vérifiez les noms exacts dans le panneau de gauche avant de copier les formules.

---

### Mesures à créer (copier-coller une par une)

#### 1️⃣ MRR (Monthly Recurring Revenue)
```dax
MRR = 
CALCULATE(
    SUM(fact_subscriptions[monthly_fee]),
    fact_subscriptions[status] = "Active"
)
```

#### 2️⃣ ARR (Annual Recurring Revenue)
```dax
ARR = [MRR] * 12
```

#### 3️⃣ Active Subscribers (Abonnés actifs)
```dax
Active Subscribers = 
CALCULATE(
    COUNTROWS(fact_subscriptions),
    fact_subscriptions[status] = "Active"
)
```

#### 4️⃣ Total Subscribers (Total abonnés)
```dax
Total Subscribers = COUNTROWS(fact_subscriptions)
```

#### 5️⃣ Churn Rate (Taux de résiliation)
```dax
Churn Rate = 
VAR ChurnedCount = CALCULATE(
    COUNTROWS(fact_subscriptions),
    fact_subscriptions[status] = "Churned"
)
VAR TotalCount = COUNTROWS(fact_subscriptions)
RETURN DIVIDE(ChurnedCount, TotalCount, 0)
```

#### 6️⃣ Total Views (Nombre de vues)
```dax
Total Views = SUM(fact_content_views[views])
```

#### 7️⃣ Total Watch Time Hours (Heures de visionnage)
```dax
Total Watch Time Hours = DIVIDE(SUM(fact_content_views[watch_time_minutes]), 60, 0)
```

#### 8️⃣ Avg Completion Rate (Taux de complétion moyen)
```dax
Avg Completion Rate = AVERAGE(fact_content_views[completion_rate])
```

#### 9️⃣ NPS Score (Net Promoter Score)
```dax
NPS Score = 
VAR Promoters = CALCULATE(COUNTROWS(fact_surveys), fact_surveys[score] >= 9)
VAR Detractors = CALCULATE(COUNTROWS(fact_surveys), fact_surveys[score] <= 6)
VAR TotalResponses = COUNTROWS(fact_surveys)
RETURN (DIVIDE(Promoters, TotalResponses, 0) - DIVIDE(Detractors, TotalResponses, 0)) * 100
```

#### 🔟 ARPU (Average Revenue Per User)
```dax
ARPU = DIVIDE([MRR], [Active Subscribers], 0)
```

---

> 💡 **Dépannage** : Si une mesure ne fonctionne pas :
> 1. Vérifiez le nom exact de la table (clic sur la table dans le panneau gauche)
> 2. Vérifiez le nom exact de la colonne (développez la table)
> 3. Remplacez `fact_subscriptions` par le nom réel si différent

### Option B : Via Power BI Desktop

1. Dans le workspace, clic droit sur le semantic model → **Download .pbix**
2. Ouvrir dans Power BI Desktop
3. Onglet **Modeling** → **New measure**
4. Coller les mesures
5. **Publish** vers le workspace

---

## Étape 6 : Créer les rapports Power BI (10 min)

> 💡 **Pourquoi ?** Le rapport Power BI est le **tableau de bord visuel** que le CEO peut consulter à tout moment. C'est la représentation graphique des KPIs.

### 6.1 Créer un nouveau rapport

1. Dans le workspace **CEO-Demo-StreamFlow**
2. Cliquer sur le semantic model `sm_ceo_dashboard`
3. En haut, cliquer **Create report** → **Start from scratch**
4. Une page blanche de rapport s'ouvre

### 6.2 Ajouter les Cards KPI (5 visuels)

Pour chaque KPI, suivre ces étapes :

**Card 1 - MRR :**
1. Dans le panneau **Visualizations** à droite, cliquer sur l'icône **Card** (rectangle avec un chiffre)
2. Un visuel vide apparaît sur le canvas
3. Dans le panneau **Data** à droite, dérouler `fact_subscriptions`
4. Glisser la mesure **MRR** sur le visuel (ou dans le champ "Fields")
5. Le chiffre MRR apparaît !
6. Redimensionner et placer en haut à gauche

**Répéter pour les autres Cards :**
| Card | Mesure à glisser | Position |
|------|------------------|----------|
| Card 2 | `ARR` | Haut, 2ème |
| Card 3 | `Active Subscribers` | Haut, 3ème |
| Card 4 | `Churn Rate` | Haut, 4ème |
| Card 5 | `NPS Score` | Haut, 5ème |

### 6.3 Ajouter le graphique MRR Trend

1. Cliquer sur une zone vide du canvas
2. Dans **Visualizations**, cliquer sur **Line chart** (icône ligne avec points)
3. Configuration :
   - **X-axis** : Glisser `dim_date` → `month` (ou `date_key`)
   - **Y-axis** : Glisser `MRR`
4. Le graphique montre l'évolution du MRR dans le temps
5. Placer sous les Cards, à gauche

### 6.4 Ajouter le graphique Revenue par Région

1. Cliquer sur une zone vide
2. Choisir **Clustered bar chart** (barres horizontales)
3. Configuration :
   - **Y-axis** : Glisser `dim_geography` → `region`
   - **X-axis** : Glisser `MRR`
4. Placer à droite du Line chart

### 6.5 Ajouter le tableau Top Content

1. Cliquer sur une zone vide
2. Choisir **Table** (icône grille)
3. Glisser :
   - `dim_content` → `title`
   - `Total Views`
4. Placer en bas du rapport

### 6.6 Sauvegarder le rapport

1. **File** → **Save**
2. Nom : `CEO Executive Dashboard`
3. Le rapport est maintenant dans le workspace

### 📐 Layout final suggéré

```
┌─────────┬─────────┬─────────┬─────────┬─────────┐
│   MRR   │   ARR   │ Active  │  Churn  │   NPS   │
│  847K€  │ 10.2M€  │  48,234 │   2.1%  │   +42   │
└─────────┴─────────┴─────────┴─────────┴─────────┘
┌──────────────────────┬────────────────────────────┐
│                      │                            │
│   📈 MRR Trend       │   📊 MRR par Région        │
│   (Line Chart)       │   (Bar Chart)              │
│                      │                            │
└──────────────────────┴────────────────────────────┘
┌───────────────────────────────────────────────────┐
│  📋 Top Content (Table)                           │
│  Title                    | Views                 │
│  The Crown               | 125,430               │
│  Breaking News           | 98,234                │
└───────────────────────────────────────────────────┘
```

---

## Étape 7 : Créer le Fabric Data Agent (5 min) ⭐

> 💡 **C'est quoi ?** Le **Fabric Data Agent** est un agent IA dédié à vos données. Il permet au CEO de poser des questions en langage naturel et d'obtenir des réponses instantanées.

### Deux options disponibles :

| Option | Source de données | Avantages | Inconvénients |
|--------|-------------------|-----------|---------------|
| **Option A** | Semantic Model | Mesures DAX prêtes (MRR, Churn...) | Moins flexible |
| **Option B** | Lakehouse | Accès aux données brutes, SQL | Nécessite des instructions détaillées |

---

## Option A : Agent sur Semantic Model (Recommandé pour démo)

> ✅ **Avantage** : Les mesures DAX (MRR, ARR, Churn Rate, NPS) sont déjà calculées. L'agent les comprend directement.

### A.1 Créer l'Agent

1. Dans le workspace **CEO-Demo-StreamFlow**
2. Cliquer **+ New** → **Data Agent**
3. Nom : `StreamFlow CEO Assistant`
4. Description : `Assistant IA pour interroger les données StreamFlow en langage naturel. Posez vos questions sur le MRR, churn, abonnés, NPS et contenus.`
5. Cliquer **Create**

### A.2 Configurer la source de données

1. Cliquer **Add data source**
2. Sélectionner le **Semantic Model** `sm_ceo_dashboard`
3. Cliquer **Confirm**

### A.3 Instructions système (courtes)

```
Tu es un assistant data pour le CEO de StreamFlow, une plateforme de streaming.

Les mesures disponibles sont :
- MRR = Monthly Recurring Revenue
- ARR = Annual Recurring Revenue (MRR × 12)
- Active Subscribers = nombre d'abonnés actifs
- Churn Rate = taux de résiliation
- NPS Score = Net Promoter Score
- Total Views = nombre de visionnages
- Total Watch Time Hours = heures de visionnage

Régions : Europe, North America, Latin America, Asia Pacific, Africa

Réponds de manière concise et professionnelle, comme si tu parlais à un CEO.
```

### A.4 Tester

```
Quel est le MRR ?
```
```
Montre-moi le churn rate par région
```

---

## Option B : Agent sur Lakehouse (Plus puissant)

> ⚠️ **Important** : Le Lakehouse contient les données brutes, pas les mesures DAX. Il faut expliquer à l'agent comment calculer les KPIs.

### B.1 Créer l'Agent

1. Dans le workspace **CEO-Demo-StreamFlow**
2. Cliquer **+ New** → **Data Agent**
3. Nom : `StreamFlow Data Agent`
4. Description : `Agent IA dédié au pilotage de StreamFlow. Permet d'obtenir les KPIs clés (MRR, ARR, Churn, NPS), analyser les performances par région, offre ou contenu.`
5. Cliquer **Create**

### B.2 Configurer les sources de données

1. Cliquer **Add data source**
2. Sélectionner le Lakehouse `lh_streamflow`
3. Cocher toutes les tables :
   - ☑️ `dim_date`
   - ☑️ `dim_geography`
   - ☑️ `dim_customer`
   - ☑️ `dim_offer`
   - ☑️ `dim_content`
   - ☑️ `fact_subscriptions`
   - ☑️ `fact_content_views`
   - ☑️ `fact_marketing`
   - ☑️ `fact_surveys`
4. Cliquer **Confirm**

### B.3 Instructions système (DÉTAILLÉES - IMPORTANT)

> ⚠️ **Ces instructions sont essentielles** pour que l'agent comprenne comment calculer les KPIs à partir des données brutes.

```
Tu es un assistant data pour le CEO de StreamFlow, une plateforme de streaming.

## MAPPING TERMES MÉTIER → COLONNES

Quand on te demande le MRR (Monthly Recurring Revenue) :
→ Calcule : SUM(fact_subscriptions.monthly_fee) WHERE status = 'Active'

Quand on te demande l'ARR (Annual Recurring Revenue) :
→ Calcule : MRR × 12

Quand on te demande le nombre d'abonnés actifs :
→ Calcule : COUNT(*) FROM fact_subscriptions WHERE status = 'Active'

Quand on te demande le taux de churn :
→ Calcule : COUNT(status='Churned') / COUNT(*) FROM fact_subscriptions

Quand on te demande le NPS :
→ Utilise fact_surveys.score
→ Promoteurs = score >= 9, Détracteurs = score <= 6
→ NPS = (% Promoteurs - % Détracteurs) × 100

Quand on te demande les vues ou visionnages :
→ Utilise SUM(fact_content_views.views)

Quand on te demande le temps de visionnage :
→ Utilise SUM(fact_content_views.watch_time_minutes) / 60 pour les heures

## TABLES DISPONIBLES

- fact_subscriptions : customer_key, offer_key, geo_key, monthly_fee, status (Active/Churned), tenure_months, billing_type
- fact_content_views : customer_key, content_key, geo_key, date_key, views, watch_time_minutes, completion_rate, device
- fact_surveys : customer_key, date_key, score (0-10), category
- fact_marketing : geo_key, date_key, channel, spend, impressions, conversions
- dim_customer : customer_key, segment, age_group, acquisition_channel, device_preference
- dim_geography : geo_key, region, country, market_tier
- dim_offer : offer_key, offer_name, monthly_price, tier
- dim_content : content_key, title, type, genre, duration_minutes
- dim_date : date_key, year, quarter, month, month_name

## RELATIONS ENTRE TABLES

- fact_subscriptions.customer_key → dim_customer.customer_key
- fact_subscriptions.geo_key → dim_geography.geo_key
- fact_subscriptions.offer_key → dim_offer.offer_key
- fact_content_views.customer_key → dim_customer.customer_key
- fact_content_views.content_key → dim_content.content_key
- fact_content_views.geo_key → dim_geography.geo_key
- fact_surveys.customer_key → dim_customer.customer_key

## RÉGIONS
Europe, North America, Latin America, Asia Pacific, Africa

## FORMAT DE RÉPONSE
1. Le chiffre avec l'unité (€, %, nombre)
2. Tendance si pertinent
3. Interprétation business courte

Réponds de manière concise et professionnelle, comme si tu parlais à un CEO.
```

### B.4 Tester l'Agent

```
Quelle est la somme des monthly_fee pour les abonnements actifs ?
```
```
Quel est le MRR ?
```
```
Combien d'abonnés avons-nous par région ?
```
```
Quels sont les 5 contenus les plus regardés ?
```
```
Quel est le taux de churn par offre ?
```

### B.5 Partager l'Agent (optionnel)

1. Cliquer **Share** en haut à droite
2. Entrer les emails des personnes à inviter
3. Choisir le niveau d'accès (View, Edit)

---

## ✅ C'est prêt !

Votre rapport Power BI est connecté à Fabric avec toutes les mesures métier.

---

## 🤖 Bonus : Copilot for Power BI dans Fabric

> 💡 **Pourquoi ?** **Copilot for Power BI** est intégré directement dans Fabric. Il permet de poser des questions en langage naturel sur vos données, **sans configuration supplémentaire**. C'est la façon la plus rapide de démontrer "Talk to My Data".

### Comment y accéder

1. Ouvrir votre rapport Power BI dans le workspace Fabric
2. En haut à droite, cliquer sur l'icône **Copilot** (💬)
3. Le panneau Copilot s'ouvre à droite du rapport

### Ce que Copilot for Power BI peut faire

| Capacité | Description |
|----------|-------------|
| **Q&A en langage naturel** | Poser des questions sur les données |
| **Créer des visuels** | "Crée un graphique du MRR par région" |
| **Résumer la page** | "Résume les insights de cette page" |
| **Expliquer les variations** | "Pourquoi le churn a augmenté ?" |

---

### 🧪 Queries de test à essayer

Voici des questions à poser directement à Copilot for Power BI pendant la démo :

#### Questions Revenue (MRR/ARR)

```
Quel est le MRR total ?
```
```
Montre-moi l'évolution du MRR sur les 12 derniers mois
```
```
Quel est l'ARR par région ?
```
```
Compare le MRR de l'Europe vs l'Amérique du Nord
```

#### Questions Subscribers

```
Combien avons-nous d'abonnés actifs ?
```
```
Quel est le taux de churn ?
```
```
Quelle offre a le plus d'abonnés ?
```
```
Montre la répartition des abonnés par région
```

#### Questions Content & Engagement

```
Quels sont les 5 contenus les plus regardés ?
```
```
Quel est le temps de visionnage moyen ?
```
```
Quel genre de contenu performe le mieux ?
```

#### Questions NPS & Satisfaction

```
Quel est le score NPS ?
```
```
Comment évolue le NPS dans le temps ?
```
```
Quelle région a le meilleur NPS ?
```

#### Questions de création de visuels

```
Crée un graphique en barres du MRR par région
```
```
Fais un camembert de la répartition des offres
```
```
Crée un graphique de tendance du churn sur 12 mois
```

#### Questions d'analyse

```
Résume les KPIs principaux de ce dashboard
```
```
Quels sont les insights clés de cette page ?
```
```
Y a-t-il des anomalies dans les données ?
```

---

### 💬 Script de démo suggéré

**Ouvrir le rapport et activer Copilot, puis :**

1. **Question simple :** *"Quel est notre MRR ?"*
   - Montre que Copilot comprend le langage naturel

2. **Question comparative :** *"Compare le MRR de l'Europe vs l'Afrique"*
   - Montre l'analyse comparative

3. **Création de visuel :** *"Crée un graphique du churn par mois"*
   - Montre la génération automatique de visuels

4. **Question stratégique :** *"Quelle région devrait-on prioriser pour la croissance ?"*
   - Montre la capacité d'analyse

5. **Résumé :** *"Résume les points clés de ce dashboard"*
   - Montre la synthèse automatique

---

### ⚠️ Prérequis Copilot for Power BI

- **Capacité Fabric F64 ou supérieure** (ou Power BI Premium P1+)
- **Copilot activé** dans les paramètres tenant
- **Langue anglaise recommandée** pour de meilleurs résultats (le français fonctionne mais l'anglais est plus fiable)

> 💡 **Astuce démo :** Si Copilot n'est pas disponible, utilisez le mode **Q&A classique** de Power BI (icône ❓) qui permet aussi de poser des questions en langage naturel sur les données.

---

## 📊 Résumé : La valeur métier de chaque composant

| Composant | Rôle métier | Analogie |
|-----------|-------------|----------|
| **Workspace** | Espace projet isolé et sécurisé | Comme un bureau privé pour l'équipe |
| **Lakehouse** | Stockage central de toutes les données | L'entrepôt de l'entreprise |
| **Semantic Model** | Couche métier avec KPIs standardisés | Le dictionnaire business |
| **Mesures DAX** | Formules de calcul des KPIs | Les règles de calcul validées par la finance |
| **Power BI** | Tableau de bord visuel | Le cockpit du dirigeant |
| **Copilot for Power BI** | Interface conversationnelle intégrée | L'assistant IA dans le rapport |

> **🎯 Résultat final :** Le CEO peut "parler à ses données" directement dans Power BI et obtenir des réponses instantanées, sans attendre l'analyste, sans ouvrir Excel, sans formation.

---

## Checklist finale

- [ ] Workspace créé
- [ ] Lakehouse avec données
- [ ] Semantic Model avec mesures
- [ ] Rapport Power BI créé
- [ ] Test de Copilot for Power BI

**Temps total : ~15 minutes**

---

## 🚀 Pour aller plus loin : Data Agent → Teams, M365, Web...

> 💡 Le Semantic Model peut alimenter des agents IA accessibles **partout** : Teams, M365 Copilot, Web...

### Architecture simplifiée

```
                    ┌─────────────────┐
                    │ Semantic Model  │  ← Vous êtes ici ✅
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
   ┌───────────┐      ┌─────────────┐     ┌───────────┐
   │ Power BI  │      │Fabric Data  │     │  Copilot  │
   │ + Copilot │      │   Agent     │     │   Studio  │
   └───────────┘      └──────┬──────┘     └─────┬─────┘
         │                   │                  │
    Dans le            ┌─────┴─────┐      ┌─────┴─────┐
    rapport            ▼           ▼      ▼           ▼
                    Teams    M365 Copilot  Web     Mobile
                            (Word/Excel/
                             Outlook)
```

### 3 options pour exposer l'agent

| Option | Effort | Portée |
|--------|--------|--------|
| **Copilot for Power BI** | ✅ Fait | Dans le rapport |
| **Fabric Data Agent** | ~15 min | Teams + M365 Copilot |
| **Copilot Studio** | 1-2h | Teams, Web, Mobile, API... |

### Fabric Data Agent → Teams & M365 (rapide, sans Copilot Studio)

```
Fabric → + New → Data Agent → Connecter au Semantic Model → Publish
```

Le CEO peut ensuite :
- **Dans Teams** : `@DataAgent Quel est le MRR ?`
- **Dans Word/Outlook** : `@DataAgent Compare l'Europe vs Afrique`

### Copilot Studio (personnalisation avancée)

Pour workflows métier, branding custom, web/mobile :
```
copilotstudio.microsoft.com → Create → Add knowledge → Publish
```

> 📌 **Point clé :** La fondation (Lakehouse + Semantic Model) est **réutilisable** pour tous ces scénarios.
