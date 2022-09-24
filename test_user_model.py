"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py

# FLASK_ENV=production python3 -m unittest test_user_model.py
import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        
        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()


    def tearDown(self):
        """Tear down test client and sample data"""

        db.session.remove()


    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_user_repr(self):
        "Does the repr method work as expected?"

        self.assertEqual(User.__tablename__, 'users')


    def test_is_following(self):
        """Does is_following successfully detect when user1 is/isn't following user2?"""

        u1 = User(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD"
        )

        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD" 
        )

        u1.followers.append(u2)

        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        # u1 should be following u2
        self.assertTrue(u2.is_following(u1))

        u1.followers.remove(u2)
        db.session.commit()

        # # u1 should not be following u2
        self.assertFalse(u2.is_following(u1))
        

    def test_is_followed_by(self):
        """Does is_followed_by successfully detect when user1 is/isn't followed user2?"""

        u1 = User(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD"
        )

        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD" 
        )

        u1.followers.append(u2)

        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        # u1 should be following u2
        self.assertTrue(u1.is_followed_by(u2))

        u1.followers.remove(u2)
        db.session.commit()

        # # u1 should not be following u2
        self.assertFalse(u1.is_following(u2))

    
    def test_user_signup(self):
        """Does User.signup successfully create a new user given valid credentials? 
        Does User.create fail to create a new user if any of the validations (e.g. uniqueness, non-nullable fields) fail?"""

        #  create user with valid credentials
        self.assertIsInstance(User.signup(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD",
            image_url = "www.image.com"
        ), User)

     
        #  create user with invalid credentials
        with self.assertRaises(TypeError):
            User.signup(
            email="test2@test.com",
            username="testuser2",
            image_url = "www.image.com")
    

    def test_user_authenticate(self):
        """Does User.authenticate successfully return a user when given a valid username and password?"""
        
        u = User.signup(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD",
            image_url = "www.image.com"
        )
        db.session.add(u)
        db.session.commit()
        
        self.assertEqual(User.authenticate("testuser2", "HASHED_PASSWORD"), u)

        # Does User.authenticate fail to return a user when the username is invalid?
        self.assertNotEqual(User.authenticate("testuser222222", "HASHED_PASSWORD"), u)

        # Does User.authenticate fail to return a user when the password is invalid?
        self.assertNotEqual(User.authenticate("testuser2", "HASHED_"), u)
