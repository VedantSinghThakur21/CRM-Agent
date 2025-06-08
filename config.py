from typing import Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys and Authentication
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    # CRM Integration Settings
    CRM_BASE_URL = os.getenv("CRM_BASE_URL", "http://localhost:3000")
    CRM_API_KEY = os.getenv("CRM_API_KEY")
    
    # Lead Scoring Weights
    LEAD_SCORING: Dict[str, Dict[str, Any]] = {
        "deal_size": {
            "weight": 0.4,
            "thresholds": {
                "high": 50000,
                "medium": 10000,
                "low": 0
            }
        },
        "urgency": {
            "weight": 0.3,
            "values": {
                "high": 1.0,
                "medium": 0.6,
                "low": 0.3
            }
        },
        "past_behavior": {
            "weight": 0.3,
            "values": {
                "positive": 1.0,
                "neutral": 0.5,
                "negative": 0.2
            }
        }
    }
    
    # Follow-up Templates
    FOLLOWUP_TEMPLATES = {
        "site_visit": {
            "subject": "Thank you for your time during the site visit",
            "delay_days": 3,
            "template": "Hi {name}, thank you for your time during the site visit. {custom_message} We'll follow up in {delay_days} days."
        },
        "quotation_sent": {
            "subject": "Following up on our quotation",
            "delay_days": 2,
            "template": "Hi {name}, I wanted to follow up on the quotation we sent. {custom_message} Would you like to discuss any aspects in detail?"
        },
        "general": {
            "subject": "Checking in",
            "delay_days": 5,
            "template": "Hi {name}, just checking in after our {interaction_type}. {custom_message}"
        }
    }
    
    # Quotation Settings
    QUOTATION_SETTINGS = {
        "templates": {
            "standard": {
                "name": "Standard Quotation",
                "terms": "Net 30 days",
                "delivery": "7 days"
            },
            "premium": {
                "name": "Premium Service Quotation",
                "terms": "Net 45 days",
                "delivery": "3 days"
            },
            "enterprise": {
                "name": "Enterprise Solution",
                "terms": "Custom terms",
                "delivery": "Negotiable"
            }
        },
        "pricing_factors": {
            "urgency_multiplier": {
                "high": 1.15,
                "medium": 1.0,
                "low": 0.95
            },
            "customer_type_discount": {
                "vip": 0.90,
                "regular": 1.0,
                "new": 1.05
            }
        }
    }
    
    # Pipeline Stages and Risk Factors
    PIPELINE_STAGES = [
        "lead",
        "qualified",
        "meeting_scheduled",
        "proposal_sent",
        "negotiation",
        "closed_won",
        "closed_lost"
    ]
    
    RISK_FACTORS = {
        "inactive_days": 14,
        "price_sensitivity_threshold": 0.2,
        "competitor_mentioned": True,
        "delayed_response": 7
    }
    
    # Sales Coaching Rules
    SALES_COACHING = {
        "lost_reasons": {
            "price": [
                "Emphasize value proposition and ROI",
                "Explore flexible payment terms",
                "Highlight cost-saving features"
            ],
            "competition": [
                "Focus on unique differentiators",
                "Emphasize customer success stories",
                "Highlight superior support and service"
            ],
            "timing": [
                "Discuss phased implementation",
                "Offer early-bird incentives",
                "Present case studies with quick deployment"
            ]
        },
        "win_patterns": {
            "quick_close": {
                "days_to_close": 30,
                "key_factors": ["urgency", "clear_budget", "decision_maker"]
            },
            "high_value": {
                "deal_size_threshold": 100000,
                "key_factors": ["roi_discussion", "multiple_stakeholders", "pilot_program"]
            }
        }
    } 