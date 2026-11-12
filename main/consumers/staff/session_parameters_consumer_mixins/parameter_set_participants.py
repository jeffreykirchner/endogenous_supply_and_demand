import logging

from django.db import transaction

from main.models import Session


logger = logging.getLogger(__name__)


def change_parameter_set_participant(user, data, action, *, name, form_class):
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
            return {"value": "fail", "message": f"{name.capitalize()}s cannot be edited after the session starts."}

        parameter_set = session.parameter_set
        participants = getattr(parameter_set, f"parameter_set_{name}s")
        if action == "add":
            participants.create()
        else:
            participant_id = data.get(f"parameterset_{name}_id")
            participant = (participants.filter(pk=participant_id).first()
                           if isinstance(participant_id, int) else None)
            if participant is None:
                logger.warning("%s not found in session %s: %s", name.capitalize(), session_id, participant_id)
                return {"value": "fail", "message": f"{name.capitalize()} not found in this session."}
            if action == "delete":
                participant.delete()
            elif action == "duplicate":
                participant.pk = None
                participant.save()
            elif action == "update":
                form_data = data.get("form_data")
                if not isinstance(form_data, dict):
                    return {"value": "fail", "message": f"{name.capitalize()} values are required."}
                form = form_class(form_data, instance=participant)
                if not form.is_valid():
                    return {"value": "fail", "errors": dict(form.errors.items())}
                form.save()
            else:
                return {"value": "fail", "message": f"Unknown {name} action."}

        parameter_set.json()
        parameter_set.update_json_fk(**{f"update_{name}s": True})
        return {"value": "success", "parameter_set": parameter_set.json()}
