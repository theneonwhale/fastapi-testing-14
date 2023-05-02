import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import User
from src.repository.users import get_user_by_email, create_user, update_token, confirmed_email, update_avatar
from src.schemas import UserModel


class TestUsers(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(
            id=1,
            username='UserUser',
            email='test@test.com',
            password='password',
            avatar='https://www.gravatar.com/avatar/26908f788a1d4dd42238f114cd222805',
            refresh_token='refresh_token',
            confirmed=True
        )

    async def test_get_user_by_email(self):
        user = self.user
        self.session.query().filter_by().first.return_value = user
        result = await get_user_by_email(user.email, self.session)
        self.assertEqual(result, user)

    async def test_create_user(self):
        body = UserModel(
            username=self.user.username,
            email=self.user.email,
            password=self.user.password
        )
        result = await create_user(body, self.session)
        self.assertEqual(result.username, body.username)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.password, body.password)
        self.assertTrue(hasattr(result, "id"))

    async def test_update_token(self):
        user = self.user
        token = 'new_token'
        result = await update_token(user, token, self.session)
        self.assertIsNone(result)
        self.assertEqual(user.refresh_token, token)

    async def test_confirmed_email(self):
        user = self.user
        self.session.query().filter_by().first.return_value = user
        result = await confirmed_email(user.email, self.session)
        self.assertIsNone(result)
        self.assertTrue(user.confirmed)

    async def test_update_avatar(self):
        url = 'https://www.gravatar.com/avatar/6c7b95cffe6f185bce0adbd0b9a62745'
        user = self.user
        result = await update_avatar(user.email, url, self.session)
        self.assertEqual(result.avatar, url)
