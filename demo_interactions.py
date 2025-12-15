"""
Demo script to show how the recommendation system works
Run this with: python manage.py shell < demo_interactions.py
"""

from ecommerce.models import UserProductInteraction, Product
from django.contrib.auth import get_user_model
from ecommerce.recommendations import RecommendationEngine
User = get_user_model()

print("=== RECOMMENDATION SYSTEM DEMO ===\n")

# Create test users with different preferences
users_data = [
    ('fashion_lover', 'fashion@example.com', ['Designer Leather Jacket', 'Luxury Skincare Set']),
    ('tech_enthusiast', 'tech@example.com', ['Premium Smartphone Pro']),
    ('home_maker', 'home@example.com', ['Ikoti', 'Isabune']),
]

for username, email, products in users_data:
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = User.objects.create_user(username, email, 'testpass123')
        print(f"Created user: {username}")
    
    # Clear existing interactions
    UserProductInteraction.objects.filter(user=user).delete()
    
    # Add interactions
    for product_name in products:
        product = Product.objects.filter(name__contains=product_name).first()
        if product:
            # View interaction
            UserProductInteraction.objects.create(
                user=user,
                product=product,
                interaction_type='view',
                interaction_weight=0.1
            )
            # Add to cart interaction (stronger signal)
            UserProductInteraction.objects.create(
                user=user,
                product=product,
                interaction_type='add_to_cart',
                interaction_weight=0.5
            )
            print(f"  - {username} viewed and added {product.name} to cart")
    
    # Get recommendations
    engine = RecommendationEngine(user)
    recommendations = engine.get_recommendations(limit=3)
    
    print(f"\nRecommendations for {username}:")
    for i, product in enumerate(recommendations, 1):
        print(f"  {i}. {product.name} - {product.category.name} - ${product.price}")
    print()

print("=== INTERACTION TRACKING ===")
print("The system tracks:")
print("1. Product views (weight: 0.1)")
print("2. Add to cart (weight: 0.5)")
print("3. Purchases (weight: 1.0)")
print("\nRecommendations are based on:")
print("- Content similarity (product attributes, tags, category)")
print("- Collaborative filtering (users with similar behavior)")
print("- Popular products as fallback")

print("\n=== HOW TO TEST IN THE BROWSER ===")
print("1. Register a new user or login")
print("2. Browse products - views are tracked automatically")
print("3. Add products to cart")
print("4. Check the homepage and product detail pages for personalized recommendations")
print("5. The more you interact, the better the recommendations become!")
