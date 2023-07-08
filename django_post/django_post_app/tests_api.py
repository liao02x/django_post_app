from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Post
from rest_framework.test import APITestCase
from rest_framework import status
import logging

User = get_user_model()

def pp(request):
    print(request.status_code, request.json())

userc1 = {'email': 'test@user.com', 'password': '12345678'}
userc2 = {'email': 'test2@user.com', 'password': '12345678'}

class AuthTests(APITestCase):
    def test_signup(self):
        # sign up with weak password
        request = self.client.post('/api/signup/', {'email': 'test@user.com', 'password': 'foo'})
        self.assertEqual(request.status_code, status.HTTP_400_BAD_REQUEST)

        # sign up with bad email
        request = self.client.post('/api/signup/', {'email': 'testuser.com', 'password': '12345678'})
        self.assertEqual(request.status_code, status.HTTP_400_BAD_REQUEST)

        # sign up with valid email and password
        request = self.client.post('/api/signup/', userc1)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
    
    def test_login(self):
        self.client.post('/api/signup/', userc1)    
        user = User.objects.all().first()
        user.is_active = True
        user.save()

        request = self.client.post('/api/login/', {'email': 'test@user.com'})
        self.assertEqual(request.status_code, status.HTTP_400_BAD_REQUEST)

        request = self.client.post('/api/login/', {'email': 'test@user.com', 'password': 'wrongpassword'})
        self.assertEqual(request.status_code, status.HTTP_401_UNAUTHORIZED)

        request = self.client.post('/api/login/', userc1)
        self.assertEqual(request.status_code, status.HTTP_200_OK)

        self.assertEqual('access' in request.data, True)
        self.assertEqual('refresh' in request.data, True)

    def test_refresh_token(self):
        self.client.post('/api/signup/', userc1)
        user = User.objects.all().first()
        user.is_active = True
        user.save()

        request = self.client.post('/api/login/', userc1)
        self.assertEqual(request.status_code, status.HTTP_200_OK)

        request = self.client.post('/api/token/refresh/', {'refresh': request.data['refresh']})
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual('access' in request.data, True)

    def test_get_user(self):
        self.client.post('/api/signup/', userc1)
        user = User.objects.all().first()
        user.is_active = True
        user.save()

        self.client.post('/api/signup/', userc2)
        user2 = User.objects.get(email="test2@user.com")
        user2.is_active = True
        user2.save()

        request = self.client.post('/api/login/', userc1)
        header = {'HTTP_AUTHORIZATION': 'Bearer ' + request.data['access']}

        request = self.client.get('/api/users/', **header)
        self.assertEqual(request.status_code, status.HTTP_403_FORBIDDEN)

        request = self.client.get(f'/api/users/{user2.id}/', **header)
        self.assertEqual(request.status_code, status.HTTP_403_FORBIDDEN)

        request = self.client.get(f'/api/users/{user.id}/', **header)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
    
    def test_delete_user(self):
        self.client.post('/api/signup/', userc1)
        user = User.objects.all().first()
        user.is_active = True
        user.save()

        self.assertEqual(User.objects.count(), 1)

        request = self.client.post('/api/login/', userc1)
        header = {'HTTP_AUTHORIZATION': 'Bearer ' + request.data['access']}

        request = self.client.delete(f'/api/users/{user.id}/', **header)
        self.assertEqual(request.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(), 0)


class PostsTests(APITestCase):
    def setUp(self):
        self.client.post('/api/signup/', userc1)
        user = User.objects.all().first()
        user.is_active = True
        user.save()

        request = self.client.post('/api/login/', userc1)
        header = {'HTTP_AUTHORIZATION': 'Bearer ' + request.data['access']}

        self.client.post('/api/signup/', {'email': 'test2@user.com', 'password': '12345678'})
        user2 = User.objects.get(email="test2@user.com")
        user2.is_active = True
        user2.save()

        request = self.client.post('/api/login/', userc2)
        header2 = {'HTTP_AUTHORIZATION': 'Bearer ' + request.data['access']}

        self.header = header
        self.header2 = header2
    
    def test_create_post(self):
        request = self.client.post('/api/posts/', {}, **self.header)
        self.assertEqual(request.status_code, status.HTTP_400_BAD_REQUEST)

        request = self.client.post('/api/posts/', {'title': 'test title', 'content': 'test body'}, **self.header)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)
    
    def test_get_post(self):
        self.client.post('/api/posts/', {'title': 'test title', 'content': 'test body'}, **self.header)
        
        # post is available to all users or guests
        request = self.client.get('/api/posts/')
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(len(request.data["results"]), 1)
        post1 = request.data["results"][0]
        self.assertEqual(post1["title"], 'test title')

        # post detail is available to owner
        request = self.client.get(f'/api/posts/{post1["id"]}/', **self.header)
        self.assertEqual(request.status_code, status.HTTP_200_OK)

        # post detail is available to other users
        request = self.client.get(f'/api/posts/{post1["id"]}/', **self.header2)
        self.assertEqual(request.status_code, status.HTTP_200_OK)

        # post detail is available to guests
        request = self.client.get(f'/api/posts/{post1["id"]}/')
        self.assertEqual(request.status_code, status.HTTP_200_OK)

    def test_update_post(self):
        self.client.post('/api/posts/', {'title': 'test title', 'content': 'test body'}, **self.header)
        
        request = self.client.patch('/api/posts/1/', {'title': 'test title 2'}, **self.header2)
        self.assertEqual(request.status_code, status.HTTP_400_BAD_REQUEST)

        request = self.client.patch('/api/posts/1/', {'title': 'test title 2'}, **self.header)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(Post.objects.all().first().title, 'test title 2')

    def test_delete_post(self):
        self.client.post('/api/posts/', {'title': 'test title', 'content': 'test body'}, **self.header)
        self.assertEqual(Post.objects.count(), 1)
        
        request = self.client.delete('/api/posts/1/', **self.header2)
        self.assertEqual(request.status_code, status.HTTP_403_FORBIDDEN)

        request = self.client.delete('/api/posts/1/', **self.header)
        self.assertEqual(request.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Post.objects.count(), 0)

    def test_like_post(self):
        self.client.post('/api/posts/', {'title': 'test title', 'content': 'test body'}, **self.header)
        
        request = self.client.patch('/api/posts/1/', { "liked": "true" }, **self.header2)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(Post.objects.all().first().liked_by.count(), 1)

        # same user like again wouldn't change anything
        request = self.client.patch('/api/posts/1/', { "liked": "true" }, **self.header2)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(Post.objects.all().first().liked_by.count(), 1)

        # unlike wouldn't change anything if user didn't like it before
        request = self.client.patch('/api/posts/1/', { "liked": "false" }, **self.header)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(Post.objects.all().first().liked_by.count(), 1)

        request = self.client.patch('/api/posts/1/', { "liked": "false" }, **self.header2)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(Post.objects.all().first().liked_by.count(), 0)

        # test total_likes field
        self.client.patch('/api/posts/1/', { "liked": "true" }, **self.header)
        self.client.patch('/api/posts/1/', { "liked": "true" }, **self.header2)
        request = self.client.get('/api/posts/1/')
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(request.data["total_likes"], 2)

