# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Serialization of Collection subclasses: pickle, copy.deepcopy and JSON all
go through to_dict.
"""

import copy
import pickle

import pytest

from .common import eq_
from sercol import Collection


class InheritedInit(Collection):
    """Keeps Collection's constructor, like mhctools' BindingPredictionCollection."""


class SameArgsInit(Collection):
    """Overrides the constructor without changing its arguments."""

    def __init__(self, elements, distinct=False, sort_key=None, sources=None):
        Collection.__init__(
            self,
            elements=elements,
            distinct=distinct,
            sort_key=sort_key,
            sources=sources)


class RenamedInit(Collection):
    """Calls its elements something else, so needs its own to_dict."""

    def __init__(self, values):
        Collection.__init__(self, elements=values)


def pickle_round_trip(collection):
    return pickle.loads(pickle.dumps(collection))


def json_round_trip(collection):
    return type(collection).from_json(collection.to_json())


ROUND_TRIPS = [pickle_round_trip, copy.deepcopy, json_round_trip]


@pytest.mark.parametrize("cls", [InheritedInit, SameArgsInit])
@pytest.mark.parametrize("round_trip", ROUND_TRIPS)
def test_subclass_with_collection_arguments_round_trips(cls, round_trip):
    collection = cls([3, 1, 2], sort_key=abs, sources={"scores.csv"})
    restored = round_trip(collection)
    eq_(type(restored), cls)
    eq_(restored, collection)
    eq_(list(restored), [1, 2, 3])
    eq_(restored.sort_key, abs)
    eq_(restored.sources, {"scores.csv"})


def test_subclass_with_other_arguments_must_define_to_dict():
    collection = RenamedInit([1, 2])
    with pytest.raises(ValueError, match="RenamedInit .* own to_dict"):
        collection.to_dict()
    with pytest.raises(ValueError, match="RenamedInit"):
        pickle.dumps(collection)


def test_mhctools_binding_prediction_collection_round_trips():
    mhctools = pytest.importorskip("mhctools")
    prediction = mhctools.BindingPrediction(
        peptide="SIINFEKL",
        allele="HLA-A*02:01",
        affinity=120.0,
        percentile_rank=0.5,
        source_sequence_name="seq",
        offset=0)
    collection = mhctools.BindingPredictionCollection([prediction])
    for round_trip in ROUND_TRIPS:
        restored = round_trip(collection)
        eq_(type(restored), mhctools.BindingPredictionCollection)
        eq_(restored, collection)
