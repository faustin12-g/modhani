import joblib
import os
import numpy as np
import pandas as pd

class ClusterRegistry:
    _instance = None
    _model = None
    _scaler = None
    _cluster_stats = None  # Store cluster characteristics

    @classmethod
    def get_instance(cls):
        """
        Singleton Pattern: Checks if the brain is loaded.
        If yes, returns it. If no, loads it first.
        """
        if cls._instance is None:
            cls._instance = ClusterRegistry()
            cls._instance._load_artifacts()
        return cls._instance

    def _load_artifacts(self):
        """
        Internal method to load the .pkl files from the hard drive.
        """
        # Determine the path to the 'saved_models' folder relative to this file
        base_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(base_dir, 'saved_models', 'kmeans_v1.pkl')
        scaler_path = os.path.join(base_dir, 'saved_models', 'scaler_v1.pkl')
        data_path = os.path.join(base_dir, 'data', 'Mall_Customers.csv')
        
        print("---------------------------------------")
        print(f"Loading CohortAI Artifacts...")
        
        try:
            self._model = joblib.load(model_path)
            self._scaler = joblib.load(scaler_path)
            print("Brain Loaded: K-Means Model & Scaler are ready.")
            
            # Analyze clusters to determine their actual characteristics
            self._analyze_clusters(data_path)
        except FileNotFoundError:
            print(f"ERROR: Could not find .pkl files at {model_path}")
            print("   Did you run 'train_model.py'?")
        print("---------------------------------------")

    def _analyze_clusters(self, data_path):
        """
        Analyze the actual cluster characteristics from the training data.
        This ensures labels match what the clusters actually represent.
        """
        try:
            # Load the training data
            df = pd.read_csv(data_path)
            df.rename(columns={
                'Annual Income (k$)': 'Annual_Income',
                'Spending Score (1-100)': 'Spending_Score'
            }, inplace=True)
            
            # Prepare features and get cluster assignments
            features = ['Age', 'Annual_Income', 'Spending_Score']
            X = df[features].values
            X_scaled = self._scaler.transform(X)
            df['Cluster'] = self._model.predict(X_scaled)
            
            # Calculate statistics for each cluster
            self._cluster_stats = {}
            overall_mean_income = df['Annual_Income'].mean()
            overall_mean_score = df['Spending_Score'].mean()
            
            for cluster_id in sorted(df['Cluster'].unique()):
                cluster_data = df[df['Cluster'] == cluster_id]
                self._cluster_stats[cluster_id] = {
                    'mean_income': cluster_data['Annual_Income'].mean(),
                    'mean_score': cluster_data['Spending_Score'].mean(),
                    'mean_age': cluster_data['Age'].mean(),
                    'count': len(cluster_data),
                    'overall_mean_income': overall_mean_income,
                    'overall_mean_score': overall_mean_score
                }
            
            print("Cluster characteristics analyzed and stored.")
        except Exception as e:
            print(f"Warning: Could not analyze clusters: {e}")
            self._cluster_stats = None

    def get_cluster_stats(self):
        """Return the cluster statistics for label generation."""
        return self._cluster_stats

    def predict_segment(self, age, income, score):
        """
        Takes raw customer data, scales it, and returns the Cluster ID.
        """
        # 1. Prepare input (2D array expected by sklearn)
        # The order MUST match exactly what we used in training: [Age, Annual_Income, Spending_Score]
        raw_input = np.array([[age, income, score]])
        
        # 2. Scale the data
        # We must use the SAME scaler we saved. 
        # (e.g., it knows that '50,000' is an average income, not a huge number)
        scaled_input = self._scaler.transform(raw_input)
        
        # 3. Predict the Cluster
        cluster_id = self._model.predict(scaled_input)[0]
        
        return int(cluster_id)