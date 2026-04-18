from functools import cached_property

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    role = models.TextField(blank=True, null=True, help_text="User's role in the team")

    disc_d = models.IntegerField(
        "Доминирование", null=True, help_text="Score for Dominance dimension (0-100)", default=0
    )
    disc_i = models.IntegerField("Влияние", help_text="Score for Influence dimension (0-100)", default=0)
    disc_s = models.IntegerField("Стабильность", help_text="Score for Steadiness dimension (0-100)", default=0)
    disc_c = models.IntegerField("Соответствие", help_text="Score for Compliance dimension (0-100)", default=0)

    motype_in = models.IntegerField("Инструментальный", default=0)
    motype_pr = models.IntegerField("Профессиональный", default=0)
    motype_pa = models.IntegerField("Патриотический", default=0)
    motype_ho = models.IntegerField("Хозяйский", default=0)
    motype_lu = models.IntegerField("Люмпенизированный", default=0)

    age = models.TextField(blank=True, null=True, help_text="Age or generation (e.g., Gen Z, Millennial, etc.)")

    image = models.ImageField(null=True, blank=True)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.username} ({self.role if self.role else 'No Role'})"

    @cached_property
    def disc_profile(self):
        return {
            "dominance": self.disc_d or 0,
            "influence": self.disc_i or 0,
            "steadiness": self.disc_s or 0,
            "compliance": self.disc_c or 0,
        }

    @cached_property
    def motypes(self):
        return [
            {"name": "Инструментальный", "percent": self.motype_in, "color": "#2E7D32"},
            {"name": "Профессиональный", "percent": self.motype_pr, "color": "#1976D2"},
            {"name": "Патриотический", "percent": self.motype_pa, "color": "#C62828"},
            {"name": "Хозяйский", "percent": self.motype_ho, "color": "#F57C00"},
            {"name": "Люмпенизированный", "percent": self.motype_lu, "color": "#616161"},
        ]

    @cached_property
    def motypes_circle(self):
        return [
            {
                "start_percent": 0,
                "percent": self.motype_in,
                "color": "#2E7D32",
            },
            {
                "start_percent": self.motype_in,
                "percent": self.motype_pr + self.motype_in,
                "color": "#1976D2",
            },
            {
                "start_percent": self.motype_pr + self.motype_in,
                "percent": self.motype_pr + self.motype_in + self.motype_pa,
                "color": "#C62828",
            },
            {
                "start_percent": self.motype_pr + self.motype_in + self.motype_pa,
                "percent": self.motype_pr + self.motype_in + self.motype_pa + self.motype_ho,
                "color": "#F57C00",
            },
            {
                "start_percent": self.motype_pr + self.motype_in + self.motype_pa + self.motype_ho,
                "percent": 100,
                "color": "#616161",
            },
        ]

    @property
    def total_disc_score(self):
        return sum(self.disc_profile.values())
