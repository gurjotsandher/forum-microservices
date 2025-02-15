from flask import Blueprint, request, jsonify
from models import Board, Thread
from schemas import BoardSchema
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import Config
from marshmallow import ValidationError
from common.db_utils import get_tenant_db_url

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
    tenant_id = request.headers.get('X-Tenant-ID')
    try:
        data = board_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    db_session = get_db_session(tenant_id)
    board = Board(name=data['name'], description=data.get('description'))
    db_session.add(board)
    db_session.commit()
    return jsonify({"message": "Board created successfully", "board_id": board.id}), 201

@board_bp.route('/', methods=['GET'])
def get_all_boards():
    """Retrieve all boards for a tenant with optional pagination and search."""
    tenant_id = request.headers.get('X-Tenant-ID')
    db_session = get_db_session(tenant_id)
    print('db session retrieved')
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

    return jsonify(response), 200

@board_bp.route('/<int:board_id>', methods=['GET'])
def get_board(board_id):
    """Retrieve a single board by its ID, including its threads."""
    tenant_id = request.headers.get('X-Tenant-ID')
    db_session = get_db_session(tenant_id)

    board = db_session.query(Board).get(board_id)
    if board is None:
        return jsonify({"error": "Board not found"}), 404

    threads = db_session.query(Thread).filter_by(board_id=board.id).all()
    return jsonify({
        "id": board.id,
        "name": board.name,
        "description": board.description,
        "threads": [{"id": thread.id, "title": thread.title} for thread in threads]
    }), 200

@board_bp.route('/<int:board_id>', methods=['PUT'])
def update_board(board_id):
    """Update an existing board by its ID with Marshmallow validation."""
    tenant_id = request.headers.get('X-Tenant-ID')
    try:
        data = board_schema.load(request.get_json(), partial=True)
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    db_session = get_db_session(tenant_id)
    board = db_session.query(Board).get(board_id)
    if board is None:
        return jsonify({"error": "Board not found"}), 404

    board.name = data.get('name', board.name)
    board.description = data.get('description', board.description)
    db_session.commit()

    return jsonify({"message": "Board updated successfully"}), 200

@board_bp.route('/<int:board_id>', methods=['DELETE'])
def delete_board(board_id):
    """Delete a board by its ID."""
    tenant_id = request.headers.get('X-Tenant-ID')
    db_session = get_db_session(tenant_id)

    board = db_session.query(Board).get(board_id)
    if board is None:
        return jsonify({"error": "Board not found"}), 404

    db_session.delete(board)
    db_session.commit()
    return jsonify({"message": "Board deleted successfully"}), 200
