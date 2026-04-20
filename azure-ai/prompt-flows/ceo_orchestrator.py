"""
CEO Data Agent - Orchestrator Prompt Flow
Advanced orchestration with RAG capabilities for strategic questions
"""

import os
import json
from typing import Optional
from promptflow import tool
from promptflow.connections import AzureOpenAIConnection
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

FABRIC_QUERIES = {
    "revenue": {
        "measures": ["MRR", "ARR", "MRR Growth MoM", "MRR Growth YoY"],
        "description": "Revenue and financial metrics"
    },
    "subscribers": {
        "measures": ["Active Subscribers", "Churn Rate", "Net Subscriber Growth"],
        "description": "Subscriber and retention metrics"
    },
    "content": {
        "measures": ["Total Views", "Total Watch Time Hours", "Content ROI"],
        "description": "Content performance metrics"
    },
    "marketing": {
        "measures": ["Total Marketing Spend", "CPA (Cost per Acquisition)", "ROAS"],
        "description": "Marketing efficiency metrics"
    },
    "satisfaction": {
        "measures": ["NPS Score", "Average Survey Score"],
        "description": "Customer satisfaction metrics"
    }
}


# ═══════════════════════════════════════════════════════════════
# TOOLS
# ═══════════════════════════════════════════════════════════════

@tool
def classify_intent(question: str, connection: AzureOpenAIConnection) -> dict:
    """
    Classify user intent to determine routing
    
    Returns:
        dict with 'intent' (data|strategic|hybrid) and 'topics' list
    """
    from openai import AzureOpenAI
    
    client = AzureOpenAI(
        azure_endpoint=connection.api_base,
        api_key=connection.api_key,
        api_version="2024-02-15-preview"
    )
    
    system_prompt = """You are an intent classifier for a CEO Data Agent.
    
Classify the user's question into one of these intents:
- "data": Questions about metrics, KPIs, numbers (queries Fabric semantic model)
- "strategic": Questions about strategy, recommendations, analysis (uses RAG on documents)
- "hybrid": Questions that need both data AND strategic context

Also identify relevant topics: revenue, subscribers, content, marketing, satisfaction

Respond in JSON format:
{
    "intent": "data|strategic|hybrid",
    "topics": ["topic1", "topic2"],
    "reasoning": "brief explanation"
}"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ],
        response_format={"type": "json_object"},
        max_tokens=200
    )
    
    return json.loads(response.choices[0].message.content)


@tool
def query_fabric_semantic_model(
    topics: list,
    workspace_id: str,
    model_id: str
) -> dict:
    """
    Query Fabric Semantic Model for relevant metrics
    
    Note: This is a simplified version. In production, use 
    Fabric REST API or direct DAX queries.
    """
    import requests
    from msal import ConfidentialClientApplication
    
    # Collect relevant measures based on topics
    all_measures = []
    for topic in topics:
        if topic in FABRIC_QUERIES:
            all_measures.extend(FABRIC_QUERIES[topic]["measures"])
    
    # Remove duplicates
    all_measures = list(set(all_measures))
    
    # In a real implementation, this would:
    # 1. Authenticate to Fabric
    # 2. Execute DAX query
    # 3. Return actual data
    
    # Placeholder response for demo
    mock_data = {
        "MRR": "€847,500",
        "ARR": "€10,170,000",
        "MRR Growth MoM": "+2.3%",
        "MRR Growth YoY": "+18.5%",
        "Active Subscribers": "48,250",
        "Churn Rate": "2.1%",
        "Net Subscriber Growth": "+1,250",
        "Total Views": "2,850,000",
        "Total Watch Time Hours": "4,750,000",
        "Content ROI": "156%",
        "Total Marketing Spend": "€285,000",
        "CPA (Cost per Acquisition)": "€42.50",
        "ROAS": "3.8x",
        "NPS Score": "42",
        "Average Survey Score": "7.8"
    }
    
    return {
        "measures_requested": all_measures,
        "data": {k: v for k, v in mock_data.items() if k in all_measures}
    }


@tool
def search_strategic_documents(
    question: str,
    search_endpoint: str,
    index_name: str,
    top_k: int = 3
) -> list:
    """
    Search strategic documents using Azure AI Search (RAG)
    """
    credential = DefaultAzureCredential()
    
    client = SearchClient(
        endpoint=search_endpoint,
        index_name=index_name,
        credential=credential
    )
    
    results = client.search(
        search_text=question,
        select=["title", "content", "source"],
        top=top_k,
        query_type="semantic",
        semantic_configuration_name="default"
    )
    
    documents = []
    for result in results:
        documents.append({
            "title": result["title"],
            "content": result["content"][:500],  # Truncate for context
            "source": result["source"]
        })
    
    return documents


@tool
def generate_response(
    question: str,
    intent: str,
    fabric_data: Optional[dict],
    strategic_docs: Optional[list],
    connection: AzureOpenAIConnection
) -> str:
    """
    Generate final response combining data and context
    """
    from openai import AzureOpenAI
    
    client = AzureOpenAI(
        azure_endpoint=connection.api_base,
        api_key=connection.api_key,
        api_version="2024-02-15-preview"
    )
    
    # Build context
    context_parts = []
    
    if fabric_data and fabric_data.get("data"):
        data_str = "\n".join([f"- {k}: {v}" for k, v in fabric_data["data"].items()])
        context_parts.append(f"## Current Metrics (from Fabric)\n{data_str}")
    
    if strategic_docs:
        docs_str = "\n\n".join([
            f"### {doc['title']}\n{doc['content']}\n*Source: {doc['source']}*"
            for doc in strategic_docs
        ])
        context_parts.append(f"## Strategic Documents\n{docs_str}")
    
    context = "\n\n".join(context_parts) if context_parts else "No additional context available."
    
    system_prompt = f"""You are the CEO Data Agent for StreamFlow, a streaming platform.
    
