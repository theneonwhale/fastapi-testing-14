from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session
from src.database.models import Contact, User
from src.schemas import ContactModel


async def get_contacts(user: User, limit: int, offset: int, db: Session):
    """
    The get_contacts function returns a list of contacts for the user.

    :param user: User: Filter the contacts by user id
    :param limit: int: Limit the number of contacts returned
    :param offset: int: Specify the number of records to skip before starting to return rows
    :param db: Session: Pass the database session to the function
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = db.query(Contact).filter_by(user_id=user.id).limit(limit).offset(offset).all()
    return contacts


async def get_contact_by_id(user: User, contact_id: int, db: Session):
    """
    The get_contact_by_id function returns a contact from the database by its id.

    :param user: User: Get the user's id
    :param contact_id: int: Filter the database by contact id
    :param db: Session: Pass the database session to the function
    :return: The contact with the given id
    :doc-author: Trelent
    """
    contact = db.query(Contact).filter_by(user_id=user.id, id=contact_id).first()
    return contact


async def get_contact_by_email(user: User, email: str, db: Session):
    """
    The get_contact_by_email function takes in a user and an email address,
    and returns the contact associated with that email address.


    :param user: User: Get the user_id from the user object
    :param email: str: Filter the database query by email
    :param db: Session: Connect to the database
    :return: A contact object
    :doc-author: Trelent
    """
    contact = db.query(Contact).filter_by(user_id=user.id, email=email).first()
    return contact


async def get_contact_by_phone(user: User, phone: str, db: Session):
    """
    The get_contact_by_phone function returns a contact object from the database based on the user's id and phone number.
        Args:
            user (User): The User object that is associated with the contact.
            phone (str): The phone number of the desired Contact object.

    :param user: User: Identify the user that is making the request
    :param phone: str: Filter the contact by phone number
    :param db: Session: Access the database
    :return: A contact
    :doc-author: Trelent
    """
    contact = db.query(Contact).filter_by(user_id=user.id, phone=phone).first()
    return contact


async def create_contact(user: User, body: ContactModel, db: Session):
    """
    The create_contact function creates a new contact in the database.

    :param user: User: Get the user id from the jwt token
    :param body: ContactModel: Deserialize the request body into a contactmodel object
    :param db: Session: Create a new contact in the database
    :return: A contact object
    :doc-author: Trelent
    """
    contact = Contact(**body.dict(), user_id=user.id)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def update_contact(user: User, contact_id: int, body: ContactModel, db: Session):
    """
    The update_contact function updates a contact in the database.
        Args:
            user (User): The user who is making the request.
            contact_id (int): The id of the contact to be updated.
            body (ContactModel): A ContactModel object containing all of the information for updating a contact.

    :param user: User: Check if the user is authorized to update a contact
    :param contact_id: int: Get the contact by id
    :param body: ContactModel: Pass the updated contact information
    :param db: Session: Pass the database session to the function
    :return: The contact that has been updated
    :doc-author: Trelent
    """
    contact = await get_contact_by_id(user, contact_id, db)
    if contact:
        contact.name = body.name
        contact.surname = body.surname
        contact.email = body.email
        contact.phone = body.phone
        contact.birthday = body.birthday
        contact.additional_info = body.additional_info
        db.commit()
    return contact


async def delete_contact(user: User, contact_id: int, db: Session):
    """
    The delete_contact function deletes a contact from the database.
        Args:
            user (User): The user who is deleting the contact.
            contact_id (int): The id of the contact to be deleted.
            db (Session): A connection to our database, used for querying and updating data.

    :param user: User: Identify the user who is deleting the contact
    :param contact_id: int: Identify the contact to be deleted
    :param db: Session: Pass the database session to the function
    :return: The contact that was deleted
    :doc-author: Trelent
    """
    contact = await get_contact_by_id(user, contact_id, db)
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def search_contacts(user: User, query: str, db: Session):
    """
    The search_contacts function searches for contacts in the database.
        Args:
            user (User): The user who is searching for contacts.
            query (str): The search query string, which can be a name, surname, email or phone number of a contact.

    :param user: User: Get the user id from the database
    :param query: str: Search for a contact in the database
    :param db: Session: Connect to the database
    :return: A list of contacts that match the query
    :doc-author: Trelent
    """
    contacts = db.query(Contact).filter_by(user_id=user.id).filter(
        func.lower(Contact.name).contains(func.lower(query)) |
        func.lower(Contact.surname).contains(func.lower(query)) |
        func.lower(Contact.email).contains(func.lower(query)) |
        func.lower(Contact.phone).contains(func.lower(query))
    ).all()
    return contacts


async def get_birthdays(user: User, db: Session):
    """
    The get_birthdays function returns a list of contacts whose birthday is within the next 7 days.


    :param user: User: Specify the user that is currently logged in
    :param db: Session: Access the database
    :return: A list of contacts whose birthdays are in the next week
    :doc-author: Trelent
    """
    now = datetime.now().date()
    contacts = db.query(Contact).filter_by(user_id=user.id).all()
    birthday_contacts = []
    for contact in contacts:
        birthday = contact.birthday
        if birthday:
            birthday_this_year = birthday.replace(year=now.year)
            days_until_birthday = (birthday_this_year - now).days
            if days_until_birthday in range(8):
                birthday_contacts.append(contact)

    return birthday_contacts
