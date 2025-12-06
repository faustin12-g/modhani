"""
Script to analyze the actual cluster characteristics from the trained model.
This helps us determine what each cluster actually represents.
"""
import pandas as pd
import joblib
import os
import numpy as np

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'Mall_Customers.csv')
MODEL_PATH = os.path.join(BASE_DIR, 'saved_models', 'kmeans_v1.pkl')
SCALER_PATH = os.path.join(BASE_DIR, 'saved_models', 'scaler_v1.pkl')

def analyze_clusters():
    """Analyze the actual characteristics of each cluster."""
    # Load data
    df = pd.read_csv(DATA_PATH)
    df.rename(columns={
        'Annual Income (k$)': 'Annual_Income',
        'Spending Score (1-100)': 'Spending_Score'
    }, inplace=True)
    
    # Load model and scaler
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    
    # Prepare features
    features = ['Age', 'Annual_Income', 'Spending_Score']
    X = df[features].values
    X_scaled = scaler.transform(X)
    
    # Get cluster assignments
    df['Cluster'] = model.predict(X_scaled)
    
    # Analyze each cluster
    print("\n" + "="*60)
    print("CLUSTER ANALYSIS")
    print("="*60)
    
    cluster_stats = {}
    
    for cluster_id in sorted(df['Cluster'].unique()):
        cluster_data = df[df['Cluster'] == cluster_id]
        
        mean_income = cluster_data['Annual_Income'].mean()
        mean_score = cluster_data['Spending_Score'].mean()
        mean_age = cluster_data['Age'].mean()
        count = len(cluster_data)
        
        cluster_stats[cluster_id] = {
            'mean_income': mean_income,
            'mean_score': mean_score,
            'mean_age': mean_age,
            'count': count
        }
        
        print(f"\nCluster {cluster_id}:")
        print(f"  Count: {count} customers")
        print(f"  Mean Income: {mean_income:.2f} k$")
        print(f"  Mean Spending Score: {mean_score:.2f}")
        print(f"  Mean Age: {mean_age:.2f}")
    
    # Determine overall thresholds
    overall_mean_income = df['Annual_Income'].mean()
    overall_mean_score = df['Spending_Score'].mean()
    
    print(f"\n{'='*60}")
    print(f"OVERALL AVERAGES:")
    print(f"  Mean Income: {overall_mean_income:.2f} k$")
    print(f"  Mean Spending Score: {overall_mean_score:.2f}")
    print(f"{'='*60}\n")
    
    # Generate labels based on actual characteristics
    print("RECOMMENDED LABELS:")
    print("-" * 60)
    
    for cluster_id in sorted(cluster_stats.keys()):
        stats = cluster_stats[cluster_id]
        income = stats['mean_income']
        score = stats['mean_score']
        
        # Determine income level
        if income > overall_mean_income * 1.1:
            income_level = "High Income"
        elif income < overall_mean_income * 0.9:
            income_level = "Low Income"
        else:
            income_level = "Average Income"
        
        # Determine spending level
        if score > overall_mean_score * 1.1:
            spend_level = "High Spend"
        elif score < overall_mean_score * 0.9:
            spend_level = "Low Spend"
        else:
            spend_level = "Average Spend"
        
        # Generate label
        if income_level == "High Income" and spend_level == "High Spend":
            label = "Target Customer (High Income, High Spend)"
        elif income_level == "High Income" and spend_level == "Low Spend":
            label = "Careful Spender (High Income, Low Spend)"
        elif income_level == "Low Income" and spend_level == "High Spend":
            label = "Impulse Buyer (Low Income, High Spend)"
        elif income_level == "Low Income" and spend_level == "Low Spend":
            label = "Sensible Customer (Low Income, Low Spend)"
        else:
            label = f"Standard Customer ({income_level}, {spend_level})"
        
        print(f"  {cluster_id}: \"{label}\"")
    
    print("\n" + "="*60)
    
    return cluster_stats

if __name__ == "__main__":
    analyze_clusters()

