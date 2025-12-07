from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from .models import Category, Product, CustomerProfile, Cart, Order, OrderItem
from ml_engine.registry import ClusterRegistry
from ml_engine.logic import get_cluster_name
import json


def home(request):
    """Homepage with personalized product recommendations"""
    categories = Category.objects.all()[:6]
    
    # Get personalized products based on user segment
    products = list(Product.objects.filter(is_active=True))
    
    if request.user.is_authenticated:
        try:
            profile = request.user.customer_profile
            if profile.segment is not None:
                # Filter products for user's segment (Python filtering for SQLite compatibility)
                segment = profile.segment
                filtered_products = []
                for product in products:
                    # Check if segment is in target_segments list
                    if segment in (product.target_segments or []):
                        filtered_products.append(product)
                    # Target customers get premium products
                    elif segment == 1 and product.is_premium:
                        filtered_products.append(product)
                    # Sensible/Budget customers get budget items
                    elif segment in [0, 3] and product.is_budget:
                        filtered_products.append(product)
                
                products = filtered_products if filtered_products else products
        except CustomerProfile.DoesNotExist:
            pass
    
    featured_products = products[:8]
    new_products = list(Product.objects.filter(is_active=True).order_by('-created_at')[:8])
    
    context = {
        'categories': categories,
        'featured_products': featured_products,
        'new_products': new_products,
    }
    return render(request, 'ecommerce/home.html', context)


def product_list(request, category_slug=None):
    """Product listing page with filtering"""
    products = Product.objects.filter(is_active=True)
    category = None
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    # Convert to list early for consistent handling
    products = list(products)
    
    # Segment-based filtering for authenticated users
    if request.user.is_authenticated:
        try:
            profile = request.user.customer_profile
            if profile.segment is not None:
                segment_filter = request.GET.get('segment_filter', 'all')
                if segment_filter == 'personalized':
                    # Python filtering for SQLite compatibility
                    segment = profile.segment
                    filtered_products = []
                    for product in products:
                        if segment in (product.target_segments or []):
                            filtered_products.append(product)
                        elif segment == 1 and product.is_premium:
                            filtered_products.append(product)
                        elif segment in [0, 3] and product.is_budget:
                            filtered_products.append(product)
                    products = filtered_products if filtered_products else products
        except CustomerProfile.DoesNotExist:
            pass
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        products = [p for p in products if search_query.lower() in p.name.lower() or search_query.lower() in p.description.lower()]
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.all()
    
    context = {
        'products': page_obj,
        'categories': categories,
        'current_category': category,
        'search_query': search_query,
    }
    return render(request, 'ecommerce/product_list.html', context)


def product_detail(request, product_slug):
    """Product detail page with personalized recommendations"""
    product = get_object_or_404(Product, slug=product_slug, is_active=True)
    
    # Get similar products (same category)
    similar_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]
    
    # Personalized recommendations based on segment
    recommended_products = None
    if request.user.is_authenticated:
        try:
            profile = request.user.customer_profile
            if profile.segment is not None:
                # Python filtering for SQLite compatibility
                segment = profile.segment
                all_products = list(Product.objects.filter(is_active=True).exclude(id=product.id))
                filtered_products = []
                for prod in all_products:
                    if segment in (prod.target_segments or []):
                        filtered_products.append(prod)
                    elif segment == 1 and prod.is_premium:
                        filtered_products.append(prod)
                    elif segment in [0, 3] and prod.is_budget:
                        filtered_products.append(prod)
                recommended_products = filtered_products[:4] if filtered_products else all_products[:4]
        except CustomerProfile.DoesNotExist:
            pass
    
    context = {
        'product': product,
        'similar_products': similar_products,
        'recommended_products': recommended_products or similar_products,
    }
    return render(request, 'ecommerce/product_detail.html', context)


@login_required
def cart_view(request):
    """Shopping cart page"""
    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.total_price for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'ecommerce/cart.html', context)


