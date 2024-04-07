import unittest
from app import app, db
from models import User

class UserTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_home(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/users', response.location)  

    def test_user_list(self):
        """test that user list displays"""
        response = self.client.get('/users')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Users', response.get_data(as_text=True))

    def test_add_new_user(self):
        response = self.client.post('/users/new', data=dict(first_name='John', last_name='Doe', image_url=''), follow_redirects=True)
        self.assertIn('John Doe', response.get_data(as_text=True))

    def test_user_detail_page(self):
        """test user detail page."""
        with app.app_context():
            new_user = User(first_name='Test', last_name='User', image_url='')
            db.session.add(new_user)
            db.session.commit()
            response = self.client.get(f'/users/{new_user.id}')
            self.assertEqual(response.status_code, 200)
            self.assertIn('Test User', response.get_data(as_text=True))
            db.session.delete(new_user)
            db.session.commit()

    def test_edit_user(self):
        with app.app_context():
            new_user = User(first_name='Test', last_name='User', image_url='')
            db.session.add(new_user)
            db.session.commit()

            response = self.client.post(f'/users/{new_user.id}/edit', data=dict(first_name='Edited', last_name='User', image_url=''), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn('Edited User', response.get_data(as_text=True))  
            db.session.delete(new_user)
            db.session.commit()

if __name__ == '__main__':
    unittest.main()
