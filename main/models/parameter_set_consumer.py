from django.core.validators import MinValueValidator
from django.db import models

from main.models import ParameterSet


class ParameterSetConsumer(models.Model):
    parameter_set = models.ForeignKey(
        ParameterSet, on_delete=models.CASCADE, related_name="parameter_set_consumers"
    )
    value = models.IntegerField(verbose_name="Value (cents)", default=50, validators=[MinValueValidator(0)])
    quantity = models.IntegerField(verbose_name="Quantity", default=1, validators=[MinValueValidator(1)])
    transfer_length = models.IntegerField(
        verbose_name="Transfer length (seconds)", default=10, validators=[MinValueValidator(0)]
    )
    x = models.IntegerField(verbose_name="Location X", default=100, validators=[MinValueValidator(0)])
    y = models.IntegerField(verbose_name="Location Y", default=100, validators=[MinValueValidator(0)])
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Parameter Set Consumer"
        verbose_name_plural = "Parameter Set Consumers"
        ordering = ["id"]

    def __str__(self):
        return f"Consumer {self.pk}"

    def from_dict(self, values):
        for field in ("value", "quantity", "transfer_length", "x", "y"):
            setattr(self, field, values[field])
        self.save()

    def json(self):
        return {
            "id": self.id,
            "value": self.value,
            "quantity": self.quantity,
            "transfer_length": self.transfer_length,
            "x": self.x,
            "y": self.y,
        }

    def get_json_for_subject(self, update_required=False):
        return self.json()
