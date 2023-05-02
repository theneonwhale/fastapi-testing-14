import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.repository.contacts import get_contacts, get_contact_by_id, get_contact_by_email, \
    get_contact_by_phone, create_contact, update_contact, delete_contact, search_contacts, get_birthdays

from src.schemas import ContactModel


class TestUsers(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)
        self.contact = Contact(
            id=1,
            name='ContactName',
            surname='ContactSurname',
            email='test@test.com',
            phone='1234567890',
            birthday='2000-10-10',
            additional_info='some info',
            created_at='2023-01-05',
            updated_at='2023-01-05',
            user_id=self.user.id
        )

    async def test_get_contacts(self):
        contacts = [Contact(), Contact(), Contact()]
        self.session.query().filter_by().limit().offset().all.return_value = contacts
        result = await get_contacts(self.user, 10, 0, self.session)
        self.assertEqual(result, contacts)

    async def test_get_contact_by_id(self):
        contact = self.contact
        self.session.query().filter_by().first.return_value = contact
        result = await get_contact_by_id(self.user, contact.id, self.session)
        self.assertEqual(result, contact)

    async def test_get_contact_by_email(self):
        contact = self.contact
        self.session.query().filter_by().first.return_value = contact
        result = await get_contact_by_email(self.user, contact.email, self.session)
        self.assertEqual(result, contact)

    async def test_get_contact_by_phone(self):
        contact = self.contact
        self.session.query().filter_by().first.return_value = contact
        result = await get_contact_by_phone(self.user, contact.phone, self.session)
        self.assertEqual(result, contact)

    async def test_create_contact(self):
        contact = ContactModel(
            name='ContactName2',
            surname='ContactSurname2',
            email='test2@test.com',
            phone='1234567891',
            birthday='2000-10-11',
            additional_info='some info 2'
        )
        result = await create_contact(self.user, contact, self.session)
        self.assertEqual(result.name, contact.name)
        self.assertEqual(result.surname, contact.surname)
        self.assertEqual(result.email, contact.email)
        self.assertEqual(result.phone, contact.phone)
        self.assertEqual(result.birthday, contact.birthday)
        self.assertEqual(result.additional_info, contact.additional_info)
        self.assertTrue(hasattr(result, "id"))
        self.assertTrue(hasattr(result, "user_id"))
        self.assertTrue(hasattr(result, "created_at"))
        self.assertTrue(hasattr(result, "updated_at"))

    async def test_update_contact(self):
        updated_contact = ContactModel(
            name='ContactName3',
            surname='ContactSurname3',
            email='test3@test.com',
            phone='1234567892',
            birthday='2000-10-12',
            additional_info='some info 3'
        )
        result = await update_contact(self.user, self.contact.id, updated_contact, self.session)
        self.assertEqual(result.name, updated_contact.name)
        self.assertEqual(result.surname, updated_contact.surname)
        self.assertEqual(result.email, updated_contact.email)
        self.assertEqual(result.phone, updated_contact.phone)
        self.assertEqual(result.birthday, updated_contact.birthday)
        self.assertEqual(result.additional_info, updated_contact.additional_info)
        self.assertTrue(hasattr(result, "id"))
        self.assertTrue(hasattr(result, "user_id"))
        self.assertTrue(hasattr(result, "created_at"))
        self.assertTrue(hasattr(result, "updated_at"))

    async def test_delete_contact(self):
        self.session.query().filter_by().first.return_value = self.contact
        result = await delete_contact(self.user, self.contact.id, self.session)
        self.assertEqual(result, self.contact)
