from django.urls import path
from . import views 
from django.contrib.auth import views as auth_views
from .serviceview import serviceurlpattern



# all the urls of the site are present here 
# every path in the urlpatters list takes three parameters(
# 1. url endpoint, 
# 2.function of the views.py, 
# 3. Assigns a name for every url for the html use 
# )
urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.HandymanLogin, name='handyman-login'),
    path('logout/', views.HandymanLogout, name='handyman-logout'),
    path('registration/', views.HandymanRegister, name="handyman-registration"),
    path('profile-edit/<str:pk>/', views.ProfileEditViewHandyman.as_view(), name='handyman-profile'),
    path('profile-edit-employer/<str:pk>/', views.ProfileEditViewCustomer.as_view(), name='customer-profile'),
    path('search/', views.HandymaSearch, name='handyman-search'),
    path('user-details/<int:id>/', views.SearchDetailView, name='user-details'),
    path('book-service/<int:id>/', views.BookService, name='handyman-booking'),
    path('search-by-tags/', views.SearchTags, name='search-tags'),
    path('accept-service/<int:id>', views.HandymanAccept, name='handyman-accept'),
    path('decline-service/<int:id>/', views.HandymanDecline, name='handyman-decline'),
    path('service-done/<int:id>/', views.HandymanComplete, name='handyman-complete'),

    path('service_approved/', views.HandymanServiceApproved, name="service-approved"),
    path('password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('Previous_booking/', views.previous_booking_list, name='previous-booking'),
    path('handyman-rating-view/<int:id>/<int:booking_id>/', views.handyman_rating_view, name='handyman-rating'),
    
    path(
      'booking-customer-details/<int:id>/',
      views.HandymanServiceApprovedDetails, 
      name='service-approved-details'
      ),

    # Below view are not from userhandle/view.py but are inbuilt django.contrib.auth.views
    path(
    'password_reset/',
     auth_views.PasswordResetView.as_view(template_name="password_reset.html"),
     name='password_reset'
     ),

    path(
      'pasword_reset/done',
      auth_views.PasswordResetDoneView.as_view(template_name="password_reset_done.html"),
      name="password_reset_done"
      ),

    path(
      "password_reset/<uidb64>/<token>/",
      auth_views.PasswordResetConfirmView.as_view(template_name="password_reset_confirm.html"),
      name="password_reset_confirm"
      ),

    path(
    "password_reset_complete/",
     auth_views.PasswordResetCompleteView.as_view(template_name="password_reset_complete.html"),
     name="password_reset_complete"
     )

    

]

urlpatterns = urlpatterns + serviceurlpattern