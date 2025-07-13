from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from bson import ObjectId
import os

study_groups_bp = Blueprint('study_groups', __name__)

# MongoDB collections - will be set up in main app
study_groups_collection = None
group_messages_collection = None
group_resources_collection = None

def init_collections(db_instance):
    global study_groups_collection, group_messages_collection, group_resources_collection
    study_groups_collection = db_instance.study_groups
    group_messages_collection = db_instance.group_messages
    group_resources_collection = db_instance.group_resources

@study_groups_bp.route('/api/groups', methods=['GET'])
@jwt_required()
def get_study_groups():
    """Get all available study groups"""
    try:
        user_id = get_jwt_identity()
        
        # Get public groups and groups user is member of
        groups = list(study_groups_collection.find({
            '$or': [
                {'is_public': True},
                {'members': user_id}
            ]
        }).sort('last_activity', -1))
        
        # Convert ObjectId to string
        for group in groups:
            group['_id'] = str(group['_id'])
            group['created_at'] = group['created_at'].isoformat()
            group['last_activity'] = group['last_activity'].isoformat()
        
        return jsonify({'groups': groups}), 200
        
    except Exception as e:
        return jsonify({'error': f'Error retrieving groups: {str(e)}'}), 500

@study_groups_bp.route('/api/groups', methods=['POST'])
@jwt_required()
def create_study_group():
    """Create a new study group"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        name = data.get('name')
        description = data.get('description')
        subject = data.get('subject')
        topic = data.get('topic')
        max_members = data.get('max_members', 10)
        is_public = data.get('is_public', True)
        
        if not all([name, description, subject, topic]):
            return jsonify({'error': 'Name, description, subject, and topic are required'}), 400
        
        group_data = {
            'name': name,
            'description': description,
            'subject': subject,
            'topic': topic,
            'created_by': user_id,
            'members': [user_id],  # Creator is automatically a member
            'max_members': max_members,
            'is_public': is_public,
            'created_at': datetime.utcnow(),
            'last_activity': datetime.utcnow()
        }
        
        result = study_groups_collection.insert_one(group_data)
        group_data['_id'] = result.inserted_id
        
        return jsonify({
            'success': True,
            'group': {
                'id': str(result.inserted_id),
                'name': name,
                'description': description,
                'subject': subject,
                'topic': topic
            }
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Error creating group: {str(e)}'}), 500

@study_groups_bp.route('/api/groups/<group_id>/join', methods=['POST'])
@jwt_required()
def join_study_group(group_id):
    """Join a study group"""
    try:
        user_id = get_jwt_identity()
        
        group = study_groups_collection.find_one({'_id': ObjectId(group_id)})
        if not group:
            return jsonify({'error': 'Group not found'}), 404
        
        if user_id in group['members']:
            return jsonify({'error': 'You are already a member of this group'}), 400
        
        if len(group['members']) >= group['max_members']:
            return jsonify({'error': 'Group is full'}), 400
        
        study_groups_collection.update_one(
            {'_id': ObjectId(group_id)},
            {
                '$push': {'members': user_id},
                '$set': {'last_activity': datetime.utcnow()}
            }
        )
        
        return jsonify({'success': True, 'message': 'Successfully joined group'}), 200
        
    except Exception as e:
        return jsonify({'error': f'Error joining group: {str(e)}'}), 500

@study_groups_bp.route('/api/groups/<group_id>/leave', methods=['POST'])
@jwt_required()
def leave_study_group(group_id):
    """Leave a study group"""
    try:
        user_id = get_jwt_identity()
        
        group = study_groups_collection.find_one({'_id': ObjectId(group_id)})
        if not group:
            return jsonify({'error': 'Group not found'}), 404
        
        if user_id not in group['members']:
            return jsonify({'error': 'You are not a member of this group'}), 400
        
        if user_id == group['created_by']:
            return jsonify({'error': 'Group creator cannot leave. Transfer ownership or delete the group.'}), 400
        
        study_groups_collection.update_one(
            {'_id': ObjectId(group_id)},
            {
                '$pull': {'members': user_id},
                '$set': {'last_activity': datetime.utcnow()}
            }
        )
        
        return jsonify({'success': True, 'message': 'Successfully left group'}), 200
        
    except Exception as e:
        return jsonify({'error': f'Error leaving group: {str(e)}'}), 500

@study_groups_bp.route('/api/groups/<group_id>/messages', methods=['GET'])
@jwt_required()
def get_group_messages(group_id):
    """Get messages for a study group"""
    try:
        user_id = get_jwt_identity()
        
        # Check if user is member of group
        group = study_groups_collection.find_one({'_id': ObjectId(group_id)})
        if not group:
            return jsonify({'error': 'Group not found'}), 404
        
        if user_id not in group['members']:
            return jsonify({'error': 'You are not a member of this group'}), 403
        
        # Get messages
        messages = list(group_messages_collection.find(
            {'group_id': ObjectId(group_id)}
        ).sort('created_at', 1))
        
        # Convert ObjectId to string
        for message in messages:
            message['_id'] = str(message['_id'])
            message['group_id'] = str(message['group_id'])
            message['created_at'] = message['created_at'].isoformat()
        
        return jsonify({'messages': messages}), 200
        
    except Exception as e:
        return jsonify({'error': f'Error retrieving messages: {str(e)}'}), 500

@study_groups_bp.route('/api/groups/<group_id>/messages', methods=['POST'])
@jwt_required()
def send_group_message(group_id):
    """Send a message to a study group"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        content = data.get('content')
        message_type = data.get('message_type', 'text')
        
        if not content:
            return jsonify({'error': 'Message content is required'}), 400
        
        # Check if user is member of group
        group = study_groups_collection.find_one({'_id': ObjectId(group_id)})
        if not group:
            return jsonify({'error': 'Group not found'}), 404
        
        if user_id not in group['members']:
            return jsonify({'error': 'You are not a member of this group'}), 403
        
        # Get user name
        from app import users_collection
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        user_name = user['full_name'] if user else 'Unknown User'
        
        message_data = {
            'group_id': ObjectId(group_id),
            'user_id': user_id,
            'content': content,
            'message_type': message_type,
            'user_name': user_name,
            'created_at': datetime.utcnow()
        }
        
        result = group_messages_collection.insert_one(message_data)
        
        # Update group last activity
        study_groups_collection.update_one(
            {'_id': ObjectId(group_id)},
            {'$set': {'last_activity': datetime.utcnow()}}
        )
        
        return jsonify({
            'success': True,
            'message': {
                'id': str(result.inserted_id),
                'content': content,
                'user_name': user_name,
                'created_at': message_data['created_at'].isoformat()
            }
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Error sending message: {str(e)}'}), 500

@study_groups_bp.route('/api/groups/<group_id>/resources', methods=['GET'])
@jwt_required()
def get_group_resources(group_id):
    """Get resources for a study group"""
    try:
        user_id = get_jwt_identity()
        
        # Check if user is member of group
        group = study_groups_collection.find_one({'_id': ObjectId(group_id)})
        if not group:
            return jsonify({'error': 'Group not found'}), 404
        
        if user_id not in group['members']:
            return jsonify({'error': 'You are not a member of this group'}), 403
        
        # Get resources
        resources = list(group_resources_collection.find(
            {'group_id': ObjectId(group_id)}
        ).sort('created_at', -1))
        
        # Convert ObjectId to string
        for resource in resources:
            resource['_id'] = str(resource['_id'])
            resource['group_id'] = str(resource['group_id'])
            resource['created_at'] = resource['created_at'].isoformat()
        
        return jsonify({'resources': resources}), 200
        
    except Exception as e:
        return jsonify({'error': f'Error retrieving resources: {str(e)}'}), 500

@study_groups_bp.route('/api/groups/<group_id>/resources', methods=['POST'])
@jwt_required()
def add_group_resource(group_id):
    """Add a resource to a study group"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        title = data.get('title')
        description = data.get('description', '')
        url = data.get('url', '')
        file_type = data.get('file_type', 'link')
        
        if not title:
            return jsonify({'error': 'Resource title is required'}), 400
        
        # Check if user is member of group
        group = study_groups_collection.find_one({'_id': ObjectId(group_id)})
        if not group:
            return jsonify({'error': 'Group not found'}), 404
        
        if user_id not in group['members']:
            return jsonify({'error': 'You are not a member of this group'}), 403
        
        resource_data = {
            'group_id': ObjectId(group_id),
            'title': title,
            'description': description,
            'url': url,
            'file_type': file_type,
            'uploaded_by': user_id,
            'created_at': datetime.utcnow()
        }
        
        result = group_resources_collection.insert_one(resource_data)
        
        return jsonify({
            'success': True,
            'resource': {
                'id': str(result.inserted_id),
                'title': title,
                'description': description,
                'url': url,
                'file_type': file_type
            }
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Error adding resource: {str(e)}'}), 500

@study_groups_bp.route('/api/groups/<group_id>', methods=['GET'])
@jwt_required()
def get_study_group_details(group_id):
    """Get detailed information about a study group"""
    try:
        user_id = get_jwt_identity()
        
        group = study_groups_collection.find_one({'_id': ObjectId(group_id)})
        if not group:
            return jsonify({'error': 'Group not found'}), 404
        
        # Check if user can access this group
        if not group['is_public'] and user_id not in group['members']:
            return jsonify({'error': 'You do not have access to this group'}), 403
        
        # Get member details
        from app import users_collection
        members = []
        for member_id in group['members']:
            user = users_collection.find_one({'_id': ObjectId(member_id)})
            if user:
                members.append({
                    'id': str(user['_id']),
                    'name': user['full_name'],
                    'grade_level': user.get('grade_level', ''),
                    'subjects': user.get('subjects', [])
                })
        
        group['_id'] = str(group['_id'])
        group['created_at'] = group['created_at'].isoformat()
        group['last_activity'] = group['last_activity'].isoformat()
        group['members'] = members
        group['is_member'] = user_id in [m['id'] for m in members]
        
        return jsonify({'group': group}), 200
        
    except Exception as e:
        return jsonify({'error': f'Error retrieving group details: {str(e)}'}), 500
