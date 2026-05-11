"""
Sentiment Analysis Module using HuggingFace Transformers
"""
import torch
from transformers import pipeline
from typing import Tuple, Dict, List
import streamlit as st


@st.cache_resource
def load_sentiment_model():
    """Load and cache the sentiment analysis model."""
    model_name = "distilbert-base-uncased-finetuned-sst-2-english"
    sentiment_pipeline = pipeline(
        "sentiment-analysis",
        model=model_name,
        device=0 if torch.cuda.is_available() else -1
    )
    return sentiment_pipeline


def analyze_sentiment(text: str) -> Dict[str, any]:
    """
    Analyze the sentiment of a student feedback text.

    This function uses a DistilBERT sentiment-analysis model from HuggingFace.
    The selected model is binary by default, meaning it mainly predicts either
    POSITIVE or NEGATIVE. To support a simple prototype-level NEUTRAL label,
    this function applies a confidence threshold:

    - If the model confidence is below 0.70, the feedback is treated as NEUTRAL.
    - If confidence is 0.70 or higher, the model's POSITIVE/NEGATIVE label is used.

    Args:
        text: Student feedback text.

    Returns:
        A dictionary containing:
        - sentiment_label: POSITIVE, NEGATIVE, or NEUTRAL
        - confidence: model confidence score from 0.0 to 1.0
        - emotion_tags: simple keyword-based emotion tags
    """

    # Handle empty, missing, or very short feedback.
    # Very short feedback like "Good.", "Okay.", or "Bad." may show emotion,
    # but it does not provide enough useful context for actionable analysis.
    if not text:
        return {
            "sentiment_label": "NEUTRAL",
            "confidence": 0.0,
            "emotion_tags": ["low_information"]
        }

    clean_text = str(text).strip()

    if len(clean_text.split()) < 3:
        return {
            "sentiment_label": "NEUTRAL",
            "confidence": 0.0,
            "emotion_tags": ["low_information"]
        }

    try:
        # Load cached HuggingFace sentiment model.
        pipeline_model = load_sentiment_model()

        # Convert to string and limit input length.
        # DistilBERT has a token limit, so this keeps processing safe for long feedback.    
        result = pipeline_model(clean_text[:512])[0]

        # HuggingFace output example:
        # {"label": "POSITIVE", "score": 0.98}
        raw_label = result.get("label", "NEUTRAL")
        score = float(result.get("score", 0.0))

        # Prototype neutral handling:
        # Since the model is binary, low confidence predictions are treated as neutral.
        neutral_threshold = 0.70

        if score < neutral_threshold:
            sentiment_label = "NEUTRAL"
        elif raw_label == "POSITIVE":
            sentiment_label = "POSITIVE"
        elif raw_label == "NEGATIVE":
            sentiment_label = "NEGATIVE"
        else:
            sentiment_label = "NEUTRAL"

        # Infer emotion tags using keyword rules.
        emotion_tags = _extract_emotion_tags(clean_text, sentiment_label)

        return {
            "sentiment_label": sentiment_label,
            "confidence": round(score, 3),
            "emotion_tags": emotion_tags
        }

    except Exception as e:
        # Safe fallback so one failed prediction does not crash the whole app.
        print(f"Error analyzing sentiment: {e}")
        return {
            "sentiment_label": "NEUTRAL",
            "confidence": 0.0,
            "emotion_tags": ["error"]
        }

def _extract_emotion_tags(text: str, sentiment: str) -> List[str]:
    """
    Extract emotion tags from text based on keywords.
    
    Args:
        text: Feedback text
        sentiment: POSITIVE or NEGATIVE sentiment
        
    Returns:
        List of emotion tags
    """
    text_lower = text.lower()
    emotion_tags = []
    
    # Negative emotion indicators
    negative_keywords = {
        "frustration": ["frustrat", "annoyed", "annoying", "irritat"],
        "concern": ["concerned", "concern", "worry", "worried"],
        "complaint": ["complain", "problem", "issue", "bad", "terrible", "awful"],
        "urgency": ["urgent", "critical", "immediate", "asap", "now"],
    }
    
    # Positive emotion indicators
    positive_keywords = {
        "satisfaction": ["satisf", "happy", "glad", "love"],
        "praise": ["excellent", "great", "awesome", "amazing", "outstanding"],
        "appreciation": ["appreciate", "thank", "grateful", "grateful"],
        "suggestion": ["suggest", "recommend", "could", "would like"],
    }
    
    keywords_to_check = negative_keywords if sentiment == "NEGATIVE" else positive_keywords
    
    for emotion, keywords in keywords_to_check.items():
        for keyword in keywords:
            if keyword in text_lower:
                emotion_tags.append(emotion)
                break
    
    return emotion_tags if emotion_tags else ["general"]
