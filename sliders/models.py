from django.db import models
from cloudinary.models import CloudinaryField

# Create your models here.
class Slider(models.Model):     
    order = models.CharField(max_length=2, verbose_name=("Orden"))
    image = CloudinaryField(
        "Imagen",
        blank=True,
        transformation=[
            {"width": 800, "crop": "limit"},           
        ],
        format="webp",
    )    

    class Meta:
        verbose_name = "Slider"
        verbose_name_plural = "Sliders"
 
    def __str__(self):
        return self.order
