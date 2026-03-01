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

# 3. Sidebar - Data Connection
st.sidebar.header("1. Connect Data")
st.sidebar.markdown("Paste your *Published as CSV* Google Sheet link below.")
sheet_url = st.sidebar.text_input("Google Sheet CSV URL:")

# --- REFRESH BUTTON ---
if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.sidebar.success("Fetching fresh data!")

# 4. Main App Logic
if sheet_url:
    df = load_data(sheet_url)
    
    if not df.empty:
        st.sidebar.header("2. Dashboard Filters")
        
        # Source Filter
        available_sources = df['Source'].dropna().unique().tolist()
        selected_sources = st.sidebar.multiselect("Select Source(s):", available_sources, default=available_sources)
        
        # Metric Filter
        metrics = ['Retweets', 'Replies', 'Likes', 'Views', 'Bookmarks', 'Engagements', 'Meaningful engagements']
        selected_metric = st.sidebar.selectbox("Rank posts by:", metrics)
        
        # Top N Filter
        max_posts = len(df)
        top_n = st.sidebar.slider("Number of posts to display (Top N):", min_value=1, max_value=max_posts, value=min(5, max_posts))
        
        # Apply the filters to the data
        filtered_df = df[df['Source'].isin(selected_sources)]
        
        # THE BOUNCER: Drop duplicate URLs
        filtered_df = filtered_df.drop_duplicates(subset=['URL'])
        
        # Sort and get the Top N
        sorted_df = filtered_df.sort_values(by=selected_metric, ascending=False).head(top_n)
        
        # 5. Display the Data
        st.subheader(f"Top {top_n} Posts Ranked by {selected_metric}")
        
        for index, row in sorted_df.iterrows():
            st.markdown("---")
            st.markdown(f"**Source:** {row.get('Source', 'N/A')} | **{selected_metric}:** {row.get(selected_metric, 0)}")
            
            # The code that actually embeds the X post
            url = str(row['URL']).replace("x.com", "twitter.com")
            
            embed_html = f"""
            <blockquote class="twitter-tweet" data-theme="light">
                <a href="{url}"></a>
            </blockquote>
            <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
            """
            components.html(embed_html, height=800, scrolling=False)

else:
    st.info("👈 Please paste your published Google Sheet CSV link in the sidebar to load the dashboard.")
