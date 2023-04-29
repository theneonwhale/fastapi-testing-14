from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session
from src.database.models import Contact, User
from src.schemas import ContactModel


async def get_contacts(user: User, limit: int, offset: int, db: Session):
    contacts = db.query(Contact).filter_by(user_id=user.id).limit(limit).offset(offset).all()
    return contacts


async def get_contact_by_id(user: User, contact_id: int, db: Session):
    contact = db.query(Contact).filter_by(user_id=user.id, id=contact_id).first()
    return contact


async def get_contact_by_email(user: User, email: str, db: Session):
    contact = db.query(Contact).filter_by(user_id=user.id, email=email).first()
    return contact


async def get_contact_by_phone(user: User, phone: str, db: Session):
    contact = db.query(Contact).filter_by(user_id=user.id, phone=phone).first()
    return contact


async def create_contact(user: User, body: ContactModel, db: Session):
    contact = Contact(**body.dict(), user_id=user.id)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def update_contact(user: User, contact_id: int, body: ContactModel, db: Session):
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
    contact = await get_contact_by_id(user, contact_id, db)
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def search_contacts(user: User, query: str, db: Session):
    contacts = db.query(Contact).filter_by(user_id=user.id).filter(
        func.lower(Contact.name).contains(func.lower(query)) |
        func.lower(Contact.surname).contains(func.lower(query)) |
        func.lower(Contact.email).contains(func.lower(query)) |
        func.lower(Contact.phone).contains(func.lower(query))
    ).all()
    return contacts


async def get_birthdays(user: User, db: Session):
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
