from typing import List, Optional

from fastapi import Query, Depends, HTTPException, Path, APIRouter
from sqlalchemy.orm import Session
from starlette import status
from fastapi_limiter.depends import RateLimiter

from src.database.db import get_db
from src.database.models import User, Role
from src.schemas import ContactResponse, ContactModel
from src.repository import contacts as repository_contacts
from src.services.auth import auth_service
from src.services.roles import RoleAccess

router = APIRouter(prefix="/contacts", tags=['contacts'])

allowed_operation_get = RoleAccess([Role.admin, Role.moderator, Role.user])
allowed_operation_create = RoleAccess([Role.admin, Role.moderator, Role.user])
allowed_operation_update = RoleAccess([Role.admin, Role.moderator])
allowed_operation_remove = RoleAccess([Role.admin])


@router.get('/', response_model=List[ContactResponse],
            dependencies=[Depends(allowed_operation_get), Depends(RateLimiter(times=2, seconds=5))],
            name="get contacts")
async def get_contacts(limit: int = Query(10, le=500), offset: int = 0, db: Session = Depends(get_db),
                       user: User = Depends(auth_service.get_current_user)):
    """
    The get_contacts function returns a list of contacts.

    :param limit: int: Limit the number of contacts returned
    :param le: Limit the maximum value of a parameter
    :param offset: int: Skip the first offset contacts
    :param db: Session: Pass the database session to the repository
    :param user: User: Get the current user
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = await repository_contacts.get_contacts(user, limit, offset, db)
    return contacts


@router.get('/search', response_model=List[ContactResponse],
            dependencies=[Depends(allowed_operation_get), Depends(RateLimiter(times=2, seconds=5))])
async def search_contacts(query: Optional[str] = None, db: Session = Depends(get_db),
                          user: User = Depends(auth_service.get_current_user)):
    """
    The search_contacts function searches for contacts in the database.

    :param query: Optional[str]: Search for contacts
    :param db: Session: Get the database session
    :param user: User: Get the current user from the database
    :return: A list of contacts that match the query
    :doc-author: Trelent
    """
    contacts = await repository_contacts.search_contacts(user, query, db)
    return contacts


@router.get('/birthdays', response_model=List[ContactResponse],
            dependencies=[Depends(allowed_operation_get), Depends(RateLimiter(times=2, seconds=5))])
async def get_birthdays(db: Session = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    """
    The get_birthdays function returns a list of contacts that have birthdays in the current month.
        The user is passed as an argument to ensure that only the logged-in user's contacts are returned.

    :param db: Session: Pass the database session to the function
    :param user: User: Get the current user from the database
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = await repository_contacts.get_birthdays(user, db)
    return contacts


@router.get('/{contact_id}', response_model=ContactResponse, name="get contact",
            dependencies=[Depends(allowed_operation_get), Depends(RateLimiter(times=2, seconds=5))])
async def get_contact(contact_id: int = Path(ge=1), db: Session = Depends(get_db),
                      user: User = Depends(auth_service.get_current_user)):
    """
    The get_contact function is a GET request that returns the contact with the given ID.
    The function takes in an optional contact_id parameter, which defaults to 1 if not provided.
    It also takes in a db Session object and user object as parameters, both of which are
    provided by dependency injection.

    :param contact_id: int: Specify the contact id that we want to get
    :param db: Session: Pass the database session to the function
    :param user: User: Get the current user
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await repository_contacts.get_contact_by_id(user, contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return contact


@router.post('/', response_model=ContactResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(allowed_operation_create), Depends(RateLimiter(times=2, seconds=5))])
async def create_contact(body: ContactModel, db: Session = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    """
    The create_contact function creates a new contact in the database.

    :param body: ContactModel: Get the data from the request body
    :param db: Session: Pass the database session to the repository layer
    :param user: User: Get the current user from the database
    :return: A contactmodel object, which is the same as the
    :doc-author: Trelent
    """
    has_contact_by_email = await repository_contacts.get_contact_by_email(user, body.email, db)
    has_contact_by_phone = await repository_contacts.get_contact_by_phone(user, body.phone, db)
    if has_contact_by_email or has_contact_by_phone:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already exists")
    contact = await repository_contacts.create_contact(user, body, db)
    return contact


@router.put('/{contact_id}', response_model=ContactResponse,
            dependencies=[Depends(allowed_operation_get), Depends(RateLimiter(times=2, seconds=5))])
async def update_contact(body: ContactModel, contact_id: int = Path(ge=1), db: Session = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    """
    The update_contact function updates a contact in the database.
        The function takes an id of the contact to be updated, and a body containing all fields that are to be updated.
        If no such contact exists, it returns 404 Not Found error. Otherwise it updates the fields and returns 200 OK.

    :param body: ContactModel: Get the information from the request body
    :param contact_id: int: Specify the contact id in the url
    :param db: Session: Get the database session
    :param user: User: Get the current user from the database
    :return: The updated contact
    :doc-author: Trelent
    """
    contact = await repository_contacts.update_contact(user, contact_id, body, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    contact.name = body.name
    contact.surname = body.surname
    contact.email = body.email
    contact.phone = body.phone
    contact.birthday = body.birthday
    contact.additional_info = body.additional_info
    db.commit()
    return contact


@router.delete('/{contact_id}', status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(allowed_operation_get), Depends(RateLimiter(times=2, seconds=5))])
async def delete_contact(contact_id: int = Path(ge=1), db: Session = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    """
    The delete_contact function deletes a contact from the database.
        The function takes in an integer representing the id of the contact to be deleted,
        and returns a dictionary containing information about that contact.

    :param contact_id: int: Get the contact id from the path
    :param db: Session: Get the database session
    :param user: User: Get the current user
    :return: The deleted contact
    :doc-author: Trelent
    """
    contact = await repository_contacts.delete_contact(user, contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    db.delete(contact)
    db.commit()
    return contact
