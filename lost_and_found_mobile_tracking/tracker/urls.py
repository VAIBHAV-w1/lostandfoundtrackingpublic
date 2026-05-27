from django.urls import path
from . import views

app_name = 'tracker'

urlpatterns = [
    path('', views.home, name='home'),
    path('report/', views.report_item, name='report_item'), 
    path('report/<int:report_id>/', views.report_detail, name='report_detail'),
    path('search/', views.search_reports, name='search'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('profile/', views.user_profile, name='profile'),
    path('message/<int:report_id>/', views.send_message, name='send_message'),
    path('chat/<int:report_id>/<int:other_user_id>/', views.view_chat, name='chat_thread'),
    path('resolve/<int:report_id>/', views.resolve_item, name='resolve_item'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
]
