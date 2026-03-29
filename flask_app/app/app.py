"""Flask Benchmark Application - Main entry point"""

from flask import Flask, request, jsonify
from datetime import datetime
import time
import logging

from .config import Config
from .database import db
from .models import Item
from .schemas import ItemCreateSchema, ItemUpdateSchema, ItemResponseSchema

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

item_create_schema = ItemCreateSchema()
item_update_schema = ItemUpdateSchema()
item_response_schema = ItemResponseSchema()
items_response_schema = ItemResponseSchema(many=True)



# ============= API Endpoints =============

@app.route('/api/items/', methods=['GET'])
def list_items():
    """List all items with pagination"""
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        category = request.args.get('category')
        in_stock = request.args.get('in_stock')
        
        query = Item.query
        if category:
            query = query.filter_by(category=category)
        if in_stock is not None:
            query = query.filter_by(in_stock=in_stock.lower() == 'true')
        
        items = query.offset(skip).limit(limit).all()
        return jsonify(items_response_schema.dump(items)), 200
        
    except Exception as e:
        logger.error(f"Error listing items: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/items/', methods=['POST'])
def create_item():
    """Create a new item"""
    try:
        data = request.get_json()
        
        errors = item_create_schema.validate(data)
        if errors:
            return jsonify({'errors': errors}), 400
        
        item = Item(
            name=data['name'],
            description=data.get('description'),
            price=data['price'],
            in_stock=data.get('in_stock', True),
            category=data.get('category')
        )
        
        db.session.add(item)
        db.session.commit()
        
        logger.info(f"Created item with id={item.id}")
        return jsonify(item_response_schema.dump(item)), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating item: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    """Get item by ID"""
    try:
        item = Item.query.get(item_id)
        if not item:
            return jsonify({'error': 'Item not found'}), 404
        
        return jsonify(item_response_schema.dump(item)), 200
        
    except Exception as e:
        logger.error(f"Error getting item {item_id}: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    """Update an existing item"""
    try:
        item = Item.query.get(item_id)
        if not item:
            return jsonify({'error': 'Item not found'}), 404
        
        data = request.get_json()
        
        errors = item_update_schema.validate(data)
        if errors:
            return jsonify({'errors': errors}), 400
        
        if 'name' in data:
            item.name = data['name']
        if 'description' in data:
            item.description = data['description']
        if 'price' in data:
            item.price = data['price']
        if 'in_stock' in data:
            item.in_stock = data['in_stock']
        if 'category' in data:
            item.category = data['category']
        
        item.updated_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"Updated item with id={item_id}")
        return jsonify(item_response_schema.dump(item)), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating item {item_id}: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    """Delete an item"""
    try:
        item = Item.query.get(item_id)
        if not item:
            return jsonify({'error': 'Item not found'}), 404
        
        db.session.delete(item)
        db.session.commit()
        
        logger.info(f"Deleted item with id={item_id}")
        return '', 204
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting item {item_id}: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# ============= Test Endpoints =============

@app.route('/api/slow', methods=['GET'])
def slow_endpoint():
    """Endpoint with artificial delay for I/O testing (blocking!)"""
    time.sleep(0.1)
    return jsonify({"status": "ok", "delay_ms": 100})


# ============= System Endpoints =============

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'framework': 'Flask',
        'version': '2.0.0',
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Simple metrics endpoint"""
    return jsonify({
        'framework': 'Flask',
        'version': '2.0.0',
        'status': 'operational'
    })

with app.app_context():
    db.create_all()
    logger.info("Database tables created")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)