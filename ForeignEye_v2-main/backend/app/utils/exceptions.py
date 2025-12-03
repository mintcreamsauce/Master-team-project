"""
커스텀 예외 클래스

API에서 사용하는 일관된 예외 처리를 제공합니다.
"""


class APIException(Exception):
    """
    API 예외 기본 클래스
    
    모든 커스텀 API 예외의 부모 클래스입니다.
    
    Attributes:
        code (str): 에러 코드
        message (str): 사용자 친화적 메시지
        status_code (int): HTTP 상태 코드
        details (dict): 추가 상세 정보
    """
    
    def __init__(self, code, message, status_code=400, details=None):
        """
        Args:
            code (str): 에러 코드 (예: 'VALIDATION_ERROR')
            message (str): 에러 메시지
            status_code (int): HTTP 상태 코드
            details (dict): 추가 정보 (선택적)
        """
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class ValidationError(APIException):
    """
    입력 검증 오류
    
    사용자 입력이 유효하지 않을 때 발생합니다.
    HTTP 400 Bad Request
    """
    
    def __init__(self, message, field=None):
        """
        Args:
            message (str): 에러 메시지
            field (str): 문제가 발생한 필드명 (선택적)
        """
        super().__init__(
            code='VALIDATION_ERROR',
            message=message,
            status_code=400,
            details={'field': field} if field else None
        )


class NotFoundError(APIException):
    """
    리소스 없음 오류
    
    요청한 리소스를 찾을 수 없을 때 발생합니다.
    HTTP 404 Not Found
    """
    
    def __init__(self, resource, resource_id=None):
        """
        Args:
            resource (str): 리소스 타입 (예: '기사', '개념')
            resource_id (int): 리소스 ID (선택적)
        """
        message = f'{resource}를 찾을 수 없습니다.'
        super().__init__(
            code='NOT_FOUND',
            message=message,
            status_code=404,
            details={'resource': resource, 'resource_id': resource_id}
        )


class DuplicateEntryError(APIException):
    """
    중복 데이터 오류
    
    이미 존재하는 데이터를 생성하려고 할 때 발생합니다.
    HTTP 409 Conflict
    """
    
    def __init__(self, message, field=None):
        """
        Args:
            message (str): 에러 메시지
            field (str): 중복된 필드명 (선택적)
        """
        super().__init__(
            code='DUPLICATE_ENTRY',
            message=message,
            status_code=409,
            details={'field': field} if field else None
        )


class UnauthorizedError(APIException):
    """
    인증 실패 오류
    
    인증이 필요하거나 인증 정보가 잘못되었을 때 발생합니다.
    HTTP 401 Unauthorized
    """
    
    def __init__(self, message='인증이 필요합니다.'):
        """
        Args:
            message (str): 에러 메시지 (기본값: '인증이 필요합니다.')
        """
        super().__init__(
            code='UNAUTHORIZED',
            message=message,
            status_code=401
        )


class ForbiddenError(APIException):
    """
    권한 없음 오류
    
    요청한 작업을 수행할 권한이 없을 때 발생합니다.
    HTTP 403 Forbidden
    """
    
    def __init__(self, message='이 작업을 수행할 권한이 없습니다.'):
        """
        Args:
            message (str): 에러 메시지
        """
        super().__init__(
            code='FORBIDDEN',
            message=message,
            status_code=403
        )


class RateLimitError(APIException):
    """
    요청 제한 초과 오류
    
    API 호출 횟수 제한을 초과했을 때 발생합니다.
    HTTP 429 Too Many Requests
    """
    
    def __init__(self, message='요청이 너무 많습니다. 잠시 후 다시 시도해주세요.', retry_after=60):
        """
        Args:
            message (str): 에러 메시지
            retry_after (int): 재시도까지 대기 시간 (초)
        """
        super().__init__(
            code='RATE_LIMIT_EXCEEDED',
            message=message,
            status_code=429,
            details={'retry_after': retry_after}
        )

