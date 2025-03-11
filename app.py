import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
from urllib.parse import urljoin, urlparse
import re

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
st.title("Website Keyword Scanner")
st.write("Enter a website URL to scan all its subpages for specific keywords.")
st.write("You have comments? Please direct them to Dr. Abdelaziz Lawani at alawani@tnstate.edu")

url = st.text_input("Enter website URL")
if st.button("Scan Website and Subpages"):
    if url:
        subpages = find_subpages(url)
        st.write(f"Found {len(subpages)} subpages. Scanning now...")
        
        all_results = []
        
        for page in subpages:
            st.write(f"Scanning: {page}")
            website_text, soup = get_website_text(page)
            if "Error" in website_text:
                st.warning(f"Skipping {page} due to an error.")
            else:
                for keyword in keywords:
                    snippets = find_keyword_context(website_text, keyword)
                    if snippets:
                        all_results.append((page, keyword, snippets))
        
        if not all_results:
            st.warning("No keywords found across subpages.")
        else:
            st.success("Analysis complete. Generating report...")
            html_report = generate_html_report(all_results)
            
            # Save the report to a file
            with open("keyword_report.html", "w", encoding="utf-8") as file:
                file.write(html_report)
            
            st.download_button(
                label="Download HTML Report",
                data=html_report,
                file_name="keyword_report.html",
                mime="text/html"
            )
    else:
        st.warning("Please enter a valid URL.")
