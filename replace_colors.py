import os
import re

# The new color palette
# 1. Primary background: #f6f0d7
# 2. Light green accent: #c5d89d
# 3. Sage green accent: #9cab84
# 4. Dark olive focus/header: #89986d

color_replacements = {
    # backgrounds
    r'#d1cece9c': '#f6f0d7',
    r'whitesmoke': '#f6f0d7',
    r'rgb\(253, 229, 233\)': '#f6f0d7',
    
    # sidebar and dark colors
    r'#0c1e35': '#89986d',
    r'#bd508d': '#89986d',
    
    # buttons, accents
    r'rgba\(255,\ 165,\ 0,\ 1\)': '#9cab84',
    r'#f69221': '#9cab84',
    r'#f6911e': '#9cab84',
    r'lightpink': '#c5d89d',
    r'rgb\(236, 227, 209\)': '#c5d89d',
    r'#f3008a': '#89986d',
    r'#49c1a2': '#9cab84', # Create test button
    
    # Gradients
    r'linear-gradient\(90deg, rgba\(255, 165, 0, 1\) 0%, rgb\(230, 0, 230\) 100%\)': '#89986d',
}

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    new_content = content
    for old_color, new_color in color_replacements.items():
        new_content = re.sub(old_color, new_color, new_content, flags=re.IGNORECASE)
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {filepath}")

base_dir = '/Users/mohitnandaniya.appleicloud.com/Downloads/QuizWithAdmin-master/quiz/'
for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file.endswith('.css') or file.endswith('.html'):
            process_file(os.path.join(root, file))
