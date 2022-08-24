from django.contrib import admin
from .models import Category, Product, MessageBox, MissionStatement, MissionStatementTopics, MissionDetails, \
    Feedback, FeedBackAnswers, FeedBackQuestions, SubmitBug
from order.models import CartItem, Order, OrderItem
from users.models import Profile
from users.models import CustomUser

models = [
    CustomUser,
    Order,
    CartItem,
    OrderItem,
    Profile,
    Category,
    Product,
    MessageBox,
    MissionStatement,
    MissionStatementTopics,
    MissionDetails,
    Feedback,
    FeedBackAnswers,
    FeedBackQuestions,
    SubmitBug
]
# Register your models here.
for model in models:
    admin.site.register(model)
