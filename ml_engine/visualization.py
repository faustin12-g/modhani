import matplotlib
matplotlib.use('Agg')  # Required for Django to run headers-less
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import io
import base64
import os
import numpy as np
import joblib

# Define Path to Data (for background context)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'Mall_Customers.csv')
MODEL_PATH = os.path.join(BASE_DIR, 'saved_models', 'kmeans_v1.pkl')
SCALER_PATH = os.path.join(BASE_DIR, 'saved_models', 'scaler_v1.pkl')

def generate_cluster_plot(user_income, user_score, current_cluster_id):
    """
    Generates a scatter plot image showing clusters in different colors.
    This makes it clear which cluster the customer belongs to.
    """
    # 1. Load Background Data
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH)
        # Rename for consistency
        df.rename(columns={'Annual Income (k$)': 'Income', 'Spending Score (1-100)': 'Score'}, inplace=True)
    else:
        return None

    # 2. Load model and scaler to get cluster assignments
    try:
        model = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
        
        # Get cluster assignments for all customers
        # Prepare features for prediction (only Income and Spending Score)
        df_temp = df.copy()
        df_temp.rename(columns={'Income': 'Annual_Income', 'Score': 'Spending_Score'}, inplace=True)
        features = ['Annual_Income', 'Spending_Score']
        X = df_temp[features].values
        X_scaled = scaler.transform(X)
        df['Cluster'] = model.predict(X_scaled)
    except Exception as e:
        # If model loading fails, just show all as gray
        print(f"Warning: Could not load model for visualization: {e}")
        df['Cluster'] = -1

    # 3. Setup the Plot
    # Close any existing figures to prevent multiple stars from appearing
    plt.close('all')
    plt.figure(figsize=(10, 7))
    sns.set_style("whitegrid")

    # 4. Plot customers by cluster with different colors
    scatter = sns.scatterplot(
        x='Income', 
        y='Score',
        hue='Cluster',
        palette='viridis',
        data=df,
        legend='full',
        alpha=0.7
    )

    # 5. Plot the CURRENT User (Big Red Star with black border)
    plt.scatter(
        x=[user_income], 
        y=[user_score], 
        color='red', 
        s=400, 
        marker='*', 
        label='Current Customer',
        zorder=10,  # Force it to the top
        edgecolors='black',
        linewidths=2
    )

    # 6. Add Labels
    plt.title(f"Customer Segmentation Map (Your Customer: Cluster {current_cluster_id})", fontsize=14, fontweight='bold')
    plt.xlabel("Annual Income (k$)", fontsize=12)
    plt.ylabel("Spending Score (1-100)", fontsize=12)
    # Add note about 3D clustering
    plt.text(0.02, 0.98, "Note: Clusters are separated by Age, Income, and Spending Score.\nOverlapping clusters differ in Age.", 
             transform=plt.gca().transAxes, fontsize=8, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    plt.legend(loc='upper right', fontsize=9)
    plt.grid(True, alpha=0.3)

    # 7. Save to Memory (Buffer) instead of a file
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
    buffer.seek(0)
    
    # 8. Convert to Base64 String (for HTML)
    image_png = buffer.getvalue()
    buffer.close()
    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')
    
    plt.close() # Close plot to free memory
    
    return graphic