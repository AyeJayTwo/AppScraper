import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import io
from database.db_utils import get_all_ratings, save_rating, get_all_retailers, update_retailer, delete_retailer
from database.models import init_db, RetailerRating
from utils.retailer_ratings import RetailerRatings

# Initialize database
init_db()

st.set_page_config(
    page_title="Retailer App Ratings Dashboard",
    page_icon="📱",
    layout="wide"
)

st.title("📱 Retailer App Ratings Dashboard")

# Sidebar for CSV upload
st.sidebar.header("Upload Retailer Data")
uploaded_file = st.sidebar.file_uploader("Upload CSV file", type=['csv'])

if uploaded_file is not None:
    try:
        # Read the CSV file
        df = pd.read_csv(uploaded_file)
        required_columns = ['retailer_name', 'ios_url', 'android_url']
        
        if all(col in df.columns for col in required_columns):
            st.sidebar.success("CSV file uploaded successfully!")
            
            # Process the CSV file
            if st.sidebar.button("Process CSV"):
                processor = RetailerRatings()
                # Save the uploaded file temporarily
                temp_file = "temp_retailers.csv"
                df.to_csv(temp_file, index=False)
                
                # Process the CSV
                results = processor.process_csv(temp_file)
                
                if results:
                    st.sidebar.success(f"Processed {len(results)} retailers!")
                    # Refresh the page to show new data
                    st.rerun()
                else:
                    st.sidebar.error("No results were processed. Check the logs for errors.")
        else:
            st.sidebar.error("CSV must contain columns: retailer_name, ios_url, android_url")
    except Exception as e:
        st.sidebar.error(f"Error processing CSV: {str(e)}")

# Main content area
tab1, tab2, tab3 = st.tabs(["Latest Ratings", "Historical Data", "Manage Retailers"])

