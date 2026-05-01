"""
Topic/Category Extraction Module
"""
from typing import Tuple, List, Dict
import re


CATEGORY_KEYWORDS = {
    "Facilities": [
        "library", "classroom", "building", "lab", "laboratory", "parking",
        "restroom", "bathroom", "air conditioning", "ac", "heat", "heating",
        "desk", "chair", "table", "lighting", "light", "clean", "maintenance",
        "equipment", "furniture", "cafeteria", "canteen", "lounge"
    ],
    "Teaching Quality": [
        "professor", "instructor", "teacher", "lecture", "teaching", "class",
        "lesson", "course", "curriculum", "assignment", "exam", "test",
        "grade", "grading", "explain", "explanation", "method", "technique",
        "engagement", "interactive", "methodology", "feedback", "TA", "tutor"
    ],
    "Student Services": [
        "student services", "counseling", "health", "medical", "doctor",
        "mental health", "support", "guidance", "career", "placement",
        "internship", "activity", "event", "club", "organization",
        "advisement", "advisor", "mentoring", "housing", "dormitory", "dorm"
    ],
    "Infrastructure": [
        "wifi", "internet", "network", "bandwidth", "connection", "server",
        "system", "technology", "computer", "lab", "database", "system",
        "access", "connectivity", "signal", "router", "connectivity"
    ],
    "Administrative Services": [
        "registrar", "enrollment", "transcript", "document", "admission",
        "application", "fee", "tuition", "payment", "bookstore", "book",
        "office", "staff", "process", "admin", "administrative", "schedule",
        "shuttle", "transport", "alert", "security"
    ],
    "Other": []
}


def extract_topic(text: str) -> Dict[str, any]:
    """
    Extract primary topic/category from feedback text.
    
    Args:
        text: Student feedback text
        
    Returns:
        Dictionary with primary_topic, keywords_found, and confidence
    """
    if not text:
        return {
            "primary_topic": "Other",
            "keywords_found": [],
            "confidence": 0.0
        }
    
    text_lower = text.lower()
    category_scores = {}
    
    # Score each category
    for category, keywords in CATEGORY_KEYWORDS.items():
        if category == "Other":
            continue
            
        matches = []
        for keyword in keywords:
            # Use word boundary matching
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, text_lower):
                matches.append(keyword)
        
        if matches:
            category_scores[category] = len(matches)
    
    if not category_scores:
        return {
            "primary_topic": "Other",
            "keywords_found": [],
            "confidence": 0.0
        }
    
    # Get top category
    primary_topic = max(category_scores, key=category_scores.get)
    keywords_found = _get_matching_keywords(text_lower, CATEGORY_KEYWORDS[primary_topic])
    confidence = min(len(keywords_found) / 3, 1.0)  # Normalize to 0-1
    
    return {
        "primary_topic": primary_topic,
        "keywords_found": keywords_found,
        "confidence": round(confidence, 3)
    }


def _get_matching_keywords(text_lower: str, keywords: List[str]) -> List[str]:
    """Get all matching keywords from text."""
    matches = []
    for keyword in keywords:
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, text_lower):
            matches.append(keyword)
    return matches


def extract_entities(text: str) -> List[str]:
    """
    Extract key entities from feedback (nouns, problems, solutions).
    Simple keyword extraction without NLP library.
    
    Args:
        text: Student feedback text
        
    Returns:
        List of important entities/phrases
    """
    # Common problem words to extract
    problem_words = [
        "noise", "noisy", "slow", "broken", "outdated", "overcrowded",
        "unclear", "difficult", "unclear", "frustrating", "confusing",
        "limited", "insufficient", "lacking", "poor", "low", "high"
    ]
    
    # Solution/improvement words
    solution_words = [
        "improve", "upgrade", "expand", "update", "repair", "clean",
        "increase", "reduce", "add", "maintain", "fix", "extend"
    ]
    
    text_lower = text.lower()
    entities = []
    
    # Extract problem descriptions
    for word in problem_words:
        if word in text_lower:
            # Try to extract phrase around the word
            idx = text_lower.find(word)
            start = max(0, idx - 20)
            end = min(len(text), idx + 30)
            phrase = text[start:end].strip()
            entities.append(phrase)
    
    return entities[:3]  # Return top 3 entities
