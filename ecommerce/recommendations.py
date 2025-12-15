from django.db.models import Count
from .models import Product, UserProductInteraction, ProductSimilarity

class RecommendationEngine:
    def __init__(self, user):
        self.user = user
    
    def get_recommendations(self, limit=10):
        """Get hybrid recommendations for the user"""
        # Get content-based recommendations
        content_based = self._get_content_based_recommendations(limit//2)
        
        # Get collaborative filtering recommendations
        collaborative = self._get_collaborative_recommendations(limit//2)
        
        # Combine and deduplicate
        seen = set()
        recommendations = []
        
        for product in [*content_based, *collaborative]:
            if product.id not in seen:
                seen.add(product.id)
                recommendations.append(product)
                if len(recommendations) >= limit:
                    break
        
        return recommendations[:limit]
    
    def _get_content_based_recommendations(self, limit):
        """Get recommendations based on product similarity"""
        # Get user's recently interacted products
        recent_interactions = UserProductInteraction.objects.filter(
            user=self.user
        ).select_related('product').order_by('-created_at')[:20]
        
        if not recent_interactions:
            return self._get_popular_products(limit)
        
        # Get similar products
        similar_products = ProductSimilarity.objects.filter(
            product__in=[i.product for i in recent_interactions]
        ).exclude(
            similar_product__in=[i.product for i in recent_interactions]
        ).order_by('-similarity_score')[:limit*2]
        
        return [s.similar_product for s in similar_products][:limit]
    
    def _get_collaborative_recommendations(self, limit):
        """Get recommendations based on user behavior"""
        # Find users with similar interactions
        similar_users = self._find_similar_users(limit=3)
        if not similar_users:
            return self._get_popular_products(limit)
            
        # Get products those users interacted with
        return Product.objects.filter(
            userproductinteraction__user__in=similar_users
        ).exclude(
            userproductinteraction__user=self.user
        ).annotate(
            interaction_count=Count('userproductinteraction')
        ).order_by('-interaction_count')[:limit]
    
    def _find_similar_users(self, limit=3):
        """Find users with similar interaction patterns"""
        # Get current user's interactions
        user_products = set(UserProductInteraction.objects.filter(
            user=self.user
        ).values_list('product_id', flat=True))
        
        if not user_products:
            return []
            
        # Find users who interacted with the same products
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        return list(User.objects.filter(
            userproductinteraction__product_id__in=user_products
        ).exclude(
            id=self.user.id
        ).annotate(
            common_products=Count('userproductinteraction__product')
        ).order_by('-common_products')[:limit])
    
    def _get_popular_products(self, limit):
        """Fallback to popular products"""
        return Product.objects.annotate(
            popularity=Count('userproductinteraction')
        ).order_by('-popularity')[:limit]
