from langchain_community.tools import WikipediaQueryRun, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.tools import Tool
from datetime import datetime, timedelta
import random
from typing import Dict, Any, List, Optional
import json
from config import Config

# --- Utility Tools ---

def save_to_txt(data: str, filename: str = "research_output.txt") -> dict:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_text = f"--- Research Output ---\nTimestamp: {timestamp}\n\n{data}\n\n"
    with open(filename, "a", encoding="utf-8") as f:
        f.write(formatted_text)
    summary = f"Data successfully saved to {filename} at {timestamp}."
    return {
        "summary": summary,
        "topic": "Save Data",
        "tools_used": ["save_text_to_file"],
        "source": [filename]
    }

save_tool = Tool(
    name="save_text_to_file",
    func=save_to_txt,
    description=(
        "Saves structured research data to a text file. "
        "Input: a string containing the data to save. "
        "Returns a confirmation message."
    )
)

search = DuckDuckGoSearchRun()

def search_summary(query: str) -> dict:
    result = search.run(query)
    if isinstance(result, list):
        summary = "\n".join(str(item) for item in result)
    else:
        summary = str(result)
    summary = summary[:1000]
    return {
        "summary": f"### Web Search Results for '{query}':\n{summary}",
        "topic": "Web Search",
        "tools_used": ["web_search"],
        "source": []
    }

search_tool = Tool(
    name="web_search",
    func=search_summary,
    description=(
        "Search the web for information using DuckDuckGo. "
        "Input: a string with the search query. "
        "Returns a dictionary with a detailed summary of the search results."
    )
)

api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=2000)
def wiki_summary(query: str) -> dict:
    result = wiki_tool.run(query)
    return {
        "summary": f"### Wikipedia Summary for '{query}':\n{result}",
        "topic": "Wikipedia Search",
        "tools_used": ["wikipedia"],
        "source": []
    }

wiki_tool = Tool(
    name="wikipedia",
    func=wiki_summary,
    description=(
        "Search Wikipedia for factual information. "
        "Input: a string with the topic to look up. "
        "Returns a summary from Wikipedia."
    )
)

# --- CRM/Agentic Tools ---

def calculate_lead_score(lead_info: Dict[str, Any]) -> float:
    """Calculate a normalized lead score based on configured weights and thresholds."""
    score = 0.0
    scoring_config = Config.LEAD_SCORING
    
    # Deal size scoring
    deal_size = lead_info.get("deal_size", 0)
    if deal_size >= scoring_config["deal_size"]["thresholds"]["high"]:
        size_score = 1.0
    elif deal_size >= scoring_config["deal_size"]["thresholds"]["medium"]:
        size_score = 0.6
    else:
        size_score = 0.3
    score += size_score * scoring_config["deal_size"]["weight"]
    
    # Urgency scoring
    urgency = lead_info.get("urgency", "low").lower()
    urgency_score = scoring_config["urgency"]["values"].get(urgency, 0.3)
    score += urgency_score * scoring_config["urgency"]["weight"]
    
    # Past behavior scoring
    behavior = lead_info.get("past_behavior", "neutral").lower()
    behavior_score = scoring_config["past_behavior"]["values"].get(behavior, 0.5)
    score += behavior_score * scoring_config["past_behavior"]["weight"]
    
    return round(score * 100, 2)

def lead_qualifier_tool(lead_info: Dict[str, Any]) -> Dict[str, Any]:
    """Enhanced lead qualification with detailed analysis and recommendations."""
    score = calculate_lead_score(lead_info)
    
    # Determine segment
    if score >= 70:
        segment = "hot"
        priority = "high"
        recommended_actions = [
            "Schedule immediate follow-up",
            "Prepare customized proposal",
            "Alert senior sales representative"
        ]
    elif score >= 40:
        segment = "warm"
        priority = "medium"
        recommended_actions = [
            "Schedule follow-up within 48 hours",
            "Send relevant case studies",
            "Prepare standard proposal"
        ]
    else:
        segment = "cold"
        priority = "low"
        recommended_actions = [
            "Add to nurture campaign",
            "Schedule follow-up in 1 week",
            "Send company information"
        ]
    
    analysis = {
        "deal_size_analysis": f"Deal size: ${lead_info.get('deal_size', 0):,}",
        "urgency_level": lead_info.get("urgency", "low").capitalize(),
        "historical_engagement": lead_info.get("past_behavior", "neutral").capitalize()
    }
    
    summary = (
        f"### Lead Qualification Results\n"
        f"**Score:** {score}/100\n"
        f"**Segment:** {segment.capitalize()} ({priority.capitalize()} Priority)\n\n"
        f"**Analysis:**\n"
        f"- {analysis['deal_size_analysis']}\n"
        f"- Urgency: {analysis['urgency_level']}\n"
        f"- Historical Engagement: {analysis['historical_engagement']}\n\n"
        f"**Recommended Actions:**\n"
        + "\n".join(f"- {action}" for action in recommended_actions)
    )
    
    return {
        "summary": summary,
        "topic": "Lead Qualification",
        "tools_used": ["lead_qualifier"],
        "source": []
    }

