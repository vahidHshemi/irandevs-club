# Django includes a “signal dispatcher” which helps decoupled applications get notified when actions
# occur elsewhere in the framework. In a nutshell, signals allow certain senders to notify a set of receivers
# that some action has taken place. They’re especially useful when many pieces of code may be interested in
# the same events.

# **** to triggered signals correctly it's necessary add signal.py file into users/apps.py ****

# Django provides a set of built-in signals that let user code get notified by Django itself of certain actions.
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from django.contrib.auth.models import User
from .models import Profile

from django.core.mail import send_mail
from django.conf import settings


# create a listener to make a profile automatically when a user registered into the database
# we can do this based on django signal
# @receiver(post_save, sender=Profile)


def createProfile(sender, instance, created, **kwargs):
    if created:
        user = instance
        profile = Profile.objects.create(
            user=user,
            username=user.username,
            email=user.email,
            name=user.first_name,
        )

        subject = 'Welcome to DevSearch'
        message = 'We are glad you are here!'

        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [profile.email],
            fail_silently=False,
        )


def updateUser(sender, instance, created, **kwargs):
    profile = instance
    user = profile.user  # there is a one to one relationship

    if created == False:
        user.first_name = profile.name
        user.username = profile.username
        user.email = profile.email
        user.save()


def deleteUser(sender, instance, **kwargs):
    try:
        user = instance.user
        user.delete()
    except:
        pass


post_save.connect(createProfile, sender=User)
post_save.connect(updateUser, sender=Profile)
post_delete.connect(deleteUser, sender=Profile)

# sample example
# 2. the second way to use signals methods based on receiver decorator
# @receiver(post_save, sender=Profile)
# def profile_update(sender, instance, created, **kwargs):
#     print('profile saved!')
#     print('instance: ', instance)
#     print('created: ', created)
#
#
# @receiver(post_delete, sender=Profile)
# def profile_delete(sender, instance, **kwargs):
#     print('Deleting User...')

# 1. the first way to use signals methods
# post_save.connect(profile_update, sender=Profile)
# post_delete.connect(profile_delete, sender=Profile)
