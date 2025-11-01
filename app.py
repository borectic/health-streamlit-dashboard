import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from database import get_users, get_daily_records, get_daily_tasks

st.set_page_config(page_title="Health Dashboard", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .stMetric > label {
        font-size: 14px !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

st.title('🏥 Health & Wellness Dashboard')
st.markdown("---")

# Fetch data with error handling
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_data():
    try:
        users_df = get_users()
        daily_records_df = get_daily_records()
        daily_tasks_df = get_daily_tasks()
        return users_df, daily_records_df, daily_tasks_df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

users_df, daily_records_df, daily_tasks_df = load_data()

if users_df.empty:
    st.error("No data available. Please check your database connection.")
    st.stop()

# Data preprocessing
daily_records_df['date'] = pd.to_datetime(daily_records_df['date'])
daily_tasks_df['created_at'] = pd.to_datetime(daily_tasks_df['created_at'])

# Merge data for analysis
merged_df = daily_records_df.merge(users_df[['id', 'full_name', 'pod_type']], 
                                  left_on='user_id', right_on='id', how='left')

# SIDEBAR FILTERS
st.sidebar.header("🔍 Filters")

# Date range filter
min_date = daily_records_df['date'].min().date()
max_date = daily_records_df['date'].max().date()
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Pod type filter
pod_types = ['All'] + list(users_df['pod_type'].dropna().unique())
selected_pod = st.sidebar.selectbox("Select Pod Type", pod_types)

# User filter - Multi-select with exclusions
all_users = list(users_df['full_name'].dropna().unique())
excluded_by_default = ['Michael P', 'Brandon Fernandez', 'Haris Becirovic', 'alexandergilardi']

# Default to all users except the excluded ones
default_users = [user for user in all_users if user not in excluded_by_default]

# Initialize session state for user selection
if 'selected_users' not in st.session_state:
    st.session_state.selected_users = default_users

# Quick selection buttons
col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("Select All", key="select_all"):
        st.session_state.selected_users = all_users
        st.rerun()
with col2:
    if st.button("Reset Default", key="reset_default"):
        st.session_state.selected_users = default_users
        st.rerun()

selected_users = st.sidebar.multiselect(
    "Select Users (excluded by default: Michael P, Brandon, Haris, Alex)",
    options=all_users,
    default=st.session_state.selected_users,
    help="Users excluded by default can be re-selected if needed",
    key="user_multiselect"
)

# Show user selection summary
if selected_users:
    excluded_users = [user for user in all_users if user not in selected_users]
    st.sidebar.info(f"📊 Showing {len(selected_users)} of {len(all_users)} users")
    if excluded_users:
        with st.sidebar.expander("👥 Excluded Users"):
            for user in excluded_users:
                st.write(f"• {user}")
else:
    st.sidebar.warning("⚠️ No users selected - dashboard will show empty data")

# Apply filters
filtered_records = daily_records_df.copy()
filtered_users = users_df.copy()

if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_records = filtered_records[
        (filtered_records['date'].dt.date >= start_date) & 
        (filtered_records['date'].dt.date <= end_date)
    ]

if selected_pod != 'All':
    filtered_users = filtered_users[filtered_users['pod_type'] == selected_pod]
    filtered_records = filtered_records[filtered_records['user_id'].isin(filtered_users['id'])]

if selected_users:  # If any users are selected
    filtered_users = filtered_users[filtered_users['full_name'].isin(selected_users)]
    filtered_records = filtered_records[filtered_records['user_id'].isin(filtered_users['id'])]
else:  # If no users selected, show empty data
    filtered_users = filtered_users.iloc[0:0]  # Empty dataframe with same structure
    filtered_records = filtered_records.iloc[0:0]

# MAIN DASHBOARD
# Key Metrics Row
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_users = len(filtered_users)
    st.metric("👥 Total Users", total_users)

with col2:
    completed_questionnaires = filtered_users['has_completed_questionnaire'].sum()
    questionnaire_rate = (completed_questionnaires / total_users * 100) if total_users > 0 else 0
    st.metric("📋 Questionnaire Rate", f"{questionnaire_rate:.1f}%", 
              f"{completed_questionnaires}/{total_users}")

with col3:
    total_records = len(filtered_records)
    completed_days = filtered_records['all_completed'].sum()
    completion_rate = (completed_days / total_records * 100) if total_records > 0 else 0
    st.metric("✅ Daily Completion Rate", f"{completion_rate:.1f}%", 
              f"{completed_days}/{total_records}")

with col4:
    # Task completion rate for filtered data
    filtered_task_records = daily_tasks_df[
        daily_tasks_df['daily_record_id'].isin(filtered_records['id'])
    ] if not filtered_records.empty else pd.DataFrame()
    
    if not filtered_task_records.empty:
        task_completion_rate = (filtered_task_records['completed'].sum() / len(filtered_task_records) * 100)
        st.metric("🎯 Task Completion Rate", f"{task_completion_rate:.1f}%")
    else:
        st.metric("🎯 Task Completion Rate", "0%")

st.markdown("---")

# Charts Row 1
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Pod Type Distribution")
    if not filtered_users.empty and 'pod_type' in filtered_users.columns:
        pod_counts = filtered_users['pod_type'].value_counts()
        fig_pie = px.pie(values=pod_counts.values, names=pod_counts.index, 
                        color_discrete_sequence=px.colors.qualitative.Set3)
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, width='stretch')
    else:
        st.info("No pod type data available for selected filters")

with col2:
    st.subheader("📈 Daily Completion Trend")
    if not filtered_records.empty:
        # Create a complete date range to show all dates
        date_range = pd.date_range(start=filtered_records['date'].min(), 
                                 end=filtered_records['date'].max(), 
                                 freq='D')
        
        daily_completion = filtered_records.groupby('date').agg({
            'all_completed': ['sum', 'count']
        }).round(2)
        daily_completion.columns = ['Completed', 'Total']
        daily_completion['Completion_Rate'] = (daily_completion['Completed'] / daily_completion['Total'] * 100).round(1)
        
        # Reindex to include all dates, fill missing with 0
        daily_completion = daily_completion.reindex(date_range, fill_value=0)
        daily_completion.index.name = 'date'
        
        # For dates with no data, set completion rate to 0
        daily_completion['Completion_Rate'] = daily_completion['Completion_Rate'].fillna(0)
        
        fig_line = px.line(daily_completion.reset_index(), x='date', y='Completion_Rate',
                          title="Daily Completion Rate (%) - All Dates Shown")
        fig_line.update_traces(line_color='#1f77b4', line_width=3)
        fig_line.update_layout(
            yaxis_title="Completion Rate (%)", 
            xaxis_title="Date",
            xaxis=dict(tickmode='linear', dtick=86400000.0)  # Show every day
        )
        st.plotly_chart(fig_line, width='stretch')
    else:
        st.info("No daily records available for selected filters")

# Charts Row 2
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏆 Top Performers")
    if not filtered_records.empty:
        user_performance = filtered_records.merge(
            filtered_users[['id', 'full_name']], 
            left_on='user_id', right_on='id', how='left'
        ).groupby('full_name').agg({
            'all_completed': ['sum', 'count']
        }).round(2)
        user_performance.columns = ['Completed_Days', 'Total_Days']
        user_performance['Completion_Rate'] = (
            user_performance['Completed_Days'] / user_performance['Total_Days'] * 100
        ).round(1)
        user_performance = user_performance.sort_values('Completion_Rate', ascending=False).head(10)
        
        fig_bar = px.bar(user_performance.reset_index(), x='Completion_Rate', y='full_name',
                        orientation='h', title="Top 10 Users by Completion Rate")
        fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_bar, width='stretch')
    else:
        st.info("No performance data available for selected filters")

