from django.test import TestCase
from django.contrib.auth import get_user_model


class AccountsTests(TestCase):
	def test_register_and_login(self):
		User = get_user_model()
		resp = self.client.post('/accounts/web/register/', data={'username':'tester','email':'t@example.com','role':'cliente','password1':'testpass123','password2':'testpass123'}, follow=True)
		self.assertEqual(resp.status_code, 200)
		user = User.objects.filter(username='tester').first()
		self.assertIsNotNone(user)
		# try login
		resp = self.client.post('/accounts/web/login/', data={'username':'tester','password':'testpass123'}, follow=True)
		self.assertEqual(resp.status_code, 200)
		# session should have _auth_user_id
		self.assertIn('_auth_user_id', self.client.session)
