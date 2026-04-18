from django.http import HttpResponseRedirect
from django.views.generic import DetailView, View, ListView, CreateView

from core.models import Team
from users.models import User


class TeamListView(ListView):
    def get_queryset(self):
        return Team.objects.prefetch_related("users").filter(created_by=self.request.user)


class TeamDetailView(DetailView):
    def get_queryset(self):
        return Team.objects.prefetch_related("users").filter(created_by=self.request.user)

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs) | {"all_users": User.objects.all()}


class TeamCreateView(CreateView):
    model = Team
    fields = ["description", "disc_d", "disc_i", "disc_s", "disc_c"]

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.created_by = self.request.user
        return super().form_valid(form)


class TeamUserAddView(View):
    def get(self, request, team_id, user_id):
        Team.objects.get(id=team_id).users.add(User.objects.get(id=user_id))
        return HttpResponseRedirect(f"/team/{team_id}/")


class TeamUserRemoveView(View):
    def get(self, request, team_id, user_id):
        Team.objects.get(id=team_id).users.remove(User.objects.get(id=user_id))
        return HttpResponseRedirect(f"/team/{team_id}/")