@login_required
@require_POST
def add_to_cart(request, product_id):
    """Add product to cart"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > product.stock:
        messages.error(request, f'Only {product.stock} items available in stock.')
        return redirect('ecommerce:product_detail', product_slug=product.slug)
    
    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not created:
        cart_item.quantity += quantity
        if cart_item.quantity > product.stock:
            cart_item.quantity = product.stock
        cart_item.save()
    
    messages.success(request, f'{product.name} added to cart!')
    return redirect('ecommerce:cart')


@login_required
@require_POST
def update_cart(request, cart_id):
    """Update cart item quantity"""
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > cart_item.product.stock:
        messages.error(request, f'Only {cart_item.product.stock} items available.')
        return redirect('ecommerce:cart')
    
    if quantity <= 0:
        cart_item.delete()
        messages.success(request, 'Item removed from cart.')
    else:
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, 'Cart updated!')
    
    return redirect('ecommerce:cart')


@login_required
def remove_from_cart(request, cart_id):
    """Remove item from cart"""
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    cart_item.delete()
    messages.success(request, 'Item removed from cart.')
    return redirect('ecommerce:cart')


@login_required
def checkout(request):
    """Checkout page"""
    cart_items = Cart.objects.filter(user=request.user)
    
    if not cart_items.exists():
        messages.warning(request, 'Your cart is empty.')
        return redirect('ecommerce:cart')
    
    total = sum(item.total_price for item in cart_items)
    
    # Get user profile for pre-filling
    try:
        profile = request.user.customer_profile
    except CustomerProfile.DoesNotExist:
        profile = None
    
    context = {
        'cart_items': cart_items,
        'total': total,
        'profile': profile,
    }
    return render(request, 'ecommerce/checkout.html', context)


@login_required
@require_POST
def process_checkout(request):
    """Process order"""
    cart_items = Cart.objects.filter(user=request.user)
    
    if not cart_items.exists():
        messages.error(request, 'Your cart is empty.')
        return redirect('ecommerce:cart')
    
    shipping_address = request.POST.get('shipping_address', '')
    if not shipping_address:
        messages.error(request, 'Please provide a shipping address.')
        return redirect('ecommerce:checkout')
    
    # Calculate total
    total = sum(item.total_price for item in cart_items)
    
    # Create order
    order = Order.objects.create(
        user=request.user,
        total_amount=total,
        shipping_address=shipping_address,
    )
    
    # Create order items
    for cart_item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            quantity=cart_item.quantity,
            price=cart_item.product.current_price,
        )
        # Update stock
        cart_item.product.stock -= cart_item.quantity
        cart_item.product.save()
    
    # Clear cart
    cart_items.delete()
    
    messages.success(request, f'Order {order.order_number} placed successfully!')
    return redirect('ecommerce:order_detail', order_number=order.order_number)


@login_required
def order_list(request):
    """User's order history"""
    orders = Order.objects.filter(user=request.user)
    context = {
        'orders': orders,
    }
    return render(request, 'ecommerce/order_list.html', context)


@login_required
def order_detail(request, order_number):
    """Order detail page"""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    context = {
        'order': order,
    }
    return render(request, 'ecommerce/order_detail.html', context)


@login_required
def profile(request):
    """User profile with segment information"""
    try:
        profile = request.user.customer_profile
    except CustomerProfile.DoesNotExist:
        profile = CustomerProfile.objects.create(user=request.user)
    
    context = {
        'profile': profile,
    }
    return render(request, 'ecommerce/profile.html', context)


@login_required
@require_POST
def update_segment(request):
    """Update user segment based on demographics"""
    try:
        profile = request.user.customer_profile
    except CustomerProfile.DoesNotExist:
        profile = CustomerProfile.objects.create(user=request.user)
    
    age = request.POST.get('age')
    income = request.POST.get('annual_income')
    score = request.POST.get('spending_score')
    
    if age and income and score:
        try:
            age = int(age)
            income = float(income)
            score = int(score)
            
            profile.age = age
            profile.annual_income = income
            profile.spending_score = score
            
            # Get segment from ML model
            registry = ClusterRegistry.get_instance()
            segment_id = registry.predict_segment(age, income, score)
            segment_label = get_cluster_name(segment_id)
            
            profile.segment = segment_id
            profile.segment_label = segment_label
            profile.save()
            
            messages.success(request, 'Your preferences have been updated! You\'ll now see personalized product recommendations.')
        except (ValueError, TypeError):
            messages.error(request, 'Invalid input values.')
    else:
        messages.error(request, 'Please fill all fields.')
    
    return redirect('ecommerce:profile')


def segment_info(request):
    """AJAX endpoint for segment information"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    try:
        profile = request.user.customer_profile
        if profile.segment is None:
            return JsonResponse({'error': 'No segment assigned'}, status=400)
        
        return JsonResponse({
            'segment_id': profile.segment,
            'segment_label': profile.segment_label,
            'age': profile.age,
            'income': float(profile.annual_income) if profile.annual_income else None,
            'score': profile.spending_score,
        })
    except CustomerProfile.DoesNotExist:
        return JsonResponse({'error': 'Profile not found'}, status=404)


def register_view(request):
    """User registration"""
    if request.user.is_authenticated:
        return redirect('ecommerce:home')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create customer profile
            CustomerProfile.objects.create(user=user)
            # Auto-login after registration
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, f'Welcome {username}! Please complete your profile for personalized recommendations.')
                return redirect('ecommerce:profile')
    else:
        form = UserCreationForm()
    
    return render(request, 'ecommerce/register.html', {'form': form})


def login_view(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('ecommerce:home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            next_url = request.GET.get('next', 'ecommerce:home')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'ecommerce/login.html')


@login_required
def logout_view(request):
    """User logout"""
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('ecommerce:home')
