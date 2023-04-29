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
    print('get_contacts', 12)
    contacts = await repository_contacts.get_contacts(user, limit, offset, db)
    return contacts


@router.get('/search', response_model=List[ContactResponse],
            dependencies=[Depends(allowed_operation_get), Depends(RateLimiter(times=2, seconds=5))])
async def search_contacts(query: Optional[str] = None, db: Session = Depends(get_db),
                          user: User = Depends(auth_service.get_current_user)):
    contacts = await repository_contacts.search_contacts(user, query, db)
    return contacts


@router.get('/birthdays', response_model=List[ContactResponse],
            dependencies=[Depends(allowed_operation_get), Depends(RateLimiter(times=2, seconds=5))])
async def get_birthdays(db: Session = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    contacts = await repository_contacts.get_birthdays(user, db)
    return contacts


@router.get('/{contact_id}', response_model=ContactResponse, name="get contact",
            dependencies=[Depends(allowed_operation_get), Depends(RateLimiter(times=2, seconds=5))])
async def get_contact(contact_id: int = Path(ge=1), db: Session = Depends(get_db),
                      user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.get_contact_by_id(user, contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return contact


@router.post('/', response_model=ContactResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(allowed_operation_create), Depends(RateLimiter(times=2, seconds=5))])
async def create_contact(body: ContactModel, db: Session = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
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
    contact = await repository_contacts.delete_contact(user, contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    db.delete(contact)
    db.commit()
    return contact
