import unittest
from app import app, db
from models import User, Post

class BloglyTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test client and configure app for testing."""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = app.test_client()

        with app.app_context():
            db.create_all()

    def tearDown(self):
        """Clean up any leftover transactions."""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_home(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_user_list(self):
        """Test displaying the user list."""
        response = self.client.get('/users')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Users', response.get_data(as_text=True))

    def test_add_new_user(self):
        """Test adding a new user."""
        response = self.client.post('/users/new', data={'first_name': 'John', 'last_name': 'Doe', 'image_url': ''}, follow_redirects=True)
        self.assertIn('John Doe', response.get_data(as_text=True))

    def test_user_detail_page(self):
        """Test display of the user detail page."""
        with app.app_context():
            new_user = User(first_name='Test', last_name='User', image_url='')
            db.session.add(new_user)
            db.session.commit()
            response = self.client.get(f'/users/{new_user.id}')
            self.assertIn('Test User', response.get_data(as_text=True))

    def test_add_new_post(self):
        """Test adding a new post to a user."""
        with app.app_context():
            new_user = User(first_name='Test', last_name='User', image_url='')
            db.session.add(new_user)
            db.session.commit()
            response = self.client.post(f'/users/{new_user.id}/posts/new', data={'title': 'Test Post', 'content': 'Test Content'}, follow_redirects=True)
            self.assertIn('Test Post', response.get_data(as_text=True))

    def test_view_post_detail(self):
        """Test viewing a single post detail."""
        with app.app_context():
            user = User(first_name='Test', last_name='User')
            db.session.add(user)
            db.session.commit()

            post = Post(title='Test Post', content='This is a test.', user_id=user.id)
            db.session.add(post)
            db.session.commit()

            response = self.client.get(f'/posts/{post.id}')
            self.assertIn('This is a test.', response.get_data(as_text=True))
    
            




if __name__ == '__main__':
    unittest.main()