lead_qualifier = Tool(
    name="lead_qualifier",
    func=lead_qualifier_tool,
    description=(
        "Advanced lead scoring and qualification system. "
        "Input: a dictionary with keys: deal_size (int), urgency (str: 'high'/'medium'/'low'), past_behavior (str: 'positive'/'neutral'/'negative'). "
        "Returns detailed qualification analysis with score, segment, and recommendations."
    )
)

def generate_followup_message(template_key: str, context: Dict[str, Any]) -> Dict[str, str]:
    """Generate a personalized follow-up message based on template and context."""
    template_config = Config.FOLLOWUP_TEMPLATES.get(
        template_key,
        Config.FOLLOWUP_TEMPLATES["general"]
    )
    
    # Extract context variables
    name = context.get("name", "Valued Customer")
    custom_message = context.get("custom_message", "")
    interaction_type = context.get("interaction_type", "last interaction")
    
    # Format template
    message = template_config["template"].format(
        name=name,
        custom_message=custom_message,
        interaction_type=interaction_type,
        delay_days=template_config["delay_days"]
    )
    
    return {
        "subject": template_config["subject"],
        "message": message,
        "delay_days": template_config["delay_days"]
    }

def followup_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """Enhanced follow-up system with smart scheduling and personalization."""
    lead_context = args.get("lead_context", {})
    last_interaction = args.get("last_interaction", "").lower()
    
    # Determine template key based on interaction
    template_key = "general"
    if "site" in last_interaction and "visit" in last_interaction:
        template_key = "site_visit"
    elif "quot" in last_interaction:
        template_key = "quotation_sent"
    
    # Generate follow-up content
    followup_content = generate_followup_message(
        template_key,
        {
            "name": lead_context.get("name", "Valued Customer"),
            "custom_message": lead_context.get("custom_message", ""),
            "interaction_type": last_interaction
        }
    )
    
    # Calculate next follow-up date
    next_followup = datetime.now() + timedelta(days=followup_content["delay_days"])
    
    summary = (
        f"### Follow-up Plan\n"
        f"**Subject:** {followup_content['subject']}\n"
        f"**Message:**\n{followup_content['message']}\n"
        f"**Schedule for:** {next_followup.strftime('%Y-%m-%d')}\n"
        f"**Delay:** {followup_content['delay_days']} days"
    )
    
    return {
        "summary": summary,
        "topic": "Follow-up",
        "tools_used": ["followup"],
        "source": []
    }

followup = Tool(
    name="followup",
    func=followup_tool,
    description=(
        "Smart follow-up system with templating and scheduling. "
        "Input: a dictionary with keys: lead_context (dict with 'name', 'custom_message'), last_interaction (str). "
        "Returns personalized message and scheduling recommendations."
    )
)

def select_quotation_template(deal_context: Dict[str, Any]) -> str:
    """Select the most appropriate quotation template based on deal context."""
    deal_size = deal_context.get("base_price", 0)
    customer_type = deal_context.get("customer_type", "regular")
    
    if deal_size >= 100000 or customer_type == "vip":
        return "enterprise"
    elif deal_size >= 50000 or customer_type == "premium":
        return "premium"
    return "standard"

def calculate_adjusted_price(base_price: float, deal_context: Dict[str, Any]) -> float:
    """Calculate adjusted price based on various factors."""
    pricing_factors = Config.QUOTATION_SETTINGS["pricing_factors"]
    
    # Apply urgency multiplier
    urgency = deal_context.get("urgency", "medium").lower()
    urgency_multiplier = pricing_factors["urgency_multiplier"].get(urgency, 1.0)
    
    # Apply customer type discount
    customer_type = deal_context.get("customer_type", "regular").lower()
    customer_multiplier = pricing_factors["customer_type_discount"].get(customer_type, 1.0)
    
    # Calculate final price
    adjusted_price = base_price * urgency_multiplier * customer_multiplier
    return round(adjusted_price, 2)

