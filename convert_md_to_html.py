import sys
import re
import html

input_file = sys.argv[1]
output_file = sys.argv[2]

with open(input_file, 'r') as f:
    lines = f.readlines()

# handle front matter
front_matter = []
content_start = 0
if lines and lines[0].strip() == '---':
    front_matter.append(lines[0])
    for i in range(1, len(lines)):
        front_matter.append(lines[i])
        if lines[i].strip() == '---':
            content_start = i + 1
            break
else:
    content_start = 0

html_lines = []
list_tag = None

# helper for inline formatting
def convert_inline(text):
    text = html.escape(text)
    text = re.sub(r'!\[([^\]]+)\]\(([^)]+)\)', r'<img src="\2" alt="\1"/>', text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
    return text

for line in lines[content_start:]:
    stripped = line.rstrip('\n')
    if not stripped:
        if list_tag:
            html_lines.append(f'</{list_tag}>')
            list_tag = None
        continue
    heading_match = re.match(r'(#+)\s+(.*)', stripped)
    if heading_match:
        if list_tag:
            html_lines.append(f'</{list_tag}>')
            list_tag = None
        level = len(heading_match.group(1))
        text = convert_inline(heading_match.group(2).strip())
        html_lines.append(f'<h{level}>{text}</h{level}>')
        continue
    ul_match = re.match(r'[\s]*[-\*]\s+(.*)', stripped)
    if ul_match:
        if list_tag and list_tag != 'ul':
            html_lines.append(f'</{list_tag}>')
            list_tag = None
        if not list_tag:
            list_tag = 'ul'
            html_lines.append('<ul>')
        html_lines.append(f'  <li>{convert_inline(ul_match.group(1).strip())}</li>')
        continue
    ol_match = re.match(r'\d+\.\s+(.*)', stripped)
    if ol_match:
        if list_tag and list_tag != 'ol':
            html_lines.append(f'</{list_tag}>')
            list_tag = None
        if not list_tag:
            list_tag = 'ol'
            html_lines.append('<ol>')
        html_lines.append(f'  <li>{convert_inline(ol_match.group(1).strip())}</li>')
        continue
    # regular paragraph
    if list_tag:
        html_lines.append(f'</{list_tag}>')
        list_tag = None
    html_lines.append(f'<p>{convert_inline(stripped)}</p>')

if list_tag:
    html_lines.append(f'</{list_tag}>')

with open(output_file, 'w') as f:
    for line in front_matter:
        f.write(line)
    for line in html_lines:
        f.write(line + '\n')