with col2:
    st.subheader("📅 Weekly Activity Heatmap")
    if not filtered_records.empty:
        # Create weekly heatmap
        filtered_records['weekday'] = filtered_records['date'].dt.day_name()
        filtered_records['week'] = filtered_records['date'].dt.isocalendar().week
        
        heatmap_data = filtered_records.groupby(['week', 'weekday'])['all_completed'].mean().unstack(fill_value=0)
        
        # Reorder weekdays
        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        heatmap_data = heatmap_data.reindex(columns=weekday_order, fill_value=0)
        
        fig_heatmap = px.imshow(heatmap_data.values, 
                               x=heatmap_data.columns, 
                               y=[f"Week {w}" for w in heatmap_data.index],
                               color_continuous_scale="RdYlGn",
                               aspect="auto")
        fig_heatmap.update_layout(title="Weekly Completion Rate Heatmap")
        st.plotly_chart(fig_heatmap, width='stretch')
    else:
        st.info("No activity data available for selected filters")

# Task Analysis Section
st.markdown("---")
st.subheader("🎯 Task Analysis")

if not daily_tasks_df.empty:
    # Filter tasks based on selected records
    filtered_tasks = daily_tasks_df[
        daily_tasks_df['daily_record_id'].isin(filtered_records['id'])
    ] if not filtered_records.empty else pd.DataFrame()
    
    if not filtered_tasks.empty:
        # Merge tasks with user information for analysis
        tasks_with_users = filtered_tasks.merge(
            filtered_records[['id', 'user_id']], 
            left_on='daily_record_id', right_on='id', how='left'
        ).merge(
            filtered_users[['id', 'full_name']], 
            left_on='user_id', right_on='id', how='left'
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Task completion by type
            task_completion = tasks_with_users.groupby('task_id').agg({
                'completed': ['sum', 'count']
            }).round(2)
            task_completion.columns = ['Completed', 'Total']
            task_completion['Completion_Rate'] = (task_completion['Completed'] / task_completion['Total'] * 100).round(1)
            task_completion = task_completion.sort_values('Completion_Rate', ascending=True)
            
            fig_task_bar = px.bar(task_completion.reset_index(), 
                                 x='Completion_Rate', y='task_id',
                                 orientation='h', 
                                 title="Task Completion Rates by Type")
            st.plotly_chart(fig_task_bar, width='stretch')
        
        with col2:
            # Task completion by user
            user_task_completion = tasks_with_users.groupby('full_name').agg({
                'completed': ['sum', 'count']
            }).round(2)
            user_task_completion.columns = ['Completed', 'Total']
            user_task_completion['Completion_Rate'] = (user_task_completion['Completed'] / user_task_completion['Total'] * 100).round(1)
            user_task_completion = user_task_completion.sort_values('Completion_Rate', ascending=True).head(10)
            
            fig_user_tasks = px.bar(user_task_completion.reset_index(), 
                                   x='Completion_Rate', y='full_name',
                                   orientation='h', 
                                   title="Task Completion by User")
            fig_user_tasks.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_user_tasks, width='stretch')
    else:
        st.info("No task data available for selected filters")

# Detailed Data Section (Collapsible)
with st.expander("📋 Detailed Data Tables"):
    tab1, tab2, tab3 = st.tabs(["Users", "Daily Records", "Tasks"])
    
    with tab1:
        st.dataframe(filtered_users, width='stretch')
    
    with tab2:
        display_records = filtered_records.merge(
            filtered_users[['id', 'full_name']], 
            left_on='user_id', right_on='id', how='left'
        )[['full_name', 'date', 'all_completed', 'created_at']]
        st.dataframe(display_records, width='stretch')
    
    with tab3:
        if not filtered_tasks.empty:
            # Merge tasks with user information
            tasks_with_users = filtered_tasks.merge(
                filtered_records[['id', 'user_id']], 
                left_on='daily_record_id', right_on='id', how='left'
            ).merge(
                filtered_users[['id', 'full_name']], 
                left_on='user_id', right_on='id', how='left'
            )
            
            display_tasks = tasks_with_users[['full_name', 'task_text', 'completed', 'created_at']].sort_values('created_at', ascending=False)
            display_tasks.columns = ['User', 'Task', 'Completed', 'Created At']
            st.dataframe(display_tasks, width='stretch')
        else:
            st.info("No tasks available for selected filters")

# Refresh button
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()
