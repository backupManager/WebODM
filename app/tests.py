from django.test import TestCase

from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.test import Client

from .models import Project, Task

class TestApp(TestCase):

    fixtures = ['test_users', 'test_processingnodes', ]

    def setUp(self):
        self.credentials = {
            'username': 'testuser',
            'password': 'test1234',
            'email': 'test@mail.com'}

        # Create a test Group
        my_group, created = Group.objects.get_or_create(name='test_group')

        # Add user to test Group
        User.objects.get(pk=1).groups.add(my_group)

    def tearDown(self):
        pass

    def test_user_login(self):
        c = Client()
        # User points the browser to the landing page
        res = c.post('/', follow=True)

        # the user is not logged in
        self.assertFalse(res.context['user'].is_authenticated)
        # and is redirected to the login page
        self.assertRedirects(res, '/login/')

        # The login page is being rendered by the correct template
        self.assertTemplateUsed(res, 'registration/login.html')

        # asks the user to login using a set of valid credentials
        res = c.post('/login/', data=self.credentials, follow=True)

        # The system acknowledges him
        self.assertTrue(res.context['user'].is_authenticated)

        # and moves him at the dashboard
        self.assertTemplateUsed(res, 'app/dashboard.html')

    def test_views(self):
        c = Client()

        # Connecting to dashboard without auth redirects to /
        res = c.get('/dashboard/', follow=True)
        self.assertFalse(res.context['user'].is_authenticated)
        self.assertRedirects(res, '/login/?next=/dashboard/')

        res = c.get('/processingnode/1/', follow=True)
        self.assertRedirects(res, '/login/?next=/processingnode/1/')

        # Login
        c.post('/login/', data=self.credentials, follow=True)

        # We can access a processingnode view that exists
        res = c.get('/processingnode/1/')
        self.assertTrue(res.status_code == 200)
        self.assertTemplateUsed(res, 'app/processing_node.html')

        # We can access a processingnode that is offline
        # (and there's a warning message when we do that)
        res = c.get('/processingnode/2/')
        self.assertTrue(res.status_code == 200)
        self.assertTemplateUsed(res, 'app/processing_node.html')

        message = list(res.context['messages'])[0]
        self.assertEqual(message.tags, 'warning')
        self.assertTrue("offline" in message.message)

        res = c.get('/processingnode/9999/')
        self.assertTrue(res.status_code == 404)

        res = c.get('/processingnode/abc/')
        self.assertTrue(res.status_code == 404)
