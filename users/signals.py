from django.dispatch import receiver
from django.db.models.signals import post_save
from users.models import Profile
from users.models import CustomUser


@receiver(post_save, sender=CustomUser)
def create_profile(sender, instance, created, **kwargs):
    if created:
        print('email'+instance.email)
        Profile.objects.create(id=instance.id,
                               email=instance.email,
                               user=instance,
                               first_name=instance.first_name,
                               last_name=instance.last_name)


@receiver(post_save, sender=CustomUser)
def save_profile(sender, instance, created, **kwargs):
    instance.profile.save()