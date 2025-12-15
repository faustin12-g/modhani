from django.contrib import admin
from .models import CustomerLog

@admin.register(CustomerLog)
class CustomerLogAdmin(admin.ModelAdmin):
    list_display = ('segment_label', 'annual_income', 'spending_score', 'created_at')
    list_filter = ('segment_label', 'created_at')