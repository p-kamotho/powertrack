from django.db import models
class Tariff(models.Model):
    name=models.CharField(max_length=100);rate_per_kwh=models.DecimalField(max_digits=10,decimal_places=2);effective_from=models.DateField();effective_to=models.DateField(null=True,blank=True);is_active=models.BooleanField(default=True)
    def __str__(self):return f"{self.name} • KSh {self.rate_per_kwh}/kWh"
