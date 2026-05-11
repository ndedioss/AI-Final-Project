"""
Pipeline Orchestrator Module
Coordinates the entire processing flow
"""
from typing import List, Dict, Tuple
import pandas as pd
import streamlit as st
from src.sentiment_analyzer import analyze_sentiment
from src.topic_extractor import extract_topic
from src.insights_generator import generate_insight
from src.aggregator import (
    rank_insights_by_priority,
    get_insights_by_category,
    get_insights_by_priority,
    calculate_sentiment_distribution
)


def process_feedback_batch(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[Dict], Dict]:
    """
    Process a batch of feedback through the entire pipeline.
    
    Args:
        df: DataFrame with columns: feedback_text, category, date, rating, department, campus
        
    Returns:
        Tuple of (enriched_df, insights_list, metrics_dict)
    """
    if df.empty:
        return df, [], {}
    
    # Initialize progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_rows = len(df)
    enriched_data = []
    insights_list = []
    
    # Process each feedback
    for idx, row in df.iterrows():
        # Update progress
        progress = (idx + 1) / total_rows
        progress_bar.progress(progress)
        status_text.text(f"Processing feedback {idx + 1} of {total_rows}...")
        
        feedback_text = row.get("feedback_text", "")
        
        # Step 1: Sentiment Analysis
        sentiment_result = analyze_sentiment(feedback_text)
        
        # Step 2: Topic Extraction
        topic_result = extract_topic(feedback_text)
        
        # Step 3: Combine results for insight generation
        combined_data = {
            **sentiment_result,
            **topic_result,
            "feedback_text": feedback_text
        }
        
        # Step 4: Generate Insight
        insight = generate_insight(combined_data)

        # Attach a stable feedback_id so insights can still be matched
        # to the correct DataFrame row even after priority ranking.
        insight["feedback_id"] = idx

        # Create enriched row
        enriched_row = row.copy()
        enriched_row["feedback_id"] = idx
        enriched_row["sentiment"] = sentiment_result["sentiment_label"]
        enriched_row["sentiment_confidence"] = sentiment_result["confidence"]
        enriched_row["emotion_tags"] = ", ".join(sentiment_result["emotion_tags"])
        enriched_row["topic"] = topic_result["primary_topic"]
        enriched_row["topic_confidence"] = topic_result["confidence"]
        enriched_row["insight"] = insight["insight_text"]
        enriched_row["priority_level"] = insight["priority_level"]
        enriched_row["assigned_department"] = insight["assigned_department"]
        
        enriched_data.append(enriched_row)
        insights_list.append(insight)
    
    # Clear progress indicators
    progress_bar.empty()
    status_text.empty()
    
    # Convert to DataFrame
    enriched_df = pd.DataFrame(enriched_data)
    
    # Step 5: Rank and aggregate insights
    ranked_insights = rank_insights_by_priority(insights_list)
    
    # Calculate metrics
    metrics = calculate_pipeline_metrics(enriched_df, ranked_insights)
    
    return enriched_df, ranked_insights, metrics


def calculate_pipeline_metrics(enriched_df: pd.DataFrame, insights_list: List[Dict]) -> Dict:
    """
    Calculate overall metrics from processed feedback.
    
    Args:
        enriched_df: Enriched DataFrame with processing results
        insights_list: List of ranked insights
        
    Returns:
        Dictionary with key metrics
    """
    total_feedback = len(enriched_df)
    
    # Sentiment distribution
    sentiment_dist = enriched_df["sentiment"].value_counts().to_dict()
    
    # Priority distribution
    priority_dist = enriched_df["priority_level"].value_counts().to_dict()
    
    # Topic distribution
    topic_dist = enriched_df["topic"].value_counts().to_dict()
    
    # Department distribution
    dept_dist = enriched_df["assigned_department"].value_counts().to_dict()
    
    # Average confidence scores
    avg_sentiment_confidence = enriched_df["sentiment_confidence"].mean()
    avg_topic_confidence = enriched_df["topic_confidence"].mean()
    
    # Critical issues count
    critical_count = len(enriched_df[enriched_df["priority_level"] == "Critical"])
    
    metrics = {
        "total_feedback": total_feedback,
        "sentiment_distribution": sentiment_dist,
        "priority_distribution": priority_dist,
        "topic_distribution": topic_dist,
        "department_distribution": dept_dist,
        "avg_sentiment_confidence": round(avg_sentiment_confidence, 3),
        "avg_topic_confidence": round(avg_topic_confidence, 3),
        "critical_issues": critical_count,
        "critical_percentage": round(critical_count / total_feedback * 100, 2) if total_feedback > 0 else 0
    }
    
    return metrics


def filter_insights(
    enriched_df: pd.DataFrame,
    insights_list: List[Dict],
    filters: Dict = None
) -> Tuple[pd.DataFrame, List[Dict]]:
    """
    Filter insights and corresponding rows based on criteria.
    
    Args:
        enriched_df: Enriched DataFrame
        insights_list: List of insights
        filters: Dictionary with filter criteria (sentiment, priority, topic, date_range)
        
    Returns:
        Tuple of (filtered_df, filtered_insights)
    """
    if not filters:
        return enriched_df, insights_list
    
    filtered_df = enriched_df.copy()
    
    # Filter by sentiment
    if "sentiment" in filters and filters["sentiment"]:
        filtered_df = filtered_df[filtered_df["sentiment"].isin(filters["sentiment"])]
    
    # Filter by priority
    if "priority" in filters and filters["priority"]:
        filtered_df = filtered_df[filtered_df["priority_level"].isin(filters["priority"])]
    
    # Filter by topic
    if "topic" in filters and filters["topic"]:
        filtered_df = filtered_df[filtered_df["topic"].isin(filters["topic"])]
    
    # Filter by date range
    if "date_range" in filters and filters["date_range"]:
        start_date, end_date = filters["date_range"]

        # Convert both DataFrame dates and Streamlit date_input values
        # into the same Pandas Timestamp type before comparison.
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        filtered_df["date"] = pd.to_datetime(filtered_df["date"], errors="coerce")

        filtered_df = filtered_df[
            (filtered_df["date"] >= start_date) &
            (filtered_df["date"] <= end_date)
        ]
    
    # Filter insights corresponding to filtered rows
    # Use feedback_id instead of list position because insights may be reordered
    # after priority ranking.
    filtered_feedback_ids = set(filtered_df["feedback_id"].tolist())

    filtered_insights = [
        insight for insight in insights_list
        if insight.get("feedback_id") in filtered_feedback_ids
    ]
    
    return filtered_df, filtered_insights
