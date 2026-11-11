import asyncio
from contextlib import suppress

from django.conf import settings
from django.test import SimpleTestCase
from django.utils.module_loading import import_string


class ChannelLayerTimeoutTests(SimpleTestCase):
    async def test_idle_channel_receives_message_after_multiple_blocking_reads(self):
        config = settings.CHANNEL_LAYERS["default"]
        layer = import_string(config["BACKEND"])(**config["CONFIG"])
        channel = await layer.new_channel()
        receive_task = asyncio.create_task(layer.receive(channel))
        try:
            await asyncio.sleep(11)
            if receive_task.done():
                await receive_task
                self.fail("Channel receive ended before a message was sent")

            message = {"type": "test.message", "value": "received"}
            await layer.send(channel, message)
            self.assertEqual(await asyncio.wait_for(receive_task, timeout=2), message)
        finally:
            if not receive_task.done():
                receive_task.cancel()
                with suppress(asyncio.CancelledError):
                    await receive_task
            await layer.close_pools()
