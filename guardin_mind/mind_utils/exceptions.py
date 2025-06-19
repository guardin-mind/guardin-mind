'''
Custom exceptions for Guaridn Mind
'''

class PythonVersionError(RuntimeError):
    """Exception raised when the Python version does not meet requirements."""
    pass

class MindVersionError(RuntimeError):
    """An exception caused if the Python version does not match"""
    pass