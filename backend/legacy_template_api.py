from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Database file để lưu templates
TEMPLATES_DB = 'templates.json'

def load_templates():
    """Load templates từ file"""
    if os.path.exists(TEMPLATES_DB):
        with open(TEMPLATES_DB, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_templates(templates):
    """Save templates vào file"""
    with open(TEMPLATES_DB, 'w', encoding='utf-8') as f:
        json.dump(templates, f, ensure_ascii=False, indent=2)

@app.route('/api/templates', methods=['GET'])
def get_templates():
    """Lấy danh sách tất cả templates"""
    try:
        templates = load_templates()
        return jsonify({
            "success": True,
            "templates": templates,
            "count": len(templates)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/templates', methods=['POST'])
def create_template():
    """Tạo template mới"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['id', 'name', 'wordContent']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "error": f"Missing required field: {field}"
                }), 400
        
        # Load existing templates
        templates = load_templates()
        
        # Create new template
        new_template = {
            "id": data['id'],
            "name": data['name'],
            "description": data.get('description', ''),
            "wordContent": data['wordContent'],
            "ocrFields": data.get('ocrFields', []),
            "createdAt": data.get('createdAt', datetime.now().isoformat()),
            "isOcrReady": data.get('isOcrReady', True),
            "usageCount": 0,
            "lastUsed": None
        }
        
        # Add to templates list
        templates.append(new_template)
        
        # Save to file
        save_templates(templates)
        
        return jsonify({
            "success": True,
            "template": new_template,
            "message": f"Template '{new_template['name']}' đã được lưu thành công!"
        }), 201
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/templates/<template_id>', methods=['GET'])
def get_template(template_id):
    """Lấy template theo ID"""
    try:
        templates = load_templates()
        template = next((t for t in templates if t['id'] == template_id), None)
        
        if not template:
            return jsonify({
                "success": False,
                "error": "Template không tồn tại"
            }), 404
        
        return jsonify({
            "success": True,
            "template": template
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/templates/<template_id>', methods=['DELETE'])
def delete_template(template_id):
    """Xóa template"""
    try:
        templates = load_templates()
        template = next((t for t in templates if t['id'] == template_id), None)
        
        if not template:
            return jsonify({
                "success": False,
                "error": "Template không tồn tại"
            }), 404
        
        # Remove template
        templates = [t for t in templates if t['id'] != template_id]
        save_templates(templates)
        
        return jsonify({
            "success": True,
            "message": f"Template '{template['name']}' đã được xóa"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/templates/<template_id>/use', methods=['POST'])
def use_template(template_id):
    """Đánh dấu template được sử dụng (cho OCR)"""
    try:
        templates = load_templates()
        template_index = next((i for i, t in enumerate(templates) if t['id'] == template_id), None)
        
        if template_index is None:
            return jsonify({
                "success": False,
                "error": "Template không tồn tại"
            }), 404
        
        # Update usage statistics
        templates[template_index]['usageCount'] = templates[template_index].get('usageCount', 0) + 1
        templates[template_index]['lastUsed'] = datetime.now().isoformat()
        
        save_templates(templates)
        
        return jsonify({
            "success": True,
            "template": templates[template_index],
            "message": "Template usage recorded"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/templates/ocr-ready', methods=['GET'])
def get_ocr_ready_templates():
    """Lấy các templates sẵn sàng cho OCR"""
    try:
        templates = load_templates()
        ocr_ready = [t for t in templates if t.get('isOcrReady', False)]
        
        return jsonify({
            "success": True,
            "templates": ocr_ready,
            "count": len(ocr_ready)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/templates/search', methods=['GET'])
def search_templates():
    """Tìm kiếm templates"""
    try:
        query = request.args.get('q', '').lower()
        templates = load_templates()
        
        if not query:
            return jsonify({
                "success": True,
                "templates": templates,
                "count": len(templates)
            })
        
        # Search in name and description
        filtered_templates = [
            t for t in templates 
            if query in t['name'].lower() or query in t.get('description', '').lower()
        ]
        
        return jsonify({
            "success": True,
            "templates": filtered_templates,
            "count": len(filtered_templates),
            "query": query
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "template-api",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 Starting Template API Server...")
    print("📊 Templates will be stored in:", TEMPLATES_DB)
    print("🔗 API URL: http://localhost:3001")
    
    app.run(
        host='0.0.0.0',
        port=3001,
        debug=True
    )