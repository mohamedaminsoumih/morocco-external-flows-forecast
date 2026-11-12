"""Calendar effects specific to Morocco: Eid holidays and COVID.

Eid moves about 11 days earlier every year (Hijri calendar), so it falls
in a different Gregorian month over time. Remittances and travel spike
around Eid, so a model that only knows "the month" misses this effect.
"""

import pandas as pd
from hijridate import Hijri

# Hijri years covering 1999 to 2030
HIJRI_YEARS = range(1420, 1452)

# Borders closed in March 2020, reopened in February 2022
COVID_START = pd.Timestamp("2020-03-01")
COVID_END = pd.Timestamp("2022-01-01")


def _eid_months(hijri_month: int, hijri_day: int) -> set[tuple[int, int]]:
    """(year, month) of every Gregorian month containing this Eid."""
    months = set()
    for year in HIJRI_YEARS:
        day = Hijri(year, hijri_month, hijri_day).to_gregorian()
        months.add((day.year, day.month))
    return months


EID_AL_FITR = _eid_months(hijri_month=10, hijri_day=1)
EID_AL_ADHA = _eid_months(hijri_month=12, hijri_day=10)


def covid_flag(index: pd.DatetimeIndex) -> pd.Series:
    """1 during the COVID border closures, 0 otherwise."""
    flag = (index >= COVID_START) & (index <= COVID_END)
    return pd.Series(flag.astype(int), index=index)


def calendar_features(index: pd.DatetimeIndex) -> pd.DataFrame:
    """Month number, Eid months and COVID flag for each date."""
    months = list(zip(index.year, index.month))
    return pd.DataFrame(
        {
            "month": index.month,
            "eid_al_fitr": [int(m in EID_AL_FITR) for m in months],
            "eid_al_adha": [int(m in EID_AL_ADHA) for m in months],
            "covid": covid_flag(index),
        },
        index=index,
    )
