'''
Experimental morphologies entities

.. inheritance-diagram:: entity_management.experiment
   :top-classes: entity_management.experiment.Entity
   :parts: 1
'''
from entity_management.base import Identifiable
from entity_management.util import attributes
from entity_management.mixins import DistributionMixin


@attributes()
class Entity(DistributionMixin, Identifiable):
    '''Base class for experiment Enitities'''
    _type_namespace = 'nsg'
    _url_domain = 'experiment'
