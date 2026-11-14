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

from pathlib import Path

import pytest
from serializable import Serializable

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


def named_sort_key(x):
    return -x


def test_default_sources_are_not_shared():
    first = Collection([1])
    second = Collection([2])
    first.sources.add("x.vcf")
    eq_(second.sources, set())
    eq_(Collection([3]).sources, set())


def test_sources_are_copied_from_the_argument():
    sources = {"a.vcf"}
    collection = Collection([1], sources=sources)
    clone = collection.filter(lambda x: True)
    sources.add("b.vcf")
    clone.sources.add("c.vcf")
    eq_(collection.sources, {"a.vcf"})
    eq_(clone.sources, {"a.vcf", "c.vcf"})


def test_sources_accepts_none_string_and_list():
    eq_(Collection([1], sources=None).sources, set())
    eq_(Collection([1], sources="a.vcf").sources, {"a.vcf"})
    eq_(Collection([1], sources=["a.vcf", "b.vcf"]).sources, {"a.vcf", "b.vcf"})


def test_elements_from_iterator():
    collection = Collection(iter([1, 2, 3]))
    eq_(len(collection), 3)
    eq_(list(collection), [1, 2, 3])
    eq_(list(collection), [1, 2, 3])
    eq_(collection[0], 1)
    eq_(len(Collection(x for x in "ab")), 2)


def test_elements_are_copied_from_the_argument():
    elements = [1, 2]
    collection = Collection(elements)
    elements.append(3)
    eq_(list(collection), [1, 2])


def test_json_rejects_lambda_sort_key():
    collection = Collection([3, 1, 2], sort_key=lambda x: x)
    with pytest.raises(ValueError, match="sort_key"):
        collection.to_json()

    def nested(x):
        return x

    with pytest.raises(ValueError, match="sort_key"):
        Collection([3, 1, 2], sort_key=nested).to_json()


def test_json_rejects_lambda_sort_key_when_writing_file(tmp_path):
    collection = Collection([3, 1, 2], sort_key=lambda x: x)
    with pytest.raises(ValueError, match="sort_key"):
        collection.write_json_file(tmp_path / "collection.json")


def test_json_roundtrip_with_named_sort_key():
    collection = Collection([1, 3, 2], sort_key=named_sort_key)
    restored = Collection.from_json(collection.to_json())
    eq_(list(restored), [3, 2, 1])
    assert restored.sort_key is named_sort_key
    eq_(list(Collection.from_json(Collection([2, 1], sort_key=abs).to_json())), [1, 2])


def test_to_string_limit():
    collection = Collection([1, 2])
    eq_(collection.to_string(limit=0),
        "<Collection with 2 elements>\n  ... and 2 more")
    eq_(collection.to_string(limit=1),
        "<Collection with 2 elements>\n  -- 1\n  ... and 1 more")
    eq_(collection.to_string(limit=2),
        "<Collection with 2 elements>\n  -- 1\n  -- 2")
    eq_(collection.to_string(),
        "<Collection with 2 elements>\n  -- 1\n  -- 2")
    eq_(Collection([]).to_string(limit=0), "<Collection with 0 elements>")
    eq_(str(collection), collection.to_string(limit=50))
    with pytest.raises(ValueError, match="limit"):
        collection.to_string(limit=-1)


def test_filename_without_sources_raises_value_error():
    with pytest.raises(ValueError, match="No source file"):
        Collection([1]).filename
    with pytest.raises(ValueError, match="No source file"):
        Collection([1], sources={""}).filename
    eq_(Collection([1], sources={"/data/a.vcf"}).filename, "a.vcf")


def test_sources_are_listed_in_sorted_order():
    sources = {"/data/%s.vcf" % name for name in "hgfedcba"}
    collection = Collection([1], sources=sources)
    eq_(collection.short_string(),
        "<Collection from '%s' with 1 elements>" % ",".join(sorted(sources)))
    eq_(collection.filenames, ["%s.vcf" % name for name in "abcdefgh"])
    eq_(collection.filename, "a.vcf")


def test_eq_compares_sources():
    neq_(Collection([1], sources={"a.vcf"}), Collection([1], sources={"b.vcf"}))
    neq_(Collection([1], sources={"a.vcf"}), Collection([1]))
    eq_(Collection([1], sources={"a.vcf"}), Collection([1], sources=["a.vcf"]))
    neq_(Collection([1]), None)
    neq_(Collection([1]), [1])


def test_to_dataframe_of_scalars():
    df = Collection([1, 2]).to_dataframe()
    eq_(list(df.columns), ["value"])
    eq_(list(df["value"]), [1, 2])
    eq_(list(Collection(["a", "b"]).to_dataframe()["value"]), ["a", "b"])
    eq_(len(Collection([]).to_dataframe()), 0)


