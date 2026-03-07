import csv
import json
import requests
from typing import Dict, Any
import time

def call_ollama(prompt: str) -> str:
    """
    Call local Ollama API with Llama 3.2
    """
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2",
                "prompt": prompt,
                "stream": False,
                "format": "json"
            },
            timeout=120
        )
        
        result = response.json()
        return result.get("response", "")
    
    except Exception as e:
        print(f"❌ Ollama error: {e}")
        return None


def analyze_lead(lead: Dict[str, str]) -> Dict[str, Any]:
    """
    Analyze a single lead with Llama 3.2
    """
    
    name = lead.get("Name", "Unknown")
    area = lead.get("Area", "Unknown")
    budget = lead.get("Budget", "Unknown")
    property_type = lead.get("Property_Type", "Unknown")
    
    prompt = f"""You are an elite Dubai real estate AI evaluating a lead. Return ONLY valid JSON. Do not add markdown.

LEAD TO ANALYZE:
- Name: {name}
- Area: {area}
- Budget: {budget} AED/month
- Property Type: {property_type}

RULES:
1. "quality_score" MUST be a decimal (e.g., 8.4, 3.2, 9.1). High score if budget matches area, low score if budget is too small.
2. "agent_notes" MUST be a short, direct command to the agent.

EXAMPLE OUTPUT FORMAT:
{{
  "quality_score": 8.7,
  "area_tier": "Premium",
  "budget_segment": "Mid",
  "urgency": "High",
  "property_recommendation": "1BR Apartment",
  "agent_notes": "Strong budget. Schedule viewing immediately."
}}

Generate the JSON for {name} now:"""

    print(f"Analyzing: {name} ({area})...")
    
    ai_response = call_ollama(prompt)
    
    if not ai_response:
        # Fallback if AI fails
        return {
            "quality_score": 5.0,
            "area_tier": "Unknown",
            "budget_segment": "Unknown",
            "urgency": "Medium",
            "property_recommendation": property_type,
            "agent_notes": "Manual review needed"
        }
    
    try:
        # Clean response
        ai_response = ai_response.strip()
        
        # Remove markdown if present
        if "```" in ai_response:
            ai_response = ai_response.split("```")[1]
            if ai_response.startswith("json"):
                ai_response = ai_response[4:]
        
        # Parse JSON
        analysis = json.loads(ai_response)
        
        print(f"  ✅ Score: {analysis.get('quality_score', 0)}/10")
        
        return analysis
    
    except Exception as e:
        print(f"  ⚠️ Parse error: {e}")
        
        # Return safe fallback
        return {
            "quality_score": 5.0,
            "area_tier": area,
            "budget_segment": f"{budget} AED",
            "urgency": "Medium",
            "property_recommendation": property_type,
            "agent_notes": "AI parsing failed"
        }


def main():
    """
    Process all leads from CSV
    """
    
    print("=" * 60)
    print("AI LEAD ENRICHMENT SYSTEM")
    print("   Model: Llama 3.2 (Local via Ollama)")
    print("=" * 60)
    print()
    
    # Read CSV
    leads = []
    with open("leads.csv", "r") as f:
        reader = csv.DictReader(f)
        leads = list(reader)
    
    print(f"Found {len(leads)} leads to analyze\n")
    
    # Analyze each lead
    enriched_leads = []
    
    for i, lead in enumerate(leads, 1):
        print(f"[{i}/{len(leads)}]", end=" ")
        
        # Get AI analysis
        analysis = analyze_lead(lead)
        
        # Combine original + AI data safely
        enriched = {
            **lead,
            "ai_quality_score": analysis.get("quality_score", 5.0),
            "ai_area_tier": analysis.get("area_tier", "Unknown Tier"),
            "ai_budget_segment": analysis.get("budget_segment", "Unknown Budget"),
            "ai_urgency": analysis.get("urgency", "Medium"),
            "ai_property_rec": analysis.get("property_recommendation", "Standard Review"),
            "ai_agent_notes": analysis.get("agent_notes", "Needs manual review")
        }
        
        enriched_leads.append(enriched)
        
        # Small delay to not overwhelm Ollama
        time.sleep(0.5)
    
    # Save results
    output_file = "enriched_leads.json"
    with open(output_file, "w") as f:
        json.dump(enriched_leads, f, indent=2)
    
    print()
    print("=" * 60)
    print(f"✅ Analysis complete!")
    print(f"Results saved to: {output_file}")
    print()
    
    # Calculate stats
    total = len(enriched_leads)
    avg_score = sum(float(l["ai_quality_score"]) for l in enriched_leads) / total
    high_quality = sum(1 for l in enriched_leads if float(l["ai_quality_score"]) >= 7)
    
    print("STATISTICS:")
    print(f"   Total Analyzed: {total}")
    print(f"   Average Quality Score: {avg_score:.2f}/10")
    print(f"   High Quality Leads (≥7): {high_quality} ({high_quality/total*100:.0f}%)")
    print()
    print("Open dashboard.html in browser to view results!")
    print("=" * 60)


if __name__ == "__main__":
    main()
