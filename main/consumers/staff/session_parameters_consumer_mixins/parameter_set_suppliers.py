import logging

from channels.db import database_sync_to_async
from django.db import transaction

from main.forms import ParameterSetSupplierForm
from main.models import Session


logger = logging.getLogger(__name__)


@database_sync_to_async
def change_parameter_set_supplier(user, data, action):
    session_id = data.get("session_id")
    if not user.is_authenticated or not user.is_active or not isinstance(session_id, int):
        return {"value": "fail", "message": "Permission denied."}

    with transaction.atomic():
        session = Session.objects.filter(pk=session_id).select_for_update().first()
        if not session or not (
            user.is_superuser or session.creator_id == user.id or session.collaborators.filter(pk=user.id).exists()
        ):
            return {"value": "fail", "message": "Permission denied."}
        if session.started:
            return {"value": "fail", "message": "Suppliers cannot be edited after the session starts."}

        parameter_set = session.parameter_set
        if action == "add":
            parameter_set.parameter_set_suppliers.create()
        else:
            supplier_id = data.get("parameterset_supplier_id")
            supplier = (parameter_set.parameter_set_suppliers.filter(pk=supplier_id).first()
                        if isinstance(supplier_id, int) else None)
            if supplier is None:
                logger.warning("Supplier not found in session %s: %s", session_id, supplier_id)
                return {"value": "fail", "message": "Supplier not found in this session."}
            if action == "delete":
                supplier.delete()
            elif action == "duplicate":
                supplier.pk = None
                supplier.save()
            else:
                form_data = data.get("form_data")
                if not isinstance(form_data, dict):
                    return {"value": "fail", "message": "Supplier values are required."}
                form = ParameterSetSupplierForm(form_data, instance=supplier)
                if not form.is_valid():
                    return {"value": "fail", "errors": dict(form.errors.items())}
                form.save()

        parameter_set.json()
        parameter_set.update_json_fk(update_suppliers=True)
        return {"value": "success", "parameter_set": parameter_set.json()}


class ParameterSetSuppliersMixin:
    async def supplier_change_response(self, event, action):
        status = await change_parameter_set_supplier(self.scope["user"], event["message_text"], action)
        parameter_set = status.pop("parameter_set", None)
        message_data = {"status": status, "parameter_set": parameter_set, "source": "supplier"}
        await self.send_message(message_to_self=message_data, message_to_group=None,
                                message_type="update_parameter_set",
                                send_to_client=True, send_to_group=False)

    async def add_parameterset_supplier(self, event):
        await self.supplier_change_response(event, "add")

    async def update_parameter_set_supplier(self, event):
        await self.supplier_change_response(event, "update")

    async def remove_parameterset_supplier(self, event):
        await self.supplier_change_response(event, "delete")

    async def duplicate_parameterset_supplier(self, event):
        await self.supplier_change_response(event, "duplicate")
