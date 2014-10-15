from django.db import models

# Create your models here.

class FigConf(models.Model):

    mkChkExp = models.CharField(max_length=600)
    mkChkFld = models.CharField(max_length=100)
    adChkExp = models.CharField(max_length=600)
    adChkFld = models.CharField(max_length=100)
    selpc = models.CharField(max_length=20)
    smag = models.CharField(max_length=20)
    Op1 = models.CharField(max_length=30)
    Op2 = models.CharField(max_length=30)    
    Op3 = models.CharField(max_length=30)
    cycle3D = models.CharField(max_length=10)
    contog = models.BooleanField()
    cmap = models.CharField(max_length=30)
    kmt = models.BooleanField()
    Submit = models.BooleanField()