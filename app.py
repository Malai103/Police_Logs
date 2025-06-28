import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px

# Database Connection
def Create_connection():
    try:
        connection = psycopg2.connect(
            user="postgres",          
            password="malai123",
            host="localhost",
            port="5432",
            database="postgres"
        )
        return connection
    except Exception as e:
        st.error(f"Database Connection Error: {e}")
        return None

# Fetch data from database 
def fetch_data(query):
    connection = Create_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                # get column names from cursor
                columns = [desc[0] for desc in cursor.description]
                df = pd.DataFrame(result, columns=columns)  # assign column names
                return df
        finally:
            connection.close()
    else:
        return pd.DataFrame()

# Streamlit UI
st.set_page_config(page_title="🚓 Securecheck police dashboard", layout="wide")

st.title("🚨 Police check post Digital Ledger")
st.markdown("👮📄")

# Show full table
st.header("📄 Police Logs Overview")
query = "SELECT * FROM traffic_logs"
data = fetch_data(query)
st.dataframe(data, use_container_width=True)

# Quick Metrics
st.header("📈 Core Metric")

# add columns
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_stops = data.shape[0]
    st.metric("Total Police Stops",total_stops)

with col2:
    arrests = data[data["stop_outcome"].str.contains("Arrest", case=False, na=False)].shape[0]
    st.metric("Total Arrest", arrests)    

with col3:
    warnings = data[data['stop_outcome'].str.contains("warning", case=False, na=False)].shape[0]
    st.metric("Total Warnings", warnings)

with col4:
    drug_related = data[data['drugs_related_stop'] == 1].shape[0]
    st.metric("Drug Related Stops", drug_related)

# Adavanced Queries
st.header("🔎 Advanced Insights")

Selected_Query = st.selectbox("Select a Query To Run",[
    "the top 10 vehicle_Number involved in drug-related stops?",
    "Which vehicles were most frequently searched?",
    "Which driver age group had the highest arrest rate?",
    "What is the gender distribution of drivers stopped in each country?",
    "Which race and gender combination has the highest search rate?",
    "What time of day sees the most traffic stops?",
    "What is the average stop duration for different violations?",
    "Are stops during the night more likely to lead to arrests?",
    "Which violations are most associated with searches or arrests?",
    "Which violations are most common among younger drivers (<25)?",
    "Is there a violation that rarely results in search or arrest?",
    "Which countries report the highest rate of drug-related stops?",
    "What is the arrest rate by country and violation?",
    "Which country has the most stops with search conducted?",
    "Yearly Breakdown of Stops and Arrests by Country",
    "Driver Violation Trends Based on Age and Race",
    "Time Period Analysis of Stops",
    "Violations with High Search and Arrest Rates",
    "Driver Demographics by Country",
    "Top 5 Violations with Highest Arrest Rates"

])

