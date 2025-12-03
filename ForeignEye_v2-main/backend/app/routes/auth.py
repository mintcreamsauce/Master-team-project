"""
인증 API 라우트 (JWT 기반)

회원가입, 로그인, 토큰 갱신, 사용자 정보 조회 API
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity
)

from app.utils.response import success_response, error_response
from app.utils.exceptions import ValidationError, DuplicateEntryError, UnauthorizedError
from app.utils.validators import validate_username, validate_email_address, validate_password
from app.extensions import limiter
from app.services.auth_service import AuthService
from app.models.user import User

bp = Blueprint('auth', __name__)


@bp.route('/register', methods=['POST'])
@limiter.limit("3 per hour")
def register():
    """
    회원가입 API (JWT)
    
    POST /api/v1/auth/register
    응답: access_token, refresh_token, user
    """
    try:
        data = request.get_json()
        
        # 입력 검증
        username = validate_username(data.get('username'))
        email = validate_email_address(data.get('email'))
        password = validate_password(data.get('password'))
        password_confirm = data.get('password_confirm')
        
        if password != password_confirm:
            raise ValidationError('비밀번호가 일치하지 않습니다.', 'password_confirm')
        
        # 서비스 호출
        user = AuthService.register_user(username, email, password)
        
        # JWT 토큰 생성 (identity는 문자열이어야 함)
        access_token = create_access_token(identity=str(user.user_id))
        refresh_token = create_refresh_token(identity=str(user.user_id))
        
        return success_response({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict(),
            'message': '회원가입이 완료되었습니다.'
        }, status=201)
        
    except (ValidationError, DuplicateEntryError) as e:
        raise
    except Exception as e:
        return error_response('INTERNAL_ERROR', str(e), 500)


@bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    """
    로그인 API (JWT)
    
    POST /api/v1/auth/login
    응답: access_token, refresh_token, user
    """
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            raise ValidationError('사용자명과 비밀번호를 입력해주세요.')
        
        # 서비스 호출
        user = AuthService.authenticate(username, password)
        
        # JWT 토큰 생성 (identity는 문자열이어야 함)
        access_token = create_access_token(identity=str(user.user_id))
        refresh_token = create_refresh_token(identity=str(user.user_id))
        
        return success_response({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict(),
            'message': '로그인되었습니다.'
        })
        
    except (ValidationError, UnauthorizedError) as e:
        raise
    except Exception as e:
        return error_response('INTERNAL_ERROR', str(e), 500)


@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    로그아웃 API (JWT)
    
    POST /api/v1/auth/logout
    JWT는 stateless이므로 클라이언트에서 토큰 삭제
    """
    # JWT는 서버 측에서 할 일이 없음 (클라이언트가 토큰 삭제)
    return success_response({'message': '로그아웃되었습니다.'})


@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    현재 사용자 정보 조회 API (JWT)
    
    GET /api/v1/auth/me
    Authorization: Bearer <access_token>
    """
    user_id = get_jwt_identity()  # 문자열로 받음
    user = User.query.get(int(user_id))  # DB 조회를 위해 정수로 변환
    
    if not user:
        raise UnauthorizedError('사용자를 찾을 수 없습니다.')
    
    user_data = user.to_dict()
    
    # 통계 추가
    stats = AuthService.get_user_stats(int(user_id))
    user_data['stats'] = stats
    
    return success_response({'user': user_data})


@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    토큰 갱신 API
    
    POST /api/v1/auth/refresh
    Authorization: Bearer <refresh_token>
    """
    user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=user_id)
    
    return success_response({
        'access_token': new_access_token,
        'message': '토큰이 갱신되었습니다.'
    })

