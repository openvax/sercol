# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import inspect
import numbers
import os.path
from collections import defaultdict

import pandas as pd
import serializable

# Constructor arguments which clone_with_new_elements() passes on only to
# constructors which accept them.
_OPTIONAL_STATE = ("distinct", "sort_key", "sources")

# Elements which to_dataframe() puts in a single "value" column.
_SCALAR_TYPES = (str, bytes, numbers.Number, type(None))


class Collection(serializable.Serializable):
    """
    Collection base class with grouping and filtering functions.
    """
    def __init__(
            self,
            elements,
            distinct=False,
            sort_key=None,
            sources=None):
        """
        Parameters
        ----------
        elements : iterable
            Elements of any class which is compatible with the sort key.
            They are copied into a new list, so an iterator or generator is
            accepted and later changes to the argument don't affect this
            collection.

        distinct : bool
            Keep only the first occurrence of each element (elements must
            be hashable) or allow duplicates.

        sort_key : fn
            Function which maps each element to a sorting criterion.

        sources : set of str, str, path or None
            Files from which this collection was generated. They are copied
            into a new set, so collections never share one; a single string
            or path is one source and None means no sources.
        """
        self.distinct = distinct
        if distinct:
            elements = list(dict.fromkeys(elements))
        else:
            elements = list(elements)
        self.sort_key = sort_key
        if self.sort_key is not None:
            elements = sorted(elements, key=sort_key)
        self.elements = elements
        if sources is None:
            sources = set()
        elif isinstance(sources, os.PathLike):
            sources = {os.fspath(sources)}
        elif isinstance(sources, (str, bytes)):
            sources = {sources}
        else:
            sources = set(sources)
        self.sources = sources

    def to_dict(self):
        """
        Return the constructor arguments needed to rebuild this collection.

        This also serves subclasses whose constructor takes the same
        arguments, such as one that inherits ``Collection.__init__``, so they
        can be pickled, copied and saved as JSON without their own
        ``to_dict``.

        Returns
        -------
        dict
            ``elements``, ``distinct``, ``sort_key`` and ``sources``.

        Raises
        ------
        ValueError
            If this object's class has a constructor with other arguments.
            Such a subclass must define its own ``to_dict``.
        """
        state = dict(
            elements=self.elements,
            distinct=self.distinct,
            sort_key=self.sort_key,
            sources=self.sources)
        if set(inspect.signature(type(self)).parameters) != set(state):
            raise ValueError(
                "%s takes different constructor arguments than Collection, "
                "so it must define its own to_dict()" % type(self).__name__)
        return state

    def to_json(self):
        """
        Returns a string containing a JSON representation of this collection.

        Raises
        ------
        ValueError
            If ``sort_key`` is a lambda or a function defined inside another
            function. JSON stores a function as its module and name, so only
            one which can be looked up that way can be loaded again.
        """
        sort_key = self.sort_key
        # Only functions are stored by name; other callables, such as a
        # Serializable instance, are left to serializable.
        if inspect.isroutine(sort_key):
            qualified_name = getattr(sort_key, "__qualname__", None)
            module_name = getattr(sort_key, "__module__", None)
            if qualified_name is None or module_name is None or "<" in qualified_name:
                raise ValueError(
                    "Can't save %s as JSON: its sort_key %r can't be looked up "
                    "by name when loading. Use a function defined at the top "
                    "level of a module instead of a lambda or nested "
                    "function." % (type(self).__name__, sort_key))
        return super().to_json()

    def to_dataframe(self):
        """
        Build a table with one row per element.

        Strings, bytes, numbers and None each become a row with a single
        ``value`` column. Any other element is converted with
        ``serializable.to_dict``, so it must be a dict, an object with a
        ``to_dict`` method (such as a ``Serializable`` instance), or an
        object whose attributes match its constructor arguments.

        Returns
        -------
        pandas.DataFrame
        """
        return pd.DataFrame.from_records([
            {"value": x} if isinstance(x, _SCALAR_TYPES) else serializable.to_dict(x)
            for x in self
        ])

    def to_csv(self, path, index=False):
        """
        Write ``to_dataframe()`` to a CSV file.

        Parameters
        ----------
        path : str or path-like
            Destination file; an existing file is overwritten.

        index : bool
            Also write the row numbers as an unnamed first column.
        """
        return self.to_dataframe().to_csv(path, index=index)

    def clone_with_new_elements(
            self,
            new_elements,
            drop_keywords=(),
            rename_dict=None,
            extra_kwargs=None):
        """
        Create another Collection of the same class and with same state but
        possibly different entries. Extra parameters to control which keyword
        arguments get passed to the initializer are necessary since derived
        classes have different constructors than the base class.

        A subclass constructor which differs only by leaving out ``distinct``,
        ``sort_key`` or ``sources``, or by giving its first argument a name
        other than ``elements``, needs none of the extra parameters: the
        arguments it doesn't take are left out and the elements are passed
        by position. The elements are only passed by position to a first
        argument which is required; one with a default value, or ``*args``,
        is not assumed to hold the elements.

        Parameters
        ----------
        new_elements : list
            Elements of the new collection.

        drop_keywords : set of str
            Base-class constructor arguments (``distinct``, ``sort_key``,
            ``sources``) to leave out.

        rename_dict : dict
            Maps base-class argument names to the names the subclass
            constructor uses.

        extra_kwargs : dict
            Additional constructor arguments, applied last.

        Returns
        -------
        Collection
            A new instance of ``self.__class__``.

        Raises
        ------
        TypeError
            If the constructor of ``self.__class__`` can't be called with
            the resulting arguments, for example because it requires others.
            Such a subclass must pass ``extra_kwargs`` or override this
            method.
        """
        kwargs = dict(
            elements=new_elements,
            distinct=self.distinct,
            sort_key=self.sort_key,
            sources=self.sources)
        for name in drop_keywords:
            kwargs.pop(name)
        for old_name, new_name in (rename_dict or {}).items():
            kwargs[new_name] = kwargs.pop(old_name)
        kwargs.update(extra_kwargs or {})

        cls = self.__class__
        signature = inspect.signature(cls)
        parameters = signature.parameters
        args = []
        first = next(iter(parameters.values()), None)
        if (
                "elements" in kwargs and
                "elements" not in parameters and
                first is not None and
                first.name not in kwargs and
                first.default is first.empty and
                first.kind in (
                    first.POSITIONAL_ONLY,
                    first.POSITIONAL_OR_KEYWORD)):
            args.append(kwargs.pop("elements"))
        if not any(p.kind is p.VAR_KEYWORD for p in parameters.values()):
            for name in _OPTIONAL_STATE:
                if name in kwargs and name not in parameters:
                    del kwargs[name]
        try:
            signature.bind(*args, **kwargs)
        except TypeError as error:
            raise TypeError(
                "Can't clone %s: its constructor %s%s doesn't fit the arguments "
                "(%s) which clone_with_new_elements() passes (%s). Override "
                "clone_with_new_elements() in %s, or call it with "
                "drop_keywords, rename_dict or extra_kwargs." % (
                    cls.__name__,
                    cls.__name__,
                    signature,
                    ", ".join(["<elements>"] * len(args) + sorted(kwargs)),
                    error,
                    cls.__name__)) from error
        return cls(*args, **kwargs)

    @property
    def source(self):
        """
        Returns the single source name for a variant collection if it is unique,
        otherwise raises an error.
        """
        if len(self.sources) == 0:
            raise ValueError("No source associated with %s" % self.__class__.__name__)
        elif len(self.sources) > 1:
            raise ValueError("Multiple sources for %s" % self.__class__.__name__)
        return list(self.sources)[0]

    @property
    def path(self):
        """
        Alternative name for ``source``, maintained for backward compatibility.
        """
        return self.source

    @property
    def filenames(self):
        """
        Sorted base names of the non-empty sources, assuming they are file
        paths (for example VCF or MAF files). A source without a base name,
        such as a directory path ending in a separator, is left out.
        """
        filenames = (
            os.path.basename(source) for source in self.sources if source)
        return sorted(filename for filename in filenames if filename)

    @property
    def filename(self):
        """
        First entry of ``filenames`` (the only one when there is a single
        source), kept for backward compatibility.

        Raises ValueError when ``filenames`` is empty.
        """
        filenames = self.filenames
        if len(filenames) == 0:
            raise ValueError(
                "No source file associated with %s" % self.__class__.__name__)
        return filenames[0]

    def short_string(self):
        """
        Compact string representation which doesn't print any of the
        collection elements. Sources are listed in sorted order.
        """
        source_str = ""
        if self.sources:
            source_str = " from '%s'" % ",".join(
                sorted(str(source) for source in self.sources))
        return "<%s%s with %d elements>" % (
            self.__class__.__name__,
            source_str,
            len(self))

    def to_string(self, limit=None):
        """
        Create a string representation of this collection, showing up to
        `limit` items (all of them when `limit` is None).

        Raises ValueError when `limit` is negative.
        """
        if limit is not None and limit < 0:
            raise ValueError("limit must not be negative, got %r" % (limit,))
        lines = [self.short_string()]
        lines.extend(
            "  -- %s" % (element,)
            for element in self.elements[:limit])
        if limit is not None and len(self) > limit:
            lines.append("  ... and %d more" % (len(self) - limit))
        return "\n".join(lines)

    def __str__(self):
        return self.to_string(limit=50)

    def __len__(self):
        return len(self.elements)

    def __iter__(self):
        return iter(self.elements)

    def __hash__(self):
        return hash(len(self))

    def __getitem__(self, idx):
        return self.elements[idx]

    def __eq__(self, other):
        """
        Collections are equal when they have the same class, the same
        elements in the same order and the same sources.
        """
        if self is other:
            return True
        return (
            self.__class__ == other.__class__ and
            len(self) == len(other) and
            self.sources == other.sources and
            all(x == y for (x, y) in zip(self, other)))

    def filter(self, filter_fn):
        """
        Keep the elements for which ``filter_fn`` returns a true value.

        Parameters
        ----------
        filter_fn : callable
            Takes one element and returns a truthy or falsy value.

        Returns
        -------
        Collection
            A collection of the same class, built with
            ``clone_with_new_elements``.
        """
        return self.clone_with_new_elements([
            element
            for element in self.elements
            if filter_fn(element)])

    def groupby(self, key_fn):
        """
        Group elements by the key ``key_fn`` returns for each.

        Parameters
        ----------
        key_fn : callable
            Takes one element and returns a hashable grouping key.

        Returns
        -------
        dict
            Maps each key to a collection of the same class, built with
            ``clone_with_new_elements`` from that key's elements in
            iteration order (so ``distinct`` and ``sort_key`` still apply).
        """
        result_dict = defaultdict(list)

        for x in self:
            result_dict[key_fn(x)].append(x)

        # convert result lists into same Collection type as this one
        return {
            k: self.clone_with_new_elements(elements)
            for (k, elements)
            in result_dict.items()
        }

    def multi_groupby(self, key_fn):
        """
        Like ``groupby``, but ``key_fn`` returns several keys for each element,
        and the element is added to the group for every one of them.

        Parameters
        ----------
        key_fn : callable
            Takes one element and returns an iterable of hashable keys.

        Returns
        -------
        dict
            Maps each key to a collection of the same class.
        """
        result_dict = defaultdict(list)

        for x in self:
            for key in key_fn(x):
                result_dict[key].append(x)

        # convert result lists into same Collection type as this one
        return {
            k: self.clone_with_new_elements(elements)
            for (k, elements)
            in result_dict.items()
        }

    def filter_above_threshold(
            self,
            key_fn,
            value_dict,
            threshold,
            default_value=0.0):
        """Keep elements whose looked-up value is above a threshold.

        For example, keep variant effects whose gene expression is above a
        cutoff.

        Parameters
        ----------
        key_fn : callable
            Given an element of this collection, returns a key into `value_dict`

        value_dict : dict
            Dict from keys returned by `key_fn` to float values

        threshold : float
            Only keep elements whose value in `value_dict` is above this
            threshold.

        default_value : float
            Value to use for elements whose key is not in `value_dict`

        Returns
        -------
        Collection
            A collection of the same class, as ``filter`` returns.
        """
        def filter_fn(x):
            key = key_fn(x)
            value = value_dict.get(key, default_value)
            return value > threshold
        return self.filter(filter_fn)

    def filter_any_above_threshold(
            self,
            multi_key_fn,
            value_dict,
            threshold,
            default_value=0.0):
        """Like filter_above_threshold but `multi_key_fn` returns multiple
        keys and the element is kept if any of them have a value above
        the given threshold.

        Parameters
        ----------
        multi_key_fn : callable
            Given an element of this collection, returns multiple keys
            into `value_dict`

        value_dict : dict
            Dict from keys returned by `multi_key_fn` to float values

        threshold : float
            Only keep elements whose value in `value_dict` is above this
            threshold.

        default_value : float
            Value to use for elements whose key is not in `value_dict`

        Returns
        -------
        Collection
            A collection of the same class, as ``filter`` returns.
        """
        def filter_fn(x):
            for key in multi_key_fn(x):
                value = value_dict.get(key, default_value)
                if value > threshold:
                    return True
            return False
        return self.filter(filter_fn)
