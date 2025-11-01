import os
import streamlit as st
import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Function to create a Supabase client
def get_supabase_client():
    url: str = os.environ.get("SUPABASE_URL")
    # Try service key first (for backend operations), fallback to anon key
    key: str = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in environment variables")
    
    print(f"Supabase URL: {url}")
    print(f"Using key type: {'service' if 'SUPABASE_SERVICE_KEY' in os.environ else 'anon'}")
    supabase: Client = create_client(url, key)
    return supabase

# Function to fetch users data
def get_users():
    supabase = get_supabase_client()
    response = supabase.table('users').select("*").execute()
    print(response)
    df = pd.DataFrame(response.data)
    return df

# Function to fetch daily records
def get_daily_records():
    supabase = get_supabase_client()
    response = supabase.table('daily_records').select("*").execute()
    df = pd.DataFrame(response.data)
    return df

# Function to fetch daily tasks
def get_daily_tasks():
    supabase = get_supabase_client()
    response = supabase.table('daily_tasks').select("*").execute()
    df = pd.DataFrame(response.data)
    return df