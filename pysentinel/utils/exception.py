class ScannerException(Exception):
    """Base exception for scanner errors"""
    pass


class DataSourceException(ScannerException):
    """Exception for data source related errors"""
    pass


class ThresholdException(ScannerException):
    """Exception for threshold related errors"""
    pass
