import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import io

# Streamlit app title
st.title("Google SERP Title Scraper for Months")

# Provide detailed explanation of what the tool does
st.markdown("""
    This tool scrapes Google's Search Engine Results Page (SERP) for a designated keyword and determines how many of the meta titles contain a specific month (e.g., January, February). 
    It's useful for identifying time-sensitive content in search results, such as blog posts, articles, or announcements.

    ### Example:
    A meta title like **"Best Credit Cards for Travel in October 2024"** would be identified because it contains the month **October**.

    You can choose to scrape up to 50 results from Google, upload a CSV of multiple keywords for bulk scraping, and optionally download the results as a CSV file.
""")

# User input for mode selection (single keyword or bulk upload)
search_mode = st.radio("Choose the search mode:", ('Single Keyword Search', 'Bulk Upload CSV'))

# Function to scrape the titles and URLs directly from Google's search results page
def scrape_google_titles_and_urls(keyword, num_results):
    # Construct the URL for the search engine's results page
    url = f'https://www.google.com/search?q={keyword}&num={num_results}'

    # Send a GET request to the search engine's results page
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code != 200:
        return None

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the title tags and URLs in the search results
    results = soup.select('.BNeawe.vvjwJb.AP7Wnd')  # Titles
    links = soup.select('.BNeawe.UPmit.AP7Wnd')     # URLs

    # Ensure there are results before proceeding
    if not results or not links:
        return None

    # Extract the titles and URLs
    titles_and_urls = [(results[i].get_text(), links[i].get_text()) for i in range(min(len(results), len(links)))]

    return titles_and_urls

# List of months to search for in the titles
months = ["january", "february", "march", "april", "may", "june",
          "july", "august", "september", "october", "november", "december"]

# Single keyword search input
if search_mode == 'Single Keyword Search':
    keyword = st.text_input("Enter the keyword to search for (e.g., 'best credit cards'):")
    num_results = st.number_input("Enter the number of results to scrape (up to 50):", min_value=1, max_value=50, value=10)

# Bulk keyword upload input
elif search_mode == 'Bulk Upload CSV':
    uploaded_file = st.file_uploader("Upload a CSV file with a column of keywords", type=["csv"])
    num_results = st.number_input("Enter the number of results to scrape for each keyword (up to 50):", min_value=1, max_value=50, value=10)

# Button to trigger the scraping process
if st.button("Search"):
    all_results = []

    if search_mode == 'Single Keyword Search':
        if keyword:
            # Scrape the specified number of Google titles and URLs for the entered keyword
            titles_and_urls = scrape_google_titles_and_urls(keyword, num_results)

            if titles_and_urls is None:
                st.error("Failed to retrieve results. Please try again.")
            else:
                # Process the scraped results
                for index, (title, url) in enumerate(titles_and_urls):
                    contains_month = any(month in title.lower() for month in months)
                    all_results.append({
                        "Rank": index + 1,
                        "Keyword": keyword,
                        "Title": title,
                        "URL": url,
                        "Contains Month": contains_month
                    })
                
                # Display and download results
                df = pd.DataFrame(all_results)
                st.write(f"Number of titles with a month: **{df['Contains Month'].sum()}**")
                st.dataframe(df)

                # Download option
                st.download_button(
                    label="Download results as CSV",
                    data=df.to_csv(index=False),
                    file_name=f"serp_results_{keyword}.csv",
                    mime="text/csv"
                )
        else:
            st.warning("Please enter a keyword to search.")

    elif search_mode == 'Bulk Upload CSV' and uploaded_file is not None:
        # Read CSV file
        try:
            df_uploaded = pd.read_csv(uploaded_file)
            keywords = df_uploaded.iloc[:, 0].tolist()  # Assuming the first column contains the keywords
        except Exception as e:
            st.error(f"Error reading the file: {e}")
            keywords = []

        if keywords:
            for keyword in keywords:
                titles_and_urls = scrape_google_titles_and_urls(keyword, num_results)

                if titles_and_urls is not None:
                    for index, (title, url) in enumerate(titles_and_urls):
                        contains_month = any(month in title.lower() for month in months)
                        all_results.append({
                            "Rank": index + 1,
                            "Keyword": keyword,
                            "Title": title,
                            "URL": url,
                            "Contains Month": contains_month
                        })
            
            # Display and download results
            if all_results:
                df_bulk = pd.DataFrame(all_results)
                st.write(f"Number of titles with a month: **{df_bulk['Contains Month'].sum()}**")
                st.dataframe(df_bulk)

                # Download option
                st.download_button(
                    label="Download results as CSV",
                    data=df_bulk.to_csv(index=False),
                    file_name="bulk_serp_results.csv",
                    mime="text/csv"
                )
        else:
            st.warning("No keywords found in the uploaded file.")
