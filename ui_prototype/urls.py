from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('dashboard/', views.dashboard_view, name='dashboard_alt'),
    path('feedback/', views.feedback_inbox_view, name='feedback_inbox'),
    path('feedback/<str:item_id>/', views.feedback_detail_view, name='feedback_detail'),
    path('analytics/departments/', views.department_analytics_view, name='dept_analytics'),
    path('analytics/locations/', views.location_analytics_view, name='location_analytics'),
    path('alerts/', views.trend_alerts_view, name='trend_alerts'),
    path('integrations/', views.integrations_hub_view, name='integrations_hub'),
    path('settings/notifications/', views.staff_notifications_view, name='staff_notifications'),
    path('accounts/login/', views.login_view, name='login'),
]
