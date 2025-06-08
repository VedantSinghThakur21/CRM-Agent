# Agentic CRM Assistant

An intelligent CRM assistant powered by LangChain and Google's Gemini model, designed to enhance sales team productivity and effectiveness.

## Features

### 1. Lead Qualification & Prioritization
- Automated lead scoring using multiple factors (deal size, urgency, past behavior)
- Smart segmentation into hot, warm, and cold leads
- Detailed analysis and recommended actions for each lead
- Configurable scoring weights and thresholds

### 2. Outbound & Follow-up Automation
- Personalized message generation based on interaction context
- Smart scheduling with optimal follow-up timing
- Template-based communication with dynamic content
- Multi-channel support (email, messages, WhatsApp)

### 3. Quotation Assistant
- Intelligent template selection based on deal context
- Dynamic pricing with configurable factors
- Special terms and conditions based on customer type
- Automated validity and delivery terms

### 4. Pipeline Management
- Advanced risk assessment and early warning system
- Stage progression tracking and recommendations
- Activity logging and deal health monitoring
- Automated notifications for at-risk deals

### 5. Sales Coaching & Insights
- Pattern analysis of successful and lost deals
- Actionable recommendations based on historical data
- Win/loss analysis with targeted improvement suggestions
- Performance tracking and best practices sharing

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with required credentials:
   ```env
   GOOGLE_API_KEY=your_google_api_key
   CRM_BASE_URL=your_crm_base_url
   CRM_API_KEY=your_crm_api_key
   ```

## Configuration

The system is highly configurable through the `config.py` file:

- Lead scoring weights and thresholds
- Follow-up templates and timing
- Quotation templates and pricing rules
- Pipeline stages and risk factors
- Sales coaching rules and patterns

## Integration with Web CRM

The assistant is designed to integrate seamlessly with your existing web-based CRM through:

1. REST API endpoints
2. Webhook notifications
3. Database synchronization
4. Real-time event processing

## Usage Examples

### Lead Qualification
```python
lead_info = {
    "deal_size": 50000,
    "urgency": "high",
    "past_behavior": "positive"
}
result = lead_qualifier_tool(lead_info)
```

### Follow-up Generation
```python
context = {
    "lead_context": {
        "name": "John Smith",
        "custom_message": "Thanks for your interest in our enterprise solution"
    },
    "last_interaction": "site visit"
}
result = followup_tool(context)
```

### Quotation Generation
```python
deal_context = {
    "base_price": 75000,
    "urgency": "high",
    "customer_type": "vip"
}
result = quotation_tool(deal_context)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - feel free to use this in your own projects! 
