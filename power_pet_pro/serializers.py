# For our Django server view [* NOTE: that all Serializers will start with R for serializer]
from users.models import CustomUser, Profile
from power_pet_pro_app.models import Category, Product, Feedback
from rest_framework import serializers, viewsets
from rest_framework.permissions import IsAdminUser, SAFE_METHODS
from power_pet_pro_app.serializers import ProductSerializer, CategorySerializer, FeedbackSerializer


# Admin or Read only
class IsAdminUserOrReadOnly(IsAdminUser):

    def has_permission(self, request, view):
        is_admin = super(
            IsAdminUserOrReadOnly,
            self).has_permission(request, view)
        # Python3: is_admin = super().has_permission(request, view)
        return request.method in SAFE_METHODS or is_admin


# Serializers for API representation
class RUserSerializer(serializers.HyperlinkedModelSerializer):
    is_staff = serializers.SerializerMethodField('get_is_staff')

    def get_is_staff(self, user):
        # you could also from pprint import pprint
        # if you're in django shell_plus you could get a specific user then pprint(user.__dict__)
        return user.is_superuser

    class Meta:
        model = CustomUser
        fields = [
            'username',
            'is_staff'
        ]


# ViewSets for view behavior
class RUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = RUserSerializer
    permission_classes = [IsAdminUserOrReadOnly]


# Let's recycle Some Serializers from power_pet_pro_app and use them in our viewset
class RCategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUserOrReadOnly]


class RProductViewSet(viewsets.ModelViewSet):
    """
    Used To Grab all of our Products
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminUserOrReadOnly]


class RFeedbackViewSet(viewsets.ModelViewSet):
    """
    Used To Grab all of our Feedbacks from users
    """
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [IsAdminUserOrReadOnly]