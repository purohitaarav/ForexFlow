"""
Historical Data Service

Handles loading and querying of historical Forex data from CSV.
Provides caching and efficient data access for backtesting and analysis.
"""
import os
import logging
from typing import List, Optional, Dict, Union
from datetime import date, datetime

import pandas as pd

logger = logging.getLogger(__name__)

# Default path relative to the backend root
DEFAULT_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "daily_forex_rates.csv")

class HistoricalDataService:
    """
    Service for managing historical forex data.
    """

    def __init__(self, csv_path: str = DEFAULT_DATA_PATH):
        self.csv_path = csv_path
        self._df: Optional[pd.DataFrame] = None

    def load_historical_data(self) -> pd.DataFrame:
        """
        Load historical data from CSV into a pandas DataFrame.

        The source CSV is structured as long-form records with columns:
        [currency, base_currency, currency_name, exchange_rate, date].

        During loading we pivot the dataset to obtain a wide DataFrame where each
        column is a currency (quoted against the base currency, typically EUR)
        and each row is a date.

        Returns:
            pd.DataFrame: Pivoted DataFrame of currency rates indexed by date.
        """
        if self._df is not None:
            return self._df

        if not os.path.exists(self.csv_path):
            logger.error(f"Historical data file not found at: {self.csv_path}")
            # Return empty DF structure if file missing, to avoid crashing immediately
            return pd.DataFrame()

        try:
            logger.info(f"Loading historical data from {self.csv_path}")
            df = pd.read_csv(self.csv_path)

            # Normalize column names for consistent access
            df.columns = [col.strip().upper() for col in df.columns]

            required_columns = {"CURRENCY", "BASE_CURRENCY", "EXCHANGE_RATE", "DATE"}
            if not required_columns.issubset(df.columns):
                missing = required_columns - set(df.columns)
                raise ValueError(
                    "CSV must contain columns: currency, base_currency, exchange_rate, date. "
                    f"Missing: {', '.join(sorted(missing))}"
                )

            # Parse dates and ensure chronological order
            df["DATE"] = pd.to_datetime(df["DATE"])
            df.sort_values("DATE", inplace=True)

            # Pivot to get one column per currency (quoted vs base currency)
            pivot = df.pivot_table(
                index="DATE",
                columns="CURRENCY",
                values="EXCHANGE_RATE",
                aggfunc="last"
            )

            pivot.sort_index(inplace=True)

            self._df = pivot
            logger.info(
                "Successfully loaded %s rows and %s currencies.",
                len(pivot),
                len(pivot.columns)
            )
            return self._df

        except Exception as e:
            logger.error(f"Failed to load historical data: {e}")
            raise

    def get_available_pairs(self, df: pd.DataFrame) -> List[str]:
        """
        Get list of available currency pairs in the dataset.

        Args:
            df: The loaded historical DataFrame.

        Returns:
            List[str]: List of column names representing currency pairs (e.g. ['EURUSD', 'GBPUSD']).
        """
        if df is None or df.empty:
            return []
        return df.columns.tolist()

    def get_pair_history(self, df: pd.DataFrame, pair: str) -> pd.DataFrame:
        """
        Get historical data for a specific currency pair.

        Args:
            df: The loaded historical DataFrame.
            pair: The currency pair symbol (e.g. 'EURUSD').

        Returns:
            pd.DataFrame: DataFrame with columns ['rate'], indexed by Date.
                          Returns empty DataFrame if pair not found.
        """
        if df is None or df.empty:
            return pd.DataFrame()

        normalized_pair = pair.upper().replace('/', '').strip()

        base_currency = normalized_pair[:3]
        quote_currency = normalized_pair[3:]

        base_series = self._get_currency_series(df, base_currency)
        quote_series = self._get_currency_series(df, quote_currency)

        if base_series.empty or quote_series.empty:
            logger.warning(
                "Unable to compute pair %s: missing currency data (base=%s, quote=%s)",
                normalized_pair,
                base_currency,
                quote_currency
            )
            return pd.DataFrame()

        rate_series = (quote_series / base_series).dropna()

        if rate_series.empty:
            logger.warning("No overlapping data available for pair %s", normalized_pair)
            return pd.DataFrame()

        pair_data = rate_series.to_frame(name='rate')
        return pair_data

    def get_window(self, df: pd.DataFrame, pair: str, end_date: Union[date, datetime], window_size: int) -> pd.DataFrame:
        """
        Get a window of historical data ending at a specific date.

        Args:
            df: The loaded historical DataFrame.
            pair: The currency pair symbol.
            end_date: The last date of the window (inclusive).
            window_size: Number of trading days to include.

        Returns:
            pd.DataFrame: DataFrame containing the window of data with 'rate' column.
                          Returns available data if window_size exceeds history.
        """
        # Get full history for pair first
        pair_df = self.get_pair_history(df, pair)
        if pair_df.empty:
            return pair_df

        # Ensure end_date is a timestamp for comparison
        ts_end = pd.Timestamp(end_date)
        
        # Filter data up to end_date
        # We use loc with a slice. Since index is sorted, this is efficient.
        # Note: We want rows WHERE date <= end_date
        filtered_df = pair_df.loc[:ts_end]
        
        if filtered_df.empty:
            return pd.DataFrame()

        # Take the last window_size rows
        return filtered_df.tail(window_size)

    def _get_currency_series(self, df: pd.DataFrame, currency: str) -> pd.Series:
        """Return the time series for a specific currency quoted against the base currency."""
        if df is None or df.empty:
            return pd.Series(dtype=float)

        code = currency.upper()

        if code == "EUR":
            # Base currency is EUR in the historical dataset; return series of ones.
            return pd.Series(1.0, index=df.index)

        if code not in df.columns:
            logger.warning("Currency %s not found in historical data.", code)
            return pd.Series(dtype=float)

        return df[code]

# Singleton instance
_service_instance = None

def get_historical_data_service() -> HistoricalDataService:
    """Get or create the global HistoricalDataService instance."""
    global _service_instance
    if _service_instance is None:
        _service_instance = HistoricalDataService()
    return _service_instance
