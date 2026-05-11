"""
Actionable Insights Generator Module
Uses rule-based templates to generate insights
"""
from typing import Dict, Tuple, List
import re


INSIGHT_TEMPLATES = {
    ("Facilities", "NEGATIVE"): [
        "Issue identified: {entity}. Recommend: Prioritize maintenance and upgrade {category_focus} facilities.",
        "Critical issue: {entity}. Suggested action: Schedule immediate inspection and repair of affected areas.",
        "Complaint regarding {category_focus}: {entity}. Recommended solution: Allocate budget for facility improvements.",
    ],
    ("Facilities", "POSITIVE"): [
        "Positive feedback: {entity}. Recommended action: Continue maintenance standards for {category_focus}.",
        "Strength identified: {entity}. Suggestion: Document best practices and maintain current facility standards.",
    ],
    ("Facilities", "NEUTRAL"): [
        "Neutral feedback noted regarding {category_focus}: {entity}. Recommended action: Monitor similar feedback before taking major action.",
    ],
    ("Teaching Quality", "NEGATIVE"): [
        "Teaching concern: {entity}. Recommended action: Provide professional development workshops for faculty.",
        "Issue noted: {entity}. Suggested action: Review course design and implement student-centered teaching methods.",
        "Complaint: {entity}. Recommendation: Offer faculty training on {category_focus} and student engagement.",
    ],
    ("Teaching Quality", "POSITIVE"): [
        "Excellent teaching practice noted: {entity}. Recommendation: Recognize and reward outstanding faculty.",
        "Strength: {entity}. Suggested action: Use as model for faculty development programs.",
    ],
    ("Teaching Quality", "NEUTRAL"): [
        "Neutral teaching-related feedback noted: {entity}. Recommended action: Review if similar comments appear repeatedly.",
    ],
    ("Student Services", "NEGATIVE"): [
        "Service gap identified: {entity}. Recommended action: Increase staffing and resources for {category_focus}.",
        "Issue noted: {entity}. Suggestion: Implement efficiency improvements in {category_focus} operations.",
        "Complaint: {entity}. Recommendation: Streamline processes and improve response times.",
    ],
    ("Student Services", "POSITIVE"): [
        "Positive feedback: {entity}. Recommendation: Continue excellent service delivery.",
        "Strength identified: {entity}. Suggested action: Maintain current service excellence.",
    ],
    ("Student Services", "NEUTRAL"): [
        "Neutral student services feedback noted: {entity}. Recommended action: Track recurring mentions for possible improvement.",
    ],
    ("Infrastructure", "NEGATIVE"): [
        "Infrastructure issue: {entity}. Recommended action: IT department should investigate and upgrade {category_focus} systems.",
        "Problem identified: {entity}. Suggestion: Conduct IT audit and implement infrastructure improvements.",
        "Complaint: {entity}. Recommendation: Allocate budget for {category_focus} infrastructure upgrades.",
    ],
    ("Infrastructure", "POSITIVE"): [
        "Infrastructure strength: {entity}. Recommendation: Maintain current systems and plan for future scalability.",
    ],
     ("Infrastructure", "NEUTRAL"): [
        "Neutral infrastructure feedback noted: {entity}. Recommended action: Monitor system-related comments for recurring patterns.",
    ],
    ("Administrative Services", "NEGATIVE"): [
        "Administrative process issue: {entity}. Recommended action: Streamline {category_focus} procedures.",
        "Complaint: {entity}. Suggestion: Review and improve administrative efficiency.",
        "Issue identified: {entity}. Recommendation: Implement process improvements in {category_focus}.",
    ],
    ("Administrative Services", "POSITIVE"): [
        "Positive feedback: {entity}. Recommendation: Continue excellent administrative service.",
    ],
    ("Administrative Services", "NEUTRAL"): [
        "Neutral administrative feedback noted: {entity}. Recommended action: Observe if this becomes a recurring concern.",
    ],
    ("Other", "NEGATIVE"): [
        "Issue noted: {entity}. Recommendation: Investigate and take appropriate action.",
    ],
    ("Other", "POSITIVE"): [
        "Positive feedback: {entity}. Recommendation: Continue supporting student experience.",
    ],
     ("Other", "NEUTRAL"): [
        "Neutral or low-information feedback received: {entity}. Recommended action: No immediate action needed; collect more detailed feedback if repeated.",
    ],
}

