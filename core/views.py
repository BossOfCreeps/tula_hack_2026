from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import DetailView, View, ListView, CreateView, TemplateView

from core.models import Team, AIReviews
from users.models import User
from utils.disk import check_disk_compatibility
from utils.gpt import call_ai
from utils.prompts import MAIN_PROMPT


class TeamListView(ListView):
    def get_queryset(self):
        return Team.objects.prefetch_related("users").filter(created_by=self.request.user)


class TeamDetailView(DetailView):
    def get_queryset(self):
        return Team.objects.prefetch_related("users").filter(created_by=self.request.user)

    def get_context_data(self, **kwargs):
        obj: Team = self.get_object()

        return super().get_context_data(**kwargs) | {
            "all_users": User.objects.all(),
            "disk_compatibility": check_disk_compatibility(
                {"D": obj.disc_d, "I": obj.disc_i, "S": obj.disc_s, "C": obj.disc_c},
                [{"user": u, "D": u.disc_d, "I": u.disc_i, "S": u.disc_s, "C": u.disc_c} for u in obj.users.all()],
            ),
        }


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
        return HttpResponseRedirect(reverse("team-detail", kwargs={"pk": team_id}))


class TeamUserRemoveView(View):
    def get(self, request, team_id, user_id):
        Team.objects.get(id=team_id).users.remove(User.objects.get(id=user_id))
        return HttpResponseRedirect(reverse("team-detail", kwargs={"pk": team_id}))


class TeamRunAIView(View):
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

        result = call_ai(prompt)

        team_members_analysis = []
        for tma in result["team_members_analysis"]:
            if tma["tension_points"]:
                prefix = f'"{tma["name"]} ({tma["role"]})"'
                for p in tma["tension_points"]:
                    team_members_analysis.append(f'{prefix} с "{p["with"]}".\nПроблема: {p["reason"]}')

        ai_review = AIReviews.objects.create(
            team=team,
            #
            strengths="\n\n".join(result["swot_analysis"]["strengths"]) or "-",
            weaknesses="\n\n".join(result["swot_analysis"]["weaknesses"]) or "-",
            opportunities="\n\n".join(result["swot_analysis"]["opportunities"]) or "-",
            threats="\n\n".join(result["swot_analysis"]["threats"]) or "-",
            #
            team_fit=result["conclusion"]["team_fit"],
            key_issues="\n\n".join(result["conclusion"]["key_issues"]) or "-",
            recommendations="\n\n".join(result["conclusion"]["recommendations"]) or "-",
            #
            team_members_analysis="\n\n".join(team_members_analysis) or "-",
        )

        return HttpResponseRedirect(reverse("team-ai_reviews", kwargs={"team_id": team.id, "pk": ai_review.id}))


class TeamAIReviewView(TemplateView):
    template_name = "core/aireview_list.html"

    def get_context_data(self, *, object_list=..., **kwargs):
        qs = AIReviews.objects.filter(team_id=self.kwargs["team_id"])
        if self.kwargs["pk"] > 0:
            object_ = qs.get(pk=self.kwargs["pk"])
        else:
            object_ = qs.first()

        return super().get_context_data(object_list=object_list, **kwargs) | {"reviews": qs, "object": object_}
