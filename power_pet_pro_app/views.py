from django.shortcuts import render, redirect
from rest_framework.generics import ListCreateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser, MultiPartParser, JSONParser
from .serializers import ProductSerializer, CategorySerializer, CustomUserSerializer, \
    MessageBoxSerializer, MissionStatementSerializer, MissionStatementTopicsSerializer, MissionDetailsSerializer, \
    FeedbackSerializer, FeedbackQuestionsSerializer, FeedbackAnswersSerializer, SubmitBugSerializer
from .models import Product, Category, MessageBox, MissionStatement, MissionStatementTopics, MissionDetails, Feedback, \
    FeedBackAnswers, FeedBackQuestions, SubmitBug
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from power_pet_pro_app.pagination import ProductResultsSetPagination, MessageBarViewPagination, \
    FeedbackResultsSetPagination, SubmitBugPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, IsAdminUser
from rest_framework.decorators import api_view, permission_classes, parser_classes
from django.db.models import Q
from rest_framework_simplejwt.views import TokenObtainPairView
from power_pet_pro_app.serializers import MyTokenObtainPairSerializer
from django.conf import settings
from users.models import Profile

# Error Handling
from django.http import Http404, HttpResponse
from django.db import IntegrityError
from rest_framework import status


# Create your views here.


# Default authentication is isAuthenticated
def activate_acc(request, uid, token):
    if uid and token:
        frontend_url = f'{settings.FRONTEND_BASE_URL}activate/{uid}/{token}'
        return redirect(frontend_url)


def reset_password(request, uid, token):
    if uid and token:
        frontend_url = f'{settings.FRONTEND_BASE_URL}password/reset/confirm/{uid}/{token}'
        return redirect(frontend_url)


class ProductList(ListAPIView):
    """
    List all of the products in our database
    """
    queryset = Product.objects.all()
    permission_classes = (IsAdminUser,)
    serializer_class = ProductSerializer
    pagination_class = ProductResultsSetPagination


class CategoryList(APIView):
    """
    List all of the categories in our database
    """

    def get(self, request):
        categories = Category.objects.all()  # Note that these categories are already ordered by name
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# class ProductDetail(APIView):     ## id format
#     """
#     List details about ONE specific product given the product id
#     """
#
#     def get(self, request, product_id):
#         product = Product.objects.get(id=product_id)
#         serializer = ProductSerializer(product, many=False)
#         return Response(serializer.data)

# Slug
class ProductDetail(APIView):
    """
    Provides details about a single product given the category_slug and product_slug
    """

    def get_object(self, category_slug, product_slug):
        # lets check if the obj exist
        try:
            return Product.objects.filter(category__slug=category_slug).get(slug=product_slug)
        except Product.DoesNotExist:
            raise Http404

    # time to override the get function: make sure to pass in the slugs
    def get(self, request, category_slug, product_slug, format=None):
        # we need to get the product so
        product = self.get_object(category_slug, product_slug)  # so we are using that get_obj function passing in args
        serializer = ProductSerializer(product, many=False)
        return Response(serializer.data)


class CategoryDetail(APIView):
    """
    Provides details about a single category given the category_slug
        1) We need to retrieve the category
        2) Use that category to access all the products that are under those categories
        3) Return them as an array of items
    """

    def get_object(self, category_slug):
        try:
            # return Category.objects.filter(slug=category_slug) <-- using filter gives queryset <- queryset no attr
            return Category.objects.get(slug=category_slug)
        except Category.DoesNotExist:
            raise Http404

    def get(self, request, category_slug, format=None):
        category = self.get_object(category_slug)
        product_category = Product.objects.filter(category=category.id).all()
        serializer = ProductSerializer(product_category, many=True)
        return Response(serializer.data)


class LatestProducts(APIView):
    """
    List the first 10 items that are in our Products model
    """

    def get(self, request):
        latest_products = Product.objects.all()[:8]  # 8 items [start:stop] stop excludes similar to range
        serializer = ProductSerializer(latest_products, many=True)
        return Response(serializer.data)


