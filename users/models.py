# from django.contrib.auth.models import AbstractUser
from email.policy import default
import os
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist


from django.core.files.storage import default_storage

def profile_image_path(instance, filename):
    # Upload to 'media/profile_pics/{user_id}/' directory with a unique filename
    folder_path = os.path.join('profile_pics', str(instance.user_id))
    os.makedirs(folder_path, exist_ok=True)
    return os.path.join(folder_path, filename)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to=profile_image_path, default='default.jpg', max_length=255)
    dob = models.DateField(null=True)
    gender = models.CharField(max_length=10, null=True)
    address = models.CharField(max_length = 150, null=True)
    phone = models.CharField(max_length = 10, null=True)

    def __str__(self):
        return f'{self.user.username} Profile'
    
class SkinDisease(models.Model):
    disease_id = models.AutoField(primary_key=True)
    disease_name = models.CharField(max_length =255)
    disease_overview = models.TextField(null = True)
    disease_symptoms = models.TextField(null = True)
    disease_causeses = models.TextField(null = True)
    disease_preventions = models.TextField(null = True)
    disease_images_folder = models.TextField(null = True)

    def __str__(self) -> str:
        return self.disease_name
    
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class DetectInfo(models.Model):
    detect_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    detect_date = models.DateTimeField()
    detect_photo = models.ImageField(upload_to='detect_pics/')
    detect_result = models.TextField(null=True)   
    disease = models.ForeignKey(SkinDisease, on_delete=models.CASCADE, null=True)
    detect_score = models.FloatField(null=True)
    
    def __str__(self) -> str:
        return super().__str__()

@receiver(post_save, sender=Profile)
def create_profile_image_path(sender, instance, created, **kwargs):
    if created:
        profile_image_path(instance, instance.avatar.name)
        instance.save()

@receiver(pre_save, sender=Profile)
def delete_old_avatar(sender, instance, **kwargs):
    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except ObjectDoesNotExist:
        return

    # Check if a new avatar file is being set
    if old_instance.avatar and old_instance.avatar != instance.avatar:
        try:
            # Delete the old avatar file only if it is not the default avatar
            if not old_instance.avatar.name.endswith('default.jpg'):
                old_avatar_path = old_instance.avatar.path
                old_instance.avatar.delete(save=False)

                # Confirm that the file is deleted
                if os.path.exists(old_avatar_path):
                    print(f"Failed to delete old avatar file at path: {old_avatar_path}")
                else:
                    print(f"Successfully deleted old avatar file at path: {old_avatar_path}")

        except PermissionError:
            # Handle PermissionError (file in use) here, log it or take appropriate action
            print(f"Permission error while deleting old avatar file at path")
            pass    


# Save the new avatar and resize if needed
@receiver(pre_save, sender=Profile)
def save_new_avatar(sender, instance, **kwargs):
    img = Image.open(instance.avatar.path)

    # Convert the image to RGB if it has an alpha channel
    if img.mode == 'RGBA':
        img = img.convert('RGB')

    if img.height > 300 or img.width > 300:
        output_size = (300, 300)
        img.thumbnail(output_size)
    img.save(instance.avatar.path, 'JPEG', quality=95)
