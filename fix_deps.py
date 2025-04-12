#!/usr/bin/env python3
"""
Fix for parsimonious library in Python 3.11
This patches the parsimonious library by modifying the expressions.py file
to use inspect.getfullargspec instead of the deprecated getargspec.
"""

import os
import sys
import site
import subprocess

def find_parsimonious_path():
    """Find the parsimonious package without importing it."""
    # Try to get site packages directories
    site_packages = site.getsitepackages()
    
    # Add user site-packages
    if site.USER_SITE:
        site_packages.append(site.USER_SITE)
    
    # Also check current Python path
    site_packages.extend(sys.path)
    
    for path in site_packages:
        parsimonious_path = os.path.join(path, 'parsimonious')
        expressions_path = os.path.join(parsimonious_path, 'expressions.py')
        if os.path.exists(expressions_path):
            return expressions_path
    
    # If we can't find it in site-packages, try using pip to locate it
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'show', '-f', 'parsimonious'], 
            capture_output=True, 
            text=True
        )
        
        if result.returncode == 0:
            # Parse the output to find the location
            lines = result.stdout.strip().split('\n')
            location = None
            for line in lines:
                if line.startswith('Location:'):
                    location = line.split(':', 1)[1].strip()
                    break
            
            if location:
                expressions_path = os.path.join(location, 'parsimonious', 'expressions.py')
                if os.path.exists(expressions_path):
                    return expressions_path
    except Exception:
        pass
        
    return None

def patch_parsimonious():
    expressions_path = find_parsimonious_path()
    
    if not expressions_path:
        print("❌ Could not find parsimonious package. Is it installed?")
        return False
    
    print(f"Patching {expressions_path}...")
    
    try:
        # Read the file
        with open(expressions_path, 'r') as f:
            content = f.read()
        
        # Direct fix for the specific error
        if 'from inspect import getargspec' in content:
            content = content.replace('from inspect import getargspec', 'from inspect import getfullargspec as getargspec')
            
            # Write the file back
            with open(expressions_path, 'w') as f:
                f.write(content)
            
            print("✅ Successfully patched parsimonious!")
            return True
        else:
            print("⚠️ Could not find 'from inspect import getargspec' in the file.")
            return False
    except Exception as e:
        print(f"❌ Error patching parsimonious: {str(e)}")
        return False

if __name__ == "__main__":
    if patch_parsimonious():
        print("\nYou can now run your Streamlit app with: streamlit run streamlit_app.py")
    else:
        print("\nPlease try reinstalling the dependencies with: pip install -r requirements.txt") 