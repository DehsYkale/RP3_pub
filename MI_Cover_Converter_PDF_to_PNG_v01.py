
import lao
import os
import sys
from pdf2image import convert_from_path
from PIL import Image

def convert_pdf_to_png(pdf_path, output_path, width=600, height=776, dpi=600):
	"""
	Convert the first page of a PDF to a PNG image with specified dimensions and resolution.
	
	Args:
		pdf_path (str): Path to the PDF file
		output_path (str): Path where to save the PNG file
		width (int): Desired width of the output image in pixels
		height (int): Desired height of the output image in pixels
		dpi (int): Resolution in pixels per inch
	"""
	try:
		# Convert first page of PDF to image at specified DPI
		pages = convert_from_path(pdf_path, dpi=dpi, first_page=1, last_page=1)
		
		# Get the first page (should be only one since we specified first_page=1, last_page=1)
		if pages:
			img = pages[0]
			
			# Resize to the desired dimensions
			img = img.resize((width, height), Image.LANCZOS)
			
			# Save the image as PNG
			img.save(output_path, "PNG")
			
			print(f"Successfully converted first page of {pdf_path} to {output_path}")
			print(f"Image dimensions: {width}x{height} pixels at {dpi} DPI")
		else:
			print("No pages were converted from the PDF.")
		
	except Exception as e:
		print(f"Error converting PDF to PNG: {e}")
		print(f"Error details: {sys.exc_info()}")

if __name__ == "__main__":
	# Get input from user
	# pdf_path = input("Enter the path to the PDF file: ")
	pdf_path = lao.guiFileOpen(path='F:/Research Department/MIMO/Market Insights', titlestring='Open PDF', extension=[('pdf files', '.pdf'), ('all files', '.*')])

	# Create output filename based on input filename
	base_name = os.path.splitext(os.path.basename(pdf_path))[0]
	output_path = f"F:/Research Department/MIMO/Market Insights/E-Blast Covers/{base_name}.png"
	
	# Convert the PDF to PNG with specified parameters
	convert_pdf_to_png(pdf_path, output_path)