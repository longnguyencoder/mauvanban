
from pdf2image import convert_from_path, pdfinfo_from_path
import sys
import os

def check_poppler():
    print("Checking Poppler...")
    try:
        # Try to get info from a dummy PDF or just check dependency
        # We need a PDF file.
        # Find one
        pdf_path = r'c:\Users\PT COMPUTER\Documents\GitHub\mauvanban\backend\uploads\documents\0c92b4eba078466dbe42ad094f92bfb5_20251217_143842.pdf'
        if not os.path.exists(pdf_path):
            print("PDF not found for check.")
            return

        print(f"Testing with {pdf_path}")
        info = pdfinfo_from_path(pdf_path)
        print("✅ Poppler found! PDF Info:")
        print(info)
    except Exception as e:
        print("❌ Poppler check failed:")
        print(str(e))
        
        # Check PATH
        print("\nCurrent PATH:")
        for p in os.environ['PATH'].split(';'):
            print(p)

if __name__ == "__main__":
    check_poppler()
