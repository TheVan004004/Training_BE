import uuid

from sanic import Blueprint
from sanic.response import json
from app.constants.cache_constants import CacheConstants
from app.databases.mongodb import MongoDB, logger
from app.databases.redis_cached import get_cache, set_cache, delete_cache
from app.decorators.auth import protected, check_owner
from app.decorators.json_validator import validate_with_jsonschema
from app.hooks.error import ApiInternalError, ApiNotFound
from app.models.book import create_book_json_schema, Book, update_book_json_schema

books_bp = Blueprint('books_blueprint', url_prefix='/books')

_db = MongoDB()

async def get_book_owner(request, book_id, **kwargs):
    book = _db.get_book_by_id(book_id)
    if not book:
        raise ApiNotFound('Fail to find book')
    return book.owner if book else None

@books_bp.route('/')
@books_bp.route('/', methods={'GET'})
async def get_all_books(request):
    async with request.app.ctx.redis as r:
        cached_books = await get_cache(r, CacheConstants.all_books)

        if cached_books is not None:
            books = cached_books
        else:
            book_objs = _db.get_books()
            books = [book.to_dict() for book in book_objs]
            await set_cache(r, CacheConstants.all_books, books)

    return json({
        'n_books': len(books),
        'books': books
    })


@books_bp.route('/', methods={'POST'})
@protected  # TODO: Authenticate
@validate_with_jsonschema(create_book_json_schema)  # To validate request body
async def create_book(request, username):
    body = request.json

    book_id = str(uuid.uuid4())
    book = Book(book_id).from_dict(body)
    book.owner = username

    # # TODO: Save book to database
    inserted = _db.add_book(book)
    if not inserted:
        raise ApiInternalError('Fail to create book')

    # TODO: Update cache
    async with request.app.ctx.redis as r:
        await delete_cache(r, CacheConstants.all_books)

    return json({'status': 'success'})


# TODO: write api get, update, delete book
@books_bp.route('/<book_id>', methods=['GET'])
def get_book_by_id(request, book_id: str):
    try:
        doc = _db.get_book_by_id(book_id)
        if doc:
            return Book(book_id).from_dict(doc)
    except Exception as ex:
        raise ApiInternalError(str(ex))

@books_bp.route('/<book_id>', methods=['PUT'])
@protected
@check_owner(get_book_owner)
@validate_with_jsonschema(update_book_json_schema)
async def update_book(request, book_id: str):
    update_data = request.json

    try:
        result = _db.update_book(
            book_id,
            update_data
        )

        if not result:
            raise ApiNotFound('Fail to find book')

        # TODO: Update cache
        async with request.app.ctx.redis as r:
            await delete_cache(r, CacheConstants.all_books)

        return json({"status": "updated"}, status=200)

    except Exception as ex:
        raise ApiInternalError(str(ex))

@books_bp.route('/<book_id>', methods=['DELETE'])
@protected
@check_owner(get_book_owner)
async def delete_book(request, book_id: str, **kwargs):
    try:
        result = _db.delete_book(book_id)

        if not result:
            raise ApiNotFound('Fail to find book')

        # TODO: Update cache
        async with request.app.ctx.redis as r:
            await delete_cache(r, CacheConstants.all_books)

        return json({"status": "deleted"}, status=200)

    except Exception as ex:
        raise ApiInternalError(str(ex))