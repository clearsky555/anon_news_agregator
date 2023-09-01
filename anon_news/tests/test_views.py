from django.test import TestCase

from apps.accounts.models import User
from django.urls import reverse


class UserListViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        #Create 13 authors for pagination tests
        number_of_users = 13
        for user_num in range(number_of_users):
            User.objects.create(username='Christian %s' % user_num, password = 'Surname %s' % user_num,)

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get('/api/v1/users/')
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse('users_api'))
        self.assertEqual(resp.status_code, 200)

    def test_pagination_is_ten(self):
        resp = self.client.get(reverse('users_api'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['results']), 10)
        self.assertTrue(resp.data['next'] is not None)

    def test_lists_all_authors(self):
        page_number = 2
        url = reverse('users_api') + f'?page={page_number}'
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200)
        self.assertTrue('results' in resp.data)
        self.assertTrue(resp.data['count'] > 3)  # Assuming there are more than 3 authors
        self.assertTrue(resp.data['next'] is None)  # Confirming that there is no next page
        self.assertEqual(len(resp.data['results']), 3)  # Checking that it has exactly 3 items on the page