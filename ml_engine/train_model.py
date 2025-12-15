import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import joblib
import os

# 1. SETUP PATHS
# Get the folder where this script lives
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Path to the dataset
DATA_PATH = os.path.join(BASE_DIR, 'data', 'Mall_Customers.csv')

# Paths where we will save the "Brain"
MODEL_PATH = os.path.join(BASE_DIR, 'saved_models', 'kmeans_v1.pkl')
SCALER_PATH = os.path.join(BASE_DIR, 'saved_models', 'scaler_v1.pkl')

def train_brain():
    print("Starting CohortAI Training...")
    
    # 2. LOAD DATA
    if not os.path.exists(DATA_PATH):
        print(f"Error: Could not find file at: {DATA_PATH}")
        return

    df = pd.read_csv(DATA_PATH)
    print(f"Loaded {len(df)} customers from CSV.")

    # 3. CLEANING
    # The Kaggle dataset has complex names like "Annual Income (k$)". 
    # Let's rename them to keep our code clean.
    df.rename(columns={
        'Annual Income (k$)': 'Annual_Income',
        'Spending Score (1-100)': 'Spending_Score'
    }, inplace=True)

    # We only need these 2 columns for clustering (excluding Age)
    features = ['Annual_Income', 'Spending_Score']
    X = df[features].values

    # 4. SCALING (Crucial for K-Means)
    # This squeezes numbers like "50,000" (Income) and "30" (Age) into a similar range (approx -2 to 2)
    print("Scaling data...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 5. TRAIN THE MODEL
    # We are asking the machine to find 5 distinct groups (Clusters)
    print("Finding patterns (K-Means)...")
    kmeans = KMeans(n_clusters=5, init='k-means++', random_state=42)
    kmeans.fit(X_scaled)

    # 6. SAVE THE BRAIN
    # We must save BOTH the model and the scaler
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(kmeans, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)

    print("---------------------------------------")
    print(f"Model Saved: {MODEL_PATH}")
    print(f"Scaler Saved: {SCALER_PATH}")
    print("---------------------------------------")

if __name__ == "__main__":
    train_brain()