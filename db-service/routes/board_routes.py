from flask import Blueprint, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from marshmallow import ValidationError
from models import Board, Thread
from schemas import BoardSchema
from common.db_utils import get_tenant_db_url
from common.error_handlers import get_dynamic_logger

board_bp = Blueprint('board', __name__)
board_schema = BoardSchema()

def get_db_session(tenant_id):
    """Get a session for the tenant's specific database."""
    db_url = get_tenant_db_url(tenant_id)
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    return Session()

# ------------------------ CRUD Operations ------------------------

@board_bp.route('/', methods=['POST'])
def create_board():
    """Create a new board for a tenant with Marshmallow validation."""
    logger = get_dynamic_logger()
    tenant_id = request.headers.get('X-Tenant-ID')
    try:
        data = board_schema.load(request.get_json())
    except ValidationError as err:
        logger.warning(f"Validation Error: {err.messages}")  # Log validation error
        return jsonify({"error": err.messages}), 400

    db_session = get_db_session(tenant_id)
    board = Board(name=data['name'], description=data.get('description'))
    db_session.add(board)
    db_session.commit()
    logger.info(f"Board created: {board.name}, ID: {board.id}")  # Log creation
    return jsonify({"message": "Board created successfully", "board_id": board.id}), 201

@board_bp.route('/', methods=['GET'])
def get_all_boards():
    """Retrieve all boards for a tenant with optional pagination and search."""
    logger = get_dynamic_logger()
    tenant_id = request.headers.get('X-Tenant-ID')
    db_session = get_db_session(tenant_id)

    search = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))

    query = db_session.query(Board)
    if search:
        query = query.filter(Board.name.ilike(f"%{search}%"))

    total = query.count()
    boards = query.offset((page - 1) * per_page).limit(per_page).all()

    response = {
        "total": total,
        "page": page,
        "per_page": per_page,
        "boards": []
    }

    for board in boards:
        threads = db_session.query(Thread).filter_by(board_id=board.id).all()
        response["boards"].append({
            "id": board.id,
            "name": board.name,
            "description": board.description,
            "threads": [{"id": thread.id, "title": thread.title} for thread in threads]
        })

    logger.info(f"Retrieved {len(boards)} boards for tenant {tenant_id}")  # Log the number of boards fetched
    return jsonify(response), 200

@board_bp.route('/<int:board_id>', methods=['GET'])
def get_board(board_id):
    """Retrieve a single board by its ID, including its threads."""
    logger = get_dynamic_logger()
    tenant_id = request.headers.get('X-Tenant-ID')
    db_session = get_db_session(tenant_id)

    board = db_session.query(Board).get(board_id)
    if board is None:
        logger.warning(f"Board not found: ID {board_id}, Tenant: {tenant_id}")  # Log if board not found
        return jsonify({"error": "Board not found"}), 404

    threads = db_session.query(Thread).filter_by(board_id=board.id).all()
    logger.info(f"Retrieved board: {board.name}, ID: {board.id}")  # Log board retrieval
    return jsonify({
        "id": board.id,
        "name": board.name,
        "description": board.description,
        "threads": [{"id": thread.id, "title": thread.title} for thread in threads]
    }), 200

@board_bp.route('/<int:board_id>', methods=['PUT'])
def update_board(board_id):
    """Update an existing board by its ID with Marshmallow validation."""
    logger = get_dynamic_logger()
    tenant_id = request.headers.get('X-Tenant-ID')
    try:
        data = board_schema.load(request.get_json(), partial=True)
    except ValidationError as err:
        logger.warning(f"Validation Error: {err.messages}")  # Log validation error
        return jsonify({"error": err.messages}), 400

    db_session = get_db_session(tenant_id)
    board = db_session.query(Board).get(board_id)
    if board is None:
        logger.warning(f"Board not found: ID {board_id}, Tenant: {tenant_id}")  # Log if board not found
        return jsonify({"error": "Board not found"}), 404

    board.name = data.get('name', board.name)
    board.description = data.get('description', board.description)
    db_session.commit()
    logger.info(f"Board updated: {board.name}, ID: {board.id}")  # Log board update
    return jsonify({"message": "Board updated successfully"}), 200

@board_bp.route('/<int:board_id>', methods=['DELETE'])
def delete_board(board_id):
    """Delete a board by its ID."""
    logger = get_dynamic_logger()
    tenant_id = request.headers.get('X-Tenant-ID')
    db_session = get_db_session(tenant_id)

    board = db_session.query(Board).get(board_id)
    if board is None:
        logger.warning(f"Board not found: ID {board_id}, Tenant: {tenant_id}")  # Log if board not found
        return jsonify({"error": "Board not found"}), 404

    db_session.delete(board)
    db_session.commit()
    logger.info(f"Board deleted: ID {board_id}, Tenant: {tenant_id}")  # Log board deletion
    return jsonify({"message": "Board deleted successfully"}), 200