Query_map = {"the top 10 vehicle_Number involved in drug-related stops?": """
SELECT vehicle_number, COUNT(*) AS stop_count
FROM traffic_logs
WHERE drugs_related_stop = TRUE
GROUP BY vehicle_number
ORDER BY stop_count DESC
LIMIT 10;
""","Which vehicles were most frequently searched?": """
SELECT vehicle_number, COUNT(*) AS search_count
FROM traffic_logs
WHERE search_conducted = TRUE
GROUP BY vehicle_number
ORDER BY search_count DESC
LIMIT 10;
""",
    "Which driver age group had the highest arrest rate?": """
SELECT
    CASE
        WHEN driver_age < 25 THEN 'Under 25'
        WHEN driver_age BETWEEN 25 AND 40 THEN '25-40'
        ELSE 'Over 40'
    END AS age_group,
    ROUND(AVG(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) * 100, 2) AS arrest_rate_percentage
FROM traffic_logs
GROUP BY age_group
ORDER BY arrest_rate_percentage DESC
LIMIT 1;
""",
    "What is the gender distribution of drivers stopped in each country?":"""
SELECT
    country_name,
    driver_gender,
    COUNT(*) AS total_count
FROM traffic_logs
GROUP BY country_name, driver_gender
ORDER BY country_name, total_count DESC;
""",
    "Which race and gender combination has the highest search rate?":"""
SELECT
    driver_gender,
    ROUND(AVG(CASE WHEN search_conducted = TRUE THEN 1 ELSE 0 END) * 100, 2) AS search_rate_percentage
FROM traffic_logs
GROUP BY driver_gender
ORDER BY search_rate_percentage DESC
LIMIT 2;
""",
    "What time of day sees the most traffic stops?": """
SELECT
    EXTRACT(HOUR FROM stop_datetime) AS hour_of_day,
    COUNT(*) AS stop_count
FROM traffic_logs
GROUP BY hour_of_day
ORDER BY stop_count DESC
LIMIT 1;
""",
    "What is the average stop duration for different violations?": """
SELECT
    violation,
    ROUND(AVG(duration_minutes)::numeric, 2) AS avg_stop_minutes
FROM (
    SELECT
        violation,
        CASE 
            WHEN stop_duration ~ '^[0-9]+-[0-9]+' THEN
                (
                    CAST(split_part(stop_duration, '-', 1) AS FLOAT) + 
                    CAST(split_part(split_part(stop_duration, ' ', 1), '-', 2) AS FLOAT)
                ) / 2
            WHEN stop_duration ~ '^[0-9]+' THEN
                CAST(regexp_replace(stop_duration, '[^0-9]', '', 'g') AS FLOAT)
            ELSE NULL
        END AS duration_minutes
    FROM traffic_logs
    WHERE stop_duration IS NOT NULL
) AS parsed
WHERE duration_minutes IS NOT NULL
GROUP BY violation
ORDER BY avg_stop_minutes DESC;
""",
    "Are stops during the night more likely to lead to arrests?": """
SELECT
    CASE 
        WHEN EXTRACT(HOUR FROM stop_datetime) >= 20 OR EXTRACT(HOUR FROM stop_datetime) < 6 
        THEN 'Night'
        ELSE 'Day'
    END AS time_of_day,
    ROUND(AVG(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) * 100, 2) AS arrest_rate_percentage,
    COUNT(*) AS total_stops
FROM traffic_logs
GROUP BY time_of_day
ORDER BY arrest_rate_percentage DESC;
""",
    "Which violations are most associated with searches or arrests?": """
SELECT
    violation,
    ROUND(AVG(CASE WHEN search_conducted = TRUE THEN 1 ELSE 0 END) * 100, 2) AS search_rate,
    ROUND(AVG(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) * 100, 2) AS arrest_rate,
    COUNT(*) AS total_stops
FROM traffic_logs
GROUP BY violation
ORDER BY (
    AVG(CASE WHEN search_conducted = TRUE THEN 1 ELSE 0 END) * 100 +
    AVG(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) * 100
) DESC
LIMIT 10;
""",
    "Which violations are most common among younger drivers (<25)?": """
SELECT
    violation,
    COUNT(*) AS total_count
FROM traffic_logs
WHERE driver_age < 25
GROUP BY violation
ORDER BY total_count DESC
LIMIT 10;
""",
    "Is there a violation that rarely results in search or arrest?": """
SELECT
    violation,
    ROUND(AVG(CASE WHEN search_conducted = TRUE THEN 1 ELSE 0 END) * 100, 2) AS search_rate,
    ROUND(AVG(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) * 100, 2) AS arrest_rate,
    COUNT(*) AS total_count
FROM traffic_logs
GROUP BY violation
ORDER BY (
    AVG(CASE WHEN search_conducted = TRUE THEN 1 ELSE 0 END) * 100 +
    AVG(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) * 100
) ASC
LIMIT 10;
""",
    "Which countries report the highest rate of drug-related stops?": """
SELECT
    country_name,
    ROUND(AVG(CASE WHEN drugs_related_stop = TRUE THEN 1 ELSE 0 END) * 100, 2) AS drug_related_rate,
    COUNT(*) AS total_stops
FROM traffic_logs
GROUP BY country_name
ORDER BY drug_related_rate DESC
LIMIT 10;
""",
    "What is the arrest rate by country and violation?": """
SELECT
    country_name,
    violation,
    ROUND(AVG(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) * 100, 2) AS arrest_rate,
    COUNT(*) AS total_stops
FROM traffic_logs
GROUP BY country_name, violation
ORDER BY arrest_rate DESC
LIMIT 10;
""",
    "Which country has the most stops with search conducted?": """
SELECT
    country_name,
    COUNT(*) AS total_searches
FROM traffic_logs
WHERE search_conducted = TRUE
GROUP BY country_name
ORDER BY total_searches DESC
LIMIT 5;
""",
    "Yearly Breakdown of Stops and Arrests by Country": """
WITH yearly_data AS (
    SELECT
        country_name,
        EXTRACT(YEAR FROM stop_datetime) AS year,
        COUNT(*) AS total_stops,
        SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) AS total_arrests
    FROM traffic_logs
    GROUP BY country_name, EXTRACT(YEAR FROM stop_datetime)
)
SELECT
    country_name,
    year,
    total_stops,
    total_arrests,
    ROUND((total_arrests::DECIMAL / total_stops) * 100, 2) AS arrest_rate_percentage,
    RANK() OVER (PARTITION BY year ORDER BY total_stops DESC) AS rank_by_year
FROM yearly_data
ORDER BY year, rank_by_year;
""",
    "Driver Violation Trends Based on Age and Race": """
WITH age_groups AS (
    SELECT
        CASE
            WHEN driver_age < 25 THEN 'Under 25'
            WHEN driver_age BETWEEN 25 AND 40 THEN '25–40'
            ELSE 'Over 40'
        END AS age_group,
        country_name,
        violation,
        COUNT(*) AS total_count
    FROM traffic_logs
    GROUP BY 1, 2, 3
)

SELECT
    age_group,
    country_name,
    violation,
    total_count,
    RANK() OVER (PARTITION BY age_group, country_name ORDER BY total_count DESC) AS rank_in_group
FROM age_groups
ORDER BY age_group, country_name, rank_in_group
LIMIT 20;
""",
    "Time Period Analysis of Stops": """
SELECT
    EXTRACT(YEAR FROM stop_datetime) AS year,
    EXTRACT(MONTH FROM stop_datetime) AS month,
    EXTRACT(HOUR FROM stop_datetime) AS hour,
    COUNT(*) AS total_stops
FROM traffic_logs
GROUP BY 1, 2, 3
ORDER BY year, month, hour;
""",
    "Violations with High Search and Arrest Rates": """
WITH stats AS (
    SELECT
        violation,
        ROUND(AVG(CASE WHEN search_conducted = TRUE THEN 1 ELSE 0 END) * 100, 2) AS search_rate,
        ROUND(AVG(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) * 100, 2) AS arrest_rate
    FROM traffic_logs
    GROUP BY violation
),
ranked AS (
    SELECT
        violation,
        search_rate,
        arrest_rate,
        (search_rate + arrest_rate) AS combined_rate,
        RANK() OVER (ORDER BY (search_rate + arrest_rate) DESC) AS rate_rank
    FROM stats
)
SELECT *
FROM ranked
ORDER BY rate_rank
LIMIT 10;
""",
    "Driver Demographics by Country": """
WITH age_groups AS (
    SELECT
        country_name,
        CASE
            WHEN driver_age < 25 THEN 'Under 25'
            WHEN driver_age BETWEEN 25 AND 40 THEN '25-40'
            ELSE 'Over 40'
        END AS age_group,
        driver_gender,
        COUNT(*) AS total_count
    FROM traffic_logs
    GROUP BY country_name, age_group, driver_gender
)
SELECT
    country_name,
    age_group,
    driver_gender,
    total_count,
    ROUND(100.0 * total_count / SUM(total_count) OVER (PARTITION BY country_name), 2) AS percentage_in_country
FROM age_groups
ORDER BY country_name, age_group, driver_gender;
""",
    "Top 5 Violations with Highest Arrest Rates": """
SELECT
    violation,
    ROUND(AVG(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) * 100, 2) AS arrest_rate,
    COUNT(*) AS total_stops
FROM traffic_logs
GROUP BY violation
ORDER BY arrest_rate DESC
LIMIT 5;
"""}

