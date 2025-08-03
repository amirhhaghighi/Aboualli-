from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import FiatWallet


@receiver(post_save, sender=User)
def create_fiat_wallet(sender, instance, created, **kwargs):
    """ایجاد کیف پول فیات برای کاربران جدید"""
    if created:
        FiatWallet.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_fiat_wallet(sender, instance, **kwargs):
    """ذخیره کیف پول فیات"""
    if hasattr(instance, 'fiat_wallet'):
        instance.fiat_wallet.save() 