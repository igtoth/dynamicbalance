from django.db import models

# Create your models here.

class Tickers(models.Model):
    name = models.CharField(max_length=255)
    label = models.CharField(max_length=255)
    label_full = models.CharField(max_length=255)

    def __self__(self):
        return self.name


