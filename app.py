import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
from urllib.parse import urljoin, urlparse
import re

def get_website_text(url):
    """Fetches and extracts text from a given website URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text(" ")  # Extracting text content
        return text.lower(), soup  # Convert text to lowercase for case-insensitive matching
    except requests.exceptions.RequestException as e:
        return f"Error fetching the webpage: {e}", None

def find_subpages(base_url):
    """Finds all internal subpage links from a given webpage."""
    try:
        response = requests.get(base_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        base_domain = urlparse(base_url).netloc
        subpages = set()
        
        for link in soup.find_all("a", href=True):
            href = link["href"]
            full_url = urljoin(base_url, href)
            if urlparse(full_url).netloc == base_domain and full_url.startswith(base_url):
                subpages.add(full_url)
        
        return list(subpages)
    except requests.exceptions.RequestException as e:
        return []

def find_keyword_context(text, keyword):
    """Finds snippets of text where a keyword appears."""
    matches = []
    for match in re.finditer(rf'\b{keyword}\b', text, re.IGNORECASE):
        start = max(match.start() - 50, 0)
        end = min(match.end() + 50, len(text))
        snippet = text[start:end]
        matches.append(snippet)
    return matches

def generate_html_report(results):
    """Generates an HTML report highlighting keyword occurrences."""
    html_content = """<html><head><title>Keyword Analysis Report</title>
    <style>
        body { font-family: Arial, sans-serif; }
        h2 { color: #333; }
        .result { margin-bottom: 20px; padding: 10px; border: 1px solid #ddd; }
        .keyword { font-weight: bold; color: red; }
        .snippet { background-color: #f9f9f9; padding: 5px; }
    </style>
    </head><body>
    <h1>Keyword Analysis Report</h1>
    """
    
    for page, keyword, snippets in results:
        html_content += f'<div class="result"><h2><a href="{page}" target="_blank">{page}</a></h2>'
        html_content += f'<p><span class="keyword">Keyword:</span> {keyword}</p>'
        for snippet in snippets:
            html_content += f'<p class="snippet">... {snippet} ...</p>'
        html_content += "</div>"
    
    html_content += "</body></html>"
    return html_content

# Streamlit App
st.title("Website Keyword Scanner App")
st.write("Enter a website URL and specify keywords to scan all subpages for occurrences.")
st.write("\n\nYou have Questions? Please contact **Dr. Abdelaziz Lawani** at **alawani@tnstate.edu**")

url = st.text_input("Enter website URL")
keywords_input = st.text_area("**:red[Enter keywords (separate by commas)]**\n\n*To get accurate results, please follow this format.*")

if st.button("Scan Website and Subpages"):
    if url and keywords_input:
        raw_keywords = [kw.strip() for kw in keywords_input.split(",") if kw.strip()]
        valid_keywords = [kw for kw in raw_keywords if re.match(r'^[a-zA-Z]+$', kw)]
        excluded_keywords = list(set(raw_keywords) - set(valid_keywords))
        
        subpages = find_subpages(url)
        st.write(f"Found {len(subpages)} subpages. Scanning now...")
        
        all_results = []
        keyword_counts = {kw: 0 for kw in valid_keywords}
        
        progress_bar = st.progress(0)
        for index, page in enumerate(subpages):
            st.write(f"Scanning: {page}")
            progress_bar.progress((index + 1) / len(subpages))
            website_text, soup = get_website_text(page)
            if "Error" in website_text:
                st.warning(f"Skipping {page} due to an error.")
            else:
                for keyword in valid_keywords:
                    snippets = find_keyword_context(website_text, keyword)
                    if snippets:
                        keyword_counts[keyword] += len(snippets)
                        all_results.append((page, keyword, snippets))
        
        df = pd.DataFrame(keyword_counts.items(), columns=["Keyword", "Frequency"])
        df = df.sort_values(by="Frequency", ascending=False)
        
        if df.empty:
            st.warning("No keywords found across subpages.")
        else:
            st.write("### Keyword Frequency Report:")
            st.dataframe(df)
            
            if excluded_keywords:
                st.write("### Excluded Keywords:")
                st.write(", ".join(excluded_keywords))
            
            # Generate and save HTML report
            html_report = generate_html_report(all_results)
            with open("keyword_report.html", "w", encoding="utf-8") as file:
                file.write(html_report)
            
            st.download_button(
                label="Download HTML Report",
                data=html_report,
                file_name="keyword_report.html",
                mime="text/html"
            )
    else:
        st.warning("Please enter a valid URL and at least one keyword in the correct format (separated by commas). Example: keyword1, keyword2, keyword3")


