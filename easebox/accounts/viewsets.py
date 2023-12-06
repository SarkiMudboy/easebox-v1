from rest_framework import mixins, viewsets
from rest_framework import permissions, authentication

class BaseCreateListRetrieveUpdateViewSet(viewsets.ModelViewSet):
    
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]