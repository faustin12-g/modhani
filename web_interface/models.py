from django.db import models

class CustomerLog(models.Model):
    # Inputs
    age = models.IntegerField()
    annual_income = models.FloatField()
    spending_score = models.FloatField()
    
    # Outputs
    predicted_cluster = models.IntegerField()
    segment_label = models.CharField(max_length=100)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.segment_label} - {self.created_at.strftime('%Y-%m-%d')}"