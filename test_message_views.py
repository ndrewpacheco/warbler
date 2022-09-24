"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

    def test_add_message(self):
        """Can user add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_delete_message(self):
        """Can user delete a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

                # Now, that session setting is saved, so we can have
                # the rest of ours test

            # post new msg
            c.post("/messages/new", data={"text": "Hello"})
        
            msg = Message.query.one()
            user = User.query.get(self.testuser.id)
                
            # test for new message
            self.assertIn(msg, user.messages)

            # delete msg
            resp = c.post(f"/messages/{msg.id}/delete")
            user = User.query.get(self.testuser.id)

            # test for deleted message
            self.assertNotIn(msg, user.messages)

    def test_logged_out_add_msg(self):
        "Are you prohibited from adding a msg when logged out"

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:
        
        with self.client as c:
            with c.session_transaction() as sess:
                # login
                sess[CURR_USER_KEY] = self.testuser.id

                # then logout
                del sess[CURR_USER_KEY]

        # attempt to add a msg
        resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
        html = resp.get_data(as_text=True)

        # should go to home-anon.html view
        self.assertEqual(resp.status_code, 200)
        self.assertIn('<h4>New to Warbler?</h4>', html)

    def test_logged_out_delete_msg(self):
        "Are you prohibited from deleting a msg when logged out"
        

        "Are you prohibited from adding a msg when logged out"

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:
        
        with self.client as c:
            with c.session_transaction() as sess:
                # login
                sess[CURR_USER_KEY] = self.testuser.id
            
            # add new msg
            c.post("/messages/new", data={"text": "Hello"})

            # then logout
            with c.session_transaction() as sess:
                del sess[CURR_USER_KEY]
            msg = Message.query.one()
                 # attempt to add a msg
            resp = c.post(f"/messages/{msg.id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            # should go to home-anon.html view
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h4>New to Warbler?</h4>', html)