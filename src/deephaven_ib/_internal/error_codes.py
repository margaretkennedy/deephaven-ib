"""Functionality for working with error codes."""

from typing import Dict, Tuple

import pandas as pd


def load_error_codes() -> Tuple[Dict[int, str], Dict[int, str]]:
    """Load dictionaries of error code messages and notes."""

    html_tables = pd.read_html('https://interactivebrokers.github.io/tws-api/message_codes.html')

    error_messages = {}
    error_notes = {}

    for df in html_tables:
        try:
            df = df.fillna('')
            codes = df['Code']
            messages = df['TWS message']
            notes = df['Additional notes']

            for code, message in zip(codes, messages):
                error_messages[code] = message

            for code, note in zip(codes, notes):
                error_notes[code] = note
        except KeyError:
            pass

    overrides = {
        0: "Warning: Approaching max rate of 50 messages per second",
        504: "Not connected",
        502: "Couldn't connect to TWS. Confirm that 'Enable ActiveX and Socket EClients' is enabled and connection port is the same as 'Socket Port' on the TWS 'Edit->Global Configuration...->API->Settings' menu. Live Trading ports: TWS: 7496; IB Gateway: 4001. Simulated Trading ports for new installations of version 954.1 or newer:  TWS: 7497; IB Gateway: 4002",
        2113: "The order size for Bonds (Bills) is entered as a nominal par value of the order, and must be a multiple",
        10187: "Failed to request historical ticks",
        10189: "Failed to request tick-by-tick data",
    }

    for k, v in overrides.items():
        if k not in error_messages:
            error_messages[k] = v
            error_notes[k] = ""

    return error_messages, error_notes
