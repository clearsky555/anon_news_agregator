from django.test import TestCase

from apps.accounts.models import User


# class YourTestClass(TestCase):
#
#     @classmethod
#     def setUpTestData(cls):
#         print("setUpTestData: Run once to set up non-modified data for all class methods.")
#         pass
#
#     def setUp(self):
#         print("setUp: Run once for every test method to setup clean data.")
#         pass
#
#     def test_false_is_false(self):
#         print("Method: test_false_is_false.")
#         self.assertFalse(False)
#
#     def test_false_is_true(self):
#         print("Method: test_false_is_true.")
#         self.assertTrue(True)
#
#     def test_one_plus_one_equals_two(self):
#         print("Method: test_one_plus_one_equals_two.")
#         self.assertEqual(1 + 1, 2)


class UserModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create(username='Big', password='Test12345')

    def test_username_label(self):
        user=User.objects.get(id=1)
        field_label = user._meta.get_field('username').verbose_name
        self.assertEquals(field_label,'username')

    def test_username_max_length(self):
        user=User.objects.get(id=1)
        max_length = user._meta.get_field('username').max_length
        self.assertEquals(max_length,150)

    def test_object_name_is_username(self):
        user=User.objects.get(id=1)
        expected_object_name = user.username
        self.assertEquals(expected_object_name,str(user))

    def test_is_staff_default(self):
        user = User.objects.get(id=1)
        field = user._meta.get_field('is_staff')
        self.assertFalse(field.default)

    def test_ip_address_null_and_blank(self):
        user = User.objects.get(id=1)
        field = user._meta.get_field('ip_address')
        self.assertTrue(field.null)
        self.assertTrue(field.blank)

    def test_image_upload_to(self):
        user = User.objects.get(id=1)
        field = user._meta.get_field('image')
        self.assertEqual(field.upload_to, 'user/images/')