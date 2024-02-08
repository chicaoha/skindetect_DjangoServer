# from django.contrib.auth.models import AbstractUser
from email.policy import default
import os
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from PIL import Image, UnidentifiedImageError
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
class DetectInfo(models.Model):
    detect_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    detect_date = models.DateTimeField()
    detect_photo = models.ImageField(upload_to='detect_pics/')
    detect_result = models.CharField(max_length=255)
    disease = models.ForeignKey('SkinDisease', on_delete=models.CASCADE)
    detect_score = models.FloatField()
    
    def __str__(self) -> str:
        return super().__str__()
    

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
class DetectInfo(models.Model):
    detect_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    detect_date = models.DateTimeField()
    detect_photo = models.ImageField(upload_to='detect_pics/')
    detect_result = models.TextField()   
    disease = models.ForeignKey(SkinDisease, on_delete=models.CASCADE)
    detect_score = models.FloatField()
    
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

        
# @receiver(pre_save, sender=Profile)
# def delete_old_avatar(sender, instance, **kwargs):
#     try:
#         old_instance = sender.objects.get(pk=instance.pk)
#     except ObjectDoesNotExist:
#         return

#     # Check if a new avatar file is being set
#     if old_instance.avatar and old_instance.avatar != instance.avatar:
#         try:
#             # Delete the old avatar file only if it is not the default avatar
#             if not old_instance.avatar.name.endswith('default.jpg'):
#                 old_instance.avatar.delete(save=False)
#         except PermissionError:
#             # Handle PermissionError (file in use) here, log it or take appropriate action
#             pass

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
# @receiver(pre_save, sender=Profile)
# def save_new_avatar(sender, instance, **kwargs):
#     img = Image.open(instance.avatar.path)
#     if img.height > 300 or img.width > 300:
#         output_size = (300, 300)
#         img.thumbnail(output_size)
#         img.save(instance.avatar.path)

# # Connect the signal handlers
# pre_save.connect(delete_old_avatar, sender=Profile)
# pre_save.connect(save_new_avatar, sender=Profile)  
    
# @receiver(post_save, sender=Profile)
# def save_new_avatar(sender, instance, **kwargs):
#     if not hasattr(instance, '_saving_avatar') and instance.avatar and os.path.isfile(instance.avatar.path):
#         try:
#             # Add a flag to prevent recursion
#             instance._saving_avatar = True

#             img = Image.open(instance.avatar.path)
#             max_size = (300, 300)
#             img.thumbnail(max_size, Image.LANCZOS)

#             # Generate a unique filename using UUID
#             unique_filename = f"{uuid.uuid4().hex}.jpg"

#             # Create the directory if it doesn't exist
#             destination_folder = 'media/profile_pics/'
#             os.makedirs(destination_folder, exist_ok=True)

#             # Save the new avatar with the unique filename
#             destination_path = os.path.join(destination_folder, unique_filename)
#             img.save(destination_path)
#             img.close()

#             # Update the instance avatar field
#             instance.avatar.name = os.path.relpath(destination_path, 'media')
#             instance.save()

#         except (UnidentifiedImageError, OSError) as e:
#             print(f"Error processing avatar: {e}")

# @receiver(pre_save, sender=Profile)
# def replace_old_avatar(sender, instance, **kwargs):
#     # Check if a new avatar is being set and it's different from the old one
#     if instance.avatar and hasattr(instance, '_old_avatar'):
#         old_avatar = instance._old_avatar
#         new_avatar = instance.avatar
#         if old_avatar != new_avatar:
#             # Check if the old avatar file exists before attempting to remove it
#             old_avatar_path = default_storage.path(old_avatar.name)
#             if default_storage.exists(old_avatar.name):
#                 try:
#                     default_storage.delete(old_avatar.name)
#                 except Exception as e:
#                     print(f"Error deleting old avatar: {e}")
#             elif os.path.exists(old_avatar_path):
#                 try:
#                     os.remove(old_avatar_path)
#                 except Exception as e:
#                     print(f"Error deleting old avatar: {e}")


# # Connect the signal handlers
# pre_save.connect(replace_old_avatar, sender=Profile)
# post_save.connect(save_new_avatar, sender=Profile)



