"""
Aggregator and Priority Ranking Module
Groups similar insights and ranks by urgency
"""
from typing import List, Dict, Tuple
from collections import Counter
import pandas as pd


PRIORITY_SCORE_MAP = {
    "Critical": 4,
    "High": 3,
    "Medium": 2,
    "Low": 1
}

SENTIMENT_WEIGHT = {
    "NEGATIVE": 2.0,
    "NEUTRAL": 1.0,
    "POSITIVE": 0.5
}


def aggregate_insights(insights_list: List[Dict]) -> List[Dict]:
    """
    Group similar insights by topic and count frequency.
    
    Args:
        insights_list: List of insight dictionaries
        
    Returns:
        List of aggregated insights with frequency counts
    """
    if not insights_list:
        return []
    
    # Group by topic and assigned department
    grouped = {}
    
    for insight in insights_list:
        key = (insight["topic"], insight["assigned_department"])
        if key not in grouped:
            grouped[key] = {
                "topic": insight["topic"],
                "assigned_department": insight["assigned_department"],
                "insights": [],
                "count": 0,
                "sentiment_counts": {"POSITIVE": 0, "NEGATIVE": 0, "NEUTRAL": 0}
            }
        
        grouped[key]["insights"].append(insight)
        grouped[key]["count"] += 1
        grouped[key]["sentiment_counts"][insight["sentiment"]] += 1
    
    # Convert to list
    aggregated = []
    for key, group_data in grouped.items():
        aggregated.append({
            "topic": group_data["topic"],
            "assigned_department": group_data["assigned_department"],
            "insight_samples": group_data["insights"][:2],  # Keep first 2 as examples
            "frequency": group_data["count"],
            "sentiment_breakdown": group_data["sentiment_counts"],
            "negative_ratio": group_data["sentiment_counts"]["NEGATIVE"] / max(group_data["count"], 1)
        })
    
    return aggregated


def rank_insights_by_priority(insights_list: List[Dict], aggregated_data: List[Dict] = None) -> List[Dict]:
    """
    Rank insights by priority using frequency and sentiment intensity.
    
    Priority = (priority_score × sentiment_weight × frequency) + urgency_boost
    
    Args:
        insights_list: List of individual insight dictionaries
        aggregated_data: Optional pre-aggregated data
        
    Returns:
        Sorted list of insights with priority scores
    """
    if not insights_list:
        return []
    
    ranked = []
    
    for insight in insights_list:
        # Base priority score from priority level
        base_score = PRIORITY_SCORE_MAP.get(insight["priority_level"], 2)
        
        # Sentiment weight
        sentiment_weight = SENTIMENT_WEIGHT.get(insight["sentiment"], 1.0)
        
        # Calculate final priority score
        priority_score = base_score * sentiment_weight
        
        # Add confidence weight
        confidence = insight.get("confidence", 0.5)
        final_score = priority_score * (1 + confidence)
        
        insight_copy = insight.copy()
        insight_copy["priority_score"] = round(final_score, 3)
        
        ranked.append(insight_copy)
    
    # Sort by priority score (descending)
    ranked.sort(key=lambda x: x["priority_score"], reverse=True)
    
    return ranked


def get_top_insights(insights_list: List[Dict], top_n: int = 10) -> List[Dict]:
    """
    Get top N most critical insights.
    
    Args:
        insights_list: List of insight dictionaries
        top_n: Number of top insights to return
        
    Returns:
        List of top N insights
    """
    ranked = rank_insights_by_priority(insights_list)
    return ranked[:top_n]


def get_insights_by_category(insights_list: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Organize insights by category/topic.
    
    Args:
        insights_list: List of insight dictionaries
        
    Returns:
        Dictionary with topics as keys and lists of insights as values
    """
    by_category = {}
    
    for insight in insights_list:
        topic = insight.get("topic", "Other")
        if topic not in by_category:
            by_category[topic] = []
        by_category[topic].append(insight)
    
    # Sort each category by priority
    for topic in by_category:
        by_category[topic].sort(
            key=lambda x: PRIORITY_SCORE_MAP.get(x["priority_level"], 2),
            reverse=True
        )
    
    return by_category


def get_insights_by_priority(insights_list: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Organize insights by priority level.
    
    Args:
        insights_list: List of insight dictionaries
        
    Returns:
        Dictionary with priority levels as keys
    """
    by_priority = {
        "Critical": [],
        "High": [],
        "Medium": [],
        "Low": []
    }
    
    for insight in insights_list:
        priority = insight.get("priority_level", "Medium")
        if priority in by_priority:
            by_priority[priority].append(insight)
    
    return by_priority


def calculate_sentiment_distribution(insights_list: List[Dict]) -> Dict[str, float]:
    """
    Calculate overall sentiment distribution across all feedback.
    
    Args:
        insights_list: List of insight dictionaries
        
    Returns:
        Dictionary with sentiment percentages
    """
    total = len(insights_list)
    if total == 0:
        return {"POSITIVE": 0, "NEGATIVE": 0, "NEUTRAL": 0}
    
    sentiment_counts = {"POSITIVE": 0, "NEGATIVE": 0, "NEUTRAL": 0}
    
    for insight in insights_list:
        sentiment = insight.get("sentiment", "NEUTRAL")
        if sentiment in sentiment_counts:
            sentiment_counts[sentiment] += 1
    
    return {
        "POSITIVE": round(sentiment_counts["POSITIVE"] / total * 100, 2),
        "NEGATIVE": round(sentiment_counts["NEGATIVE"] / total * 100, 2),
        "NEUTRAL": round(sentiment_counts["NEUTRAL"] / total * 100, 2)
    }
