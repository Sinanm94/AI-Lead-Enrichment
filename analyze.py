import csv
import json
import requests
from typing import Dict, Any
import time


# ============================================================
# FUNCTION 1: Call Ollama API
# ============================================================
def call_ollama(prompt: str) -> str:
    """
    Call local Ollama API with Llama 3.2
    """
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2",  # <--- Upgrade to the 8B model
                "prompt": prompt,
                "stream": False,
                "format": "json"
            },
            timeout=120  # <--- Bump to 2 minutes so the RAM doesn't time out
        )
        
        result = response.json()
        return result.get("response", "")
    
    except Exception as e:
        print(f"    ❌ Ollama error: {e}")
        return None


# ============================================================
# FUNCTION 2: Calculate Quality Score (Deterministic)
# ============================================================
def calculate_quality_score(area: str, budget: int, property_type: str) -> float:
    """
    Deterministic scoring based on Dubai market data.
    No AI - pure logic.
    """
    
    # Market ranges (mid-point AED/month)
    market_data = {
        # Premium
        "burj khalifa": {"studio": 10000, "1br": 20000, "2br": 32500, "penthouse": 70000},
        "palm jumeirah": {"villa": 42500, "2br": 24000},
        "jbr": {"studio": 7500, "1br": 12500, "2br": 20000},
        "dubai marina": {"studio": 6500, "1br": 9500, "2br": 16000, "apartment": 9500},
        "downtown": {"studio": 8500, "1br": 15000, "2br": 24000},
        
        # Mid-range
        "business bay": {"studio": 5000, "1br": 8000, "2br": 13000, "apartment": 8000},
        "jumeirah": {"1br": 10000, "villa": 20000, "apartment": 10000},
        "dubai hills": {"studio": 6000, "1br": 9000, "townhouse": 16000, "apartment": 9000},
        "greens": {"studio": 5000, "1br": 7500, "apartment": 7500},
        "arabian ranches": {"villa": 15000, "apartment": 12000},
        
        # Affordable
        "deira": {"studio": 2750, "1br": 4250, "apartment": 4250},
        "bur dubai": {"studio": 3250, "1br": 4500, "apartment": 4500},
        "karama": {"studio": 2750, "1br": 3750, "apartment": 3750},
        "al barsha": {"studio": 4000, "1br": 5250, "apartment": 5250},
        "silicon oasis": {"studio": 4000, "1br": 5750, "2br": 7500, "apartment": 5750},
        "motor city": {"studio": 4250, "1br": 6000, "apartment": 6000},
        "discovery gardens": {"studio": 3750, "1br": 5000, "apartment": 5000},
        "al quoz": {"studio": 3250, "1br": 4500, "apartment": 4500},
        "mirdif": {"studio": 5000, "1br": 6750, "apartment": 6750},
        "al nasr": {"studio": 3500, "1br": 5000, "2br": 7000, "apartment": 5000},
    }
    
    # Normalize inputs
    area_clean = area.lower().strip()
    prop_clean = property_type.lower().strip()
    
    # Infer property type
    if "studio" in prop_clean:
        prop_key = "studio"
    elif "1br" in prop_clean or "1 br" in prop_clean:
        prop_key = "1br"
    elif "2br" in prop_clean or "2 br" in prop_clean:
        prop_key = "2br"
    elif "villa" in prop_clean:
        prop_key = "villa"
    elif "penthouse" in prop_clean:
        prop_key = "penthouse"
    elif "townhouse" in prop_clean:
        prop_key = "townhouse"
    else:
        # Default to apartment
        prop_key = "apartment"
    
    # Get market price
    if area_clean in market_data:
        area_prices = market_data[area_clean]
        
        if prop_key in area_prices:
            market_price = area_prices[prop_key]
        else:
            # Fallback to average
            market_price = sum(area_prices.values()) / len(area_prices)
    else:
        # Unknown area - assume mid-range
        market_price = 6000
    
    # Calculate budget ratio
    try:
        budget_int = int(budget)
    except:
        return 5.0
    
    ratio = budget_int / market_price
    
    # Score based on ratio
    if ratio >= 1.5:
        score = 9.0 + min(ratio - 1.5, 1.0)
    elif ratio >= 1.2:
        score = 8.0 + (ratio - 1.2) * 3
    elif ratio >= 0.9:
        score = 7.0 + (ratio - 0.9) * 3
    elif ratio >= 0.7:
        score = 5.5 + (ratio - 0.7) * 7.5
    elif ratio >= 0.5:
        score = 3.5 + (ratio - 0.5) * 10
    else:
        score = 1.0 + min(ratio, 0.5) * 5
    
    return round(min(score, 10.0), 1)


