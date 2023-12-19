# from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django.db.models.signals import pre_save
from django.dispatch import receiver

# class CustomUser(AbstractUser):
#     email = models.EmailField(unique=True)
#     avatar = models.ImageField(default='default.jpg', upload_to='avatars')
#     dob = models.DateField(null=True)
#     gender = models.CharField(max_length=10, null=True)

#     user_permissions = models.ManyToManyField(
#         'auth.Permission',
#         related_name='customuser_permissions',
#         blank=True,
#     )
#     user_groups = models.ManyToManyField(
#         'auth.Group',
#         related_name='customuser_users',
#         blank=True,
#     )

#     def __str__(self):
#         return self.email

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='profile_pics/', default='profile_pics/default.jpg')
    dob = models.DateField(null=True)
    gender = models.CharField(max_length=10, null=True)
    address = models.CharField(max_length = 150, null=True)
    phone = models.CharField(max_length = 10, null=True)

    def __str__(self):
        return f'{self.user.username} Profile'

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

class SkinDisease(models.Model):
    disease_name = models.CharField(max_length=255)
    disease_overview = models.TextField()
    disease_symptom = models.TextField()
    disease_causes = models.TextField()
    disease_prevention = models.TextField()

    def __str__(self):
        return self.disease_name
