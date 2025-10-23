import tkinter as tk
from tkinter import scrolledtext, messagebox, Menu
from spellchecker import SpellChecker
import re

class SpellCheckerApp:
	def __init__(self, root):
		self.root = root
		self.root.title("Spell Checker")
		self.root.geometry("800x600")
		
		# Initialize spell checker
		self.spell = SpellChecker()
		
		# Create menu
		self.create_menu()
		
		# Create main frame
		self.main_frame = tk.Frame(root)
		self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
		
		# Text area for input
		self.text_label = tk.Label(self.main_frame, text="Enter text to check:")
		self.text_label.pack(anchor=tk.W)
		
		self.text_area = scrolledtext.ScrolledText(self.main_frame, wrap=tk.WORD, height=15)
		self.text_area.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
		
		# Action buttons
		self.btn_frame = tk.Frame(self.main_frame)
		self.btn_frame.pack(fill=tk.X)
		
		self.check_button = tk.Button(self.btn_frame, text="Check Spelling", command=self.check_spelling)
		self.check_button.pack(side=tk.LEFT, padx=(0, 5))
		
		self.clear_button = tk.Button(self.btn_frame, text="Clear Text", command=self.clear_text)
		self.clear_button.pack(side=tk.LEFT)
		
		# Results area
		self.result_label = tk.Label(self.main_frame, text="Results:")
		self.result_label.pack(anchor=tk.W, pady=(10, 0))
		
		self.result_area = scrolledtext.ScrolledText(self.main_frame, wrap=tk.WORD, height=10)
		self.result_area.pack(fill=tk.BOTH, expand=True)
		self.result_area.config(state=tk.DISABLED)
		
		# Status bar
		self.status_var = tk.StringVar()
		self.status_var.set("Ready")
		self.status_bar = tk.Label(root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
		self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
	
	def create_menu(self):
		menu_bar = Menu(self.root)
		
		# File menu
		file_menu = Menu(menu_bar, tearoff=0)
		file_menu.add_command(label="New", command=self.clear_text)
		file_menu.add_separator()
		file_menu.add_command(label="Exit", command=self.root.quit)
		menu_bar.add_cascade(label="File", menu=file_menu)
		
		# Edit menu
		edit_menu = Menu(menu_bar, tearoff=0)
		edit_menu.add_command(label="Check Spelling", command=self.check_spelling)
		menu_bar.add_cascade(label="Edit", menu=edit_menu)
		
		# Help menu
		help_menu = Menu(menu_bar, tearoff=0)
		help_menu.add_command(label="About", command=self.show_about)
		menu_bar.add_cascade(label="Help", menu=help_menu)
		
		self.root.config(menu=menu_bar)
	
	def check_spelling(self):
		# Get text from the text area
		text = self.text_area.get("1.0", tk.END).strip()
		
		if not text:
			messagebox.showinfo("Info", "Please enter some text to check.")
			return
		
		# Update status
		self.status_var.set("Checking spelling...")
		self.root.update_idletasks()
		
		# Split text into words
		words = re.findall(r'\b\w+\b', text.lower())
		
		# Find misspelled words
		misspelled = self.spell.unknown(words)
		
		# Clear and enable result area
		self.result_area.config(state=tk.NORMAL)
		self.result_area.delete("1.0", tk.END)
		
		if not misspelled:
			self.result_area.insert(tk.END, "No spelling errors found!")
		else:
			self.result_area.insert(tk.END, f"Found {len(misspelled)} misspelled word(s):\n\n")
			
			for word in misspelled:
				corrections = self.spell.candidates(word)
				correction_str = ", ".join(list(corrections)[:5])  # Show up to 5 suggestions
				self.result_area.insert(tk.END, f"• {word}: {correction_str}\n")
		
		# Disable result area to prevent editing
		self.result_area.config(state=tk.DISABLED)
		
		# Update status
		self.status_var.set(f"Completed. Found {len(misspelled)} misspelled word(s).")
	
	def clear_text(self):
		self.text_area.delete("1.0", tk.END)
		self.result_area.config(state=tk.NORMAL)
		self.result_area.delete("1.0", tk.END)
		self.result_area.config(state=tk.DISABLED)
		self.status_var.set("Ready")
	
	def show_about(self):
		about_text = "Spell Checker Application\n\n" \
					"A simple desktop application for checking spelling.\n" \
					"Built with Python 3, Tkinter, and SpellChecker library."
		messagebox.showinfo("About", about_text)

if __name__ == "__main__":
	root = tk.Tk()
	app = SpellCheckerApp(root)
	root.mainloop()