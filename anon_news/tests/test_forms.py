from django.test import TestCase


from apps.accounts.forms import LoginForm, UserRegisterForm
from apps.accounts.models import User


class LoginFormTest(TestCase):

    def test_form_fields_labels(self):
        form = LoginForm()
        self.assertEqual(form.fields['username'].label, 'юзернейм')
        self.assertEqual(form.fields['password'].label, 'Пароль')

    def test_form_widgets(self):
        form = LoginForm()
        self.assertEqual(form.fields['username'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['username'].widget.attrs['placeholder'], 'юзернейм')
        self.assertEqual(form.fields['password'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['password'].widget.attrs['placeholder'], 'пароль')


class UserRegisterFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create(username='Big', password='Test12345')

    def test_form_fields_labels_and_widgets(self):
        form = UserRegisterForm()

        # Check labels and widgets for username, password1, and password2 fields
        self.assertEqual(form.fields['username'].label, 'юзернейм')
        self.assertEqual(form.fields['password1'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['password1'].widget.attrs['placeholder'], 'придумайте пароль')
        self.assertEqual(form.fields['password2'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['password2'].widget.attrs['placeholder'], 'подтвердите пароль')

    def test_form_valid_data(self):
        form_data = {
            'username': 'testuser',
            'password1': 'testpassword',
            'password2': 'testpassword',
        }

        form = UserRegisterForm(data=form_data)

        # Check if the form is valid with the provided data
        self.assertTrue(form.is_valid())

    def test_form_password_mismatch(self):
        form_data = {
            'username': 'testuser',
            'password1': 'testpassword1',
            'password2': 'testpassword2',
        }

        form = UserRegisterForm(data=form_data)

        # Check if the form is invalid due to password mismatch
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_form_username_unique(self):
        user = User.objects.get(id=1)
        print(user)


        form_data = {
            'username': 'Big',  # НЕуникальное имя пользователя
            'password1': 'Test12345',
            'password2': 'Test12345',
        }

        form = UserRegisterForm(data=form_data)

        # Проверяем, что форма недопустима из-за неуникального имени пользователя
        self.assertFalse(form.is_valid())
        if form.errors:
            print(form.errors)
        self.assertIn('username', form.errors)