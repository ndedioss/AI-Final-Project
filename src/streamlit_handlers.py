"""
Streamlit Handlers Module
File upload validation and data processing handlers
"""
import pandas as pd
import streamlit as st
from typing import Tuple, Optional


REQUIRED_COLUMNS = ["feedback_text"]
OPTIONAL_COLUMNS = ["category", "date", "rating", "department", "campus", "student_id"]
ALL_EXPECTED_COLUMNS = REQUIRED_COLUMNS + OPTIONAL_COLUMNS


def validate_csv_format(df: pd.DataFrame) -> Tuple[bool, str]:
    """
    Validate that CSV has required columns and proper format.
    
    Args:
        df: Uploaded DataFrame
        
    Returns:
        Tuple of (is_valid, message)
    """
    if df.empty:
        return False, "CSV file is empty."
    
    # Check for required columns
    missing_required = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_required:
        return False, f"Missing required column(s): {', '.join(missing_required)}"
    
    # Check for at least some expected columns
    found_columns = [col for col in df.columns if col in ALL_EXPECTED_COLUMNS]
    if len(found_columns) == 0:
        return False, "CSV columns don't match expected format."
    
    # Check feedback_text column has content
    null_count = df["feedback_text"].isnull().sum()
    if null_count > 0:
        return False, f"Found {null_count} empty feedback_text cells."
    
    # Check min length of feedback
    short_feedback = (df["feedback_text"].astype(str).str.len() < 5).sum()
    if short_feedback > len(df) * 0.5:  # More than 50% too short
        return False, "More than 50% of feedback is too short (<5 characters)."
    
    return True, "CSV format is valid."


def prepare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare and clean DataFrame for processing.
    
    Args:
        df: Raw uploaded DataFrame
        
    Returns:
        Cleaned DataFrame with proper data types
    """
    df_prepared = df.copy()
    
    # Clean feedback text
    df_prepared["feedback_text"] = (
        df_prepared["feedback_text"]
        .astype(str)
        .str.strip()
        .str.replace(r'\s+', ' ', regex=True)  # Remove extra whitespace
    )
    
    # Add default values for missing optional columns
    if "category" not in df_prepared.columns:
        df_prepared["category"] = "Other"
    
    if "date" not in df_prepared.columns:
        from datetime import datetime
        df_prepared["date"] = datetime.now().strftime("%Y-%m-%d")
    else:
        df_prepared["date"] = pd.to_datetime(df_prepared["date"]).dt.strftime("%Y-%m-%d")
    
    if "rating" not in df_prepared.columns:
        df_prepared["rating"] = 0
    else:
        df_prepared["rating"] = pd.to_numeric(df_prepared["rating"], errors="coerce").fillna(0)
    
    if "department" not in df_prepared.columns:
        df_prepared["department"] = "Unspecified"
    else:
        df_prepared["department"] = df_prepared["department"].astype(str).fillna("Unspecified")
    
    if "campus" not in df_prepared.columns:
        df_prepared["campus"] = "Main Campus"
    else:
        df_prepared["campus"] = df_prepared["campus"].astype(str).fillna("Main Campus")
    
    if "student_id" not in df_prepared.columns:
        df_prepared["student_id"] = [f"STU{i+1:04d}" for i in range(len(df_prepared))]
    
    return df_prepared


def handle_csv_upload() -> Optional[pd.DataFrame]:
    """
    Handle CSV file upload in Streamlit.
    
    Returns:
        Prepared DataFrame or None if upload fails
    """
    uploaded_file = st.file_uploader(
        "Upload CSV file with student feedback",
        type=["csv"],
        help="CSV must have 'feedback_text' column. Optional: category, date, rating, department, campus, student_id"
    )
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            
            # Validate format
            is_valid, message = validate_csv_format(df)
            
            if is_valid:
                st.success(message)
                # Prepare the dataframe
                df_prepared = prepare_dataframe(df)
                return df_prepared
            else:
                st.error(f"❌ {message}")
                return None
                
        except Exception as e:
            st.error(f"Error reading CSV: {str(e)}")
            return None
    
    return None


def display_sample_csv_format():
    """
    Display sample CSV format for user reference.
    """
    sample_data = {
        "student_id": ["STU001", "STU002"],
        "feedback_text": [
            "The library is very noisy and hard to study.",
            "Excellent teaching quality and professor engagement!"
        ],
        "category": ["Facilities", "Teaching Quality"],
        "date": ["2026-05-01", "2026-05-01"],
        "rating": [2, 5],
        "department": ["Engineering", "Arts & Sciences"],
        "campus": ["Main Campus", "Main Campus"]
    }
    
    sample_df = pd.DataFrame(sample_data)
    
    with st.expander("📋 View Sample CSV Format"):
        st.dataframe(sample_df, use_container_width=True)
        st.download_button(
            "📥 Download Sample CSV",
            sample_df.to_csv(index=False),
            "sample_feedback.csv",
            "text/csv"
        )


def export_results(enriched_df: pd.DataFrame, insights_list: list, format_type: str = "csv"):
    """
    Export processed results to file.
    
    Args:
        enriched_df: Processed DataFrame
        insights_list: List of insights
        format_type: "csv" or "json"
    """
    if format_type == "csv":
        csv = enriched_df.to_csv(index=False)
        st.download_button(
            "📥 Download Processed Feedback (CSV)",
            csv,
            "processed_feedback.csv",
            "text/csv"
        )
    elif format_type == "json":
        import json
        json_str = json.dumps(insights_list, indent=2, default=str)
        st.download_button(
            "📥 Download Insights (JSON)",
            json_str,
            "insights.json",
            "application/json"
        )
