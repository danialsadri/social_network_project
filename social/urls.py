from django.urls import path
from . import views

app_name = 'social'
urlpatterns = [
    path('', views.profile, name='profile'),
    path('register/', views.user_register, name='register'),
    path('user/edit/', views.user_edit, name='user_edit'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('ticket/', views.ticket, name='ticket'),
    path('password_change/', views.CustomPasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', views.CustomPasswordChangeDoneView.as_view(), name='password_change_done'),
    path('reset_password/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('reset_password/done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset_password/confirm/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset_password/complete/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('post/list/', views.post_list, name='post_list'),
    path('post/list/<slug:tag_slug>/', views.post_list, name='post_list_by_tag'),
    path('post/detail/<int:post_id>/', views.post_detail, name='post_detail'),
    path('post/create/', views.post_create, name='post_create'),
    path('post/comment/<int:post_id>/', views.post_comment, name='post_comment'),
    path('search/', views.post_search, name='post_search'),
    path('like_post/', views.like_post, name='like_post'),
    path('save_post/', views.save_post, name='save_post'),
    path('user/list/', views.user_list, name='user_list'),
    path('user/detail/<str:username>/', views.user_detail, name='user_detail'),
    path('user/follow/', views.user_follow, name='user_follow'),
    path('user/<str:username>/<str:rel>/', views.contact, name='user_contact'),
]
