from flask import Blueprint, request, jsonify
from config import Config
from extensions import cache
from models import Thread, Board
from routes import board_bp
from schemas import ThreadSchema
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from common.db_utils import get_tenant_db_url
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from common.error_handlers import get_dynamic_logger
thread_bp = Blueprint('thread', __name__)
thread_schema = ThreadSchema()

def get_db_session(tenant_id):
    """Get a session for the tenant's specific database."""
    db_url = get_tenant_db_url(tenant_id, Config.JWT_SECRET_KEY)
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    return Session()

# ------------------------ CRUD Operations ------------------------

@thread_bp.route('/', methods=['POST'])
def create_thread():
    """Create a new thread for a tenant's board with Marshmallow validation."""
    logger = get_dynamic_logger()  # Initialize the logger here
    tenant_id = request.headers.get('X-Tenant-ID')

    try:
        data = thread_schema.load(request.get_json())  # Automatically validates input
    except ValidationError as err:
        logger.error(f"Validation error: {err.messages}")  # Log validation error
        return jsonify({"error": err.messages}), 400

    db_session = get_db_session(tenant_id)
    board = db_session.query(Board).get(data['board_id'])  # Ensure the board exists
    if not board:
        logger.warning(f"Board with ID {data['board_id']} not found for tenant {tenant_id}.")  # Log board not found
        return jsonify({"error": "Board not found"}), 404

    # Create the thread with title and description
    thread = Thread(title=data['title'], board_id=data['board_id'], description=data['description'])
    db_session.add(thread)
    db_session.commit()

    cache.delete(f"{tenant_id}/{board_bp.name}/{data['board_id']}/threads")
    cache.delete(f"{tenant_id}/{board_bp.name}/list")

    logger.info(f"Thread created: ID {thread.id}, Title: {thread.title} for tenant {tenant_id}.")  # Log thread creation success
    return jsonify({
        "message": "Thread created successfully",
        "thread_id": thread.id,
        "title": thread.title,
        "description": thread.description
    }), 201


@thread_bp.route('/', methods=['GET'])
def get_all_threads():
    """Retrieve all threads for a tenant with optional pagination and search."""
    logger = get_dynamic_logger()  # Initialize the logger here

    tenant_id = request.headers.get('X-Tenant-ID')

    if not tenant_id:
        logger.warning("Tenant ID is missing in the request headers.")
        return jsonify({"error": "Tenant ID is missing"}), 400

    try:
        search = request.args.get('search', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        board_id = str(request.args.get('board_id'))

        cache_key = f"{tenant_id}/{board_bp.name}/{board_id}/threads"
        cached_data = cache.get(cache_key)

        if cached_data:
            logger.info(f"Cache HIT: Returning cached threads for tenant {tenant_id}, board {board_id}")
            return jsonify(cached_data)

        db_session = get_db_session(tenant_id)

        query = db_session.query(Thread)

        if search:
            query = query.filter(Thread.title.ilike(f"%{search}%"))

        total = query.count()
        threads = query.offset((page - 1) * per_page).limit(per_page).all()

        response = {
            "total": total,
            "page": page,
            "per_page": per_page,
            "threads": []
        }

        for thread in threads:
            response["threads"].append({
                "id": thread.id,
                "title": thread.title,
                "board_id": thread.board_id,
                "description": thread.description
            })

        cache.set(cache_key, response, timeout=300)

        logger.info(f"Retrieved {len(threads)} threads for tenant {tenant_id}.")  # Log successful retrieval
        return jsonify(response), 200

    except SQLAlchemyError as e:
        # Log the database error
        logger.error(f"Database error occurred: {str(e)}")
        return jsonify({"error": "Database error", "message": str(e)}), 500

    except Exception as e:
        # Log any other unexpected errors
        logger.error(f"Unexpected error occurred: {str(e)}")
        return jsonify({"error": "Internal server error", "message": str(e)}), 500


@thread_bp.route('/<int:thread_id>', methods=['GET'])
def get_thread(thread_id):
    """Retrieve a single thread by its ID."""
    logger = get_dynamic_logger()  # Initialize the logger here
    tenant_id = request.headers.get('X-Tenant-ID')

    cache_key = f"{tenant_id}/{board_bp.name}/threads/{thread_id}"
    cached_data = cache.get(cache_key)

    if cached_data:
        logger.info(f"Cache HIT: Returning thread {thread_id} from cache")
        return jsonify(cached_data)

    db_session = get_db_session(tenant_id)

    thread = db_session.query(Thread).get(thread_id)
    if thread is None:
        logger.warning(f"Thread with ID {thread_id} not found for tenant {tenant_id}.")  # Log thread not found
        return jsonify({"error": "Thread not found"}), 404

    response = {
        "id": thread.id,
        "title": thread.title,
        "description": thread.description
    }

    cache.set(cache_key, response, timeout=300)

    return jsonify(response), 200


@thread_bp.route('/<int:thread_id>', methods=['PUT'])
def update_thread(thread_id):
    """Update an existing thread by its ID with Marshmallow validation."""
    logger = get_dynamic_logger()  # Initialize the logger here
    tenant_id = request.headers.get('X-Tenant-ID')

    try:
        data = thread_schema.load(request.get_json(), partial=True)
    except ValidationError as err:
        logger.error(f"Validation error: {err.messages}")  # Log validation error
        return jsonify({"error": err.messages}), 400

    db_session = get_db_session(tenant_id)
    thread = db_session.query(Thread).get(thread_id)

    if thread is None:
        logger.warning(f"Thread with ID {thread_id} not found for tenant {tenant_id}.")  # Log thread not found
        return jsonify({"error": "Thread not found"}), 404

    thread.title = data.get('title', thread.title)
    thread.board_id = data.get('board_id', thread.board_id)
    thread.description = data.get('description', thread.description)
    db_session.commit()

    cache.delete(f"{tenant_id}/{board_bp.name}/list")
    cache.delete(f"{tenant_id}/{board_bp.name}/threads/{thread_id}")
    cache.delete(f"{tenant_id}/{board_bp.name}/{thread.board_id}/threads")


    logger.info(f"Thread with ID {thread.id} updated for tenant {tenant_id}.")  # Log successful update
    return jsonify({"message": "Thread updated successfully"}), 200


@thread_bp.route('/<int:thread_id>', methods=['DELETE'])
def delete_thread(thread_id):
    """Delete a thread by its ID."""
    logger = get_dynamic_logger()  # Initialize the logger here

    tenant_id = request.headers.get('X-Tenant-ID')
    db_session = get_db_session(tenant_id)

    thread = db_session.query(Thread).get(thread_id)
    if thread is None:
        logger.warning(f"Thread with ID {thread_id} not found for tenant {tenant_id}.")  # Log thread not found
        return jsonify({"error": "Thread not found"}), 404

    db_session.delete(thread)
    db_session.commit()

    cache.delete(f"{tenant_id}/{board_bp.name}/list")
    cache.delete(f"{tenant_id}/{board_bp.name}/threads/{thread_id}")
    cache.delete(f"{tenant_id}/{board_bp.name}/{thread.board_id}/threads")

    logger.info(f"Thread with ID {thread.id} deleted for tenant {tenant_id}.")  # Log successful deletion
    return jsonify({"message": "Thread deleted successfully"}), 200
