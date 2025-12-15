from django.shortcuts import render
from ml_engine.registry import ClusterRegistry
from ml_engine.logic import get_cluster_name
from ml_engine.visualization import generate_cluster_plot  # <--- NEW IMPORT
from .models import CustomerLog

def index(request):
    context = {}
    
    if request.method == 'POST':
        try:
            # 1. Get Data
            income = float(request.POST.get('income', 0))
            score = float(request.POST.get('score', 0))

            # 2. Predict
            registry = ClusterRegistry.get_instance()
            cluster_id = registry.predict_segment(0, income, score)  # Passing 0 for age (not used)
            segment_label = get_cluster_name(cluster_id)

            # 3. Generate Plot (NEW STEP) 
            # We pass the income and score to draw the map
            plot_image = generate_cluster_plot(income, score, cluster_id)

            # 4. Save to DB
            CustomerLog.objects.create(
                annual_income=income,
                spending_score=score,
                predicted_cluster=cluster_id,
                segment_label=segment_label
            )

            # 5. Context
            context = {
                'prediction_made': True,
                'segment_label': segment_label,
                'cluster_id': cluster_id,
                'plot_image': plot_image,  # <--- Send image to HTML
                'input_income': income,
                'input_score': score,
            }
            
        except ValueError:
            context['error_message'] = "Please enter valid numbers!"

    return render(request, 'index.html', context)