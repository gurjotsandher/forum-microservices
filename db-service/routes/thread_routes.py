from flask import Blueprint, request, jsonify
from models import Thread, Board
from schemas import ThreadSchema
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from common.db_utils import get_tenant_db_url
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
import logging

thread_bp = Blueprint('thread', __name__)
thread_schema = ThreadSchema()

def get_db_session(tenant_id):
    """Get a session for the tenant's specific database."""
    db_url = get_tenant_db_url(tenant_id)
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    return Session()

# ------------------------ CRUD Operations ------------------------

@thread_bp.route('/', methods=['POST'])
def create_thread():
    """Create a new thread for a tenant's board with Marshmallow validation."""
    tenant_id = request.headers.get('X-Tenant-ID')
    try:
        data = thread_schema.load(request.get_json())  # Automatically validates input
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    db_session = get_db_session(tenant_id)
    board = db_session.query(Board).get(data['board_id'])  # Ensure the board exists
    if not board:
        return jsonify({"error": "Board not found"}), 404

    # Create the thread with title and description
    thread = Thread(title=data['title'], board_id=data['board_id'], description=data['description'])
    db_session.add(thread)
    db_session.commit()

    return jsonify({
        "message": "Thread created successfully",
        "thread_id": thread.id,
        "title": thread.title,
        "description": thread.description
    }), 201


@thread_bp.route('/', methods=['GET'])
def get_all_threads():
    """Retrieve all threads for a tenant with optional pagination and search."""
    tenant_id = request.headers.get('X-Tenant-ID')

    if not tenant_id:
        return jsonify({"error": "Tenant ID is missing"}), 400

    try:
        db_session = get_db_session(tenant_id)

        search = request.args.get('search', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))

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

        return jsonify(response), 200

    except SQLAlchemyError as e:
        # Log the error message
        logging.error(f"Database error occurred: {str(e)}")
        return jsonify({"error": "Database error", "message": str(e)}), 500

    except Exception as e:
        # Log any other unexpected errors
        logging.error(f"Unexpected error occurred: {str(e)}")
        return jsonify({"error": "Internal server error", "message": str(e)}), 500

@thread_bp.route('/<int:thread_id>', methods=['GET'])
def get_thread(thread_id):
    """Retrieve a single thread by its ID."""
    tenant_id = request.headers.get('X-Tenant-ID')
    db_session = get_db_session(tenant_id)

    thread = db_session.query(Thread).get(thread_id)
    if thread is None:
        return jsonify({"error": "Thread not found"}), 404

    return jsonify({
        "id": thread.id,
        "title": thread.title,
        "board_id": thread.board_id,
        "description": thread.description
    }), 200

@thread_bp.route('/<int:thread_id>', methods=['PUT'])
def update_thread(thread_id):
    """Update an existing thread by its ID with Marshmallow validation."""
    tenant_id = request.headers.get('X-Tenant-ID')
    try:
        data = thread_schema.load(request.get_json(), partial=True)
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    db_session = get_db_session(tenant_id)
    thread = db_session.query(Thread).get(thread_id)
    if thread is None:
        return jsonify({"error": "Thread not found"}), 404

    thread.title = data.get('title', thread.title)
    thread.board_id = data.get('board_id', thread.board_id)
    thread.description = data.get('description', thread.description)
    db_session.commit()

    return jsonify({"message": "Thread updated successfully"}), 200

@thread_bp.route('/<int:thread_id>', methods=['DELETE'])
def delete_thread(thread_id):
    """Delete a thread by its ID."""
    tenant_id = request.headers.get('X-Tenant-ID')
    db_session = get_db_session(tenant_id)

    thread = db_session.query(Thread).get(thread_id)
    if thread is None:
        return jsonify({"error": "Thread not found"}), 404

    db_session.delete(thread)
    db_session.commit()
    return jsonify({"message": "Thread deleted successfully"}), 200
