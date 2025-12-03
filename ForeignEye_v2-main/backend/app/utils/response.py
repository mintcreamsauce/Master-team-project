"""
API 응답 포맷터

일관된 JSON 응답 형식을 제공합니다.
"""

from flask import jsonify
from datetime import datetime


def success_response(data, status=200, meta=None):
    """
    성공 응답 생성
    
    Args:
        data (dict): 응답 데이터
        status (int): HTTP 상태 코드 (기본값: 200)
        meta (dict): 추가 메타데이터 (선택적)
        
    Returns:
        tuple: (JSON 응답, HTTP 상태 코드)
        
    Example:
        >>> success_response({'user': {'id': 1, 'name': 'John'}})
        ({
            "success": True,
            "data": {"user": {"id": 1, "name": "John"}},
            "meta": {"timestamp": "2025-11-11T12:34:56Z", "version": "v1"}
        }, 200)
    """
    response = {
        'success': True,
        'data': data,
        'meta': {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'version': 'v1',
            **(meta or {})
        }
    }
    return jsonify(response), status


def error_response(code, message, status=400, details=None):
    """
    에러 응답 생성
    
    Args:
        code (str): 에러 코드 (예: 'VALIDATION_ERROR', 'NOT_FOUND')
        message (str): 사용자 친화적 에러 메시지
        status (int): HTTP 상태 코드 (기본값: 400)
        details (dict): 상세 정보 (선택적)
        
    Returns:
        tuple: (JSON 응답, HTTP 상태 코드)
        
    Example:
        >>> error_response('VALIDATION_ERROR', '비밀번호가 짧습니다', 400, {'field': 'password'})
        ({
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "비밀번호가 짧습니다",
                "details": {"field": "password"}
            },
            "meta": {"timestamp": "2025-11-11T12:34:56Z", "version": "v1"}
        }, 400)
    """
    response = {
        'success': False,
        'error': {
            'code': code,
            'message': message
        },
        'meta': {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'version': 'v1'
        }
    }
    
    if details:
        response['error']['details'] = details
    
    return jsonify(response), status


def paginated_response(items, page, total_items, items_per_page, meta=None):
    """
    페이지네이션 응답 생성
    
    Args:
        items (list): 현재 페이지 항목 리스트
        page (int): 현재 페이지 번호 (1부터 시작)
        total_items (int): 전체 항목 수
        items_per_page (int): 페이지당 항목 수
        meta (dict): 추가 메타데이터 (선택적)
        
    Returns:
        tuple: (JSON 응답, HTTP 상태 코드)
        
    Example:
        >>> paginated_response([{'id': 1}, {'id': 2}], 1, 20, 10)
        ({
            "success": True,
            "data": {
                "items": [{"id": 1}, {"id": 2}],
                "pagination": {
                    "current_page": 1,
                    "total_pages": 2,
                    "total_items": 20,
                    "items_per_page": 10,
                    "has_next": True,
                    "has_prev": False
                }
            },
            "meta": {"timestamp": "...", "version": "v1"}
        }, 200)
    """
    total_pages = (total_items + items_per_page - 1) // items_per_page
    
    data = {
        'items': items,
        'pagination': {
            'current_page': page,
            'total_pages': total_pages,
            'total_items': total_items,
            'items_per_page': items_per_page,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
    }
    
    return success_response(data, meta=meta)

