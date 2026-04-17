from django.http import HttpResponseRedirect
from django.views.generic import DetailView, View

from core.models import Team
from users.models import User


class TeamDetailView(DetailView):
    queryset = Team.objects.prefetch_related("users").all()

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs) | {"all_users": User.objects.all()}


class TeamUserAddView(View):
    def get(self, request, team_id, user_id):
        Team.objects.get(id=team_id).users.add(User.objects.get(id=user_id))
        return HttpResponseRedirect(f"/team/{team_id}/")


class TeamUserRemoveView(View):
    def get(self, request, team_id, user_id):
        Team.objects.get(id=team_id).users.remove(User.objects.get(id=user_id))
        return HttpResponseRedirect(f"/team/{team_id}/")
