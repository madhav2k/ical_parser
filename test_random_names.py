#!/usr/bin/env python3
"""
Test script to verify random name generation for calendar events.
"""

import sys
import os
import string
import random

# Add the VedicCalendarParser directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'VedicCalendarParser'))

def generate_random_name(prefix):
    """
    Generate a randomized 3-letter name with the specified prefix.
    
    Args:
        prefix (str): The prefix to use ('D' for Durmuhurtam, 'V' for Varjyam)
    
    Returns:
        str: A randomized name like 'DAB', 'VXY', etc.
    """
    # Generate 2 random uppercase letters
    random_letters = ''.join(random.choices(string.ascii_uppercase, k=2))
    return f"{prefix}{random_letters}"

def test_random_names():
    """Test the random name generation function."""
    print("Testing random name generation...")
    print("=" * 40)
    
    # Test Durmuhurtam names (D prefix)
    print("Dur Muhurtamulu names (D prefix):")
    for i in range(10):
        name = generate_random_name('D')
        print(f"  {i+1:2d}. {name}")
    
    print()
    
    # Test Varjyam names (V prefix)
    print("Varjyam names (V prefix):")
    for i in range(10):
        name = generate_random_name('V')
        print(f"  {i+1:2d}. {name}")
    
    print()
    
    # Test that names are always 3 characters
    print("Verifying name length:")
    for prefix in ['D', 'V']:
        for i in range(5):
            name = generate_random_name(prefix)
            length = len(name)
            print(f"  {name}: {length} characters {'✓' if length == 3 else '✗'}")
    
    print()
    
    # Test that names start with correct prefix
    print("Verifying name prefixes:")
    for prefix in ['D', 'V']:
        for i in range(5):
            name = generate_random_name(prefix)
            starts_with_prefix = name.startswith(prefix)
            print(f"  {name}: starts with '{prefix}' {'✓' if starts_with_prefix else '✗'}")
    
    print()
    print("Test completed!")

if __name__ == "__main__":
    test_random_names() 