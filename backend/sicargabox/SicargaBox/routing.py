from channels.auth import AuthMiddlewareStack
from channels.routing import ChannelNameRouter, ProtocolTypeRouter, URLRouter
from django.conf.urls import url

# Consumer Imports
from MiCasillero.consumers import MiCasilleroConsumer
from SicargaBox.consumers import SicargaBox_WebSocketConsumer

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
