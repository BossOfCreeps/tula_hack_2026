from collections import defaultdict

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import DetailView, View, ListView, CreateView, TemplateView

from core.models import Team, AIReviews
from users.models import User
from utils.disc import check_disk_compatibility
from utils.disk_advises import DISK_ADVISES
from utils.gpt import call_ai
from utils.lib import select_team
from utils.motype import select_motype_employees, get_motype_map
from utils.prompts import MAIN_PROMPT


class TeamListView(ListView):
    def get_queryset(self):
        return Team.objects.prefetch_related("users__role").filter(created_by=self.request.user)


class TeamDetailView(DetailView):
    def get_queryset(self):
        return Team.objects.prefetch_related("users__role", "roles").filter(created_by=self.request.user)

    def get_context_data(self, **kwargs):
        obj: Team = self.get_object()

        return super().get_context_data(**kwargs) | {
            "all_users": User.objects.all(),
            "disk_compatibility": check_disk_compatibility(
                [{"user": u, "D": u.disc_d, "I": u.disc_i, "S": u.disc_s, "C": u.disc_c} for u in obj.users.all()],
            ),
            "motype_employees": [
                {"user": me["name"], "reason": me["filter_reason"]}
                for me in select_motype_employees(
                    get_motype_map(obj),
                    [{"id": u.id, "name": u, "profile": get_motype_map(u)} for u in obj.users.all()],
                )
                if not me["passed_filters"]
            ],
            "team_roles": [u.role for u in obj.users.all()],
        }


class TeamCreateView(CreateView):
    model = Team
    fields = [
        "description",
        "disc_d",
        "disc_i",
        "disc_s",
        "disc_c",
        "roles",
        "motype_in",
        "motype_pr",
        "motype_pa",
        "motype_ho",
        "motype_lu",
    ]

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.created_by = self.request.user
        return super().form_valid(form)


class TeamUserAddView(View):
    model = Team

    def get(self, request, team_id, user_id):
        self.model.objects.get(id=team_id).users.add(User.objects.get(id=user_id))
        return HttpResponseRedirect(reverse("team-detail", kwargs={"pk": team_id}))


class TeamUserRemoveView(View):
    model = Team

    def get(self, request, team_id, user_id):
        self.model.objects.get(id=team_id).users.remove(User.objects.get(id=user_id))
        return HttpResponseRedirect(reverse("team-detail", kwargs={"pk": team_id}))


class TeamFillView(View):
    model = Team

    def post(self, request, pk):
        team: Team = self.model.objects.get(id=pk)

        users_dict = defaultdict(list)
        for u in User.objects.filter(role__in=team.roles.all()):
            users_dict[u.role].append(u)

        team_users = select_team(
            {
                "disk_allowed": [k.replace("disc_", "").upper() for k, v in team.dics_dict.items() if v > 5],
                "gerchikov_allowed": [m["name"].lower() for m in team.motypes if m["percent"] > 20],
            },
            {
                r: [{"name": u, "disk": u.disc_result[:1].upper(), "gerchikov": u.motype_result.lower()} for u in users]
                for r, users in users_dict.items()
            },
        )

        if not team_users:
            return render(request, "core/team_fill-error.html", {"team_id": team.id})

        team.users.clear()
        for _, d in team_users:
            team.users.add(d["name"])

        return HttpResponseRedirect(reverse("team-detail", kwargs={"pk": team.id}))


class TeamRunAIView(View):
    model = Team

    def post(self, request, pk):
        team = self.model.objects.get(id=pk)

        users = [
            {
                "name": user.get_full_name(),
                "role": user.role,
                "age": user.age,
                "disc_metrics": f"Доминирование: {user.disc_d}, Влияние: {user.disc_i}, "
                f"Стабильность: {user.disc_s}, Соответствие: {user.disc_c}",
                "motype": f"инструментальный: {user.motype_in}%, профессиональный: {user.motype_pr}%, патриотический: "
                f"{user.motype_pa}%, хозяйский: {user.motype_ho}%, люмпенизированный: {user.motype_lu}%",
            }
            for user in team.users.all()
        ]

        prompt = MAIN_PROMPT.format(
            description=team.description,
            disc=f"Доминирование: {team.disc_d}, Влияние: {team.disc_i}, "
            f"Стабильность: {team.disc_s}, Соответствие: {team.disc_c}",
            motype=f"инструментальный: {team.motype_in}%, профессиональный: {team.motype_pr}%,"
            f"патриотический: {team.motype_pa}%, хозяйский: {team.motype_ho}%, люмпенизированный: {team.motype_lu}%",
            roles="\n".join([r.name for r in team.roles.all()]),
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


class DiskDetailView(TemplateView):
    template_name = "core/disk_advise.html"

    def get_context_data(self, *args, **kwargs):
        return super().get_context_data(**kwargs) | {"disk_advise": DISK_ADVISES[kwargs["pk"]]}
