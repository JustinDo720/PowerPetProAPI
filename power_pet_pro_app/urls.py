from django.urls import path, include
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # Everything dealing with products will have a product_list prefix (same goes for category with category_list)
    # path('', views.index, name='index'),
    path('product_list/', views.ProductList.as_view(), name='product_list'),
    path('category_list/', views.CategoryList.as_view(), name='category_list'),
    # path('product_detail/<int:product_id>/', views.ProductDetail.as_view(), name='product_detail') ## id format
    # OOOOO so slugs are basically string identifications. You don't need the <int:id> but <slug:string>
    path('product_list/product_detail/<slug:category_slug>/<slug:product_slug>/', views.ProductDetail.as_view(), name='product_detail'),
    path('category_list/category_detail/<slug:category_slug>/', views.CategoryDetail.as_view(), name='category_detail'),
    path('product_list/latest_products/', views.LatestProducts.as_view(), name='latest_products'),
    path('product_list/search/', views.search, name='search'),
    path('admin_panel/post_product/', views.PostProduct.as_view(), name='post_product'),
    path('admin_panel/product_list/update/<int:product_id>/', views.updateProduct, name='update_product'),
    path('api/token/', views.MyTokenObtainPairView.as_view(), name='token'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('activate/<str:uid>/<str:token>/', views.activate_acc, name='activate_acc'),
    path('password/reset/confirm/<str:uid>/<str:token>/', views.reset_password, name='reset_password'),
    path('admin_panel/message_box/', views.MessageBoxView.as_view(), name='message_box'),
    path('admin_panel/message_bar/', views.MessageBarView.as_view(), name='message_bar'),
    path('admin_panel/message_box/update/<int:message_id>/', views.updateMessageBoxView, name='update_msg_box_view'),
    path('admin_panel/message_box/post/', views.postMessageBoxView, name='post_msg_box_view'),
    path('admin_panel/post_category/', views.PostCategory.as_view(), name='post_category'),
    path('admin_panel/our_mission/', views.MissionStatementView.as_view(), name='mission_statement'),
    path('admin_panel/our_mission/add_mission_statement/', views.AddMissionStatement, name='add_mission_statement'),
    path('admin_panel/our_mission/all_topics/', views.MissionStatementTopicView.as_view(), name='mission_statement_topic'),
    path('admin_panel/our_mission/add_topic/', views.AddMissionStatementTopic, name='add_mission_statement_topic'),
    path('admin_panel/our_mission/update_topic/<slug:mission_topic>/', views.UpdateMissionStatementTopic, name='update_mission_statement_topic'),
    path('admin_panel/our_mission/view_topic/<slug:mission_topic>/', views.ViewMissionDetails, name='view_mission_details'),
    path('admin_panel/our_mission/update_details/<slug:mission_topic>/', views.UpdateMissionDetails,
         name='update_mission_details'),
    path('admin_panel/our_mission/add_details/', views.AddMissionDetails,
         name='add_mission_details'),
    path('admin_panel/feedbacks/', views.FeedbackView.as_view(), name='view_feedbacks'),
    path('feedbacks/add_feedback/', views.AddFeedback, name='add_feedback'),
    path('feedbacks/add_feedback_answers/', views.AddFeedbackAnswers, name='add_feedback_answers'),
    # We could use this url to and post questions and then we have another url to get questions. Admins could only sub
    path('admin_panel/feedbacks/add_questions/', views.AddFeedbackQuestions, name='add_feedback_questions'),
    path('admin_panel/feedbacks/remove_questions/<int:question_id>/', views.RemoveFeedbackQuestions, name='remove_feedback_questions'),
    path('feedbacks/questions/', views.ViewFeedbackQuestions, name='feedback_questions'),
    path('feedbacks/get_feedback/<int:feedback_id>/', views.GetFeedback, name='get_feedback'),
    # Submitting Bugs
    path('bugs/submit_bug/', views.AddBug, name='add_bug'),
    path('admin_panel/bugs/view_or_delete_bug/<int:bug_id>/', views.ViewOrDeleteBug, name='view_or_delete_bug'),
    path('admin_panel/bugs/view_all_bugs/', views.SubmitBugView.as_view(), name='view_all_bugs')
]
