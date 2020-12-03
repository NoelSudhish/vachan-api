''' Place to define all Database CRUD operations'''

from sqlalchemy.orm import Session
import db_models
import schemas

def get_content_types(db_: Session, content_type: str =None, skip: int = 0, limit: int = 100):
    '''Fetched all rows, with pagination'''
    if content_type:
        res = db_.query(db_models.ContentType).filter(
            db_models.ContentType.contentType == content_type).first()
        if res:
            return [res]
        return []
    return db_.query(db_models.ContentType).offset(skip).limit(limit).all()

def create_content_type(db_: Session, content: schemas.ContentTypeCreate):
    '''Adds a row to table'''
    db_content = db_models.ContentType(contentType = content.contentType)
    db_.add(db_content)
    db_.commit()
    db_.refresh(db_content)
    return db_content
