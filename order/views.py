import stripe
from django.shortcuts import render
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from order.pagination import OrderPagination

from rest_framework import status, authentication, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework import status

from .models import Order, OrderItem, Profile
from .serializers import OrderItemSerializer, OrderSerializer, UserOrderSerializer


# Create your views here.


@api_view(['POST'])
def checkout(request):
    serializer = OrderSerializer(data=request.data)

    if serializer.is_valid():
        stripe.api_key = settings.STRIPE_SECRET_KEY
        paid_amount = sum(item.get('quantity') * item.get('price') for item in serializer.validated_data['items'])

        try:
            charge = stripe.Charge.create(
                amount=int(paid_amount * 100),
                currency='USD',
                description='Charge from Pet Power Pro',
                source=serializer.validated_data['stripe_token']
            )

            # NOTE: If the accessToken is not provided during POST request then the request.user is actually anonymous
            serializer.save(paid_amount=paid_amount)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserOrder(ListAPIView):
    """
        Given the user id we will fetch their order
            - This includes their items, order id and paid amount
    """
    serializer_class = UserOrderSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = OrderPagination

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        queryset = Order.objects.filter(user=user_id)  # we don't need to order_by because we already ordered in meta
        return queryset


class LatestUserOrder(APIView):
    """
        Given the user id we will fetch their latest orders
            - We will grab the 3 latest/recent orders
    """

    def get(self, request, user_id):
        order = Order.objects.filter(user=user_id)[:3]
        serializer = UserOrderSerializer(order, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class IndividualUserOrder(APIView):
    """
        Given User id and Order number
            - We will fetch details about their orders and display them fully
                - for instance all of their items
                - address being shipped to
                - total cost etc
    """
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, order_id):
        order = Order.objects.get(id=order_id)
        serializer = UserOrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)


class IndividualUserOrderItems(ListAPIView):
    """
        Given User id and Order number
            - We will fetch details about their orders and display them fully
                - for instance all of their items
                - address being shipped to
                - total cost etc
    """

    serializer_class = OrderItemSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = OrderPagination  # Although this is OrderPagination we will still be using 5 items so let's reuse

    def get_queryset(self):
        order_id = self.kwargs['order_id']

        order = Order.objects.get(id=order_id)
        order_items = OrderItem.objects.filter(order=order)
        return order_items  # this is our queryset


# since we are using vue let's make this an api view for our success page on the front to call in order to send the mail
@api_view(['POST'])
def send_success_email(request, order_id):
    data = request.data
    # All of the base context
    order_link = f'{settings.FRONTEND_BASE_URL}profile/order/{order_id}/'   # NOT WORKING
    feedback_link = f'{settings.FRONTEND_BASE_URL}submit_feedback/'
    context = {
         'order_number': order_id,
         'order_link': order_link,
         'feedback_link': feedback_link,
    }

    # The main idea is that if we have a user_id then the user is auth if not then they must be an anonymous user

    # So we actually can't use user_id to access the email bc it would give us the user's email but what if they change
    # the order email to another email then we'll be sending the email of the order to the wrong person
    if 'user_id' in data and 'order_email' in data:
        user_profile = Profile.objects.get(id=data['user_id'])
        user_email = data['order_email']
        context['user_profile'] = user_profile
    elif 'anonymous_user_email' in request.data:
        # The only other way to access the anonymous user is through email
        user_email = data['anonymous_user_email']
        context['user_email'] = user_email

    email_template = render_to_string('order/email.html', context)

    email = EmailMessage(
        f'PetPowerPro Order #{order_id} Summary',
        email_template,
        settings.EMAIL_HOST_USER,
        [user_email],
    )

    email.fail_silently = False
    email.content_subtype = "html"
    email.send()
    return Response({'message': "An email has been sent to:", 'email': user_email})


@api_view(['POST'])
def check_order_number(request, order_id):
    # We made sure to have request.data['email'] because we need another identifier aside from user_id for guest users
    email = request.data['email']
    if 'user_id' in request.data:
        if Order.objects.filter(id=order_id, user=request.data['user_id'], email=email).exists():
            return Response({'order_exists': True}, status.HTTP_200_OK)
    else:
        # guest users
        if Order.objects.filter(id=order_id, email=email).exists():
            return Response({'order_exists': True}, status.HTTP_200_OK)
    return Response({'order_exists': False}, status.HTTP_200_OK)


@api_view(['POST'])
def check_email(request):
    # For guest users we are going to check if the email exist in our db and if so we could recommend them to reset etc
    email = request.data['email']
    if Profile.objects.filter(email=email).exists():
        profile_username = Profile.objects.filter(email=email)[0].user.username
        return Response({'msg': f'The email does exist with a username: {profile_username}',
                         'exists': True}, status=status.HTTP_200_OK)

    # if it doesn't exist then let's return a message saying it doesn't exist
    return Response({'exists': False}, status=status.HTTP_200_OK)