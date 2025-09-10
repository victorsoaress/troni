from django.urls import path
from .views import (
    ChatRagAPIView,
)

from django.views.generic import TemplateView

urlpatterns = [
    # UI do chat (renderiza templates/chat/index.html)
    path("", TemplateView.as_view(template_name="index.html"), name="chat_ui"),

    # APIs
    path("api/chat/rag", ChatRagAPIView.as_view(), name="chat_rag"),          
]
