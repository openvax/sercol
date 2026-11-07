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
Test methods shared by both VariantCollection and EffectCollection
"""

from .common import eq_, neq_
from sercol import Collection


def test_collection_len():
    collection = Collection([1, 2, 3])
    assert len(collection) == 3
    collection = Collection([])
    assert len(collection) == 0


def test_collection_eq():
    elements = ["a", "b", "c"]
    collection = Collection(elements)
    eq_(collection, collection, "collection should equal itself")
    eq_(collection, Collection(elements))


def test_collection_neq():
    elements = ["a", "b", "c"]
    c1 = Collection(elements)
    c2 = Collection(elements[:2])
    neq_(c1, c2)


def test_filter():
    collection = Collection([1, 2, 3, 4])
    filtered = collection.filter(lambda x: x < 3)
    expected = Collection([1, 2])
    eq_(filtered, expected)


def test_groupby():
    collection = Collection(["alpha", "able", "beta", "backroom"])
    groups = collection.groupby(lambda x: x[0])
    eq_(len(groups), 2)
    eq_(set(groups.keys()), {"a", "b"})


def test_distinct_without_sort_key_keeps_first_occurrences_in_order():
    collection = Collection([3, 1, 2, 1, 3], distinct=True)
    eq_(collection.elements, [3, 1, 2])
    eq_(collection[0], 3)
    eq_(str(collection), "<Collection with 3 elements>\n  -- 3\n  -- 1\n  -- 2")
    eq_(repr(collection), str(collection))


def test_distinct_without_sort_key_filter_and_groupby():
    collection = Collection(["b", "a", "b", "c"], distinct=True)
    eq_(collection.filter(lambda x: x != "c").elements, ["b", "a"])
    groups = collection.groupby(lambda x: x == "a")
    eq_(groups[False].elements, ["b", "c"])
    eq_(groups[True].elements, ["a"])


def test_distinct_with_sort_key_keeps_input_order_of_ties():
    collection = Collection([-2, 2, 3, -2], distinct=True, sort_key=abs)
    eq_(collection.elements, [-2, 2, 3])


def test_collection_dict_roundtrip():
    collection = Collection(["a", "b"], sources={"example.vcf"})
    state_dict = collection.to_dict()
    eq_(set(state_dict.keys()), {"elements", "distinct", "sort_key", "sources"})
    restored = Collection.from_dict(state_dict)
    eq_(restored, collection)
    eq_(restored.sources, {"example.vcf"})


def test_collection_json_roundtrip():
    collection = Collection(["a", "b"], sources={"example.vcf"})
    restored = Collection.from_json(collection.to_json())
    eq_(restored.__class__, Collection)
    eq_(restored, collection)
    eq_(restored.sources, {"example.vcf"})


def test_collection_to_dataframe():
    collection = Collection([{"x": 1}, {"x": 2}])
    df = collection.to_dataframe()
    eq_(list(df.columns), ["x"])
    eq_(list(df["x"]), [1, 2])