@api_view(['POST'])  # when making an api view you have to specify which methods you want so
def search(request):
    # query is a data sent in our axios.post in Search.vue
    query = request.data.get('query', '')

    if query:
        # We could make some big queries like containing certain words from our query
        products = Product.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    else:
        return Response({'products': []})


# Admin use only
class PostProduct(APIView):
    permission_classes = (IsAdminUser,)
    parser_classes = (MultiPartParser,)

    def post(self, request, *args, **kwargs):
        # Here we don't need file=request.FILES
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE', 'PUT'])
@permission_classes([IsAdminUser])
@parser_classes([MultiPartParser])
def updateProduct(request, product_id):
    # We are going to to use this view to take care up updating and deleting our products
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        raise Http404

    if request.method == 'PUT':
        main_serializer = ProductSerializer(product, many=False, data=request.data)
        if main_serializer.is_valid():
            main_serializer.save()
            return Response(main_serializer.data)
        return Response(main_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        product.delete()
        return Response({"success": "You have deleted an item from product list. Please refresh your page."},
                        status=status.HTTP_200_OK)


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class MessageBoxView(ListAPIView):
    """
        MessageBox will take care of retrieving all the messages in the box
            -- We will get all the messages then we are going to put them into a list
            -- We will NOT allow post requests here as post requests requires admin user ONLY
    """

    queryset = MessageBox.objects.all()
    serializer_class = MessageBoxSerializer
    pagination_class = PageNumberPagination


class MessageBarView(ListAPIView):
    """
        MessageBox will take care of retrieving all the messages in the box
            -- We will be using different pagination for our message bar
            -- We want one message at a time for them to scroll over
    """

    queryset = MessageBox.objects.all()
    serializer_class = MessageBoxSerializer
    pagination_class = MessageBarViewPagination


@api_view(['POST'])
@permission_classes([IsAdminUser])
def postMessageBoxView(request):
    # We are going to let admin users post their messages
    post_serializer = MessageBoxSerializer(data=request.data)
    if post_serializer.is_valid():
        post_serializer.save()
        return Response(post_serializer.data, status=status.HTTP_201_CREATED)
    return Response(post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE', 'PUT'])
@permission_classes([IsAdminUser])
def updateMessageBoxView(request, message_id):
    # We are going to to use this view to take care up updating and deleting our messages
    try:
        message = MessageBox.objects.get(id=message_id)
    except MessageBox.DoesNotExist:
        raise Http404

    if request.method == 'PUT':
        main_serializer = MessageBoxSerializer(message, many=False, data=request.data)
        if main_serializer.is_valid():
            main_serializer.save()
            return Response(main_serializer.data)
        return Response(main_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        message.delete()
        return Response({"success": "You have deleted an item from your messages. Please refresh your page."}, status=status.HTTP_200_OK)


# Admin use only
class PostCategory(APIView):
    permission_classes = (IsAdminUser,)

    def post(self, request, *args, **kwargs):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MissionStatementView(APIView):
    """
        Get Mission Statement from Database
    """

    def get(self, request):
        try:
            # This is going to give us a queryset so we need the first value in the queryset which is why we use 0
            mission_statement = MissionStatement.objects.all()[0]
        except MissionStatement.DoesNotExist:
            raise Http404
        except IndexError as e:
            return Response({"message": "There is currently no Mission Statement"})

        serializer = MissionStatementSerializer(mission_statement, many=False)
        return Response(serializer.data)


@api_view(['POST', 'PUT', 'DELETE'])
@permission_classes([IsAdminUser])
def AddMissionStatement(request):
    # Here we are going to handle some tasks like posting changing and deleting
    try:
        # This is going to give us a queryset so we need the first value in the queryset which is why we use 0
        mission_statement = MissionStatement.objects.all()[0]
    except MissionStatement.DoesNotExist:
        if request.method == 'POST':
            pass
        else:
            return Http404
    except IndexError as e:
        mission_statement = MissionStatement.objects.all()

    if request.method == 'POST':
        # We are trying to limit the amount of Mission Statements to only one in the database
        if MissionStatement.objects.count() == 0:
            posting_serializer = MissionStatementSerializer(data=request.data)
            if posting_serializer.is_valid():
                posting_serializer.save()
                return Response(posting_serializer.data, status=status.HTTP_201_CREATED)
            return Response(posting_serializer.errors)
        else:   # That means that we already have one count in our database so
            return Response({'message': "Please modify your current Mission Statement using PUT method."})
    elif request.method == 'PUT':
        putting_serializer = MissionStatementSerializer(mission_statement, data=request.data)
        if putting_serializer.is_valid():
            putting_serializer.save()
            return Response(putting_serializer.data, status=status.HTTP_200_OK)
        return Response(putting_serializer.errors)
    elif request.method == 'DELETE':
        mission_statement.delete()
        return Response({"message": "You have deleted an item from your messages. Please refresh your page."})


class MissionStatementTopicView(APIView):
    """
        Get Mission Statement from Database
    """

    def get(self, request):
        try:
            # We are going to grab all the Mission Statement Topics
            mission_statement_topic = MissionStatementTopics.objects.all()
        except MissionStatementTopics.DoesNotExist:
            raise Http404
        serializer = MissionStatementTopicsSerializer(mission_statement_topic, many=True)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def AddMissionStatementTopic(request):
    # We are going to post Mission Statements Only
    serializer = MissionStatementTopicsSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'DELETE'])
@permission_classes([IsAdminUser])
def UpdateMissionStatementTopic(request, mission_topic):
    # We are going to post Mission Statements Only
    try:
        mission_statement_topic = MissionStatementTopics.objects.get(slug=mission_topic)
    except MissionStatementTopics.DoesNotExist:
        raise Http404

    if request.method == 'PUT':
        serializer = MissionStatementTopicsSerializer(mission_statement_topic, data=request.data, many=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        mission_statement_topic.delete()
        return Response({'message': f'{mission_statement_topic.topic} topic has been removed.'})


@api_view(['GET'])
def ViewMissionDetails(request, mission_topic):
    try:
        # We need to get the topic for using the slug
        mission_statement_topic = MissionStatementTopics.objects.get(slug=mission_topic)
        # Once we get the topic we need the topic id. Make sure to filter because this query is possibly more than one
        mission_statement_details = MissionDetails.objects.filter(mission_topic=mission_statement_topic.id)
    except MissionStatementTopics.DoesNotExist:
        raise Http404

    if mission_statement_details.count() >= 1:
        serializer = MissionDetailsSerializer(mission_statement_details, many=True)
        return Response(serializer.data, status.HTTP_200_OK)
    else:   # This means we have no queries in our set which also means we wont be getting any data so lets return one
        return Response({
            'message': 'There are currently no queries in your topic',
            'topic': mission_statement_topic.topic
        })


@api_view(['POST'])
@permission_classes([IsAdminUser])
def AddMissionDetails(request):
    serializer = MissionDetailsSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status.HTTP_200_OK)
    return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'DELETE'])
