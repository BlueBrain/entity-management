"""Entities for s2f recipe generation."""

import re
from pathlib import Path

import attr


def _cls_name_to_snake_case(cls):
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", cls.__name__)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()


def _filter(_field, value):
    if not value:
        return False
    return True


def _serializer(_inst, _field, value):
    if isinstance(value, Path):
        return str(value)
    return value


@attr.frozen
class Strategy:
    """Base strategy class."""


@attr.frozen
class Sample:
    """Parameters for sampling bouton density."""

    size: int = 100  #: Sample size
    target: str | None = None  #: Sample target
    #: Region of interest. If provided, only axonal segments within this region would be considered.
    mask: str | None = None
    assume_nsyn_bouton: float = 1.0  #: FIMXE
    assume_syns_bouton: float = 1.0  #: Assumed synapse count per bouton


@attr.frozen
class EstimateSynsCon(Strategy):
    """Estimate the functional mean number of synapses per connection from the structural number \
    of appositions per connection. For the prediction, an algebraic expression using ‘n’ \
    (mean number of appositions) should be specified."""

    formula: str  #: Synapse number prediction formula.
    #: Synapse number prediction formula for EXC->EXC pathways.
    #: If omitted, general formula would be used
    formula_ee: str | None = None
    #: Synapse number prediction formula for EXC->INH pathways.
    #: If omitted, general formula would be used
    formula_ei: str | None = None
    #: Synapse number prediction formula for INH->EXC pathways.
    #: If omitted, general formula would be used
    formula_ie: str | None = None
    #: Synapse number prediction formula for INH->INH pathways.
    #: If omitted, general formula would be used
    formula_ii: str | None = None
    #: Max value for predicted synapse number.
    #: If omitted, the predicted synapse number is not clipped above NB: predicted synapse value
    #: would be always min-clipped to 1.0 to avoid invalid synapse count values.
    max_value: float | None = None
    #: Parameters for sampling bouton density OR path to bouton-density dataset already sampled
    sample: Sample | Path | None = None


@attr.frozen
class ExperimentalSynsCon(Strategy):
    """Use the biological mean number of synapses per connection for a number of pathways where \
    experimental data is available."""

    #: Path to nsyn-per-connection dataset representing reference biological data
    bio_data: Path


@attr.frozen
class EstimateBoutonReduction(Strategy):
    """Estimate an overall reduction factor based on an estimated mean bouton density over all \
    mtypes."""

    #: Path to bouton-density dataset representing reference biological data (OR single float value)
    bio_data: Path | float
    #: Parameters for sampling bouton density OR path to bouton-density dataset already sampled
    sample: Sample | Path | None = None


@attr.frozen
class EstimateIndividualBoutonReduction(EstimateBoutonReduction):
    """Estimate a reduction factor for each individual mtype, where experimental data is available.\
    """


@attr.frozen
class GeneralizedCv(Strategy):
    """Set cv_syns_connection value for all pathways."""

    cv: float  #: cv_syns_connection value to use


@attr.frozen
class Recipe:
    """Synapse pruning functionalizer recipe."""

    strategies: list[
        (
            EstimateSynsCon
            | ExperimentalSynsCon
            | EstimateBoutonReduction
            | EstimateIndividualBoutonReduction
            | GeneralizedCv
        )
    ] = []  #:

    def asdict(self):
        """Recipe dictionary representation."""
        return [
            {
                _cls_name_to_snake_case(type(strategy)): attr.asdict(
                    strategy, filter=_filter, value_serializer=_serializer
                )
            }
            for strategy in self.strategies
        ]
