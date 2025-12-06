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
        # Note: Model expects 'Age', 'Annual_Income', 'Spending_Score' (as used in training)
        # But we renamed to 'Income' and 'Score' for display
        df_temp = df.copy()
        df_temp.rename(columns={'Income': 'Annual_Income', 'Score': 'Spending_Score'}, inplace=True)
        features = ['Age', 'Annual_Income', 'Spending_Score']
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
    # Define colors for each cluster
    cluster_colors = {
        0: '#3498db',  # Blue
        1: '#2ecc71',  # Green
        2: '#e74c3c',  # Red
        3: '#f39c12',  # Orange
        4: '#9b59b6',  # Purple
    }
    
    # Define marker styles for better distinction (especially for overlapping clusters)
    cluster_markers = {
        0: 'o',  # Circle
        1: 's',  # Square
        2: '^',  # Triangle
        3: 'D',  # Diamond
        4: 'v',  # Triangle down
    }
    
    # Define small offsets for clusters that overlap in 2D space
    # These clusters are separated by Age (3rd dimension) but overlap in Income vs Score
    # Small offsets help visualize both clusters without misrepresenting the data
    # Note: Clusters 0 and 3 overlap in 2D but differ in Age (Cluster 0: older, Cluster 3: younger)
    cluster_offsets = {
        0: (-2.5, -2.5),  # Cluster 0: offset down-left (older customers, age 40-70)
        1: (0, 0),         # Cluster 1: no offset
        2: (0, 0),         # Cluster 2: no offset
        3: (2.5, 2.5),     # Cluster 3: offset up-right (younger customers, age 18-40)
        4: (0, 0),         # Cluster 4: no offset
    }
    
    # Plot clusters in reverse order so smaller clusters appear on top
    # This prevents larger clusters from completely hiding smaller ones
    unique_clusters = sorted([c for c in df['Cluster'].unique() if c != -1], reverse=True)
    
    for cluster_id in unique_clusters:
        cluster_data = df[df['Cluster'] == cluster_id].copy()
        color = cluster_colors.get(cluster_id, 'lightgray')
        marker = cluster_markers.get(cluster_id, 'o')
        
        # Apply small offset to separate overlapping clusters
        offset_x, offset_y = cluster_offsets.get(cluster_id, (0, 0))
        x_coords = cluster_data['Income'] + offset_x
        y_coords = cluster_data['Score'] + offset_y
        
        # Use different opacity and size for current cluster vs others
        if cluster_id == current_cluster_id:
            alpha = 0.8
            size = 60
            edge_width = 0.8
            z_order = 5  # Higher z-order for current cluster
        else:
            alpha = 0.6  # Increased from 0.4 for better visibility
            size = 50
            edge_width = 0.3
            z_order = 1  # Lower z-order for background clusters
        
        plt.scatter(
            x=x_coords, 
            y=y_coords, 
            c=color,
            s=size, 
            alpha=alpha,
            marker=marker,
            label=f'Cluster {cluster_id}',
            edgecolors='black',
            linewidths=edge_width,
            zorder=z_order
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