@permission_classes([IsAdminUser])
def UpdateMissionDetails(request, mission_topic):
    # We are going to post Mission Statements Only
    try:
        # We need to get the topic for using the slug
        mission_statement_topic = MissionStatementTopics.objects.get(slug=mission_topic)
        # Once we get the topic we need the topic id. Make sure to filter because this query is possibly more than one
        mission_statement_details = MissionDetails.objects.filter(mission_topic=mission_statement_topic.id)
    except MissionStatementTopics.DoesNotExist:
        raise Http404

    serializer = MissionDetailsSerializer(mission_statement_details, many=True)

    # We need to allow our admin to do PUT and DELETE request on mission_statement_details
    if request.method == 'PUT':
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_200_OK)
    elif request.method == 'DELETE':
        mission_statement_details.delete()
        return Response({'message': 'Your mission details has been removed.'}, status.HTTP_200_OK)


# @api_view(['POST'])
# @permission_classes([permission_classes.IsAuthenticated])
# def anonymous_checkout(request):
#     serializer = CartItemSerializer()

class FeedbackView(ListAPIView):
    """
        Admin will be able to see the feedbacks
    """
    queryset = Feedback.objects.all()
    permission_classes = (IsAdminUser,)
    serializer_class = FeedbackSerializer
    pagination_class = FeedbackResultsSetPagination


