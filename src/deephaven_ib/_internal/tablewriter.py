"""Functionality for creating Deephaven tables."""

import logging
from typing import List, Any, Sequence, Union, Dict
import collections

import deephaven.DateTimeUtils as dtu
# noinspection PyPep8Naming
import deephaven.Types as dht
import jpy
from deephaven import DynamicTableWriter

from .trace import trace_str


class TableWriter:
    """A writer for logging data to Deephaven dynamic tables.

    Empty strings are logged as None.
    """

    _dtw: DynamicTableWriter
    _string_indices: List[int]
    _receive_time: bool

    # TODO: improve types type annotation once deephaven v2 is available
    def __init__(self, names: List[str], types: List[Any], receive_time: bool = True):
        TableWriter._check_for_duplicate_names(names)
        self.names = names
        self.types = types
        self._receive_time = receive_time

        if receive_time:
            self.names.insert(0, "ReceiveTime")
            self.types.insert(0, dht.datetime)

        self._dtw = DynamicTableWriter(names, types)
        self._string_indices = [i for (i, t) in enumerate(types) if t == dht.string]

    @staticmethod
    def _check_for_duplicate_names(names: List[str]) -> None:
        counts = collections.Counter(names)
        dups = [name for name, count in counts.items() if count > 1]

        if len(dups) > 0:
            raise Exception(f"Duplicate column names: {','.join(dups)}")

    def _check_logged_value_types(self, values: List) -> None:
        for n, t, v in zip(self.names, self.types, values):
            if v is None:
                continue

            if (t is dht.string and not isinstance(v, str)) or \
                    (t is dht.int32 and not isinstance(v, int)) or \
                    (t is dht.float64 and not isinstance(v, float)):
                logging.error(
                    f"TableWriter column type and value type are mismatched: column_name={n} column_type={t} value_type={type(v)} value={v}\n{trace_str()}\n-----")

    # TODO: improve types type annotation once deephaven v2 is available
    def table(self) -> Any:
        """Gets the table data is logged to."""
        return self._dtw.getTable()

    def write_row(self, values: List) -> None:
        """Writes a row of data.  The input values may be modified."""

        if self._receive_time:
            values.insert(0, dtu.currentTime())

        self._check_logged_value_types(values)

        for i in self._string_indices:
            if values[i] == "":
                values[i] = None

        self._dtw.logRow(values)


ArrayStringSet = jpy.get_type("io.deephaven.stringset.ArrayStringSet")


def map_values(value, map, default=lambda v: f"UNKNOWN({v})") -> Any:
    """ Maps one set of values to another.  A default value is used if the value is not in the map. """

    if value is None:
        return None

    try:
        return map[value]
    except KeyError:
        logging.error(f"Unmapped value: '{value}'\n{trace_str()}\n-----")
        return default(value)


def to_string_val(value) -> Union[str, None]:
    """ Converts a value to a string. """

    if value is None:
        return None

    return str(value)


def to_string_set(value: Sequence) -> Union[ArrayStringSet, None]:
    """ Converts an iterable to a string set. """

    if value is None:
        return None

    return ArrayStringSet(list({to_string_val(v) for v in value}))
