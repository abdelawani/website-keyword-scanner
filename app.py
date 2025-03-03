import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st

# List of keywords to search for
keywords = [
    "activism", "activists", "advocacy", "advocate", "advocates", "barrier", "barriers",
    "bias", "biased", "biases", "bipoc", "black", "latinx", "community diversity",
    "community equity", "cultural differences", "cultural heritage", "culturally responsive",
    "disabilities", "disability", "discriminated", "discrimination", "discriminatory",
    "diverse backgrounds", "diverse communities", "diverse community", "diverse group",
    "diverse groups", "diversified", "diversify", "diversifying", "diversity", "diversity and inclusion",
    "diversity equity", "enhance the diversity", "enhancing diversity", "equal opportunity",
    "equality", "equitable", "equity", "ethnicity", "excluded", "female", "fostering inclusivity",
    "gender", "gender diversity", "genders", "hate speech", "hispanic minority", "historically",
    "implicit bias", "implicit biases", "inclusion", "inclusive", "inclusiveness", "inclusivity",
    "increase diversity", "increase the diversity", "indigenous community", "inequalities",
    "inequality", "inequitable", "institutional", "lgbt", "marginalize", "marginalized",
    "minorities", "minority", "multicultural", "polarization", "political", "prejudice", "privileges",
    "promoting diversity", "race and ethnicity", "racial", "racial diversity", "racial inequality",
    "racial justice", "racially", "racism", "sense of belonging", "sexual preferences",
    "social justice", "socio-cultural", "socio-economic", "sociocultural", "socioeconomic",
    "status", "stereotypes", "systemic", "trauma", "under-appreciated", "under-represented",
    "under-served", "underrepresentation", "underrepresented", "underserved", "undervalued",
    "victim", "women", "women and underrepresented"
]

def get_website_text(url):
    """Fetches and extracts text from a given website URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text(" ")  # Extracting text content
        return text.lower()  # Convert text to lowercase for case-insensitive matching
    except requests.exceptions.RequestException as e:
        return f"Error fetching the webpage: {e}"

def count_keywords(text, keywords):
    """Counts the frequency of given keywords in the text."""
    keyword_counts = {keyword: text.count(keyword) for keyword in keywords}
    return {k: v for k, v in keyword_counts.items() if v > 0}  # Filter out keywords not found

# Streamlit App
st.title("Website Keyword Scanner")
st.write("Enter a website URL to scan for specific keywords and analyze their frequency.")

url = st.text_input("Enter website URL")
if st.button("Scan Website"):
    if url:
        website_text = get_website_text(url)
        if "Error" in website_text:
            st.error(website_text)
        else:
            keyword_frequencies = count_keywords(website_text, keywords)
            df = pd.DataFrame(keyword_frequencies.items(), columns=["Keyword", "Frequency"])
            df = df.sort_values(by="Frequency", ascending=False)
            
            if df.empty:
                st.warning("No keywords found on the webpage.")
            else:
                st.write("### Keyword Frequency Report:")
                st.dataframe(df)
                
                # Create a download button for the report
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download Report as CSV",
                    data=csv,
                    file_name="keyword_report.csv",
                    mime="text/csv"
                )
    else:
        st.warning("Please enter a valid URL.")
