from django.core.management.base import BaseCommand
from django.db import transaction
from ecommerce.models import Product, ProductSimilarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class Command(BaseCommand):
    help = 'Update product similarity matrix'

    def handle(self, *args, **options):
        self.stdout.write("Updating product similarities...")
        
        # Get all active products
        products = list(Product.objects.filter(is_active=True))
        
        if not products:
            self.stdout.write(self.style.ERROR("No active products found."))
            return
            
        # Create product features (name + description + category + tags)
        product_features = []
        for p in products:
            tags = " ".join(tag.name for tag in p.tags.all())
            features = f"{p.name} {p.description} {p.category.name} {tags}"
            product_features.append(features.lower())
        
        # Calculate TF-IDF vectors
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(product_features)
        
        # Calculate cosine similarity
        cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
        
        # Update database
        with transaction.atomic():
            # Clear existing similarities
            ProductSimilarity.objects.all().delete()
            
            # Add new similarities
            for i, product in enumerate(products):
                # Get top 5 most similar products (excluding self)
                similar_indices = cosine_sim[i].argsort()[-6:-1][::-1]
                
                for idx in similar_indices:
                    if idx != i:  # Don't include self
                        similarity = float(cosine_sim[i][idx])
                        if similarity > 0.1:  # Only save meaningful similarities
                            ProductSimilarity.objects.create(
                                product=product,
                                similar_product=products[idx],
                                similarity_score=similarity
                            )
        
        self.stdout.write(
            self.style.SUCCESS(f"Successfully updated similarities for {len(products)} products")
        )
