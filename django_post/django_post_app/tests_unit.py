from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Post
User = get_user_model()

class UsersManagersTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(email="normal@user.com", password="foo")
        admin_user = User.objects.create_superuser(email="super@user.com", password="foo")

    def test_create_user(self):
        user = User.objects.get(email="normal@user.com")
        self.assertEqual(user.email, "normal@user.com")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        try:
            self.assertIsNone(user.username)
        except AttributeError:
            pass
        with self.assertRaises(TypeError):
            User.objects.create_user()
        with self.assertRaises(ValueError):
            User.objects.create_user(email="")
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="foo")
        with self.assertRaises(ValueError):
            User.objects.create_user(email="not_a_email", password="foo")
        # duplicate email
        with self.assertRaises(ValueError):
            User.objects.create_user(email="normal@user.com", password="foo")
        
    def test_email_normalize(self):
        user2 = User.objects.create_user(email="test@USER.com", password="foo")
        self.assertEqual(user2.email, "test@user.com")

    def test_create_superuser(self):
        admin_user = User.objects.get(email="super@user.com")
        self.assertEqual(admin_user.email, "super@user.com")
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        try:
            self.assertIsNone(admin_user.username)
        except AttributeError:
            pass
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="super@user.com", password="foo", is_superuser=False)

class PostsTests(TestCase):
    
    def setUp(self):
        user = User.objects.create_user(email="normal@user.com", password="foo")
        post = Post.objects.create(title="test post", author=user)
    
    def test_post(self):
        post = Post.objects.get(title="test post")
        self.assertEqual(post.title, "test post")
        self.assertEqual(post.content, "")
        self.assertEqual(post.author.email, "normal@user.com")
    
    def test_post_with_body(self):
        post = Post.objects.get(title="test post")
        post.content = "test body"
        post.save()
        self.assertEqual(post.content, "test body")

    def test_post_with_empty_title(self):
        user = User.objects.get(email="normal@user.com")
        with self.assertRaises(Exception):
            post = Post.objects.create(author=user)
            post.save()
    
    def test_post_like(self):
        user = User.objects.get(email="normal@user.com")
        post = Post.objects.get(title="test post")
        post.liked_by.add(user)
        post.save()
        self.assertEqual(post.liked_by.count(), 1)
        self.assertEqual(post.liked_by.first(), user)

    def test_post_like_by_another_user(self):
        user = User.objects.get(email="normal@user.com")
        user2 = User.objects.create_user(email="test@user.com", password="foo")
        post = Post.objects.get(title="test post")
        post.liked_by.add(user)
        post.liked_by.add(user2)
        post.save()
        self.assertEqual(post.liked_by.count(), 2)

    def test_post_unlike(self):
        user = User.objects.get(email="normal@user.com")
        post = Post.objects.get(title="test post")
        post.liked_by.remove(user)
        post.save()
        self.assertEqual(post.liked_by.count(), 0)
        
    def test_post_like_twice(self):
        user = User.objects.get(email="normal@user.com")
        post = Post.objects.get(title="test post")
        post.liked_by.add(user)
        post.save()
        post.liked_by.add(user)
        post.save()
        self.assertEqual(post.liked_by.count(), 1)
                                
                                