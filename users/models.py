from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django.db.models.signals import pre_save
from django.dispatch import receiver

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='profile_pics/', default='profile_pics/default.jpg')
    dob = models.DateField(null=True)
    gender = models.CharField(max_length=10, null=True)
    address = models.CharField(max_length = 150, null=True)
    phone = models.CharField(max_length = 10, null=True)

    def __str__(self):
        return f'{self.user.username} Profile'  
class DetectInfo(models.Model):
    detect_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    detect_date = models.DateTimeField()
    detect_photo = models.ImageField(upload_to='detect_pics/')
    detect_result = models.FileField(upload_to='detect_tex/')
    disease = models.ForeignKey('SkinDisease', on_delete=models.CASCADE)
    detect_score = models.FloatField()
    
    def __str__(self) -> str:
        return super().__str__()
    

class SkinDisease(models.Model):
    disease_id = models.AutoField(primary_key=True)
    disease_name = models.CharField(max_length =255)
    disease_overview = models.TextField()
    disease_symptoms = models.TextField()
    disease_causeses = models.TextField()
    disease_preventions = models.TextField()
    disease_image1 = models.ImageField(upload_to='disease_pics/', null=True)
    disease_image2 = models.ImageField(upload_to='disease_pics/', null=True)
    disease_image3 = models.ImageField(upload_to='disease_pics/', null=True)
    disease_image4 = models.ImageField(upload_to='disease_pics/', null=True)
    disease_image5 = models.ImageField(upload_to='disease_pics/', null=True)

    def __str__(self) -> str:
        return self.disease_name
@receiver(pre_save, sender=Profile)
def delete_old_avatar(sender, instance, **kwargs):
    try:
        old_instance = Profile.objects.get(pk=instance.pk)
        if old_instance.avatar and old_instance.avatar != instance.avatar:
            old_instance.avatar.delete(save=False)
    except Profile.DoesNotExist:
        pass

# Save the new avatar and resize if needed
@receiver(pre_save, sender=Profile)
def save_new_avatar(sender, instance, **kwargs):
    img = Image.open(instance.avatar.path)
    if img.height > 300 or img.width > 300:
        output_size = (300, 300)
        img.thumbnail(output_size)
        img.save(instance.avatar.path)

# Connect the signal handlers
pre_save.connect(delete_old_avatar, sender=Profile)
pre_save.connect(save_new_avatar, sender=Profile)  


