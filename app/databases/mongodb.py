from pymongo import MongoClient
from bson import ObjectId
from app.constants.mongodb_constants import MongoCollections
from app.models.book import Book
from app.models.user import User
from app.utils.logger_utils import get_logger
from config import MongoDBConfig

logger = get_logger('MongoDB')

class MongoDB:
    def __init__(self, connection_url=None):
        if connection_url is None:
            connection_url = f'mongodb://{MongoDBConfig.USERNAME}:{MongoDBConfig.PASSWORD}@{MongoDBConfig.HOST}:{MongoDBConfig.PORT}'

        self.connection_url = connection_url.split('@')[-1]
        self.client = MongoClient(connection_url)
        self.db = self.client[MongoDBConfig.DATABASE]
        self._books_col = self.db[MongoCollections.books]
        self._users_col = self.db[MongoCollections.users]

    def get_books(self, filter_=None, projection=None):
        try:
            filter_ = filter_ or {}
            cursor = self._books_col.find(filter_, projection=projection)
            data = []
            for doc in cursor:
                data.append(Book().from_dict(doc))
            return data
        except Exception as ex:
            logger.exception(ex)
        return []

    def get_book_by_id(self, book_id: str):
        try:
            doc = self._books_col.find_one({"_id": book_id})
            if doc:
                return Book().from_dict(doc)
        except Exception as ex:
            logger.exception(ex)
        return None

    def add_book(self, book: Book):
        try:
            result = self._books_col.insert_one(book.to_dict())
            return str(result.inserted_id)
        except Exception as ex:
            logger.exception(ex)
        return None

    def update_book(self, book_id: str, update_data: dict):
        try:
            result = self._books_col.update_one(
                {"_id": book_id},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as ex:
            logger.exception(ex)
        return False

    def delete_book(self, book_id: str):
        try:
            result = self._books_col.delete_one({"_id": book_id})
            return result.deleted_count > 0
        except Exception as ex:
            logger.exception(ex)
        return False

    def get_user_by_username(self, username: str):
        try:
            return self._users_col.find_one({"username": username})
        except Exception as ex:
            logger.exception(ex)
        return None

    def add_user(self, user: User):
        try:
            result = self._users_col.insert_one(user.to_dict())
            return str(result.inserted_id)
        except Exception as ex:
            logger.exception(ex)
        return None

    def get_user_by_id(self, user_id: str):
        try:
            doc = self._users_col.find_one({"_id": user_id})
            if doc:
                return User(user_id).from_dict(doc)
        except Exception as ex:
            logger.exception(ex)
        return None