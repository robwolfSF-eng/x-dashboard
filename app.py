import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# 1. Setup the page
st.set_page_config(page_title="X Post Dashboard", layout="wide")
st.title("📊 Interactive X Performance Dashboard")

# 2. Function to load data from your published Google Sheet
@st.cache_data(ttl=600) # Caches the data for 10 minutes so it doesn't overload
def load_data(csv_url):
    try:
        df = pd.read_csv(csv_url)
        return df
    except Exception as e:
        st.error("Could not load data. Please ensure you pasted a valid Google Sheets CSV link.")
        return pd.DataFrame()

# 3. Sidebar - Data Connection
st.sidebar.header("1. Connect Data")
st.sidebar.markdown("Paste your *Published as CSV* Google Sheet link below.")
sheet_url = st.sidebar.text_input("Google Sheet CSV URL:")

# 4. Main App Logic
if sheet_url:
    df = load_data(sheet_url)
    st.write("Columns found in sheet:", df.columns.tolist())
    
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
        sorted_df = filtered_df.sort_values(by=selected_metric, ascending=False).head(top_n)
        
        # 5. Display the Data
        st.subheader(f"Top {top_n} Posts Ranked by {selected_metric}")
        
        # Create 2 columns for a cleaner layout
        cols = st.columns(2)
        
        for index, row in sorted_df.reset_index(drop=True).iterrows():
            # Alternate placing posts in column 1 and column 2
            col = cols[index % 2] 
            with col:
                st.markdown(f"**Source:** {row.get('Source', 'N/A')} | **{selected_metric}:** {row.get(selected_metric, 0)}")
                
                # The code that actually embeds the X post
# The code that actually embeds the X post
                # We force x.com to become twitter.com so the embed script recognizes it
                url = str(row['URL']).replace("x.com", "twitter.com")
                
                embed_html = f"""
                <blockquote class="twitter-tweet">
                    <a href="{url}"></a>
                </blockquote>
                <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
                """
                components.html(embed_html, height=500, scrolling=True)
                embed_html = f"""
                <blockquote class="twitter-tweet">
                    <a href="{url}"></a>
                </blockquote>
                <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
                """
                components.html(embed_html, height=500, scrolling=True)
else:
    st.info("👈 Please paste your published Google Sheet CSV link in the sidebar to load the dashboard.")