def quotation_tool(deal_context: Dict[str, Any]) -> Dict[str, Any]:
    """Enhanced quotation generation system with smart template selection and pricing."""
    base_price = deal_context.get("base_price") or deal_context.get("deal_size") or 10000
    template_key = select_quotation_template(deal_context)
    template_config = Config.QUOTATION_SETTINGS["templates"][template_key]
    
    # Calculate adjusted price
    final_price = calculate_adjusted_price(base_price, deal_context)
    
    # Generate quotation details
    quotation_details = {
        "template_name": template_config["name"],
        "customer_type": deal_context.get("customer_type", "regular").capitalize(),
        "base_price": base_price,
        "final_price": final_price,
        "terms": template_config["terms"],
        "delivery": template_config["delivery"],
        "validity": "30 days",
        "special_notes": []
    }
    
    # Add special notes based on context
    if deal_context.get("urgency") == "high":
        quotation_details["special_notes"].append("Expedited delivery available")
    if deal_context.get("customer_type") == "vip":
        quotation_details["special_notes"].append("Premium support included")
    
    summary = (
        f"### Quotation Details\n"
        f"**Template:** {quotation_details['template_name']}\n"
        f"**Customer Type:** {quotation_details['customer_type']}\n"
        f"**Base Price:** ${quotation_details['base_price']:,.2f}\n"
        f"**Final Price:** ${quotation_details['final_price']:,.2f}\n"
        f"**Terms:** {quotation_details['terms']}\n"
        f"**Delivery:** {quotation_details['delivery']}\n"
        f"**Validity:** {quotation_details['validity']}\n"
    )
    if quotation_details["special_notes"]:
        summary += "\n**Special Notes:**\n" + "\n".join(f"- {note}" for note in quotation_details["special_notes"])
    
    return {
        "summary": summary,
        "topic": "Quotation Generation",
        "tools_used": ["quotation"],
        "source": []
    }

quotation = Tool(
    name="quotation",
    func=quotation_tool,
    description=(
        "Advanced quotation generation system with smart template selection and dynamic pricing. "
        "Input: a dictionary with keys: base_price (float), urgency (str), customer_type (str). "
        "Returns detailed quotation with pricing analysis and special terms."
    )
)

