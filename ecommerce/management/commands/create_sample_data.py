from django.core.management.base import BaseCommand
from ecommerce.models import Category, Product


class Command(BaseCommand):
    help = 'Creates sample categories and products for the e-commerce store'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')

        # Create Categories
        categories_data = [
            {'name': 'Electronics', 'slug': 'electronics', 'description': 'Latest electronic gadgets and devices'},
            {'name': 'Fashion', 'slug': 'fashion', 'description': 'Trendy clothing and accessories'},
            {'name': 'Home & Living', 'slug': 'home-living', 'description': 'Home decor and living essentials'},
            {'name': 'Sports', 'slug': 'sports', 'description': 'Sports equipment and gear'},
            {'name': 'Books', 'slug': 'books', 'description': 'Books and reading materials'},
            {'name': 'Beauty', 'slug': 'beauty', 'description': 'Beauty and personal care products'},
        ]

        categories = {}
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            categories[cat_data['slug']] = category
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {category.name}'))

        # Create Products
        products_data = [
            # Premium products for Target Customers (Segment 1)
            {
                'name': 'Premium Smartphone Pro',
                'slug': 'premium-smartphone-pro',
                'description': 'Latest flagship smartphone with advanced features',
                'category': categories['electronics'],
                'price': 999.99,
                'stock': 50,
                'is_premium': True,
                'target_segments': [1, 4],  # Target customers and careful spenders
            },
            {
                'name': 'Designer Leather Jacket',
                'slug': 'designer-leather-jacket',
                'description': 'High-quality designer leather jacket',
                'category': categories['fashion'],
                'price': 599.99,
                'stock': 30,
                'is_premium': True,
                'target_segments': [1],
            },
            
            # Budget products for Sensible/Budget customers (Segments 0, 3)
            {
                'name': 'Budget Smartphone',
                'slug': 'budget-smartphone',
                'description': 'Affordable smartphone with essential features',
                'category': categories['electronics'],
                'price': 199.99,
                'discount_price': 149.99,
                'stock': 100,
                'is_budget': True,
                'target_segments': [0, 3],
            },
            {
                'name': 'Basic T-Shirt Pack',
                'slug': 'basic-tshirt-pack',
                'description': 'Pack of 5 basic cotton t-shirts',
                'category': categories['fashion'],
                'price': 49.99,
                'discount_price': 39.99,
                'stock': 200,
                'is_budget': True,
                'target_segments': [0, 3],
            },
            
            # Products for Impulse Buyers (Segment 2)
            {
                'name': 'Trendy Wireless Earbuds',
                'slug': 'trendy-wireless-earbuds',
                'description': 'Latest trendy wireless earbuds with noise cancellation',
                'category': categories['electronics'],
                'price': 79.99,
                'discount_price': 59.99,
                'stock': 75,
                'target_segments': [2],
            },
            {
                'name': 'Fashion Sneakers',
                'slug': 'fashion-sneakers',
                'description': 'Stylish and comfortable sneakers',
                'category': categories['fashion'],
                'price': 89.99,
                'stock': 60,
                'target_segments': [2],
            },
            
            # General products
            {
                'name': 'Coffee Maker',
                'slug': 'coffee-maker',
                'description': 'Automatic coffee maker for your home',
                'category': categories['home-living'],
                'price': 129.99,
                'stock': 40,
                'target_segments': [1, 3, 4],
            },
            {
                'name': 'Yoga Mat',
                'slug': 'yoga-mat',
                'description': 'Premium non-slip yoga mat',
                'category': categories['sports'],
                'price': 39.99,
                'stock': 80,
                'target_segments': [0, 3, 4],
            },
            {
                'name': 'Best Seller Book Collection',
                'slug': 'bestseller-book-collection',
                'description': 'Collection of best-selling books',
                'category': categories['books'],
                'price': 49.99,
                'discount_price': 34.99,
                'stock': 150,
                'target_segments': [0, 2, 3],
            },
            {
                'name': 'Skincare Set',
                'slug': 'skincare-set',
                'description': 'Complete skincare routine set',
                'category': categories['beauty'],
                'price': 79.99,
                'stock': 50,
                'target_segments': [1, 2],
            },
        ]

        for prod_data in products_data:
            product, created = Product.objects.get_or_create(
                slug=prod_data['slug'],
                defaults=prod_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created product: {product.name}'))

        self.stdout.write(self.style.SUCCESS('\nSample data created successfully!'))
        self.stdout.write('\nYou can now:')
        self.stdout.write('1. Visit /store/ to see the e-commerce store')
        self.stdout.write('2. Create a superuser: python manage.py createsuperuser')
        self.stdout.write('3. Login and complete your profile to get personalized recommendations')

