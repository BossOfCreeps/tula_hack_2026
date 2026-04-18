from functools import cached_property

from django.db import models
from django.urls import reverse

from users.models import User


class Team(models.Model):
    users = models.ManyToManyField(User, related_name="team_as_member")
    created_by = models.ForeignKey(User, models.CASCADE, related_name="created_teams")
    created_at = models.DateTimeField(auto_now_add=True)

    description = models.TextField("Описание")

    disc_d = models.IntegerField("Доминирование")
    disc_i = models.IntegerField("Влияние")
    disc_s = models.IntegerField("Стабильность")
    disc_c = models.IntegerField("Соответствие")

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

    @cached_property
    def calc_polygon(self):
        """
        Перевод процентов: расстояние от центра = (значение/100) * радиус 90px (центр 130,130). Радиус до вершин ~110px
        Расчёт: (94%) -> 130, 130-110*0.94 = 130, 26.6
        """

        def _calc(k: str, znak):
            a = self.users_disc[k] / getattr(self, k)
            if a > 1:
                a = 1

            if znak == "-":
                return 130 - 110 * a
            return 130 + 110 * a

        return {
            "disc_d": f"130,{_calc('disc_d', '-')}",
            "disc_i": f"{_calc('disc_i', '+')},130",
            "disc_s": f"130,{_calc('disc_s', '+')}",
            "disc_c": f"{_calc('disc_c', '-')},130",
        }

    @cached_property
    def find_center(self):
        """

        Параметры:
        vertices: list of tuples [(x1,y1), (x2,y2), (x3,y3), (x4,y4)]
                  Вершины четырёхугольника в порядке обхода

        Возвращает:
        dict: словарь с разными типами центров
        """

        vertices = []
        for k, v in self.calc_polygon.items():
            x, y = v.split(",")
            vertices.append((float(x), float(y)))

        sum_x = sum(v[0] for v in vertices)
        sum_y = sum(v[1] for v in vertices)
        return {"x": int(sum_x / 4), "y": int(sum_y / 4)}

    def get_absolute_url(self):
        return reverse("team-detail", kwargs={"pk": self.id})


class AIReviews(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="reviews")

    strengths = models.TextField()
    weaknesses = models.TextField()
    opportunities = models.TextField()
    threats = models.TextField()

    team_fit = models.TextField()
    key_issues = models.TextField()
    recommendations = models.TextField()

    team_members_analysis = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Отзыв ИИ"
        verbose_name_plural = "Отзывы ИИ"
