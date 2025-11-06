from django.urls import re_path
from .consumers import ChatbotConsumer

websocket_urlpatterns = [
    re_path(r"ws/chat/$", ChatbotConsumer.as_asgi()),
]
