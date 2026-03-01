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

# Apply the filters to the data
        filtered_df = df[df['Source'].isin(selected_sources)]
        
        # THE BOUNCER: This forces Python to drop any rows that share the same URL, keeping only the first one it sees.
        filtered_df = filtered_df.drop_duplicates(subset=['URL'])
        
        # Sort and get the Top N
        sorted_df = filtered_df.sort_values(by=selected_metric, ascending=False).head(top_n)
        
        # 5. Display the Data (Single Vertical Column Layout)
        st.subheader(f"Top {top_n} Posts Ranked by {selected_metric}")
        
        # We removed the 'cols' logic entirely to force a single vertical stack
        for index, row in sorted_df.iterrows():
            
            # Add a visual divider line between posts for clean formatting
            st.markdown("---") 
            st.markdown(f"**Source:** {row.get('Source', 'N/A')} | **{selected_metric}:** {row.get(selected_metric, 0)}")
            
            # Ensure the URL works with the embed script
            url = str(row['URL']).replace("x.com", "twitter.com")
            
            embed_html = f"""
            <blockquote class="twitter-tweet" data-theme="light">
                <a href="{url}"></a>
            </blockquote>
            <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
            """
            
            # Increased height to 800 to prevent scrollbars, and turned off the Streamlit scrollbar feature
            components.html(embed_html, height=800, scrolling=False)

else:
    st.info("👈 Please paste your published Google Sheet CSV link in the sidebar to load the dashboard.")
