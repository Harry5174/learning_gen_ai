import logging
from fastapi import APIRouter, HTTPException
from app.pdf_processing.pre_processing import process_pdfs_in_folders

router = APIRouter()

@router.post("/process_pdfs/")
async def process_pdfs():
    raw_pdf_folder = "/app/assets/pdfs/raw_pdfs"
    processed_pdf_folder = "/app/assets/pdfs/processed_pdfs"
    try:
        result = await process_pdfs_in_folders(raw_pdf_folder, processed_pdf_folder)
        return result
    except HTTPException as he:
         # Return a dictionary with an error message
        logging.error(f"Unexpected error during web scraping: {he}")
        return {"error": he.detail}
    except Exception as e:
         # Return a dictionary with an error message
        logging.error(f"Unexpected error during web scraping: {e}")
        return {"error": "Internal server error"}
