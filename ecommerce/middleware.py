import re
from django.utils.deprecation import MiddlewareMixin
from .models import UserProductInteraction

class UserTrackingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not request.user.is_authenticated or not request.method == 'GET':
            return None
            
        # Track product views
        product_detail_match = re.match(r'^/product/(?P<slug>[\w-]+)/?$', request.path)
        if product_detail_match:
            from .models import Product
            try:
                product = Product.objects.get(slug=product_detail_match.group('slug'))
                UserProductInteraction.objects.update_or_create(
                    user=request.user,
                    product=product,
                    interaction_type='view',
                    defaults={'interaction_weight': 0.1}
                )
            except Product.DoesNotExist:
                pass
                
        return None
