from typing import List
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry  # type: ignore
from bs4 import BeautifulSoup
from fastapi import APIRouter, HTTPException, Body

import logging
import os
import pdfkit

async def scrap_webtest(url):
    """Fetches and parses content from a URL with retry logic.

    Args:
        url (str): The URL to scrape data from.

    Returns:
        str: The scraped and parsed text content, or None if fetching fails.
    """

    def fetch_url_with_retry(url, max_retries=3, backoff_factor=0.3):
        session = requests.Session()
        retries = Retry(total=max_retries, backoff_factor=backoff_factor,
                        status_forcelist=[500, 502, 503, 504])
        session.mount('http://', HTTPAdapter(max_retries=retries))
        session.mount('https://', HTTPAdapter(max_retries=retries))
        try:
            response = session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch URL: {e}")
            return None
        finally:
            session.close()

    content = fetch_url_with_retry(url)
    if content:
        soup = BeautifulSoup(content, "html.parser")
        return soup.get_text()
    else:
        return None


def clean_data(data):
    """Cleans the scraped data by removing whitespace and replacing newlines with spaces.

    Args:
        data (str): The scraped data to clean.

    Returns:
        str: The cleaned data.
    """

    cleaned_data = data.strip()  # Remove leading and trailing whitespace
    cleaned_data = cleaned_data.replace('\n', ' ')  # Replace newline characters with spaces
    return cleaned_data


def text_to_pdf(text, filename):
    """Generates a PDF from the provided text and saves it with the given filename.

    Args:
        text (str): The text content to convert to PDF.
        filename (str): The name of the PDF file to be created.

    Returns:
        str: The path to the generated PDF file, or None if creation fails.
    """

    try:
        assets_dir = os.path.join(os.path.dirname(__file__), '..', 'assets')
        os.makedirs(assets_dir, exist_ok=True)
        file_path = os.path.join(assets_dir, filename)
        path_wkhtmltopdf = '/usr/bin/wkhtmltopdf'  # Path to the wkhtmltopdf binary
        pdfkit.from_string(text, file_path, configuration=pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf))
        return file_path
    except Exception as e:
        print(f"Failed to create PDF: {e}")
        return None

async def scrape_and_create_pdfs(urls: List[str]) -> dict[str, List[str]]:  
    """
    (Function is now outside the route decorator)
    Scrapes data from a list of URLs, cleans it, creates a PDF for each URL, and names them dynamically.

    Args:
        urls (List[str]): A list of URLs to scrape and convert to PDFs.

    Returns:
        dict: A dictionary with the key 'pdf_filepaths' containing a list of file paths to the created PDFs.
    """
    pdf_filepaths = []

    for idx, url in enumerate(urls):
        try:
            logging.info(f"Scraping URL: {url}")
            response = await scrap_webtest(url)
            if response:
                cleaned_data = clean_data(response)
                pdf_filepath = text_to_pdf(cleaned_data, f"data_{idx}.pdf")

                if pdf_filepath:
                    pdf_filepaths.append(pdf_filepath)
                else:
                    raise HTTPException(status_code=500, detail=f"Failed to create PDF for URL: {url}")
            else:
                raise HTTPException(status_code=404, detail=f"Failed to fetch data from URL: {url}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    return {"pdf_filepaths": pdf_filepaths}