def calculate_deal_risk(deal_status: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate deal risk based on various factors."""
    risk_factors = Config.RISK_FACTORS
    risk_score = 0
    risk_reasons = []
    
    # Check inactive days
    inactive_days = deal_status.get("inactive_days", 0)
    if inactive_days >= risk_factors["inactive_days"]:
        risk_score += 0.4
        risk_reasons.append(f"No activity for {inactive_days} days")
    
    # Check price sensitivity
    if deal_status.get("price_sensitivity", 0) >= risk_factors["price_sensitivity_threshold"]:
        risk_score += 0.3
        risk_reasons.append("High price sensitivity")
    
    # Check competitor presence
    if deal_status.get("competitor_mentioned", False):
        risk_score += 0.2
        risk_reasons.append("Competitor actively involved")
    
    # Check response delays
    if deal_status.get("response_delay", 0) >= risk_factors["delayed_response"]:
        risk_score += 0.1
        risk_reasons.append("Delayed responses from prospect")
    
    return {
        "risk_score": round(risk_score, 2),
        "is_at_risk": risk_score >= 0.5,
        "risk_reasons": risk_reasons
    }

def pipeline_manager_tool(deal_status: Dict[str, Any]) -> Dict[str, Any]:
    """Enhanced pipeline management with risk assessment and action recommendations."""
    current_stage = deal_status.get("stage", "lead")
    risk_assessment = calculate_deal_risk(deal_status)
    
    # Determine next actions based on stage and risk
    next_actions = []
    if risk_assessment["is_at_risk"]:
        next_actions.extend([
            "Schedule urgent review meeting",
            "Prepare risk mitigation plan",
            "Consider escalation to senior sales"
        ])
    else:
        stage_idx = Config.PIPELINE_STAGES.index(current_stage)
        if stage_idx < len(Config.PIPELINE_STAGES) - 1:
            next_stage = Config.PIPELINE_STAGES[stage_idx + 1]
            next_actions.append(f"Prepare for {next_stage.replace('_', ' ').title()} stage")
    
    summary = (
        f"### Pipeline Status Update\n"
        f"**Current Stage:** {current_stage.replace('_', ' ').title()}\n"
        f"**Risk Score:** {risk_assessment['risk_score']}\n"
        f"**Status:** {'At Risk' if risk_assessment['is_at_risk'] else 'Healthy'}\n"
    )
    if risk_assessment["risk_reasons"]:
        summary += "**Risk Factors:**\n" + "\n".join(f"- {reason}" for reason in risk_assessment["risk_reasons"]) + "\n"
    if next_actions:
        summary += "\n**Recommended Actions:**\n" + "\n".join(f"- {action}" for action in next_actions)
    
    return {
        "summary": summary,
        "topic": "Pipeline Analysis",
        "tools_used": ["pipeline_manager"],
        "source": []
    }

pipeline_manager = Tool(
    name="pipeline_manager",
    func=pipeline_manager_tool,
    description=(
        "Advanced pipeline management system with risk assessment and action planning. "
        "Input: a dictionary with deal status information including stage, inactive_days, price_sensitivity, etc. "
        "Returns comprehensive pipeline analysis with risk assessment and next steps."
    )
)

def analyze_deal_patterns(deals: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze patterns in successful and lost deals."""
    win_patterns = Config.SALES_COACHING["win_patterns"]
    quick_wins = []
    high_value_wins = []
    
    for deal in deals:
        if deal.get("status") == "won":
            # Analyze quick wins
            if deal.get("days_to_close", float("inf")) <= win_patterns["quick_close"]["days_to_close"]:
                quick_wins.append(deal)
            
            # Analyze high value wins
            if deal.get("value", 0) >= win_patterns["high_value"]["deal_size_threshold"]:
                high_value_wins.append(deal)
    
    return {
        "quick_wins": len(quick_wins),
        "high_value_wins": len(high_value_wins),
        "quick_win_factors": win_patterns["quick_close"]["key_factors"],
        "high_value_factors": win_patterns["high_value"]["key_factors"]
    }

def sales_coach_tool(input_data: Any) -> Dict[str, Any]:
    """Enhanced sales coaching system with pattern analysis and targeted recommendations."""
    coaching_rules = Config.SALES_COACHING
    
    if isinstance(input_data, str):
        # Process single deal feedback
        for reason, tips in coaching_rules["lost_reasons"].items():
            if reason in input_data.lower():
                summary = (
                    f"### Coaching Tips for {reason.capitalize()} Challenge\n"
                    + "\n".join(f"- {tip}" for tip in tips)
                )
                return {
                    "summary": summary,
                    "topic": "Sales Coaching",
                    "tools_used": ["sales_coach"],
                    "source": []
                }
        return {
            "summary": "Tip: Focus on understanding customer needs and pain points.",
            "topic": "Sales Coaching",
            "tools_used": ["sales_coach"],
            "source": []
        }
    
    if isinstance(input_data, list) and input_data:
        # Analyze deal patterns
        patterns = analyze_deal_patterns(input_data)
        
        summary = "### Sales Pattern Analysis\n"
        if patterns["quick_wins"] > 0:
            summary += (
                f"\n**Quick Win Patterns** ({patterns['quick_wins']} deals):\n"
                "Key Success Factors:\n"
                + "\n".join(f"- {factor.replace('_', ' ').title()}" for factor in patterns["quick_win_factors"])
            )
        
        if patterns["high_value_wins"] > 0:
            summary += (
                f"\n**High Value Win Patterns** ({patterns['high_value_wins']} deals):\n"
                "Key Success Factors:\n"
                + "\n".join(f"- {factor.replace('_', ' ').title()}" for factor in patterns["high_value_factors"])
            )
        return {
            "summary": summary,
            "topic": "Sales Coaching",
            "tools_used": ["sales_coach"],
            "source": []
        }
    
    return {
        "summary": "Please provide more specific deal information for targeted coaching.",
        "topic": "Sales Coaching",
        "tools_used": ["sales_coach"],
        "source": []
    }

sales_coach = Tool(
    name="sales_coach",
    func=sales_coach_tool,
    description=(
        "Advanced sales coaching system with pattern analysis and targeted recommendations. "
        "Input: either a string describing a specific situation or a list of deal dictionaries for pattern analysis. "
        "Returns actionable coaching insights and recommendations."
    )
)