if st.button("Run Query"):
    result = fetch_data (Query_map[Selected_Query])
    if not result.empty:
        st.write(result)
    else:
        st.warning("No result found for the selected query ")    




# Load Excel data
@st.cache_data
def load_data(file_path):
    df = pd.read_excel(file_path, dtype=str)
    df["driver_age"] = pd.to_numeric(df["driver_age"], errors="coerce")
    df["is_arrested"] = df["is_arrested"] == "True"
    df["search_conducted"] = df["search_conducted"] == "True"
    df["drugs_related_stop"] = df["drugs_related_stop"] == "True"
    df["stop_datetime"] = pd.to_datetime(df["stop_datetime"])
    return df

st.title("🚔 Traffic Logs Lookup")

data = load_data("traffic_stops_cleaned data.xlsx")

vehicle_number = st.text_input("Enter Vehicle Number:").strip()

if vehicle_number:
    matches = data[data["vehicle_number"].str.contains(vehicle_number, case=False, na=False)]
    if not matches.empty:
        for _, row in matches.iterrows():
            time_str = row["stop_datetime"].strftime("%I:%M %p") if pd.notnull(row["stop_datetime"]) else "unknown time"
            description = (
                f"A {int(row['driver_age'])}-year-old {row['driver_gender']} driver was stopped for {row['violation']} at {time_str}. "
                f"{'A search was conducted' if row['search_conducted'] else 'No search was conducted'}, "
                f"received a {row['stop_outcome'].lower() if pd.notnull(row['stop_outcome']) else 'no outcome'}. "
                f"The stop lasted {row['stop_duration'].lower() if pd.notnull(row['stop_duration']) else 'unknown duration'} "
                f"and was {'drug-related' if row['drugs_related_stop'] else 'not drug-related'}."
            )
            st.write(description)
    else:
        st.warning("No record found for vehicle number: " + vehicle_number)
else:
    st.info("Enter a vehicle number to search.")



       