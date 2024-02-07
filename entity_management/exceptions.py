"""Exceptions module."""


class EntityManagementError(Exception):
    """Generic entity-management error."""


class ResourceNotFoundError(EntityManagementError):
    """sas"""


class EntityNotInstantiatedError(EntityManagementError):
    """Error related to entities failing to be instantiated."""
