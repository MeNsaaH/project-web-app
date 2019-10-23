from asgiref.sync import async_to_sync
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from main.models import Record


@receiver(post_save, sender=Record)
def send_websocket_message(sender, **kwargs):
    if kwargs['created']:
        instance = kwargs['instance']
        channel_layer = get_channel_layer()

        async_to_sync(channel_layer.group_send)(
            'data_results',
            {
                'type': 'chat_message',
                'message': instance.water_level
            }
        )
