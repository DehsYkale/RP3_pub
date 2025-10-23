
import sys
import os
import subprocess

def debug_python_environment():
	"""
	Debug script to identify Python environment and package installation issues
	"""
	print("="*60)
	print("PYTHON ENVIRONMENT DEBUG")
	print("="*60)
	
	# Python version and executable
	print(f"Python version: {sys.version}")
	print(f"Python executable: {sys.executable}")
	print(f"Python path: {sys.path}")
	
	# Current working directory
	print(f"Current working directory: {os.getcwd()}")
	
	# Check if we're in a virtual environment
	if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
		print("✓ Running in virtual environment")
		print(f"Virtual env prefix: {sys.prefix}")
	else:
		print("✗ NOT running in virtual environment")
	
	# Try to list installed packages
	print("\n" + "="*40)
	print("INSTALLED PACKAGES")
	print("="*40)
	
	try:
		result = subprocess.run([sys.executable, '-m', 'pip', 'list'], 
							  capture_output=True, text=True)
		if result.returncode == 0:
			packages = result.stdout
			print("Installed packages:")
			# Look for relevant packages
			for line in packages.split('\n'):
				if any(pkg in line.lower() for pkg in ['shapefile', 'pyshp', 'shapely', 'gdal', 'fiona']):
					print(f"  ✓ {line}")
		else:
			print(f"Error running pip list: {result.stderr}")
	except Exception as e:
		print(f"Could not run pip list: {e}")
	
	# Try importing the modules
	print("\n" + "="*40)
	print("MODULE IMPORT TEST")
	print("="*40)
	
	modules_to_test = ['shapefile', 'shapely', 'fiona', 'geopandas']
	for module in modules_to_test:
		try:
			__import__(module)
			print(f"  ✓ {module} - OK")
		except ImportError as e:
			print(f"  ✗ {module} - FAILED: {e}")
	
	print("\n" + "="*60)
	print("RECOMMENDATIONS")
	print("="*60)
	
	print("1. Try installing with the current Python executable:")
	print(f"   {sys.executable} -m pip install pyshp shapely")
	
	print("\n2. Or try these alternatives:")
	print("   pip install --user pyshp shapely")
	print("   python -m pip install --upgrade pip")
	print("   python -m pip install pyshp shapely")

if __name__ == "__main__":
	debug_python_environment()