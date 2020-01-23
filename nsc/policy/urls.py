from django.urls import path
from . import views


urlpatterns = [
    path(r'', views.PolicyList.as_view(), name='list'),
    path(r'new/', views.PolicyCreate.as_view(), name='create'),
    path(r'<int:pk>/', views.PolicyDetail.as_view(), name='detail'),
    path(r'<int:pk>/update/', views.PolicyUpdate.as_view(), name='update'),
    path(r'<int:pk>/delete/', views.PolicyDelete.as_view(), name='delete'),
]


app_name = 'policy'
