"""LLM integrations — behind USE_REAL_GEMINI toggle."""
from . import config


def gemini_research_plan(brief, budget, market):
    from google import genai

    client = genai.Client()
    valid = "resale_demand, search_interest, material_composition, lca_impact, market_benchmark"
    prompt = (
        f"Decompose this fashion-sustainability research brief into 4-5 data needs.\n"
        f"Brief: {brief}\nMarket: {market}\nBudget (EUR): {budget}\n"
        f"Each need's `name` MUST be one of: {valid}.\n"
        f"Return JSON with keys: market, needs (list of objects with "
        f"name, rationale (one sentence: why we need it), tags (list of strings))."
    )
    response = client.models.generate_content(
        model=config.GEMINI_TEXT_MODEL,
        contents=prompt,
    )
    import json
    text = response.text
    start, end = text.find("{"), text.rfind("}") + 1
    return json.loads(text[start:end])
