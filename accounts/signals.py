from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def assign_default_group(sender, instance, created, **kwargs):
    if created:
        employee_group, _ = Group.objects.get_or_create(name='Employee')
        instance.groups.add(employee_group)