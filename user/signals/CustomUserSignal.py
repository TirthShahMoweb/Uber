from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from user.models import User
from django.utils import timezone
from PIL import Image
import os

@receiver(pre_save, sender=User)
def updated_at_pre_save(sender,instance, **kwargs):
    instance.updated_at = timezone.now()

@receiver(post_save, sender=User)
def create_thumbnail(sender, instance, **kwargs):
    if instance.profile_pic and not instance.thumbnail_pic:
        thumbnail_size = (100, 100)
        profile_pic_path = instance.profile_pic.path
        file_name = os.path.basename(profile_pic_path)
        thumbnail_pic_path = os.path.join('media/', 'thumbnail_pics/', file_name)
        os.makedirs(os.path.dirname(thumbnail_pic_path), exist_ok=True)

        with Image.open(profile_pic_path) as img:
            img.thumbnail(thumbnail_size)
            img.save(thumbnail_pic_path)

        if not instance.thumbnail_pic:
            instance.thumbnail_pic = os.path.basename(thumbnail_pic_path)
            instance.save()
