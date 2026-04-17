from functools import cached_property

from django.db import models

from users.models import User


class Team(models.Model):
    users = models.ManyToManyField(User, related_name="team_as_member")
    created_by = models.ForeignKey(User, models.CASCADE, related_name="created_teams")
    created_at = models.DateTimeField(auto_now_add=True)

    disc_d = models.IntegerField("Доминирование")
    disc_i = models.IntegerField("Влияние")
    disc_s = models.IntegerField("Стабильность")
    disc_c = models.IntegerField("Соответствие")

    description = models.TextField(null=False)

    class Meta:
        verbose_name = "Команда"
        verbose_name_plural = "Команды"

    @cached_property
    def users_disc(self) -> dict[str, int]:
        result = {"disc_d": 0, "disc_i": 0, "disc_s": 0, "disc_c": 0}
        for user in self.users.all():
            for key in ["disc_d", "disc_i", "disc_s", "disc_c"]:
                result[key] += getattr(user, key)

        return result

    @cached_property
    def dics_match(self):
        desired = {"disc_d": self.disc_d, "disc_i": self.disc_i, "disc_s": self.disc_s, "disc_c": self.disc_c}

        data = [(self.users_disc[key] / value) if self.users_disc[key] < value else 1 for key, value in desired.items()]

        return round(sum(data) / 4 * 100, 2)
