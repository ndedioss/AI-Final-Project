"""
Main Streamlit Application
Sentiment-Based Student Feedback System with Automated Actionable Insights
"""
import streamlit as st
import pandas as pd
from typing import Optional
from src.streamlit_handlers import (
    handle_csv_upload,
    display_sample_csv_format,
    export_results
)
from src.pipeline import process_feedback_batch, filter_insights
from src.aggregator import (
    get_top_insights,
    get_insights_by_category,
    get_insights_by_priority
)
from src.visualizations import (
    plot_sentiment_distribution,
    plot_priority_distribution,
    plot_topics_distribution,
    plot_departments_distribution,
    plot_confidence_scores,
    plot_priority_matrix,
    display_metrics_summary,
    display_top_insights,
    display_insights_table,
    create_priority_heatmap
)


# Page configuration
st.set_page_config(
    page_title="Student Feedback Analysis System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-title {
        color: #1f77b4;
        font-size: 2.5em;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .subtitle {
        color: #666;
        font-size: 1.2em;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# INITIALIZE SESSION STATE
# ============================================================================

if "processed_df" not in st.session_state:
    st.session_state.processed_df = None

if "insights_list" not in st.session_state:
    st.session_state.insights_list = []

if "metrics" not in st.session_state:
    st.session_state.metrics = {}

if "current_page" not in st.session_state:
    st.session_state.current_page = "Upload & Process"


# ============================================================================
# HEADER
# ============================================================================

st.markdown(
    "<div class='main-title'>📊 Student Feedback Analysis System</div>",
    unsafe_allow_html=True
)
st.markdown(
    "<div class='subtitle'>"
    "De La Salle University - Dasmariñas | "
    "Sentiment-Based Feedback with Automated Actionable Insights"
    "</div>",
    unsafe_allow_html=True
)

st.divider()


# ============================================================================
# SIDEBAR - NAVIGATION & FILTERS
# ============================================================================

with st.sidebar:
    st.header("🧭 Navigation")
    
    page = st.radio(
        "Select Page:",
        ["Upload & Process", "Dashboard", "Insights Report", "Raw Feedback", "About"],
        key="page_selector"
    )
    
    st.divider()
    
    # Show filter options if data is processed
    if st.session_state.processed_df is not None and len(st.session_state.processed_df) > 0:
        st.header("🔍 Filters")
        
        # Sentiment filter
        sentiments = st.session_state.processed_df["sentiment"].unique().tolist()
        selected_sentiments = st.multiselect(
            "Filter by Sentiment:",
            sentiments,
            default=sentiments
        )
        
        # Priority filter
        priorities = st.session_state.processed_df["priority_level"].unique().tolist()
        selected_priorities = st.multiselect(
            "Filter by Priority:",
            priorities,
            default=priorities
        )
        
        # Topic filter
        topics = st.session_state.processed_df["topic"].unique().tolist()
        selected_topics = st.multiselect(
            "Filter by Category:",
            topics,
            default=topics
        )
        
        # Date range filter
        if "date" in st.session_state.processed_df.columns:
            st.session_state.processed_df["date"] = pd.to_datetime(st.session_state.processed_df["date"])
            date_range = st.date_input(
                "Filter by Date Range:",
                [
                    st.session_state.processed_df["date"].min().date(),
                    st.session_state.processed_df["date"].max().date()
                ]
            )
        
        # Apply filters
        if st.button("Apply Filters", type="primary", use_container_width=True):
            filters = {
                "sentiment": selected_sentiments,
                "priority": selected_priorities,
                "topic": selected_topics,
                "date_range": date_range if len(date_range) == 2 else None
            }
            filtered_df, filtered_insights = filter_insights(
                st.session_state.processed_df,
                st.session_state.insights_list,
                filters
            )
            st.session_state.filtered_df = filtered_df
            st.session_state.filtered_insights = filtered_insights
            st.success("Filters applied!")
    
    st.divider()
    
    # Display statistics
    if st.session_state.processed_df is not None:
        st.header("📈 Quick Stats")
        st.metric("Total Feedback", len(st.session_state.processed_df))
        st.metric("Critical Issues", st.session_state.metrics.get("critical_issues", 0))
        st.metric(
            "Unique Categories",
            len(st.session_state.metrics.get("topic_distribution", {}))
        )


# ============================================================================
# PAGE 1: UPLOAD & PROCESS
# ============================================================================

if page == "Upload & Process":
    st.header("📤 Upload & Process Feedback")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write("""
        ### How to use:
        1. **Prepare your CSV file** with student feedback
        2. **Upload the file** using the uploader below
        3. **View the processed results** with sentiment analysis and insights
        4. **Navigate to Dashboard** to see visualizations and trends
        """)
        
        display_sample_csv_format()
    
    with col2:
        st.info("""
        ### Required Format:
        - CSV file format
        - **Required column**: `feedback_text`
        - **Optional columns**: `category`, `date`, `rating`, `department`, `campus`, `student_id`
        """)
    
    st.divider()
    
    st.subheader("📁 Upload CSV File")
    df = handle_csv_upload()
    
    if df is not None:
        st.success(f"✅ CSV loaded successfully! {len(df)} feedback items detected.")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.info(f"Processing {len(df)} feedback items through the pipeline...")
            process_btn = st.button("🚀 Start Processing", type="primary", use_container_width=True)
        
        with col2:
            st.write("")
            st.write("")
            preview_btn = st.button("👀 Preview Data", use_container_width=True)
        
        if process_btn:
            with st.spinner("🔄 Processing feedback through pipeline..."):
                try:
                    processed_df, insights_list, metrics = process_feedback_batch(df)
                    
                    # Store in session state
                    st.session_state.processed_df = processed_df
                    st.session_state.insights_list = insights_list
                    st.session_state.metrics = metrics
                    st.session_state.filtered_df = processed_df
                    st.session_state.filtered_insights = insights_list
                    
                    st.success("✅ Processing completed successfully!")
                    st.balloons()
                    
                    # Show summary
                    st.subheader("📊 Processing Summary")
                    display_metrics_summary(metrics)
                    
                except Exception as e:
                    st.error(f"❌ Error during processing: {str(e)}")
                    st.write("Please check your CSV format and try again.")
        
        if preview_btn:
            with st.expander("📋 Preview Raw Data", expanded=True):
                st.dataframe(df.head(10), use_container_width=True)
                st.caption(f"Showing first 10 of {len(df)} rows")


# ============================================================================
# PAGE 2: DASHBOARD
# ============================================================================

elif page == "Dashboard":
    if st.session_state.processed_df is None or len(st.session_state.processed_df) == 0:
        st.warning("⚠️ No data processed yet. Please upload and process feedback first.")
        st.info("Go to **Upload & Process** tab to get started.")
    else:
        st.header("📊 Dashboard - Overview & Analytics")
        
        # Display metrics
        st.subheader("📈 Key Metrics")
        display_metrics_summary(st.session_state.metrics)
        
        st.divider()
        
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            plot_sentiment_distribution(st.session_state.metrics)
        
        with col2:
            plot_priority_distribution(st.session_state.metrics)
        
        col1, col2 = st.columns(2)
        
        with col1:
            plot_topics_distribution(st.session_state.metrics)
        
        with col2:
            plot_departments_distribution(st.session_state.metrics)
        
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            plot_confidence_scores(st.session_state.filtered_df if hasattr(st.session_state, 'filtered_df') else st.session_state.processed_df)
        
        with col2:
            create_priority_heatmap(st.session_state.filtered_df if hasattr(st.session_state, 'filtered_df') else st.session_state.processed_df)


# ============================================================================
# PAGE 3: INSIGHTS REPORT
# ============================================================================

elif page == "Insights Report":
    if st.session_state.processed_df is None or len(st.session_state.insights_list) == 0:
        st.warning("⚠️ No insights generated yet. Please upload and process feedback first.")
    else:
        st.header("💡 Actionable Insights Report")
        
        # Tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(
            ["Top Insights", "By Priority", "By Category", "Export"]
        )
        
        with tab1:
            st.subheader("🔝 Top 10 Most Critical Insights")
            insights_to_show = st.slider("Number of insights to display:", 1, 20, 10)
            display_top_insights(
                st.session_state.filtered_insights if hasattr(st.session_state, 'filtered_insights') else st.session_state.insights_list,
                insights_to_show
            )
        
        with tab2:
            st.subheader("📊 Insights by Priority Level")
            insights_by_priority = get_insights_by_priority(
                st.session_state.filtered_insights if hasattr(st.session_state, 'filtered_insights') else st.session_state.insights_list
            )
            
            for priority, insights in insights_by_priority.items():
                if insights:
                    with st.expander(f"{priority} Priority ({len(insights)} issues)", expanded=False):
                        for idx, insight in enumerate(insights[:5], 1):
                            st.write(f"{idx}. {insight['insight_text']}")
                            st.caption(
                                f"Department: {insight['assigned_department']} | "
                                f"Category: {insight['topic']} | "
                                f"Sentiment: {insight['sentiment']}"
                            )
        
        with tab3:
            st.subheader("🏷️ Insights by Category")
            insights_by_category = get_insights_by_category(
                st.session_state.filtered_insights if hasattr(st.session_state, 'filtered_insights') else st.session_state.insights_list
            )
            
            for category, insights in insights_by_category.items():
                with st.expander(f"{category} ({len(insights)} issues)", expanded=False):
                    for idx, insight in enumerate(insights[:5], 1):
                        st.write(f"{idx}. {insight['insight_text']}")
                        st.caption(
                            f"Priority: {insight['priority_level']} | "
                            f"Department: {insight['assigned_department']}"
                        )
        
        with tab4:
            st.subheader("📥 Export Results")
            col1, col2 = st.columns(2)
            
            with col1:
                export_results(
                    st.session_state.filtered_df if hasattr(st.session_state, 'filtered_df') else st.session_state.processed_df,
                    st.session_state.filtered_insights if hasattr(st.session_state, 'filtered_insights') else st.session_state.insights_list,
                    "csv"
                )
            
            with col2:
                export_results(
                    st.session_state.filtered_df if hasattr(st.session_state, 'filtered_df') else st.session_state.processed_df,
                    st.session_state.filtered_insights if hasattr(st.session_state, 'filtered_insights') else st.session_state.insights_list,
                    "json"
                )


# ============================================================================
# PAGE 4: RAW FEEDBACK
# ============================================================================

elif page == "Raw Feedback":
    if st.session_state.processed_df is None or len(st.session_state.processed_df) == 0:
        st.warning("⚠️ No data processed yet. Please upload and process feedback first.")
    else:
        st.header("📋 Raw Processed Feedback")
        
        view_type = st.radio("View as:", ["Table", "Cards"], horizontal=True)
        
        if view_type == "Table":
            display_insights_table(
                st.session_state.filtered_df if hasattr(st.session_state, 'filtered_df') else st.session_state.processed_df
            )
        
        else:
            df_to_show = st.session_state.filtered_df if hasattr(st.session_state, 'filtered_df') else st.session_state.processed_df
            
            for idx, row in df_to_show.iterrows():
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**Student ID:** {row.get('student_id', 'N/A')}")
                        st.write(f"**Feedback:** {row.get('feedback_text', 'N/A')}")
                        st.write(f"**Insight:** {row.get('insight', 'N/A')}")
                    
                    with col2:
                        sentiment = row.get("sentiment", "NEUTRAL")
                        sentiment_color = {
                            "POSITIVE": "🟢",
                            "NEGATIVE": "🔴",
                            "NEUTRAL": "🟡"
                        }
                        st.write(f"**Sentiment:** {sentiment_color.get(sentiment, '')} {sentiment}")
                        st.write(f"**Priority:** {row.get('priority_level', 'N/A')}")
                        st.write(f"**Category:** {row.get('topic', 'N/A')}")
                    
                    st.divider()


# ============================================================================
# PAGE 5: ABOUT
# ============================================================================

elif page == "About":
    st.header("ℹ️ About This System")
    
    st.write("""
    ### Sentiment-Based Student Feedback System
    **De La Salle University - Dasmariñas**
    
    #### Overview
    This system automatically processes student feedback using advanced AI techniques to:
    - Analyze sentiment (positive, negative, neutral)
    - Extract key topics and categories
    - Generate actionable insights for decision-makers
    - Prioritize issues based on urgency and frequency
    
    #### Key Features
    - **🤖 AI-Powered Analysis:** Uses DistilBERT for accurate sentiment classification
    - **📊 Interactive Dashboard:** Visualize feedback trends and patterns
    - **💡 Actionable Insights:** Generate specific recommendations for administrators
    - **⚡ Real-Time Processing:** Process 50-100+ feedback items in seconds
    - **📥 Easy Export:** Download results in CSV or JSON format
    
    #### How It Works
    1. **Input:** Upload CSV with student feedback
    2. **Sentiment Analysis:** Classify feedback as positive/negative/neutral
    3. **Topic Extraction:** Identify feedback category (Facilities, Teaching, etc.)
    4. **Insight Generation:** Create specific recommendations
    5. **Priority Ranking:** Sort by urgency and frequency
    6. **Output:** View dashboard, export results, take action
    
    #### Categories Analyzed
    - **Facilities:** Buildings, classrooms, labs, parking, maintenance
    - **Teaching Quality:** Professor engagement, course design, feedback
    - **Student Services:** Counseling, health, support programs, activities
    - **Infrastructure:** WiFi, internet, network, technology systems
    - **Administrative Services:** Admissions, registrar, schedules, bookstore
    
    #### Technical Details
    - **Sentiment Model:** DistilBERT (HuggingFace Transformers)
    - **Insight Generation:** Rule-based templates + NLP
    - **Priority Ranking:** Frequency × Sentiment Intensity
    - **Frontend:** Streamlit Web Application
    - **Data Format:** CSV (+ optional JSON export)
    
    ---
    
    **Developed for:** De La Salle University - Dasmariñas  
    **Purpose:** Support data-driven decision-making through automated feedback analysis  
    **Status:** Active Development  
    """)
