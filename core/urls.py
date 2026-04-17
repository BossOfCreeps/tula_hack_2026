from django.urls import path

from core.views import TeamDetailView

urlpatterns = [
    path("team/<int:pk>/", TeamDetailView.as_view(), name="index"),
]
