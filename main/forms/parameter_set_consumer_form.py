from django import forms

from main.models import ParameterSetConsumer


class ParameterSetConsumerForm(forms.ModelForm):
    class Meta:
        model = ParameterSetConsumer
        fields = ["value", "quantity", "transfer_length", "x", "y"]
        widgets = {
            field: forms.NumberInput(attrs={
                "v-model": f"current_parameter_set_consumer.{field}",
                "min": "1" if field == "quantity" else "0",
                "step": "1",
            })
            for field in fields
        }
