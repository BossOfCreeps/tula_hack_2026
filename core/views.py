from django.views.generic import DetailView

from core.models import Team
from users.models import User


class TeamDetailView(DetailView):
    queryset = Team.objects.prefetch_related("users").all()

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs) | {"all_users": User.objects.all()}
