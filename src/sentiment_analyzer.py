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
    Analyze sentiment of feedback text.
    
    Args:
        text: Student feedback text
        
    Returns:
        Dictionary with sentiment_label, confidence, and emotion_tags
    """
    if not text or len(text.strip()) < 5:
        return {
            "sentiment_label": "NEUTRAL",
            "confidence": 0.0,
            "emotion_tags": []
        }
    
    try:
        pipeline_model = load_sentiment_model()
        result = pipeline_model(text[:512])[0]  # Truncate to 512 chars (model limit)
        
        label = result["label"]  # POSITIVE or NEGATIVE
        score = result["score"]
        
        # Map to our labels
        sentiment_label = "POSITIVE" if label == "POSITIVE" else "NEGATIVE"
        
        # Invert score if negative (HF gives higher score to detected label)
        confidence = score if label == label else 1 - score
        
        # Infer emotion tags based on text keywords
        emotion_tags = _extract_emotion_tags(text, sentiment_label)
        
        return {
            "sentiment_label": sentiment_label,
            "confidence": round(confidence, 3),
            "emotion_tags": emotion_tags
        }
    except Exception as e:
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
