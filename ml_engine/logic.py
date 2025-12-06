# Dynamic cluster labeling based on actual data characteristics
# This ensures labels match what the clusters actually represent in the visualization

def get_cluster_name(cluster_id):
    """
    Dynamically determine cluster label based on actual cluster characteristics.
    This ensures labels match what's shown in the visualization.
    """
    from ml_engine.registry import ClusterRegistry
    
    registry = ClusterRegistry.get_instance()
    cluster_stats = registry.get_cluster_stats()
    
    # If cluster stats are not available, fall back to generic label
    if cluster_stats is None or cluster_id not in cluster_stats:
        return f"Cluster {cluster_id} (Unknown Segment)"
    
    stats = cluster_stats[cluster_id]
    mean_income = stats['mean_income']
    mean_score = stats['mean_score']
    overall_mean_income = stats['overall_mean_income']
    overall_mean_score = stats['overall_mean_score']
    
    # Determine income level (using 15% threshold for more accurate classification)
    # This helps avoid mislabeling clusters that are close to average
    if mean_income > overall_mean_income * 1.15:
        income_level = "High Income"
    elif mean_income < overall_mean_income * 0.85:
        income_level = "Low Income"
    else:
        income_level = "Average Income"
    
    # Determine spending level (using 15% threshold)
    if mean_score > overall_mean_score * 1.15:
        spend_level = "High Spend"
    elif mean_score < overall_mean_score * 0.85:
        spend_level = "Low Spend"
    else:
        spend_level = "Average Spend"
    
    # Generate descriptive label based on actual characteristics
    if income_level == "High Income" and spend_level == "High Spend":
        return "Target Customer (High Income, High Spend)"
    elif income_level == "High Income" and spend_level == "Low Spend":
        return "Careful Spender (High Income, Low Spend)"
    elif income_level == "Low Income" and spend_level == "High Spend":
        return "Impulse Buyer (Low Income, High Spend)"
    elif income_level == "Low Income" and spend_level == "Low Spend":
        return "Sensible Customer (Low Income, Low Spend)"
    elif income_level == "Average Income" and spend_level == "Average Spend":
        return "Standard Customer (Average Income, Average Spend)"
    elif income_level == "Average Income" and spend_level == "Low Spend":
        return "Budget-Conscious Customer (Average Income, Low Spend)"
    elif income_level == "Average Income" and spend_level == "High Spend":
        return "Value Seeker (Average Income, High Spend)"
    elif income_level == "High Income" and spend_level == "Average Spend":
        return "Moderate Spender (High Income, Average Spend)"
    elif income_level == "Low Income" and spend_level == "Average Spend":
        return "Balanced Customer (Low Income, Average Spend)"
    else:
        # Fallback for any other combination
        return f"Customer ({income_level}, {spend_level})"