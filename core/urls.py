from django.urls import path

from core.views import (
    TeamDetailView,
    TeamUserRemoveView,
    TeamUserAddView,
    TeamListView,
    TeamCreateView,
    TeamRunAIView,
    TeamAIReviewView,
    TeamFillView,
)

urlpatterns = [
    path("team/", TeamListView.as_view(), name="team-list"),
    path("team/<int:pk>/", TeamDetailView.as_view(), name="team-detail"),
    path("team/create", TeamCreateView.as_view(), name="team-create"),
    path("team_user/<int:team_id>/<int:user_id>/add", TeamUserAddView.as_view(), name="team_user-add"),
    path("team_user/<int:team_id>/<int:user_id>/remove", TeamUserRemoveView.as_view(), name="team_user-remove"),
    path("team/<int:pk>/fill", TeamFillView.as_view(), name="team-fill"),
    path("team/<int:pk>/run_ai", TeamRunAIView.as_view(), name="team-run_ai"),
    path("team/<int:team_id>/ai_reviews/<int:pk>", TeamAIReviewView.as_view(), name="team-ai_reviews"),
]
