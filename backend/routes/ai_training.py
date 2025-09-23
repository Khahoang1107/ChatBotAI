from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, jwt_required
from marshmallow import Schema, fields, ValidationError
from services.training_service import TrainingDataService
import logging

logger = logging.getLogger(__name__)

ai_training_bp = Blueprint('ai_training', __name__)

# Validation schemas
class TrainingQuerySchema(Schema):
    template_type = fields.Str(validate=lambda x: x in ['word', 'pdf', 'excel', 'html', 'xml'])
    limit = fields.Int(missing=100, validate=lambda x: 1 <= x <= 1000)
    include_patterns = fields.Bool(missing=True)
    include_statistics = fields.Bool(missing=False)

class FieldSearchSchema(Schema):
    field_names = fields.List(fields.Str(), required=True)
    limit = fields.Int(missing=50, validate=lambda x: 1 <= x <= 500)

class ValidationSchema(Schema):
    training_id = fields.Str(required=True)
    is_valid = fields.Bool(required=True)
    score = fields.Float(validate=lambda x: 0 <= x <= 1.0)
    feedback = fields.Str()

@ai_training_bp.route('/training-data', methods=['GET'])
def get_training_data():
    """
    API cho chatbot để lấy training data
    Không cần authentication để chatbot có thể truy cập dễ dàng
    """
    try:
        # Parse query parameters
        template_type = request.args.get('template_type')
        limit = int(request.args.get('limit', 100))
        include_patterns = request.args.get('include_patterns', 'true').lower() == 'true'
        include_statistics = request.args.get('include_statistics', 'false').lower() == 'true'
        
        # Validate parameters
        if template_type and template_type not in ['word', 'pdf', 'excel', 'html', 'xml']:
            return jsonify({'error': 'Invalid template_type'}), 400
        
        if not (1 <= limit <= 1000):
            return jsonify({'error': 'Limit must be between 1 and 1000'}), 400
        
        training_service = TrainingDataService()
        
        # Lấy training data
        result = training_service.get_training_data_for_chatbot(
            template_type=template_type,
            limit=limit
        )
        
        if 'error' in result:
            return jsonify(result), 500
        
        response_data = {
            'success': True,
            'data': result['data'],
            'total_records': result['total_records'],
            'generated_at': result['generated_at'],
            'query_params': {
                'template_type': template_type,
                'limit': limit,
                'include_patterns': include_patterns
            }
        }
        
        # Thêm thống kê nếu được yêu cầu
        if include_statistics:
            stats = training_service.get_training_statistics()
            response_data['statistics'] = stats
        
        # Loại bỏ patterns nếu không cần thiết để giảm kích thước response
        if not include_patterns and 'field_patterns' in response_data['data']:
            del response_data['data']['field_patterns']
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Lỗi khi lấy training data cho chatbot: {str(e)}")
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500

@ai_training_bp.route('/search-similar', methods=['POST'])
def search_similar_templates():
    """
    API để tìm các template tương tự dựa trên field names
    """
    schema = FieldSearchSchema()
    
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'messages': err.messages}), 400
    
    try:
        training_service = TrainingDataService()
        
        similar_templates = training_service.search_similar_templates(
            field_names=data['field_names']
        )
        
        # Limit results
        limited_results = similar_templates[:data['limit']]
        
        return jsonify({
            'success': True,
            'query': {
                'field_names': data['field_names'],
                'limit': data['limit']
            },
            'results': limited_results,
            'total_found': len(similar_templates),
            'returned': len(limited_results)
        })
        
    except Exception as e:
        logger.error(f"Lỗi khi tìm template tương tự: {str(e)}")
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500

@ai_training_bp.route('/statistics', methods=['GET'])
def get_training_statistics():
    """
    API để lấy thống kê tổng quan về training data
    """
    try:
        training_service = TrainingDataService()
        stats = training_service.get_training_statistics()
        
        if 'error' in stats:
            return jsonify(stats), 500
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
        
    except Exception as e:
        logger.error(f"Lỗi khi lấy thống kê training data: {str(e)}")
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500

@ai_training_bp.route('/validate', methods=['POST'])
@jwt_required()
def validate_training_data():
    """
    API để admin/user validate và chấm điểm training data
    """
    current_user_id = get_jwt_identity()
    schema = ValidationSchema()
    
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'messages': err.messages}), 400
    
    try:
        training_service = TrainingDataService()
        
        success = training_service.validate_and_score_training_data(
            training_id=data['training_id'],
            is_valid=data['is_valid'],
            score=data.get('score')
        )
        
        if success:
            logger.info(f"User {current_user_id} đã validate training data {data['training_id']}")
            return jsonify({
                'success': True,
                'message': 'Training data đã được validate thành công'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Không thể validate training data'
            }), 500
        
    except Exception as e:
        logger.error(f"Lỗi khi validate training data: {str(e)}")
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500

@ai_training_bp.route('/field-patterns', methods=['GET'])
def get_field_patterns():
    """
    API chuyên biệt để lấy field patterns cho việc training AI
    """
    try:
        template_type = request.args.get('template_type')
        field_name = request.args.get('field_name')
        
        training_service = TrainingDataService()
        
        if template_type:
            # Lấy patterns theo loại template
            result = training_service.get_training_data_for_chatbot(
                template_type=template_type,
                limit=1000  # Lấy nhiều để có đủ patterns
            )
            
            if 'error' in result:
                return jsonify(result), 500
            
            patterns = result['data'].get('field_patterns', {})
            
            if field_name:
                # Lọc theo field name cụ thể
                patterns = {field_name: patterns.get(field_name, [])}
            
        else:
            # Lấy tất cả patterns
            if not training_service.training_data:
                return jsonify({'error': 'MongoDB chưa được kết nối'}), 500
            
            all_patterns = training_service.training_data.get_all_field_patterns()
            patterns = all_patterns
        
        return jsonify({
            'success': True,
            'patterns': patterns,
            'query_params': {
                'template_type': template_type,
                'field_name': field_name
            }
        })
        
    except Exception as e:
        logger.error(f"Lỗi khi lấy field patterns: {str(e)}")
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500

@ai_training_bp.route('/health', methods=['GET'])
def health_check():
    """
    API để kiểm tra tình trạng kết nối MongoDB và service
    """
    try:
        training_service = TrainingDataService()
        
        if training_service.training_data is None:
            return jsonify({
                'status': 'unhealthy',
                'mongodb_connected': False,
                'error': 'MongoDB connection failed'
            }), 503
        
        # Test connection bằng cách lấy thống kê
        stats = training_service.get_training_statistics()
        
        if 'error' in stats:
            return jsonify({
                'status': 'unhealthy',
                'mongodb_connected': False,
                'error': stats['error']
            }), 503
        
        return jsonify({
            'status': 'healthy',
            'mongodb_connected': True,
            'total_records': stats.get('total_records', 0),
            'last_check': stats.get('generated_at')
        })
        
    except Exception as e:
        logger.error(f"Lỗi khi kiểm tra health: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'mongodb_connected': False,
            'error': str(e)
        }), 503

# Error handlers cho blueprint này
@ai_training_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@ai_training_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': 'Method not allowed'}), 405

@ai_training_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500