def test_to_csv_omits_index_by_default(tmp_path):
    collection = Collection([{"x": 1, "y": "a"}, {"x": 2, "y": "b"}])
    path = tmp_path / "collection.csv"
    collection.to_csv(path)
    eq_(path.read_text(), "x,y\n1,a\n2,b\n")
    collection.to_csv(path, index=True)
    eq_(path.read_text(), ",x,y\n0,1,a\n1,2,b\n")


class RenamedElements(Collection):
    def __init__(self, things, sources=None):
        Collection.__init__(self, things, sources=sources)


class ElementsOnly(Collection):
    def __init__(self, elements):
        Collection.__init__(self, elements, sort_key=named_sort_key)


class RequiresLabel(Collection):
    def __init__(self, elements, label, sources=None):
        Collection.__init__(self, elements, sources=sources)
        self.label = label


class AcceptsAnyKeywords(Collection):
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        Collection.__init__(self, **kwargs)


def test_clone_subclass_with_renamed_elements_argument():
    collection = RenamedElements([1, 2, 3], sources={"a.vcf"})
    filtered = collection.filter(lambda x: x > 1)
    eq_(type(filtered), RenamedElements)
    eq_(list(filtered), [2, 3])
    eq_(filtered.sources, {"a.vcf"})
    groups = collection.groupby(lambda x: x % 2)
    eq_({k: list(v) for k, v in groups.items()}, {1: [1, 3], 0: [2]})
    eq_(type(groups[0]), RenamedElements)


def test_clone_subclass_without_optional_arguments():
    filtered = ElementsOnly([1, 2, 3]).filter(lambda x: x > 1)
    eq_(type(filtered), ElementsOnly)
    eq_(list(filtered), [3, 2])


def test_clone_subclass_with_other_required_argument():
    collection = RequiresLabel([1, 2], label="x")
    with pytest.raises(TypeError, match="Override clone_with_new_elements"):
        collection.filter(lambda x: True)
    clone = collection.clone_with_new_elements([2], extra_kwargs={"label": "y"})
    eq_((list(clone), clone.label), ([2], "y"))


def test_clone_passes_all_state_to_keyword_constructor():
    collection = AcceptsAnyKeywords(elements=[2, 1], sources={"a.vcf"})
    clone = collection.filter(lambda x: True)
    eq_(set(clone.kwargs), {"elements", "distinct", "sort_key", "sources"})


class RenamedWithKeywords(Collection):
    def __init__(self, things, **kwargs):
        self.kwargs = kwargs
        Collection.__init__(self, things, **kwargs)


class DefaultFirstArgument(Collection):
    def __init__(self, name="x", items=()):
        Collection.__init__(self, items)
        self.name = name


class StarArguments(Collection):
    def __init__(self, *things):
        Collection.__init__(self, things)


def test_clone_subclass_with_renamed_elements_and_keywords():
    collection = RenamedWithKeywords([1, 2, 3], sources={"a.vcf"})
    filtered = collection.filter(lambda x: x > 1)
    eq_(list(filtered), [2, 3])
    eq_(set(filtered.kwargs), {"distinct", "sort_key", "sources"})
    eq_(filtered.sources, {"a.vcf"})


def test_clone_does_not_guess_which_argument_holds_elements():
    with pytest.raises(TypeError, match="Override clone_with_new_elements"):
        DefaultFirstArgument("label", [1, 2, 3]).filter(lambda x: x > 1)
    with pytest.raises(TypeError, match="Override clone_with_new_elements"):
        StarArguments(1, 2, 3).filter(lambda x: x > 1)


class CallableKey(Serializable):
    def __init__(self, sign):
        self.sign = sign

    def __call__(self, x):
        return self.sign * x


def test_json_roundtrip_with_callable_object_sort_key():
    collection = Collection([1, 3, 2], sort_key=CallableKey(-1))
    restored = Collection.from_json(collection.to_json())
    eq_(list(restored), [3, 2, 1])
    eq_(restored.sort_key.sign, -1)


def test_single_source_as_path_or_bytes():
    eq_(Collection([1], sources=Path("/data/a.vcf")).sources, {"/data/a.vcf"})
    eq_(Collection([1], sources=b"ab").sources, {b"ab"})


def test_filenames_skip_sources_without_base_name():
    collection = Collection([1], sources={"/data/run1/", "/data/z.vcf"})
    eq_(collection.filenames, ["z.vcf"])
    eq_(collection.filename, "z.vcf")
    with pytest.raises(ValueError, match="No source file"):
        Collection([1], sources={"/data/run1/"}).filename


def test_clone_keyword_controls():
    collection = RenamedElements([1, 2], sources={"a.vcf"})
    clone = collection.clone_with_new_elements(
        [5],
        drop_keywords={"distinct", "sort_key"},
        rename_dict={"elements": "things"})
    eq_((list(clone), clone.sources), ([5], {"a.vcf"}))
