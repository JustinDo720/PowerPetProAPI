from django.core.management.base import BaseCommand
from order.models import CartItem


class Command(BaseCommand):
    help = "Delete all Cart Items to avoid Integrity Error"

    def handle(self, *args, **kwargs):
        all_cart_items = CartItem.objects.all()
        all_cart_items.delete()