from django import template
from ecommerce.recommendations import RecommendationEngine

register = template.Library()

@register.inclusion_tag('ecommerce/recommendations.html')
def show_recommendations(user, limit=4):
    if not user.is_authenticated:
        return {'recommendations': []}
    
    engine = RecommendationEngine(user)
    recommendations = engine.get_recommendations(limit=limit)
    return {'recommendations': recommendations}