You have access to real-time business metrics and strategic documents.

CONTEXT:
{context}

GUIDELINES:
- Be concise and executive-focused
- Lead with key numbers when relevant
- Provide actionable insights
- Use tables for comparisons
- Flag concerns with ⚠️ and successes with ✅
- End with a recommended action if appropriate"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ],
        max_tokens=1000
    )
    
    return response.choices[0].message.content


# ═══════════════════════════════════════════════════════════════
# MAIN FLOW
# ═══════════════════════════════════════════════════════════════

@tool
def ceo_orchestrator(
    question: str,
    connection: AzureOpenAIConnection,
    workspace_id: str = "",
    model_id: str = "",
    search_endpoint: str = "",
    index_name: str = ""
) -> str:
    """
    Main orchestrator that routes and processes CEO questions
    """
    
    # Step 1: Classify intent
    intent_result = classify_intent(question, connection)
    intent = intent_result.get("intent", "data")
    topics = intent_result.get("topics", ["revenue"])
    
    # Step 2: Gather context based on intent
    fabric_data = None
    strategic_docs = None
    
    if intent in ["data", "hybrid"] and workspace_id and model_id:
        fabric_data = query_fabric_semantic_model(topics, workspace_id, model_id)
    
    if intent in ["strategic", "hybrid"] and search_endpoint and index_name:
        strategic_docs = search_strategic_documents(question, search_endpoint, index_name)
    
    # Step 3: Generate response
    response = generate_response(
        question=question,
        intent=intent,
        fabric_data=fabric_data,
        strategic_docs=strategic_docs,
        connection=connection
    )
    
    return response


# ═══════════════════════════════════════════════════════════════
# STANDALONE TESTING
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Test intent classification
    test_questions = [
        "What is our current MRR?",
        "How should we reduce churn in Europe?",
        "What's our revenue and how does it compare to our strategic goals?"
    ]
    
    for q in test_questions:
        print(f"\nQ: {q}")
        # In production, this would use actual connections
        print("(Requires Azure OpenAI connection for testing)")
