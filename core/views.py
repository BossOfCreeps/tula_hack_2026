from django.http import HttpResponseRedirect
from django.views.generic import DetailView, View, ListView, CreateView

from core.models import Team
from users.models import User
from utils.gpt import call_ai
from utils.prompts import MAIN_PROMPT


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


class TeamAICallView(View):
    def post(self, request, pk):
        team = Team.objects.get(id=pk)

        users = [
            {
                "name": user.get_full_name(),
                "role": user.role,
                "age": user.age,
                "disc_metrics": f"Доминирование: {user.disc_d}, Влияние: {user.disc_i}, "
                f"Стабильность: {user.disc_s}, Соответствие: {user.disc_c}",
                "motivational_profile": user.motivational_profile,
            }
            for user in team.users.all()
        ]

        prompt = MAIN_PROMPT.format(
            description=team.description,
            disc=f"Доминирование: {team.disc_d}, Влияние: {team.disc_i}, "
            f"Стабильность: {team.disc_s}, Соответствие: {team.disc_c}",
            users=str(users),
        )

        print(call_ai(prompt))
