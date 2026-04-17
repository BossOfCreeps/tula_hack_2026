from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    role = models.TextField(blank=True, null=True, help_text="User's role in the team")

    disc_d = models.IntegerField("Доминирование", null=True, help_text="Score for Dominance dimension (0-100)")
    disc_i = models.IntegerField("Влияние", help_text="Score for Influence dimension (0-100)", default=0)
    disc_s = models.IntegerField("Стабильность", help_text="Score for Steadiness dimension (0-100)", default=0)
    disc_c = models.IntegerField("Соответствие", help_text="Score for Compliance dimension (0-100)", default=0)

    motivational_profile = models.TextField(blank=True, null=True, help_text="User's motivational profile description")

    age = models.TextField(blank=True, null=True, help_text="Age or generation (e.g., Gen Z, Millennial, etc.)")

    image = models.ImageField(null=True, blank=True)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.username} ({self.role if self.role else 'No Role'})"

    @property
    def disc_profile(self):
        return {
            "dominance": self.disc_d or 0,
            "influence": self.disc_i or 0,
            "steadiness": self.disc_s or 0,
            "compliance": self.disc_c or 0,
        }

    @property
    def total_disc_score(self):
        return sum(self.disc_profile.values())
