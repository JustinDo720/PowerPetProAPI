from .models import Order, OrderItem, CartItem
from rest_framework_simplejwt.serializers import serializers
from power_pet_pro_app.models import CustomUser


class OrderItemSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField('get_product_name')
    email = serializers.SerializerMethodField('get_email')
    # Make sure the name of the SerializerMethodField is not the same as the function for it
    get_absolute_url = serializers.SerializerMethodField('get_abs_url')
    photo = serializers.SerializerMethodField('get_photo')
    short_description = serializers.SerializerMethodField('get_description')

    def get_product_name(self, order_item):
        return order_item.product.name

    def get_email(self, order_item):
        return order_item.order.email 

    # This cannot be get_absolute_url which brings up a config error
    def get_abs_url(self, order_item):
        return order_item.product.get_absolute_url()

    def get_photo(self, order_item):
        return order_item.product.get_image()

    def get_description(self, order_item):
        return order_item.product.get_short_description()

    class Meta:
        model = OrderItem
        fields = (
            'profile',
            'email',
            'product',
            'order',
            'quantity',
            'price',
            'get_absolute_url',
            'photo',
            'name',
            'short_description',
        )


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    username = serializers.SerializerMethodField('get_username')

    def get_username(self, order):
        if order.user:
            return order.user.username
        else:
            return None

    class Meta:
        model = Order
        fields = (
            'id',
            'user',
            'first_name',
            'last_name',
            'phone',
            'address',
            'email',
            'zipcode',
            'city',
            'country',
            'state',
            'stripe_token',
            'created_at',
            'username',
            'items'

        )

    def create(self, validated_data):
        # So when we pop with a key, the key doesn't have to be at the end (it could be anywhere)
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)

        try:
            profile = validated_data['user']    # Here is where we used the data['user'] from our front-end checkout
        except Exception:
            profile = None

        # Now once we create our order we need to make order items aka cart items
        for item_data in items_data:
            OrderItem.objects.create(order=order, profile=profile, **item_data)

        # Once we created our order and orderItems we need to make sure to delete those CartItems to "reset" the cart
        CartItem.objects.filter(profile=profile).delete()   # This will delete all the CartItems relating to the profile

        return order


class CartItemSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField('get_product_name')
    # Make sure the name of the SerializerMethodField is not the same as the function for it
    get_absolute_url = serializers.SerializerMethodField('get_abs_url')
    photo = serializers.SerializerMethodField('get_photo')

    def get_product_name(self, cart):
        return cart.product.name

    # This cannot be get_absolute_url which brings up a config error
    def get_abs_url(self, cart):
        return cart.product.get_absolute_url()

    def get_photo(self, cart):
        print(cart.product.get_image())
        return cart.product.get_image()

    class Meta:
        model = CartItem
        fields = (
            'profile',
            'product',
            'quantity',
            'name',
            'price',
            'get_absolute_url',
            'photo',
        )


class UserOrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = (
            'id',
            'user',
            'email',
            'country',
            'phone',
            'paid_amount',
            'created_at',
            'first_name',
            'last_name',
            'address',
            'city',
            'state',
            'zipcode',
            'items',
        )