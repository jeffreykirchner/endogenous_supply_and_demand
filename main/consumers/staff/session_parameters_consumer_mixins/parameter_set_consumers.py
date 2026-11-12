from channels.db import database_sync_to_async

from main.forms import ParameterSetConsumerForm
from .parameter_set_participants import change_parameter_set_participant


@database_sync_to_async
def change_parameter_set_consumer(user, data, action):
    return change_parameter_set_participant(user, data, action, name="consumer", form_class=ParameterSetConsumerForm)


class ParameterSetConsumersMixin:
    async def consumer_change_response(self, event, action):
        status = await change_parameter_set_consumer(self.scope["user"], event["message_text"], action)
        parameter_set = status.pop("parameter_set", None)
        message_data = {"status": status, "parameter_set": parameter_set, "source": "consumer"}
        await self.send_message(message_to_self=message_data, message_to_group=None,
                                message_type="update_parameter_set",
                                send_to_client=True, send_to_group=False)

    async def add_parameterset_consumer(self, event):
        await self.consumer_change_response(event, "add")

    async def update_parameter_set_consumer(self, event):
        await self.consumer_change_response(event, "update")

    async def remove_parameterset_consumer(self, event):
        await self.consumer_change_response(event, "delete")

    async def duplicate_parameterset_consumer(self, event):
        await self.consumer_change_response(event, "duplicate")
