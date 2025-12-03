"""
입력 검증 함수

사용자 입력 데이터의 유효성을 검증합니다.
"""

import re
from email_validator import validate_email, EmailNotValidError
from app.utils.exceptions import ValidationError


def validate_username(username):
    """
    사용자명 검증
    
    규칙:
    - 필수 입력
    - 3자 이상
    - 영문, 숫자, 언더스코어만 허용
    
    Args:
        username (str): 검증할 사용자명
        
    Returns:
        str: 검증된 사용자명 (trim된 상태)
        
    Raises:
        ValidationError: 검증 실패 시
    """
    if not username:
        raise ValidationError('사용자명을 입력해주세요.', 'username')
    
    username = username.strip()
    
    if len(username) < 3:
        raise ValidationError('사용자명은 최소 3자 이상이어야 합니다.', 'username')
    
    if len(username) > 50:
        raise ValidationError('사용자명은 최대 50자까지 가능합니다.', 'username')
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        raise ValidationError(
            '사용자명은 영문, 숫자, 언더스코어만 사용할 수 있습니다.',
            'username'
        )
    
    return username


def validate_email_address(email):
    """
    이메일 검증
    
    규칙:
    - 필수 입력
    - 유효한 이메일 형식
    
    Args:
        email (str): 검증할 이메일
        
    Returns:
        str: 검증된 이메일 (정규화된 상태)
        
    Raises:
        ValidationError: 검증 실패 시
    """
    if not email:
        raise ValidationError('이메일을 입력해주세요.', 'email')
    
    email = email.strip().lower()
    
    try:
        # email-validator 라이브러리 사용
        valid = validate_email(email)
        return valid.email
    except EmailNotValidError as e:
        raise ValidationError('유효한 이메일 주소를 입력해주세요.', 'email')


def validate_password(password, min_length=8, max_length=128):
    """
    비밀번호 검증
    
    규칙:
    - 필수 입력
    - 최소 길이 (기본값: 8자)
    - 최대 길이 (기본값: 128자)
    
    Args:
        password (str): 검증할 비밀번호
        min_length (int): 최소 길이
        max_length (int): 최대 길이
        
    Returns:
        str: 검증된 비밀번호
        
    Raises:
        ValidationError: 검증 실패 시
    """
    if not password:
        raise ValidationError('비밀번호를 입력해주세요.', 'password')
    
    if len(password) < min_length:
        raise ValidationError(f'비밀번호는 최소 {min_length}자 이상이어야 합니다.', 'password')
    
    if len(password) > max_length:
        raise ValidationError(f'비밀번호는 최대 {max_length}자까지 가능합니다.', 'password')
    
    return password


def validate_pagination(page, limit, max_limit=50):
    """
    페이지네이션 파라미터 검증
    
    Args:
        page (any): 페이지 번호 (문자열 또는 정수)
        limit (any): 페이지당 항목 수 (문자열 또는 정수)
        max_limit (int): 최대 제한 (기본값: 50)
        
    Returns:
        tuple: (page, limit) - 검증된 정수 값
        
    Raises:
        ValidationError: 검증 실패 시
    """
    try:
        page = int(page or 1)
        limit = int(limit or 10)
    except (ValueError, TypeError):
        raise ValidationError('페이지 번호와 제한은 정수여야 합니다.')
    
    if page < 1:
        raise ValidationError('페이지 번호는 1 이상이어야 합니다.', 'page')
    
    if limit < 1:
        raise ValidationError('제한은 1 이상이어야 합니다.', 'limit')
    
    if limit > max_limit:
        raise ValidationError(f'제한은 최대 {max_limit}까지 가능합니다.', 'limit')
    
    return page, limit


def validate_concept_id(concept_id):
    """
    개념 ID 검증
    
    Args:
        concept_id (any): 개념 ID
        
    Returns:
        int: 검증된 정수 ID
        
    Raises:
        ValidationError: 검증 실패 시
    """
    if not concept_id:
        raise ValidationError('개념 ID를 입력해주세요.', 'concept_id')
    
    try:
        concept_id = int(concept_id)
    except (ValueError, TypeError):
        raise ValidationError('개념 ID는 정수여야 합니다.', 'concept_id')
    
    if concept_id < 1:
        raise ValidationError('개념 ID는 1 이상이어야 합니다.', 'concept_id')
    
    return concept_id


def validate_sort_params(sort, order, allowed_fields):
    """
    정렬 파라미터 검증
    
    Args:
        sort (str): 정렬 필드
        order (str): 정렬 순서 ('asc' 또는 'desc')
        allowed_fields (list): 허용된 필드 목록
        
    Returns:
        tuple: (sort, order) - 검증된 값
        
    Raises:
        ValidationError: 검증 실패 시
    """
    # 기본값 설정
    sort = sort or 'created_at'
    order = order or 'desc'
    
    # 정렬 필드 검증
    if sort not in allowed_fields:
        raise ValidationError(
            f'정렬 필드는 {", ".join(allowed_fields)} 중 하나여야 합니다.',
            'sort'
        )
    
    # 정렬 순서 검증
    if order not in ['asc', 'desc']:
        raise ValidationError('정렬 순서는 asc 또는 desc여야 합니다.', 'order')
    
    return sort, order


def validate_search_query(query, min_length=2, max_length=100):
    """
    검색어 검증
    
    Args:
        query (str): 검색어
        min_length (int): 최소 길이
        max_length (int): 최대 길이
        
    Returns:
        str: 검증된 검색어 (trim된 상태)
        
    Raises:
        ValidationError: 검증 실패 시
    """
    if not query:
        raise ValidationError('검색어를 입력해주세요.', 'q')
    
    query = query.strip()
    
    if len(query) < min_length:
        raise ValidationError(f'검색어는 최소 {min_length}자 이상이어야 합니다.', 'q')
    
    if len(query) > max_length:
        raise ValidationError(f'검색어는 최대 {max_length}자까지 가능합니다.', 'q')
    
    return query

