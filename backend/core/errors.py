from typing import Optional

class AppError(Exception):
    """uygulama  genelinde beklenen (iş) hataları için taban sınıf."""
    code: str = "app_error"
    http_status: int = 400
    
    def __init__(self, message: str,*,code:Optional[str]=None,http_status:Optional[int]=None):
        super().__init__(message)
        if code:
            self.code=code
        if http_status:
            self.http_status=http_status
        self.message=message

class NotFoundError(AppError):
    code="not_found"
    http_status=404

class ValidationAppError(AppError):
    code="validation_error"
    http_status=422