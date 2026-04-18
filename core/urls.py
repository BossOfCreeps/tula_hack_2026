from django.urls import path

from core.views import TeamDetailView, TeamUserRemoveView, TeamUserAddView, TeamListView, TeamCreateView, TeamAICallView

urlpatterns = [
    path("team/", TeamListView.as_view(), name="team-list"),
    path("team/<int:pk>/", TeamDetailView.as_view(), name="team-detail"),
    path("team/create", TeamCreateView.as_view(), name="team-create"),
    path("team_user/<int:team_id>/<int:user_id>/add", TeamUserAddView.as_view(), name="team_user-add"),
    path("team_user/<int:team_id>/<int:user_id>/remove", TeamUserRemoveView.as_view(), name="team_user-remove"),
    path("team/<int:pk>/ai", TeamAICallView.as_view(), name="team-ai"),
]
