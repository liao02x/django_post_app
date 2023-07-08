from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Post
import logging

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'last_login', 'is_superuser', 'is_active', 'password')
        read_only_fields = ('signup_ip', 'username', 'is_superuser')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 8}}
    
    def create(self, validated_data, **kwargs):
        user = User.objects.create_user(**validated_data, **kwargs)
        return user
    
    def update(self, instance, validated_data):
        email = validated_data.pop('email', None)
        if email is not None and email != instance.email:
            raise serializers.ValidationError("Email cannot be changed")
        
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        
        if password:
            user.set_password(password)
            user.save()

        return user


class PostSerializer(serializers.ModelSerializer):
    # author = UserSerializer(read_only=True)
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Post
        fields = ('id', 'title', 'content', 'author', 'created_at')
        # read_only_fields = ('id', 'author', 'created_at')
        validators = (
            UniqueTogetherValidator(
                queryset=Post.objects.all(),
                fields=['title', 'author']
            ),
        )
    
    def to_representation(self, value):
        data = super().to_representation(value)
        data['total_likes'] = value.liked_by.count()

        user = self.context['request'].user
        if user.is_authenticated:
            data['liked'] = user in value.liked_by.all()
        return data
    
    def update(self, instance, validated_data):
        new_author = validated_data.get('author', None)
        if new_author is not None and new_author != instance.author:
            raise serializers.ValidationError("Author cannot be changed")

        return super().update(instance, validated_data)
    

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(self, user):
        logging.info(f"get_token: {user}")
        token = super(MyTokenObtainPairSerializer, self).get_token(user)

        token['email'] = user.email
        return token
