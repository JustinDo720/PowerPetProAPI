from django.dispatch import receiver
from django.db.models.signals import pre_save
from power_pet_pro_app.models import Feedback
from users.models import Profile


# We are saying once we receive a post save from Feedback
@receiver(pre_save, sender=Feedback)
def create_feedback_profile(sender, instance, **kwargs):
    # Since we are setting the profile, we could now see the feedback that is directly related to profile
    instance.profile = instance.user.profile