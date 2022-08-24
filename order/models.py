from django.db import models
from users.models import Profile, CustomUser
from power_pet_pro_app.models import Product

# Create your models here.


class Order(models.Model):
    user = models.ForeignKey(CustomUser, related_name='orders', on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.CharField(max_length=100, null=False, blank=False)   # This can't be unique otherwise order alr exist
    address = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=80)
    phone = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    stripe_token = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=80)
    state = models.CharField(max_length=80)

    class Meta:
        ordering = ['-created_at', ]

    def __str__(self):
        if self.user:
            return f'{self.user.username}: OrderNum {self.id}'
        else:
            return f'{self.email}: OrderNum {self.id}'


# OrderItem will take care of adding items to our order model
class OrderItem(models.Model):
    # Order and Profile could be null for anonymous users
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, null=True, blank=True)
    profile = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.IntegerField(default=1)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        # This is going to order our products from the most recent date that the product was added
        ordering = ('-date_added',)

    def __str__(self):
        if self.profile:
            msg = f'Order Item: {self.product.name} - {self.profile.username} - OrderNum {self.order.id}'
        else:
            msg = f'Order Item: {self.product.name} - {self.order.email} - OrderNum {self.order.id}'
        return msg


# CartItem will take care of adding items to our cart and saving user cart data
class CartItem(models.Model):
    profile = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.IntegerField(default=1)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        # This is going to order our products from the most recent date that the product was added
        ordering = ('-date_added',)

    def __str__(self):
        return f'Cart Item: {self.product.name} - {self.profile.username}'