@api_view(['POST'])
def AddFeedback(request):
    serializer = FeedbackSerializer(data=request.data)
    # Since user is optional, we could add user as part of the request.data
    if serializer.is_valid():
        """
            One thing to note, we are not adding the answers here. We need to make the feedback first and then take the
            survey that way we would actually link all of those answers to this firstly created feedback. This then in 
            turn, allows us to use that feedbackanswers_set.all() to retrieve all of the answers in FeedbackSerializer
        """
        serializer.save()
        return Response(serializer.data, status.HTTP_201_CREATED)
    return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def AddFeedbackAnswers(request):
    # We are going to use this to post our answers
    if request.method == 'POST':
        # We need to check if the question already exists in the feedback that way we wont allow for another submission
        print(request.data)
        # We need to loop through all the submitted data to check if the first exists or if the questions match
        PREVIOUS_QUESTION = 0
        for data in request.data:
            if FeedBackAnswers.objects.filter(feedback=data['feedback'], question=data['question']).exists() \
                    or data['question'] == PREVIOUS_QUESTION:
                return Response(
                    {"question": "Submission for this question already exists"},
                    status.HTTP_400_BAD_REQUEST)
            PREVIOUS_QUESTION = data['question']

        serializer = FeedbackAnswersSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def AddFeedbackQuestions(request):
    if request.method == 'POST':
        serializer = FeedbackQuestionsSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def ViewFeedbackQuestions(request):
    all_questions = FeedBackQuestions.objects.all()
    serializer = FeedbackQuestionsSerializer(all_questions, many=True)
    return Response(serializer.data, status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def RemoveFeedbackQuestions(request, question_id):
    if request.method == 'DELETE':
        question = FeedBackQuestions.objects.get(id=question_id)
        question.delete()
        return Response({"success": f'"{question.questions}" has been removed. Please refresh your page.'},
                        status=status.HTTP_200_OK)


@api_view(['GET'])
def GetFeedback(request, feedback_id):
    feedback = Feedback.objects.get(id=feedback_id)
    serializer = FeedbackSerializer(feedback, many=False)
    return Response(serializer.data, status.HTTP_200_OK)


class SubmitBugView(ListAPIView):
    """
        Admin will be able to see the bugs submitted by users
    """
    queryset = SubmitBug.objects.all()
    permission_classes = (IsAdminUser,)
    serializer_class = SubmitBugSerializer
    pagination_class = SubmitBugPagination  # Admins will see 3 bugs at a time


@api_view(['POST'])
def AddBug(request):
    serializer = SubmitBugSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status.HTTP_200_OK)
    return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'DELETE'])
@permission_classes([IsAdminUser])
def ViewOrDeleteBug(request, bug_id):
    bug = SubmitBug.objects.get(id=bug_id)
    serializer = SubmitBugSerializer(bug, many=False)
    if request.method == 'DELETE':
        bug.delete()    # we cannot do serializer.delete() bc we need to delete the bug itself from our db
        return Response({"success": f'"Bug ID:{bug_id}" has been removed or resolved. Please refresh your page.'},
                        status=status.HTTP_200_OK)
    elif request.method == 'GET':
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



