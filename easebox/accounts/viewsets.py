from rest_framework import mixins, viewsets
from rest_framework import permissions, authentication
from rest_framework.renderers import TemplateHTMLRenderer
from .permissions import IsVerified


class AuthViewSet(viewsets.ModelViewSet):
    
    permission_classes = [permissions.IsAuthenticated]
    # authentication_classes = [authentication.TokenAuthentication]

class AnonViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    renderer_classes = [TemplateHTMLRenderer]