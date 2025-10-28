from django.conf.urls import url

from channels.routing import ChannelNameRouter, ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

from SicargaBox.consumers import SicargaBox_WebSocketConsumer

# Consumer Imports
from MiCasillero.consumers import MiCasilleroConsumer


application = ProtocolTypeRouter(
    {
        # WebSocket handler
        "websocket": AuthMiddlewareStack(
            URLRouter(
                [
                    url(r"^ws/$", SicargaBox_WebSocketConsumer.as_asgi()),
                ]
            )
        ),
        "channel": ChannelNameRouter(
            {
                "MiCasillero": MiCasilleroConsumer,
            }
        ),
    }
)
