from django.urls import path

from .views import IndexView, AboutView,DfView

urlpatterns = [
    path('', IndexView.as_view(), name="index"),
    path('aboutus/', AboutView.as_view(), name="about"),
    path('df/', DfView.as_view(), name="df"),
]
