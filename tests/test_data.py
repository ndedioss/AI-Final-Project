"""
Test Data Generator
Generate realistic synthetic student feedback for testing
"""
import pandas as pd
import random
from datetime import datetime, timedelta


FEEDBACK_TEMPLATES = {
    "Facilities_Negative": [
        "The library is extremely noisy and it's hard to study.",
        "The air conditioning in the buildings is not working properly.",
        "Classroom lighting is poor and makes it hard to see the board.",
        "The parking lot is always full. Need more spaces.",
        "Lab equipment is outdated and frequently breaks down.",
        "Restrooms need cleaning more frequently.",
        "The cafeteria food quality needs improvement.",
    ],
    "Facilities_Positive": [
        "Excellent campus facilities! Clean and well-maintained.",
        "The new library renovations look amazing.",
        "Campus infrastructure is impressive.",
        "Great job on campus landscaping!",
    ],
    "Teaching Quality_Negative": [
        "Teaching quality varies widely. Some professors are disengaged.",
        "Class sizes are too large for meaningful interaction.",
        "Teaching methods are outdated. Need more modern approaches.",
        "Some courses lack clear learning objectives.",
    ],
    "Teaching Quality_Positive": [
        "Excellent teaching quality! Professors are knowledgeable.",
        "Great teaching methods and student engagement.",
        "Professors are very approachable and supportive.",
        "Outstanding faculty! Very inspiring classes.",
    ],
    "Student Services_Negative": [
        "Student counseling services are understaffed.",
        "Student health services have limited availability.",
        "Library extended hours would be helpful.",
        "Student support response times are slow.",
    ],
    "Student Services_Positive": [
        "Great support from student affairs team!",
        "Very responsive and helpful student services.",
        "Amazing events and activities organized this year.",
    ],
    "Infrastructure_Negative": [
        "WiFi connection is frequently unstable.",
        "Internet bandwidth is insufficient during peak hours.",
        "WiFi in dormitories keeps disconnecting.",
        "Network connection needs improvement.",
    ],
    "Infrastructure_Positive": [
        "WiFi connection is stable and fast.",
        "Excellent IT infrastructure and support.",
    ],
    "Administrative Services_Negative": [
        "Administrative processes are too complicated.",
        "Registrar office processes documents slowly.",
        "Bookstore prices are too high.",
        "Admissions office staff were unhelpful.",
    ],
    "Administrative Services_Positive": [
        "Great administrative support! Very helpful.",
        "Campus security staff are professional.",
        "Campus shuttle service runs on schedule.",
    ],
}

DEPARTMENTS = ["Engineering", "Arts & Sciences", "Business", "Information Technology"]
CAMPUSES = ["Main Campus", "Dasmariñas"]
CATEGORIES = ["Facilities", "Teaching Quality", "Student Services", "Infrastructure", "Administrative Services"]


def generate_synthetic_feedback(num_samples: int = 100) -> pd.DataFrame:
    """
    Generate realistic synthetic student feedback data.
    
    Args:
        num_samples: Number of feedback items to generate
        
    Returns:
        DataFrame with synthetic feedback
    """
    data = []
    base_date = datetime(2026, 5, 1)
    
    for i in range(num_samples):
        # Random category
        category = random.choice(CATEGORIES)
        
        # Random sentiment
        sentiment_key = random.choice([f"{category}_Positive", f"{category}_Negative"])
        if sentiment_key in FEEDBACK_TEMPLATES:
            feedback_text = random.choice(FEEDBACK_TEMPLATES[sentiment_key])
        else:
            feedback_text = f"Feedback about {category}"
        
        # Random metadata
        rating = 5 if "Positive" in sentiment_key else 2
        rating = rating + random.randint(-1, 1)  # Add some variation
        rating = max(1, min(5, rating))  # Clamp to 1-5
        
        date = base_date - timedelta(days=random.randint(0, 7))
        
        row = {
            "student_id": f"STU{i+1:04d}",
            "feedback_text": feedback_text,
            "category": category,
            "date": date.strftime("%Y-%m-%d"),
            "rating": rating,
            "department": random.choice(DEPARTMENTS),
            "campus": random.choice(CAMPUSES),
        }
        
        data.append(row)
    
    return pd.DataFrame(data)


def save_synthetic_data(df: pd.DataFrame, filepath: str = "data/generated_feedback.csv"):
    """
    Save generated feedback to CSV.
    
    Args:
        df: DataFrame with feedback
        filepath: Output file path
    """
    df.to_csv(filepath, index=False)
    print(f"✅ Generated {len(df)} feedback items saved to {filepath}")


def validate_generated_data(df: pd.DataFrame) -> dict:
    """
    Validate generated data quality.
    
    Args:
        df: Generated DataFrame
        
    Returns:
        Dictionary with validation results
    """
    stats = {
        "total_items": len(df),
        "categories": df["category"].value_counts().to_dict(),
        "departments": df["department"].value_counts().to_dict(),
        "campuses": df["campus"].value_counts().to_dict(),
        "avg_rating": round(df["rating"].mean(), 2),
        "date_range": f"{df['date'].min()} to {df['date'].max()}",
    }
    
    return stats


if __name__ == "__main__":
    # Generate and save sample data
    print("🔄 Generating synthetic feedback data...")
    df = generate_synthetic_feedback(100)
    save_synthetic_data(df)
    
    # Display statistics
    print("\n📊 Generated Data Statistics:")
    stats = validate_generated_data(df)
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Display sample
    print("\n📋 Sample Feedback:")
    print(df.head(5).to_string())
