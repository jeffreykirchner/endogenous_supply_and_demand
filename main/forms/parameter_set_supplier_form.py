from django import forms

from main.models import ParameterSetSupplier


class ParameterSetSupplierForm(forms.ModelForm):
    class Meta:
        model = ParameterSetSupplier
        fields = ["cost", "transfer_length", "x", "y"]
        widgets = {
            field: forms.NumberInput(attrs={
                "v-model": f"current_parameter_set_supplier.{field}",
                "min": "0",
                "step": "1",
            })
            for field in fields
        }
