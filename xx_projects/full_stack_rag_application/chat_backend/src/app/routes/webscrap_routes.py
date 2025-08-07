
import logging

from fastapi import APIRouter, Body, HTTPException
from typing import List
from app.web_scrap.wb_srcp import scrape_and_create_pdfs

router = APIRouter()


@router.post("/scrape_and_create_pdfs")
async def scrap_endpoint(urls: List[str] = Body(...)) -> dict[str, List[str]]:
    try:
        return await scrape_and_create_pdfs(urls)
    except HTTPException as he:
        # Return a dictionary with an error message
        logging.error(f"Error during web scraping: {he.detail}")
        return {"error": he.detail}
    except Exception as e:
        # Return a dictionary with an error message
        logging.error(f"Unexpected error during web scraping: {e}")
        return {"error": "Internal server error"}
