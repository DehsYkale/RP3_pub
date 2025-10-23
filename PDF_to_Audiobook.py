# Convert PDF to AudioBook
import lao
import PyPDF2
from gtts import gTTS
import re

def clean_pdf_text(text):
	# Remove hyphenation at line breaks
	text = re.sub(r'-\n', '', text)
	# Remove line breaks within sentences
	text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
	# Replace multiple newlines with period + space
	text = re.sub(r'\n+', '. ', text)
	# Remove multiple spaces
	text = re.sub(r'\s+', ' ', text)
	# Remove page numbers (common pattern)
	text = re.sub(r'\b\d{1,3}\b(?=\s|$)', '', text)
	# Clean up punctuation spacing
	text = re.sub(r'\s+([.,!?;:])', r'\1', text)
	return text.strip()

pdf = lao.guiFileOpen(path=r'C:\TEMP', titlestring='Select a PDF file', extension=[('PDF files', '.pdf'),  ('all files', '.*')])

# Read PDF
pdfReader = PyPDF2.PdfReader(open(pdf, 'rb'))

# Accumulate all text with cleaning
all_text = ""
for page_num in range(len(pdfReader.pages)):
	page = pdfReader.pages[page_num]
	text = page.extract_text()
	cleaned_text = clean_pdf_text(text)
	all_text += cleaned_text + " "

# Final cleanup
all_text = clean_pdf_text(all_text)

# Convert to speech using Google TTS
print("Generating audiobook...")
tts = gTTS(text=all_text, lang='en', slow=False)
tts.save(r'C:\TEMP\audiobook.mp3')

print("Audiobook saved to C:\\TEMP\\audiobook.mp3")