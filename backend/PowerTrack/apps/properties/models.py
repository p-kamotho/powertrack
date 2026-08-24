from django.db import models
class Property(models.Model):
    name=models.CharField(max_length=150); address=models.TextField(blank=True); description=models.TextField(blank=True); is_active=models.BooleanField(default=True); created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self):return self.name
class Room(models.Model):
    class Status(models.TextChoices): VACANT="VACANT","Vacant"; OCCUPIED="OCCUPIED","Occupied"; MAINTENANCE="MAINTENANCE","Maintenance"
    property=models.ForeignKey(Property,on_delete=models.CASCADE,related_name="rooms"); room_number=models.CharField(max_length=30); status=models.CharField(max_length=20,choices=Status.choices,default=Status.VACANT); floor=models.CharField(max_length=30,blank=True); description=models.TextField(blank=True)
    class Meta: constraints=[models.UniqueConstraint(fields=["property","room_number"],name="unique_room_per_property")]
    def __str__(self):return f"{self.property.name} • Room {self.room_number}"
