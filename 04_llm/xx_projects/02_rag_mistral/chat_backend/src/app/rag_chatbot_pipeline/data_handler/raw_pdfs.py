import os
import PyPDF2
from typing import List, Dict


class RawPDFProcessor:
    def __init__(self):
        self.raw_pdf_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'raw_pdfs')
        self.processed_pdf_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'processed_pdfs')

        # Create processed PDF directory if it doesn't exist
        os.makedirs(self.processed_pdf_dir, exist_ok=True)

    def get_raw_pdf_files(self) -> List[str]:
        """
        Get a list of all raw PDF files from the raw_pdfs directory.
        """
        return [f for f in os.listdir(self.raw_pdf_dir) if f.endswith('.pdf')]

    def process_pdf(self, pdf_file: str) -> Dict[str, str]:
        """
        Process an individual PDF, extract text, images, and unstructured data, and save the processed output.
        """
        pdf_path = os.path.join(self.raw_pdf_dir, pdf_file)
        processed_text_path = os.path.join(self.processed_pdf_dir, pdf_file.replace('.pdf', '_text.txt'))
        # processed_images_dir = os.path.join(self.processed_pdf_dir, pdf_file.replace('.pdf', '_images'))

        # Extract text from PDF
        extracted_text = self.extract_text_from_pdf(pdf_path)

        # Save extracted text to a file
        with open(processed_text_path, 'w', encoding='utf-8') as text_file:
            text_file.write(extracted_text)

        # Extract images from PDF
        # extracted_images = self.extract_images_from_pdf(pdf_path, processed_images_dir)

        return {
            "text_file": processed_text_path,
            # "image_folder": processed_images_dir,
            "status": "success"
        }

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extracts text from the given PDF file using PyPDF2.
        """
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
        return text

    def process_all_pdfs(self) -> Dict[str, str]:
        """
        Process all PDFs in the raw_pdfs folder by extracting text and images.
        """
        processed_files = {}
        for pdf_file in self.get_raw_pdf_files():
            try:
                result = self.process_pdf(pdf_file)
                processed_files[pdf_file] = result
            except Exception as e:
                print(f"Error processing {pdf_file}: {str(e)}")
                processed_files[pdf_file] = f"Error: {str(e)}"
        return processed_files


# Example usage
if __name__ == "__main__":
    processor = RawPDFProcessor()
    result = processor.process_all_pdfs()
    print(result)
