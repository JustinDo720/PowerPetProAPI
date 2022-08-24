# from django.dispatch import receiver
# from django.db.models.signals import pre_save
# from order.models import CartItem


"""
    This is not a good idea because you'll get an integrity error for having the same product id in cartitem
"""

# @receiver(pre_save, sender=CartItem)
# def set_cart_id(sender, instance, **kwargs):
#     ## What we want to do is set the id of cart = to the product id
#     instance.id = instance.product.id

