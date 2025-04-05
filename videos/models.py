from django.db import models


class Video(models.Model):   
    video_url = models.URLField(blank=True, null=True, verbose_name=("Video"))
    name = models.CharField(max_length=200, blank=True, null=True, verbose_name=("Nombre"))
    # created_date = models.DateTimeField(auto_now_add=True, verbose_name=("Creado"))

    class Meta:  
        verbose_name = "Video"
        verbose_name_plural = "Videos"
        
    
    
    def __str__(self):
        return f"{self.name}"