with tab1:
    st.header("Latest Ratings")
    
    # Get latest ratings
    ratings = get_all_ratings()
    if ratings:
        # Convert to DataFrame
        df = pd.DataFrame(ratings)
        
        # Get latest rating for each retailer
        latest_ratings = df.sort_values('date').groupby('retailer_name').last().reset_index()
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Retailers", len(latest_ratings))
        with col2:
            # Calculate weighted average for iOS
            total_ios_reviews = latest_ratings['ios_reviews'].sum()
            weighted_ios_avg = (latest_ratings['ios_score'] * latest_ratings['ios_reviews']).sum() / total_ios_reviews if total_ios_reviews > 0 else 0
            st.metric("Average iOS Rating", f"{weighted_ios_avg:.2f}")
        with col3:
            # Calculate weighted average for Android
            total_android_reviews = latest_ratings['android_reviews'].sum()
            weighted_android_avg = (latest_ratings['android_score'] * latest_ratings['android_reviews']).sum() / total_android_reviews if total_android_reviews > 0 else 0
            st.metric("Average Android Rating", f"{weighted_android_avg:.2f}")
        with col4:
            # Calculate overall average using weighted averages
            total_weighted_avg = latest_ratings['weighted_average'].mean()
            st.metric("Overall Average Rating", f"{total_weighted_avg:.2f}")
        
        # Create bar chart for latest ratings
        fig = px.bar(
            latest_ratings,
            x='retailer_name',
            y=['ios_score', 'android_score', 'weighted_average'],
            title="Latest App Ratings by Retailer",
            barmode='group',
            labels={'value': 'Rating', 'variable': 'Platform'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Display detailed table with refresh button
        st.subheader("Detailed Ratings")
        
        # Add refresh button
        if st.button("🔄 Refresh All Retailer Data"):
            processor = RetailerRatings()
            success_count = 0
            error_count = 0
            
            # Create a progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Process each retailer
            for i, retailer in enumerate(latest_ratings.itertuples()):
                status_text.text(f"Processing {retailer.retailer_name}...")
                try:
                    result = processor.process_retailer(
                        retailer.retailer_name,
                        retailer.ios_url,
                        retailer.android_url
                    )
                    if result:
                        success_count += 1
                    else:
                        error_count += 1
                except Exception as e:
                    st.error(f"Error processing {retailer.retailer_name}: {str(e)}")
                    error_count += 1
                
                # Update progress
                progress_bar.progress((i + 1) / len(latest_ratings))
            
            # Show completion message
            if success_count > 0:
                st.success(f"Successfully refreshed {success_count} retailers!")
            if error_count > 0:
                st.error(f"Failed to refresh {error_count} retailers.")
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
            # Refresh the page to show new data
            st.rerun()
        
        # Format the date column and add color coding
        latest_ratings['last_refreshed'] = pd.to_datetime(latest_ratings['date']).dt.strftime('%Y-%m-%d %H:%M')
        latest_ratings['days_since_refresh'] = (datetime.now() - pd.to_datetime(latest_ratings['date'])).dt.days
        
        # Create a styled DataFrame
        def style_refresh_date(s):
            days = latest_ratings['days_since_refresh']
            return ['color: green' if d <= 20 else 'color: red' for d in days]
        
        # Display the table with color-coded dates
        display_df = latest_ratings[[
            'retailer_name', 'ios_score', 'ios_reviews',
            'android_score', 'android_reviews', 'weighted_average',
            'last_refreshed'
        ]]
        
        st.dataframe(
            display_df.style.format({
                'ios_score': '{:.2f}',
                'android_score': '{:.2f}',
                'weighted_average': '{:.2f}'
            }).apply(style_refresh_date, subset=['last_refreshed']).hide(axis='index')
        )
    else:
        st.info("No ratings data available. Please upload a CSV file to get started.")

with tab2:
    st.header("Historical Data")
    
    if ratings:
        # Convert to DataFrame
        df = pd.DataFrame(ratings)
        df['date'] = pd.to_datetime(df['date'])
        
        # Date range selector
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=df['date'].min().date(),
                min_value=df['date'].min().date(),
                max_value=df['date'].max().date()
            )
        with col2:
            end_date = st.date_input(
                "End Date",
                value=df['date'].max().date(),
                min_value=df['date'].min().date(),
                max_value=df['date'].max().date()
            )
        
        # Filter data by date range
        mask = (df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)
        filtered_df = df[mask]
        
        # Create time series plot
        fig = px.line(
            filtered_df,
            x='date',
            y=['ios_score', 'android_score', 'weighted_average'],
            color='retailer_name',
            title="Rating Trends Over Time",
            labels={'value': 'Rating', 'variable': 'Platform'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Display historical data table
        st.subheader("Historical Data Table")
        st.dataframe(
            filtered_df.sort_values('date', ascending=False)[[
                'retailer_name', 'date', 'ios_score', 'ios_reviews',
                'android_score', 'android_reviews', 'weighted_average'
            ]].style.format({
                'ios_score': '{:.2f}',
                'android_score': '{:.2f}',
                'weighted_average': '{:.2f}'
            })
        )
    else:
        st.info("No historical data available. Please upload a CSV file to get started.")

with tab3:
    st.header("Manage Retailers")
    
    # Get all retailers
    retailers = get_all_retailers()
    
    # Add new retailer
    st.subheader("Add New Retailer")
    with st.form("add_retailer_form"):
        new_name = st.text_input("Retailer Name")
        new_ios_url = st.text_input("iOS App URL")
        new_android_url = st.text_input("Android App URL")
        submitted = st.form_submit_button("Add Retailer")
        
        if submitted and new_name and new_ios_url and new_android_url:
            try:
                processor = RetailerRatings()
                result = processor.process_retailer(new_name, new_ios_url, new_android_url)
                if result:
                    st.success(f"Successfully added {new_name}")
                    st.rerun()
                else:
                    st.error("Failed to add retailer. Please check the URLs.")
            except Exception as e:
                st.error(f"Error adding retailer: {str(e)}")
    
    # Edit/Delete existing retailers
    st.subheader("Edit/Delete Retailers")
    if retailers:
        for retailer in retailers:
            with st.expander(f"📱 {retailer['retailer_name']}"):
                with st.form(f"edit_retailer_{retailer['retailer_name']}"):
                    edited_name = st.text_input("Retailer Name", value=retailer['retailer_name'], key=f"name_{retailer['retailer_name']}")
                    edited_ios_url = st.text_input("iOS App URL", value=retailer['ios_url'], key=f"ios_{retailer['retailer_name']}")
                    edited_android_url = st.text_input("Android App URL", value=retailer['android_url'], key=f"android_{retailer['retailer_name']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("Update"):
                            try:
                                update_retailer(retailer['retailer_name'], {
                                    'retailer_name': edited_name,
                                    'ios_url': edited_ios_url,
                                    'android_url': edited_android_url
                                })
                                st.success("Retailer updated successfully!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error updating retailer: {str(e)}")
                    with col2:
                        if st.form_submit_button("Delete"):
                            try:
                                delete_retailer(retailer['retailer_name'])
                                st.success("Retailer deleted successfully!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error deleting retailer: {str(e)}")
    else:
        st.info("No retailers found. Add some using the form above.") 