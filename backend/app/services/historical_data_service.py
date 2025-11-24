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
        
        The DataFrame is cached in memory (self._df) to avoid repeated disk I/O.
        
        Assumptions:
        - CSV has a 'Date' column (case-insensitive search for 'date').
        - Other columns are currency pairs (e.g., 'EURUSD', 'EUR/USD').
        - Columns will be normalized to uppercase without separators (e.g., 'EUR/USD' -> 'EURUSD').
        
        Returns:
            pd.DataFrame: DataFrame containing historical rates with DatetimeIndex.
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
            
            # Find date column (case-insensitive)
            date_col = next((col for col in df.columns if col.lower() == 'date'), None)
            if not date_col:
                raise ValueError("CSV must contain a 'Date' column")

            # Parse dates
            df[date_col] = pd.to_datetime(df[date_col])
            df.set_index(date_col, inplace=True)
            df.sort_index(inplace=True)

            # Normalize column names: 'EUR/USD' -> 'EURUSD'
            # Also ensure numeric types
            clean_columns = {}
            for col in df.columns:
                clean_name = col.upper().replace('/', '').replace('_', '').strip()
                clean_columns[col] = clean_name
            
            df.rename(columns=clean_columns, inplace=True)
            
            # Filter to keep only numeric columns (actual rates)
            # This handles cases where there might be other metadata columns
            numeric_cols = df.select_dtypes(include=['number']).columns
            df = df[numeric_cols]

            self._df = df
            logger.info(f"Successfully loaded {len(df)} rows and {len(df.columns)} pairs.")
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
        
        if normalized_pair not in df.columns:
            logger.warning(f"Pair {normalized_pair} not found in historical data.")
            return pd.DataFrame()

        # Return as DataFrame with standard 'rate' column
        pair_data = df[[normalized_pair]].copy()
        pair_data.columns = ['rate']
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

# Singleton instance
_service_instance = None

def get_historical_data_service() -> HistoricalDataService:
    """Get or create the global HistoricalDataService instance."""
    global _service_instance
    if _service_instance is None:
        _service_instance = HistoricalDataService()
    return _service_instance
