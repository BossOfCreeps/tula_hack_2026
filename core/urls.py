from django.urls import path

from core.views import TeamDetailView, TeamUserRemoveView, TeamUserAddView, TeamListView

urlpatterns = [
    path("team/", TeamListView.as_view(), name="team-list"),
    path("team/<int:pk>/", TeamDetailView.as_view(), name="team-detail"),
    path("team_user/<int:team_id>/<int:user_id>/add", TeamUserAddView.as_view(), name="team_user-add"),
    path("team_user/<int:team_id>/<int:user_id>/remove", TeamUserRemoveView.as_view(), name="team_user-remove"),
]
