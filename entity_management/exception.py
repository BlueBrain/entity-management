# SPDX-License-Identifier: Apache-2.0

"""Exceptions module."""


class EntityManagementError(Exception):
    """Generic entity-management error."""


class ResourceNotFoundError(EntityManagementError):
    """Error related to failure in retrieving resources."""


class EntityNotInstantiatedError(EntityManagementError):
    """Error related to entities failing to be instantiated."""
