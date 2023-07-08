from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseBadRequest
from rest_framework import viewsets, status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .utils import get_client_ip
from .models import Post
from .permissions import UserViewSetPermissions, PostViewSetPermissions
from .serializers import  UserSerializer, PostSerializer, MyTokenObtainPairSerializer
from django_q.tasks import async_task
from django_filters import rest_framework
import logging

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    permission_classes = [UserViewSetPermissions]
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

    def perform_create(self, serializer, signup_ip):
        serializer.save(signup_ip=signup_ip)
        async_task("django_post_app.tasks.enrich_user_location", serializer.data['email'])

    
    def create(self, request, *args, **kwargs):
        client_ip = get_client_ip(request)
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer, signup_ip=client_ip)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except ValueError as e:
            logging.error(f"Error: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PostViewSet(viewsets.ModelViewSet):
    permission_classes = [PostViewSetPermissions]
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        liked = kwargs.get("liked", None)
        if liked is not None:
            if liked == "true":
                instance.liked_by.add(request.user)
            else:
                instance.liked_by.remove(request.user)

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            data = request.data
            if instance.author != request.user:
                if len(data.keys()) > 1 or "liked" not in data:
                    return HttpResponseBadRequest("You are not the author of this post")
            return super().partial_update(request, *args, **kwargs, liked=data.get("liked", None))
        except ValueError as e:
            logging.error(f"Error: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class MyObtainTokenPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = MyTokenObtainPairSerializer