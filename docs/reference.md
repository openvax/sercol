# Collection reference

| Task | Method |
| --- | --- |
| Keep matching elements | `filter()` |
| Group under one or several keys | `groupby()`, `multi_groupby()` |
| Apply lookup thresholds | `filter_above_threshold()`, `filter_any_above_threshold()` |
| Preserve metadata while replacing elements | `clone_with_new_elements()` |
| Write record-shaped elements to a table | `to_dataframe()`, `to_csv()` |
| Save or reload supported objects | Inherited `to_json()`, `from_json()` |

Table conversion expects elements that the serialization helper can turn into
field dictionaries. A collection of primitive integers is useful for filtering
examples, but is not a record table.

::: sercol.Collection
