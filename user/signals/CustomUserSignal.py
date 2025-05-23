import os

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from PIL import Image

from user.models import User


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

        # Create directory for the thumbnail if it doesn't exist
        os.makedirs(os.path.dirname(thumbnail_pic_path), exist_ok=True)

        with Image.open(profile_pic_path) as img:
            img.thumbnail(thumbnail_size)
            img.save(thumbnail_pic_path)

        # Save the thumbnail path (remove "media/" prefix)
        instance.thumbnail_pic = thumbnail_pic_path.split("media/", 1)[1]
        instance.save()

    # Check if both profile_pic and thumbnail_pic exist and if they are the same
    elif instance.profile_pic and instance.thumbnail_pic:
        profile_pic_filename = os.path.basename(instance.profile_pic.path)
        thumbnail_pic_filename = os.path.basename(instance.thumbnail_pic.path)

        # If both files are different, create a new thumbnail
        if profile_pic_filename != thumbnail_pic_filename:
            thumbnail_size = (100, 100)
            profile_pic_path = instance.profile_pic.path
            file_name = os.path.basename(profile_pic_path)
            thumbnail_pic_path = os.path.join('media/', 'thumbnail_pics/', file_name)

            os.makedirs(os.path.dirname(thumbnail_pic_path), exist_ok=True)

            with Image.open(profile_pic_path) as img:
                img.thumbnail(thumbnail_size)
                img.save(thumbnail_pic_path)

            # Save the thumbnail path (remove "media/" prefix)
            instance.thumbnail_pic = thumbnail_pic_path.split("media/", 1)[1]
            instance.save()