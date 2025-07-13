from datetime import datetime
from bson import ObjectId
from typing import List, Dict, Optional

class StudyGroup:
    def __init__(self, group_data):
        self.id = group_data['_id']
        self.name = group_data['name']
        self.description = group_data['description']
        self.subject = group_data['subject']
        self.topic = group_data['topic']
        self.created_by = group_data['created_by']
        self.members = group_data.get('members', [])
        self.max_members = group_data.get('max_members', 10)
        self.is_public = group_data.get('is_public', True)
        self.created_at = group_data['created_at']
        self.last_activity = group_data.get('last_activity', datetime.utcnow())
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'subject': self.subject,
            'topic': self.topic,
            'created_by': self.created_by,
            'members': self.members,
            'max_members': self.max_members,
            'is_public': self.is_public,
            'created_at': self.created_at,
            'last_activity': self.last_activity
        }

class GroupMessage:
    def __init__(self, message_data):
        self.id = message_data['_id']
        self.group_id = message_data['group_id']
        self.user_id = message_data['user_id']
        self.content = message_data['content']
        self.message_type = message_data.get('message_type', 'text')  # text, question, resource
        self.created_at = message_data['created_at']
        self.user_name = message_data.get('user_name', '')
    
    def to_dict(self):
        return {
            'id': self.id,
            'group_id': self.group_id,
            'user_id': self.user_id,
            'content': self.content,
            'message_type': self.message_type,
            'created_at': self.created_at,
            'user_name': self.user_name
        }

class GroupResource:
    def __init__(self, resource_data):
        self.id = resource_data['_id']
        self.group_id = resource_data['group_id']
        self.title = resource_data['title']
        self.description = resource_data.get('description', '')
        self.url = resource_data.get('url', '')
        self.file_type = resource_data.get('file_type', 'link')
        self.uploaded_by = resource_data['uploaded_by']
        self.created_at = resource_data['created_at']
    
    def to_dict(self):
        return {
            'id': self.id,
            'group_id': self.group_id,
            'title': self.title,
            'description': self.description,
            'url': self.url,
            'file_type': self.file_type,
            'uploaded_by': self.uploaded_by,
            'created_at': self.created_at
        } 