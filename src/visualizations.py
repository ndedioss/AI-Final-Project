"""
Visualizations Module
Create Streamlit charts and dashboards
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List


def plot_sentiment_distribution(metrics: Dict):
    """
    Create pie chart of sentiment distribution.
    
    Args:
        metrics: Dictionary with sentiment_distribution
    """
    sentiment_dist = metrics.get("sentiment_distribution", {})
    
    if not sentiment_dist:
        st.warning("No sentiment data to display.")
        return
    
    df = pd.DataFrame({
        "Sentiment": list(sentiment_dist.keys()),
        "Count": list(sentiment_dist.values())
    })
    
    fig = px.pie(
        df,
        values="Count",
        names="Sentiment",
        title="Sentiment Distribution",
        color="Sentiment",
        color_discrete_map={
            "POSITIVE": "#2ecc71",
            "NEGATIVE": "#e74c3c",
            "NEUTRAL": "#95a5a6"
        },
        hole=0.3
    )
    
    st.plotly_chart(fig, use_container_width=True)


def plot_priority_distribution(metrics: Dict):
    """
    Create bar chart of priority distribution.
    
    Args:
        metrics: Dictionary with priority_distribution
    """
    priority_dist = metrics.get("priority_distribution", {})
    
    if not priority_dist:
        st.warning("No priority data to display.")
        return
    
    # Order by priority level
    priority_order = ["Critical", "High", "Medium", "Low"]
    ordered_data = {k: priority_dist.get(k, 0) for k in priority_order if k in priority_dist}
    
    df = pd.DataFrame({
        "Priority": list(ordered_data.keys()),
        "Count": list(ordered_data.values())
    })
    
    color_map = {
        "Critical": "#e74c3c",
        "High": "#f39c12",
        "Medium": "#f1c40f",
        "Low": "#2ecc71"
    }
    
    fig = px.bar(
        df,
        x="Priority",
        y="Count",
        title="Issues by Priority Level",
        category_order={"Priority": priority_order},
        color="Priority",
        color_discrete_map=color_map
    )
    
    st.plotly_chart(fig, use_container_width=True)


def plot_topics_distribution(metrics: Dict):
    """
    Create horizontal bar chart of topics distribution.
    
    Args:
        metrics: Dictionary with topic_distribution
    """
    topic_dist = metrics.get("topic_distribution", {})
    
    if not topic_dist:
        st.warning("No topic data to display.")
        return
    
    df = pd.DataFrame({
        "Topic": list(topic_dist.keys()),
        "Count": list(topic_dist.values())
    }).sort_values("Count", ascending=True)
    
    fig = px.barh(
        df,
        x="Count",
        y="Topic",
        title="Feedback by Category",
        labels={"Topic": "Category", "Count": "Number of Feedback"},
        color="Count",
        color_continuous_scale="Blues"
    )
    
    st.plotly_chart(fig, use_container_width=True)


def plot_departments_distribution(metrics: Dict):
    """
    Create bar chart of affected departments.
    
    Args:
        metrics: Dictionary with department_distribution
    """
    dept_dist = metrics.get("department_distribution", {})
    
    if not dept_dist:
        st.warning("No department data to display.")
        return
    
    df = pd.DataFrame({
        "Department": list(dept_dist.keys()),
        "Count": list(dept_dist.values())
    }).sort_values("Count", ascending=False)
    
    fig = px.bar(
        df,
        x="Department",
        y="Count",
        title="Feedback by Assigned Department",
        labels={"Department": "Department", "Count": "Number of Issues"},
        color="Count",
        color_continuous_scale="Oranges"
    )
    
    st.plotly_chart(fig, use_container_width=True)


def plot_confidence_scores(enriched_df: pd.DataFrame):
    """
    Create scatter plot of sentiment vs topic confidence.
    
    Args:
        enriched_df: Processed DataFrame
    """
    if enriched_df.empty or "sentiment_confidence" not in enriched_df.columns:
        st.warning("No confidence data to display.")
        return
    
    fig = px.scatter(
        enriched_df,
        x="sentiment_confidence",
        y="topic_confidence",
        color="sentiment",
        hover_data=["topic", "priority_level"],
        title="Sentiment vs Topic Confidence Scores",
        labels={
            "sentiment_confidence": "Sentiment Confidence",
            "topic_confidence": "Topic Confidence"
        },
        color_discrete_map={
            "POSITIVE": "#2ecc71",
            "NEGATIVE": "#e74c3c",
            "NEUTRAL": "#95a5a6"
        }
    )
    
    st.plotly_chart(fig, use_container_width=True)


def plot_priority_matrix(enriched_df: pd.DataFrame):
    """
    Create scatter plot matrix (frequency vs sentiment intensity).
    
    Args:
        enriched_df: Processed DataFrame
    """
    if enriched_df.empty:
        st.warning("No data to display.")
        return
    
    # Calculate frequency by topic and sentiment
    topic_sentiment_counts = enriched_df.groupby(
        ["topic", "sentiment"]
    ).size().reset_index(name="frequency")
    
    fig = px.scatter(
        topic_sentiment_counts,
        x="topic",
        y="frequency",
        color="sentiment",
        size="frequency",
        title="Issue Frequency by Category and Sentiment",
        labels={"topic": "Category", "frequency": "Number of Issues"},
        color_discrete_map={
            "POSITIVE": "#2ecc71",
            "NEGATIVE": "#e74c3c",
            "NEUTRAL": "#95a5a6"
        }
    )
    
    st.plotly_chart(fig, use_container_width=True)


def display_metrics_summary(metrics: Dict):
    """
    Display key metrics in Streamlit columns.
    
    Args:
        metrics: Dictionary with all metrics
    """
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Feedback",
            metrics.get("total_feedback", 0)
        )
    
    with col2:
        st.metric(
            "Critical Issues",
            metrics.get("critical_issues", 0),
            delta=f"{metrics.get('critical_percentage', 0)}%"
        )
    
    with col3:
        st.metric(
            "Avg Sentiment Confidence",
            f"{metrics.get('avg_sentiment_confidence', 0):.2%}",
        )
    
    with col4:
        st.metric(
            "Avg Topic Confidence",
            f"{metrics.get('avg_topic_confidence', 0):.2%}",
        )


def display_top_insights(ranked_insights: List[Dict], top_n: int = 5):
    """
    Display top N insights in a readable format.
    
    Args:
        ranked_insights: List of ranked insights
        top_n: Number of top insights to display
    """
    if not ranked_insights:
        st.info("No insights generated yet.")
        return
    
    st.subheader("🔝 Top Critical Insights")
    
    for idx, insight in enumerate(ranked_insights[:top_n], 1):
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**{idx}. {insight['insight_text']}**")
                st.caption(
                    f"Category: {insight['topic']} | "
                    f"Department: {insight['assigned_department']} | "
                    f"Sentiment: {insight['sentiment']}"
                )
            
            with col2:
                # Color badge for priority
                priority = insight.get("priority_level", "Medium")
                priority_colors = {
                    "Critical": "🔴",
                    "High": "🟠",
                    "Medium": "🟡",
                    "Low": "🟢"
                }
                st.metric("Priority", priority_colors.get(priority, ""))
            
            st.divider()


def display_insights_table(enriched_df: pd.DataFrame):
    """
    Display processed feedback in table format.
    
    Args:
        enriched_df: Processed DataFrame
    """
    if enriched_df.empty:
        st.info("No data to display.")
        return
    
    # Select key columns for display
    display_cols = [
        "student_id", "feedback_text", "sentiment", "topic",
        "priority_level", "assigned_department", "insight"
    ]
    
    available_cols = [col for col in display_cols if col in enriched_df.columns]
    
    st.dataframe(
        enriched_df[available_cols],
        use_container_width=True,
        height=400
    )


def create_priority_heatmap(enriched_df: pd.DataFrame):
    """
    Create heatmap of topic vs priority.
    
    Args:
        enriched_df: Processed DataFrame
    """
    if enriched_df.empty:
        st.warning("No data to display.")
        return
    
    # Create cross-tabulation
    crosstab = pd.crosstab(
        enriched_df["topic"],
        enriched_df["priority_level"]
    )
    
    # Reorder columns
    priority_order = ["Critical", "High", "Medium", "Low"]
    crosstab = crosstab[[col for col in priority_order if col in crosstab.columns]]
    
    fig = go.Figure(
        data=go.Heatmap(
            z=crosstab.values,
            x=crosstab.columns,
            y=crosstab.index,
            colorscale="RdYlGn_r"
        )
    )
    
    fig.update_layout(
        title="Issue Heatmap: Category vs Priority",
        xaxis_title="Priority Level",
        yaxis_title="Category"
    )
    
    st.plotly_chart(fig, use_container_width=True)
