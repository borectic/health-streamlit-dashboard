# 🏥 Health & Wellness Dashboard

A comprehensive Streamlit dashboard for tracking user progress and participation in health and wellness programs.

## Features

- **📊 Real-time Analytics**: Live data from Supabase database
- **🔍 Advanced Filtering**: Filter by date range, pod type, and users
- **📈 Interactive Visualizations**: Charts and graphs using Plotly
- **👥 User Management**: Multi-select user filtering with smart defaults
- **🎯 Task Tracking**: Detailed task completion analysis
- **📱 Responsive Design**: Works on desktop and mobile

## Dashboard Sections

### Key Metrics
- Total users count
- Questionnaire completion rate
- Daily completion rate
- Task completion rate

### Visualizations
- Pod type distribution (pie chart)
- Daily completion trends (line chart)
- Top performers (bar chart)
- Weekly activity heatmap
- Task analysis by type and user

### Filtering Options
- **Date Range**: Select specific time periods
- **Pod Type**: Filter by consistency, recovery, momentum
- **Users**: Multi-select with smart exclusions

## Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/borectic/health-streamlit-dashboard.git
   cd health-streamlit-dashboard
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file with your Supabase credentials:
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_anon_key
   SUPABASE_SERVICE_KEY=your_service_key
   ```

5. **Run the dashboard**
   ```bash
   streamlit run app.py
   ```

## Database Schema

The dashboard expects the following Supabase tables:

- **users**: User information and pod assignments
- **daily_records**: Daily completion tracking
- **daily_tasks**: Individual task completions
- **questionnaire_responses**: User questionnaire data

## Technologies Used

- **Streamlit**: Web application framework
- **Plotly**: Interactive visualizations
- **Pandas**: Data manipulation
- **Supabase**: Backend database
- **Python**: Core programming language

## Deployment

### Streamlit Cloud (Recommended)

1. **Fork this repository** to your GitHub account
2. **Visit [share.streamlit.io](https://share.streamlit.io)**
3. **Connect your GitHub account**
4. **Deploy** by selecting this repository
5. **Add environment variables** in Streamlit Cloud settings:
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_KEY`

### Local Development

```bash
# Clone and setup
git clone https://github.com/borectic/health-streamlit-dashboard.git
cd health-streamlit-dashboard
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Supabase credentials

# Run locally
streamlit run app.py
```

### Environment Variables

Required environment variables for deployment:

- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_SERVICE_KEY`: Your Supabase service role key (for RLS bypass)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details