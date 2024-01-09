from django.db import models

# Create your models here.
class RoomsModel(models.Model):
    #name = models.CharField(max_length=255)
    #description = models.TextField()
    # IntegerField with default value
    id = models.IntegerField(default=0)
    # IntegerField allowing blank values
    #your_nullable_integer_field = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.name