PRIORITY_LEVELS = {
    "POSITIVE": "Low",
    "NEGATIVE": "High"
}

DEPARTMENT_MAPPING = {
    "Facilities": "Facilities Management",
    "Teaching Quality": "Academic Affairs",
    "Student Services": "Student Services",
    "Infrastructure": "Information Technology",
    "Administrative Services": "Administration",
    "Other": "Administration"
}


def generate_insight(feedback_data: Dict) -> Dict[str, any]:
    """
    Generate actionable insight from processed feedback.
    
    Args:
        feedback_data: Dictionary with sentiment_label, primary_topic, confidence,
                      feedback_text, emotion_tags
                      
    Returns:
        Dictionary with insight_text, priority_level, assigned_department, confidence
    """
    sentiment = feedback_data.get("sentiment_label", "NEUTRAL")
    topic = feedback_data.get("primary_topic", "Other")
    text = feedback_data.get("feedback_text", "")
    
    # Get template key
    template_key = (topic, sentiment)
    
    # Fallback if key not found
    if template_key not in INSIGHT_TEMPLATES:
        template_key = ("Other", sentiment)
    
    # Get templates
    templates = INSIGHT_TEMPLATES.get(template_key, INSIGHT_TEMPLATES[("Other", "NEGATIVE")])
    
    # Select template (use first one for simplicity)
    template = templates[0] if templates else "Feedback noted: {entity}. Recommendation: Take appropriate action."
    
    # Extract entities/problems
    entities = _extract_key_entities(text, topic)
    if sentiment == "NEUTRAL" and "low_information" in feedback_data.get("emotion_tags", []):
        entity_str = "brief feedback with limited context"
    else:
        entity_str = entities[0] if entities else "general feedback"
    
    # Format insight
    insight_text = template.format(
        entity=entity_str,
        category_focus=topic.lower()
    )
    
    # Determine priority
    priority_level = _calculate_priority(sentiment, feedback_data)
    
    # Assign department
    assigned_department = DEPARTMENT_MAPPING.get(topic, "Administration")
    
    return {
        "insight_text": insight_text,
        "priority_level": priority_level,
        "assigned_department": assigned_department,
        "confidence": feedback_data.get("confidence", 0.0),
        "topic": topic,
        "sentiment": sentiment
    }


def _extract_key_entities(text: str, topic: str) -> List[str]:
    """
    Extract key entities/problems from feedback text.
    
    Args:
        text: Feedback text
        topic: Primary topic/category
        
    Returns:
        List of key entities
    """
    entities = []
    
    # Common complaint patterns
    complaint_patterns = [
        r"(?:is|are)\s+(?:very\s+)?(\w+(?:\s+\w+)?)",  # "is [very] adjective noun"
        r"(?:the\s+)?(\w+(?:\s+\w+)?)\s+(?:is|are)\s+",  # "the noun is"
        r"(?:need|needed?|require)\s+(?:more\s+)?(\w+(?:\s+\w+)?)",  # "need/required noun"
    ]
    
    for pattern in complaint_patterns:
        matches = re.findall(pattern, text.lower())
        entities.extend(matches)
    
    # Clean and deduplicate
    entities = list(set(entities))[:3]
    
    return entities if entities else ["improvements"]


def _calculate_priority(sentiment: str, feedback_data: Dict) -> str:
    """
    Calculate priority level based on sentiment and other factors.
    
    Args:
        sentiment: POSITIVE, NEGATIVE, or NEUTRAL
        feedback_data: Additional feedback data for context
        
    Returns:
        Priority level: Critical, High, Medium, or Low
    """
    emotion_tags = feedback_data.get("emotion_tags", [])
    
    if sentiment == "NEGATIVE":
        # Check for urgent emotion tags
        if "urgency" in emotion_tags or "concern" in emotion_tags:
            return "Critical"
        elif "complaint" in emotion_tags or "frustration" in emotion_tags:
            return "High"
        else:
            return "Medium"
    elif sentiment == "POSITIVE":
        return "Low"
    else:
        return "Medium"
