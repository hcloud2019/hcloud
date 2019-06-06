from django.db import models

# Create your models here.
class File(models.Model):
    file = models.CharField(max_length=120,blank=False, null=False, default= "")
    # title = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    size = models.CharField(max_length=120, blank=False, null=False, default=0)
    # modified = models.DateTimeField(auto_now=True)
    # file_name = models.CharField(max_length=100, primary_key=True)
    # object_key = models.CharField(max_length=1025)
    # owner = models.ForeignKey('auth.User', related_name='snippets', on_delete=models.CASCADE)

    class Meta:
        ordering = ('pk',)
