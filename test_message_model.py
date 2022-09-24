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

    def test_message_repr(self):
        "Does the repr method work as expected?"

        self.assertEqual(Message.__tablename__, 'messages')
        
    def test_invalid_message_model(self):
        """Does a invalid message throw errors?"""

        u1 = User(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD"
        )

        db.session.add(u1)
        db.session.commit()  

        #  throws error user with invalid credentials (missing user_id)
        with self.assertRaises(Exception):
            msg = Message(
            text="testing")
            

            db.session.add(msg)
            db.session.commit()

        #  throws error user with invalid credentials (missing text)
        with self.assertRaises(Exception):
            msg = Message(
            user_id=u1.id )
            
            db.session.add(msg)
            db.session.commit()

    
        
    def test_valid_message_model(self):
        """Does a message with valid credentials get handled proplery?"""
        u1 = User(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD"
        )
        
        db.session.add(u1)
        db.session.commit() 
        print(u1)

        msg = Message(
            text="testing", user_id=u1.id)
            
        u1.messages.append(msg)
        db.session.commit()
     
        self.assertIn(msg, u1.messages)

