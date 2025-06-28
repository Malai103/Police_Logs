# Police_Logs 
# First data cleaning process started
# Install all required libiraries
# Load Data: Reads the Excel file into a pandas DataFrame (logs_df).
# Explore Columns: Checks unique counts of violation_raw and violation columns.
# Drop Unwanted Columns: Removes violation_raw, driver_age_raw, and driver_race columns.
# Merge Date and Time: Combines stop_date and stop_time columns into a single stop_datetime column, converts it to datetime type, and drops the original stop_date and stop_time columns.
# Clean driver_gender: Removes spaces, converts values to uppercase, and maps 'M' to 'Male' and 'F' to 'Female'.
# Standardize stop_duration: Strips spaces and converts values to lowercase.
# Check Missing Values: Displays missing value counts before and after cleaning.
# Handle search_type: Shows counts (including missing), then fills missing search_type values with 'No Search'.
# Save Cleaned Data: Writes the cleaned dataset to a new Excel file traffic_stops_cleaned data.xlsx.
# Loads cleaned data from traffic_stops_cleaned data.xlsx into a DataFrame.
# Sets up PostgreSQL connection using SQLAlchemy with credentials.
# Uploads DataFrame to PostgreSQL database table traffic_logs.
# Specifies exact data types for each column to ensure correct type mapping in PostgreSQL.
# Prepares data for running medium-level and complex SQL queries in the database (aggregations, filters, joins, etc.).
# Connects to a PostgreSQL database and fetches traffic stop data into a DataFrame.
# Displays the full traffic logs table in a Streamlit app.
# Shows quick metrics: total stops, arrests, warnings, drug-related stops.
# Provides a dropdown with 20 advanced query options; runs selected query and displays results.
# Loads traffic stop data from an Excel file using @st.cache_data for vehicle lookups.
# Allows vehicle number lookup; shows details of matching stops in a human-readable format.
# Uses Plotly Express import (but not yet implemented in plots).