# ============================================================
# FUNCTION 3: Analyze Lead (Hybrid Approach)
# ============================================================
def analyze_lead_hybrid(lead: Dict[str, str]) -> Dict[str, Any]:
    """
    HYBRID: Python calculates score, LLM generates text
    """
    
    name = lead.get("Name", "Unknown")
    area = lead.get("Area", "Unknown")
    budget = lead.get("Budget", "0")
    property_type = lead.get("Property_Type", "Unknown")
    
    # Step 1: Calculate score with deterministic logic
    quality_score = calculate_quality_score(area, budget, property_type)
    
    print(f"🤖 Analyzing: {name} ({area}, {budget} AED)")
    print(f"  📊 Calculated Score: {quality_score}/10")
    
    # Step 2: Use LLM for text generation
    prompt = f"""You are a Dubai real estate agent. A lead was scored {quality_score}/10.

Lead:
- Area: {area}
- Budget: {budget} AED/month
- Property: {property_type}
- Quality Score: {quality_score}/10

Generate agent notes based on score:
- Score 9-10: "Premium buyer, immediate priority"
- Score 7-8: "Strong lead, prioritize follow-up"
- Score 5-6: "Standard prospect, normal follow-up"
- Score 3-4: "Budget concerns, suggest alternatives"
- Score 1-2: "Unrealistic budget, educate on market"

Return ONLY this JSON:
{{
  "area_tier": "Premium/Mid-Range/Affordable",
  "budget_segment": "Luxury/Standard/Budget/Unrealistic",
  "urgency": "High/Medium/Low",
  "property_recommendation": "specific property type",
  "agent_notes": "one actionable sentence"
}}"""
    
    ai_response = call_ollama(prompt)
    
    if not ai_response:
        # Fallback
        return {
            "quality_score": quality_score,
            "area_tier": "Unknown",
            "budget_segment": "Unknown",
            "urgency": "Medium",
            "property_recommendation": property_type,
            "agent_notes": f"Score: {quality_score}/10 - Manual review"
        }
    
    try:
        # Clean response
        ai_response = ai_response.strip()
        if "```" in ai_response:
            parts = ai_response.split("```")
            for part in parts:
                if "{" in part:
                    ai_response = part.strip()
                    if ai_response.startswith("json"):
                        ai_response = ai_response[4:].strip()
                    break
        
        analysis = json.loads(ai_response)
        analysis["quality_score"] = quality_score  # Use our score
        
        print(f"  ✅ Final: {quality_score}/10 | {analysis.get('budget_segment', 'N/A')}")
        
        return analysis
    
    except Exception as e:
        print(f"  ⚠️ LLM text generation failed: {e}")
        
        return {
            "quality_score": quality_score,
            "area_tier": "Unknown",
            "budget_segment": "Unknown",
            "urgency": "Medium",
            "property_recommendation": property_type,
            "agent_notes": f"Quality score: {quality_score}/10"
        }


# ============================================================
# MAIN FUNCTION
# ============================================================
def main():
    print("=" * 60)
    print("🚀 AI LEAD ENRICHMENT SYSTEM (HYBRID)")
    print("   Scoring: Deterministic Python Logic")
    print("   Text: Llama 3.2 (Local)")
    print("=" * 60)
    print()
    
    # Check CSV
    print("DEBUG: Checking for leads.csv...")
    try:
        with open("leads.csv", "r") as f:
            reader = csv.DictReader(f)
            leads = list(reader)
        print(f"✅ Found {len(leads)} leads")
    except Exception as e:
        print(f"❌ ERROR reading CSV: {e}")
        return
    
    print()
    
    # Test first lead
    print("DEBUG: Testing analysis on first lead...")
    test_lead = leads[0]
    print(f"  Lead: {test_lead}")
    print()
    
    try:
        print("  Calling analyze_lead_hybrid...")
        analysis = analyze_lead_hybrid(test_lead)
        print(f"  ✅ Got result: {analysis}")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print()
    print("DEBUG: First lead worked! Processing all...")
    print()
    
    # Process all
    enriched_leads = []
    
    for i, lead in enumerate(leads, 1):
        print(f"[{i}/{len(leads)}]", end=" ")
        
        try:
            analysis = analyze_lead_hybrid(lead)
            
            enriched = {
                **lead,
                "ai_quality_score": analysis["quality_score"],
                "ai_area_tier": analysis.get("area_tier", "Unknown"),
                "ai_budget_segment": analysis.get("budget_segment", "Unknown"),
                "ai_urgency": analysis.get("urgency", "Medium"),
                "ai_property_rec": analysis.get("property_recommendation", "Review"),
                "ai_agent_notes": analysis.get("agent_notes", "Manual review")
            }
            
            enriched_leads.append(enriched)
            
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            continue
        
        time.sleep(0.3)
    
    # Save
    print()
    print("Saving results...")
    with open("enriched_leads.json", "w") as f:
        json.dump(enriched_leads, f, indent=2)
    
    print("✅ Saved!")
    print()
    
    # Stats
    if enriched_leads:
        total = len(enriched_leads)
        avg_score = sum(float(l["ai_quality_score"]) for l in enriched_leads) / total
        high_quality = sum(1 for l in enriched_leads if float(l["ai_quality_score"]) >= 7)
        
        print("=" * 60)
        print("📊 STATISTICS:")
        print(f"   Total: {total}")
        print(f"   Avg Score: {avg_score:.2f}/10")
        print(f"   High Quality (≥7): {high_quality} ({high_quality/total*100:.0f}%)")
        print()
        print("🌐 Open dashboard.html to view!")
        print("=" * 60)


if __name__ == "__main__":
    main()