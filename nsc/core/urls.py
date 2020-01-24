from django.urls import path, include
from . import views


condition_patterns = ([
    path(r'', views.ConditionList.as_view(), name='list'),
    path(r'new/', views.ConditionCreate.as_view(), name='create'),
    path(r'<int:pk>/', views.ConditionDetail.as_view(), name='detail'),
    path(r'<int:pk>/update/', views.ConditionUpdate.as_view(), name='update'),
    path(r'<int:pk>/delete/', views.ConditionDelete.as_view(), name='delete'),
], 'condition')

urlpatterns = [
    path('condition/', include(condition_patterns)),
]

app_name = 'core'
