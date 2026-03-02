import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# 1. Setup the page
st.set_page_config(page_title="X Post Dashboard", layout="wide")
st.title("📊 Interactive X Performance Dashboard")

# 2. Function to load data from your published Google Sheet
@st.cache_data(ttl=600)
def load_data(csv_url):
    try:
        df = pd.read_csv(csv_url)
        return df
    except Exception as e:
        st.error(f"Could not load data. Exact error: {e}")
        return pd.DataFrame()

# Bulletproof Number Formatter
def fmt_number(val):
    try:
        if pd.isna(val):
            return "0"
        if isinstance(val, str):
            val = val.replace(',', '').strip()
        return f"{int(float(val)):,}"
    except (ValueError, TypeError):
        return str(val) if pd.notna(val) else "0"

# 3. Sidebar - Data Connection
st.sidebar.header("1. Connect Data")
st.sidebar.markdown("Paste your *Published as CSV* Google Sheet link below.")
sheet_url = st.sidebar.text_input("Google Sheet CSV URL:")

if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.sidebar.success("Fetching fresh data!")

# 4. Main App Logic
if sheet_url:
    df = load_data(sheet_url)
    
    if not df.empty:
        st.sidebar.header("2. Dashboard Filters")
        
        # --- UPDATED: Account Filter (Checkboxes) ---
        if 'Account' in df.columns:
            st.sidebar.markdown("**Select Account(s):**")
            available_accounts = df['Account'].dropna().unique().tolist()
            selected_accounts = []
            
            # Draw a checkbox for each account and default it to True (Checked)
            for account in available_accounts:
                # We use a unique 'key' so Streamlit doesn't get confused between identical names
                if st.sidebar.checkbox(str(account), value=True, key=f"acc_{account}"):
                    selected_accounts.append(account)
        else:
            selected_accounts = []
            
        st.sidebar.markdown("---") # Add a small visual divider
            
        # --- UPDATED: Source Filter (Checkboxes) ---
        if 'Source' in df.columns:
            st.sidebar.markdown("**Select Source(s):**")
            available_sources = df['Source'].dropna().unique().tolist()
            selected_sources = []
            
            # Draw a checkbox for each source
            for source in available_sources:
                if st.sidebar.checkbox(str(source), value=True, key=f"src_{source}"):
                    selected_sources.append(source)
        else:
            selected_sources = []
            
        st.sidebar.markdown("---") # Add another divider before the next filter
        
        # Bulletproof Metric Filter
        non_metric_columns = ['URL', 'Source', 'Account', 'Date', 'Text'] 
        available_metrics = [col for col in df.columns if col not in non_metric_columns]
        
        if available_metrics:
            selected_metric = st.sidebar.selectbox("Rank posts by:", available_metrics)
        else:
            st.error("Could not find any metric columns to sort by. Please check your Google Sheet.")
            st.stop() 
        
        # Top N Filter
        max_posts = len(df)
        top_n = st.sidebar.slider("Number of posts to display (Top N):", min_value=1, max_value=max_posts, value=min(5, max_posts))
        
        # Apply the filters 
        filtered_df = df.copy()
        if 'Account' in df.columns and selected_accounts:
            filtered_df = filtered_df[filtered_df['Account'].isin(selected_accounts)]
        if 'Source' in df.columns and selected_sources:
            filtered_df = filtered_df[filtered_df['Source'].isin(selected_sources)]
        
        # Drop duplicate URLs
        if 'URL' in filtered_df.columns:
            filtered_df = filtered_df.drop_duplicates(subset=['URL'])
        else:
            st.error("CRITICAL: No 'URL' column found. I cannot display embeds without links.")
            st.stop()
            
        # Sort and get the Top N
        sorted_df = filtered_df.sort_values(by=selected_metric, ascending=False).head(top_n)
        
        # 5. Display the Data
        st.subheader(f"Top {top_n} Posts Ranked by {selected_metric}")
        
        for rank, (index, row) in enumerate(sorted_df.iterrows(), start=1):
            st.markdown("---")
            
            account_text = row.get('Account', 'N/A')
            source_text = row.get('Source', 'N/A')
            
            rt_val = fmt_number(row.get('Retweets', 0))
            reply_val = fmt_number(row.get('Replies', 0))
            quote_val = fmt_number(row.get('Quotes', 0))
            like_val = fmt_number(row.get('Likes', 0))
            view_val = fmt_number(row.get('Views', 0))
            eng_val = fmt_number(row.get('Engagements', 0))
            mean_eng_val = fmt_number(row.get('Meaningful Engagements', 0)) 
            
            st.markdown(f"### 🏅 Rank #{rank} (Sorted by {selected_metric})")
            st.markdown(f"**👤 Account:** {account_text} &nbsp;|&nbsp; **🏷️ Source:** {source_text}")
            
            st.markdown(f"**🔄 Retweets:** {rt_val} &nbsp;|&nbsp; **💬 Replies:** {reply_val} &nbsp;|&nbsp; **🦜 Quotes:** {quote_val} &nbsp;|&nbsp; **❤️ Likes:** {like_val}")
            st.markdown(f"**👁️ Views:** {view_val} &nbsp;|&nbsp; **💍 Engagements:** {eng_val} &nbsp;|&nbsp; **💪 Meaningful Engagements:** {mean_eng_val}")
            
            url = str(row.get('URL', '')).replace("x.com", "twitter.com")
            
            embed_html = f"""
            <blockquote class="twitter-tweet" data-theme="light">
                <a href="{url}"></a>
            </blockquote>
            <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
            """
            components.html(embed_html, height=800, scrolling=False)

else:
    st.info("👈 Please paste your published Google Sheet CSV link in the sidebar to load the dashboard.")
