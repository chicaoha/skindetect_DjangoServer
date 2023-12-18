from sys import setprofile
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True)
    gender = models.CharField(max_length=10,blank=True)
    user_address = models.CharField(max_length=255,blank=True)
    user_phone = models.CharField(max_length=15,blank=True)
    user_dob = models.DateField(null=True,blank=True)
    user_avatar = models.BinaryField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} Profile' 

    # def saveProfile(self, *args, kwargs):
    # # if kwargs['created']:
    #     # user_profile = setprofile.objects.created(user=kwargs['instance'])
    #     super().save(**args, **kwargs)

    #     # post_save.connect(createProfile, sender=User)
    #     #REZIE THE IMAGE
    #     img = Image.open(self.avatar.path)
    #     if img.height > 300 or img.width > 300:
    #         output_size = (300, 300)
    #     #CREATE A THUMBNAIL
    #         img.thumbnail(output_size)
    #     #OVERWRITE THE LARGE IMAGE
    #         img.save(self.avatar.path)   

