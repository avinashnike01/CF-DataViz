import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io

# -----------------------------------------------------------------------------
# Configuration & Setup
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="CF Registry Dashboard",
    page_icon="fq",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# Utility Functions & Debugging
# -----------------------------------------------------------------------------
def debug_shape(label, df):
    """
    Abinash's Preferred Debugging Style:
    Prints the shape of the dataframe at specific steps to the console 
    to verify data integrity during processing.
    """
    print(f"[DEBUG] {label}: Data Shape = {df.shape}")
    print(f"[DEBUG] {label}: Columns = {df.columns.tolist()}")
    print("-" * 50)

def load_sample_data():
    """Generates the sample dataset provided in the prompt."""
    data = {
        "Record ID": [1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        "Centers": ["Center1", "Center2", "Center3", "Center4", "Center5", "Center6", "Center7", "Center8", "Center9",
                    "Center1", "Center2", "Center3", "Center4", "Center5", "Center6", "Center7", "Center8", "Center9"],
        "Country": ["Country1", "Country2", "Country3", "Country4", "Country5", "Country6", "Country7", "Country8", "Country9",
                    "Country1", "Country2", "Country3", "Country4", "Country5", "Country6", "Country7", "Country8", "Country9"],
        "Year": [2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024,
                 2025, 2025, 2025, 2025, 2025, 2025, 2025, 2025, 2025],
        "People in the Registry": [34, 33, 27, 44, 45, 9, 7, 20, 4, 17, 22, 18, 2, 28, 20, 21, 15, 23],
        "Total number of clinic visits": [42, 55, 44, 96, 82, 81, 63, 90, 15, 76, 82, 21, 55, 59, 79, 39, 93, 83],
        "Number of People with CF deceased": [0, 1, 10, 0, 4, 6, 9, 0, 5, 7, 4, 0, 2, 7, 9, 2, 3, 5],
        "Total number of hospitalization events": [23, 4, 23, 11, 16, 13, 3, 19, 1, 4, 9, 6, 18, 2, 16, 13, 0, 2],
        "Median FEV1% for 10 year olds": [38, 37, 37, 29, 39, 39, 45, 57, 15, 32, 37, 57, 57, 39, 11, 22, 32, 43],
        "Median FEV1% for 18 year olds": [22, 18, 28, 53, 27, 35, 15, 53, 43, 44, 55, 12, 52, 27, 46, 21, 60, 23],
        "Median WHO Weight-for-Length Percentile for patients less than 24 months": [24, 53, 57, 32, 46, 38, 51, 27, 16, 44, 45, 48, 31, 20, 51, 14, 16, 44],
        "Median BMI%ile 2-19 years": [38, 46, 22, 55, 31, 47, 34, 15, 58, 22, 49, 39, 44, 22, 14, 43, 55, 15],
        "Median BMI for patients 20 years and older": [58, 27, 25, 53, 26, 17, 42, 39, 44, 13, 31, 47, 53, 12, 45, 27, 57, 21],
        "Total number of patients qualifying for modulator therapy": [6, 15, 12, 17, 7, 17, 8, 18, 3, 9, 18, 1, 1, 16, 15, 19, 6, 3],
        "Total number of patients on modulator med": [6, 3, 4, 6, 5, 6, 4, 15, 3, 5, 12, 0, 1, 3, 12, 4, 2, 2]
    }
    df = pd.DataFrame(data)
    debug_shape("Sample Data Generation", df)
    return df

# -----------------------------------------------------------------------------
# Main Application Logic
# -----------------------------------------------------------------------------
def main():
    st.title("📊 Modern Clinical Registry Dashboard")
    st.markdown("### Interactive Analysis & Comparison (2024 vs 2025)")
    st.markdown("---")

    # --- Sidebar: Data Upload & Filters ---
    st.sidebar.header("Data Configuration")
    
    uploaded_file = st.sidebar.file_uploader("Upload Registry Data (CSV/Excel)", type=["csv", "xlsx"])
    
    df = None
    
    # Data Loading Logic
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            st.sidebar.success("File uploaded successfully!")
            debug_shape("File Upload", df)
        except Exception as e:
            st.sidebar.error(f"Error loading file: {e}")
    else:
        st.sidebar.info("Awaiting upload. Using built-in sample data for demonstration.")
        df = load_sample_data()

    if df is not None:
        # --- Preprocessing & Filters ---
        # Ensure correct types
        cols_to_numeric = [
            'People in the Registry', 'Total number of clinic visits', 
            'Number of People with CF deceased', 'Total number of hospitalization events',
            'Median FEV1% for 10 year olds', 'Median FEV1% for 18 year olds',
            'Median WHO Weight-for-Length Percentile for patients less than 24 months',
            'Median BMI%ile 2-19 years', 'Median BMI for patients 20 years and older',
            'Total number of patients qualifying for modulator therapy',
            'Total number of patients on modulator med'
        ]
        
        for col in cols_to_numeric:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # Filters
        countries = st.sidebar.multiselect(
            "Filter by Country", 
            options=df["Country"].unique(), 
            default=df["Country"].unique()
        )
        
        # Apply Filter
        df_filtered = df[df["Country"].isin(countries)].copy()
        debug_shape("After Country Filter", df_filtered)

        # --- Dashboard Metrics (Top Row) ---
        st.subheader("Key Performance Indicators (Aggregated)")
        kpi_cols = st.columns(4)
        
        total_patients = df_filtered["People in the Registry"].sum()
        total_visits = df_filtered["Total number of clinic visits"].sum()
        total_deceased = df_filtered["Number of People with CF deceased"].sum()
        modulator_use = df_filtered["Total number of patients on modulator med"].sum()

        kpi_cols[0].metric("Total Patients in Registry", f"{total_patients:,}")
        kpi_cols[1].metric("Total Clinic Visits", f"{total_visits:,}")
        kpi_cols[2].metric("Total Deceased", f"{total_deceased}")
        kpi_cols[3].metric("Patients on Modulators", f"{modulator_use:,}")

        st.markdown("---")

        # --- Visualizations ---
        st.subheader("Visual Analytics")
        
        tab1, tab2 = st.tabs(["Demographics & Status", "Clinical Outcomes"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            # Chart 1: Patients by Country per Year
            fig_country = px.bar(
                df_filtered, 
                x="Country", 
                y="People in the Registry", 
                color="Year", 
                barmode="group",
                title="Patients by Country & Year",
                text_auto=True,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            col1.plotly_chart(fig_country, use_container_width=True)
            
            # Chart 2: Modulator Therapy Gap
            # Reshaping for visualization
            df_mod = df_filtered.groupby("Year")[["Total number of patients qualifying for modulator therapy", "Total number of patients on modulator med"]].sum().reset_index()
            df_mod_melt = df_mod.melt(id_vars="Year", var_name="Status", value_name="Count")
            
            fig_mod = px.bar(
                df_mod_melt,
                x="Year",
                y="Count",
                color="Status",
                barmode="group",
                title="Modulator Therapy: Qualified vs. On Medication",
                color_discrete_sequence=["#FFD700", "#228B22"]
            )
            col2.plotly_chart(fig_mod, use_container_width=True)

        with tab2:
            # Clinical outcomes trends
            col3, col4 = st.columns(2)
            
            # Scatter: BMI vs FEV1 (18 yr olds)
            fig_scatter = px.scatter(
                df_filtered,
                x="Median BMI for patients 20 years and older",
                y="Median FEV1% for 18 year olds",
                color="Country",
                size="People in the Registry",
                hover_data=["Year", "Centers"],
                title="Correlation: BMI (>20yrs) vs FEV1 (18yrs)",
            )
            col3.plotly_chart(fig_scatter, use_container_width=True)
            
            # Box Plot distribution of FEV1
            fig_box = px.box(
                df_filtered,
                x="Year",
                y="Median FEV1% for 10 year olds",
                color="Year",
                points="all",
                title="Distribution of Median FEV1% (10 yr olds) Across Centers"
            )
            col4.plotly_chart(fig_box, use_container_width=True)

        st.markdown("---")

        # --- Specific Report Table Generation ---
        st.subheader("Comparative Report: 2024 vs 2025")
        
        # We need to construct the specific table format requested.
        # Logic: 
        # For Count columns: SUM
        # For Median/Percentile columns: MEAN (Average of Medians is the best approximation without raw data)
        
        years = sorted(df_filtered['Year'].unique())
        if len(years) < 2:
            st.warning("Data does not contain both 2024 and 2025 for comparison. Showing available data.")
            
        # Define aggregations
        agg_map = {
            'People in the Registry': 'sum',
            'Number of People with CF deceased': 'sum',
            'Total number of clinic visits': 'sum',
            'Total number of hospitalization events': 'sum',
            'Median FEV1% for 10 year olds': 'mean',
            'Median FEV1% for 18 year olds': 'mean',
            'Median WHO Weight-for-Length Percentile for patients less than 24 months': 'mean',
            'Median BMI%ile 2-19 years': 'mean',
            'Median BMI for patients 20 years and older': 'mean',
            'Total number of patients qualifying for modulator therapy': 'sum',
            'Total number of patients on modulator med': 'sum'
        }
        
        # Group by Year
        grouped = df_filtered.groupby('Year').agg(agg_map).T
        
        # Clean up columns if years are missing or present
        grouped.columns = [str(y) for y in grouped.columns]
        
        # Calculate 'Number of People with CF by Country' (Count of unique countries or Total sum?)
        # Based on the prompt's context, this row likely asks for the number of countries participating or is a header.
        # We will calculate the number of unique countries participating.
        unique_countries = df_filtered.groupby('Year')['Country'].nunique()
        
        # Create a display dataframe
        display_df = grouped.copy()
        
        # Add the Country Count row at the correct position (2nd row)
        # We'll create a new DataFrame to respect the order
        
        # Helper to safely get value
        def get_val(year, metric, data_df, operation="sum"):
            if str(year) not in data_df.columns: return 0
            return data_df.loc[metric, str(year)]

        report_data = []
        target_years = ['2024', '2025'] # Force these columns
        
        # Mapping prompt row names to dataframe keys
        rows_config = [
            ("People in the Registry", "People in the Registry", "sum"),
            ("Number of People with CF by Country (Count of Countries)", "Country_Count_Special", "special"), # Modified label for clarity
            ("Number of People with CF deceased", "Number of People with CF deceased", "sum"),
            ("Total number of clinic visits", "Total number of clinic visits", "sum"),
            ("Total number of hospitalization events", "Total number of hospitalization events", "sum"),
            ("Median FEV1% for 10 year olds", "Median FEV1% for 10 year olds", "mean"),
            ("Median FEV1% for 18 year olds", "Median FEV1% for 18 year olds", "mean"),
            ("Median WHO Weight-for-Length Percentile (<24mo)", "Median WHO Weight-for-Length Percentile for patients less than 24 months", "mean"),
            ("Median BMI%ile 2-19 years", "Median BMI%ile 2-19 years", "mean"),
            ("Median BMI for patients 20 years and older", "Median BMI for patients 20 years and older", "mean"),
            ("Total number of patients qualifying for modulator therapy", "Total number of patients qualifying for modulator therapy", "sum"),
            ("Total number of patients on modulator med", "Total number of patients on modulator med", "sum"),
        ]

        for label, col_key, op in rows_config:
            row_dict = {"Category": label}
            for y in target_years:
                # Filter strictly for calculation if needed, but we have 'grouped' already.
                # However, grouped only has the columns present in data.
                
                val = 0
                if col_key == "Country_Count_Special":
                    # Special logic for country count
                    if int(y) in unique_countries.index:
                        val = unique_countries[int(y)]
                else:
                    if y in grouped.columns:
                        val = grouped.loc[col_key, y]
                
                # Formatting
                if "Median" in label:
                    row_dict[y] = f"{val:.1f}" # 1 decimal for medians
                else:
                    row_dict[y] = f"{int(val):,}" # Int format for counts
            
            report_data.append(row_dict)

        final_report_df = pd.DataFrame(report_data)
        
        # Display the table with styling
        st.dataframe(
            final_report_df, 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "Category": st.column_config.TextColumn("Metric Category", width="medium"),
                "2024": st.column_config.TextColumn("2024", width="small"),
                "2025": st.column_config.TextColumn("2025", width="small")
            }
        )
        
        debug_shape("Final Report Table", final_report_df)

        # --- Raw Data Expander ---
        with st.expander("View Raw Data"):
            st.dataframe(df_filtered)

if __name__ == "__main__":
    main()
