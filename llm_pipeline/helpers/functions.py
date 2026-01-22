import re
import pathlib

def extract_funding_sections(md_file_path: str) -> str:
    """
    Extract paragraphs containing acknowledgement/funding keywords from a markdown file.
    """
    keywords = ['acknowledgement', 'acknowledgements', 'funding', 'funded']
    pattern = re.compile('|'.join(keywords), re.IGNORECASE)
    
    with open(md_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    paragraphs = re.split(r'\n\s*\n', content)
    
    matched_paragraphs = []
    
    for para in paragraphs:
        if pattern.search(para):
            if len(para) > 10000:
                matches = list(pattern.finditer(para))
                if matches:
                    first_match_start = matches[0].start()
                    
                    # calculate truncation bounds. take 1000 chars before 1st keyword, 3000 chars after
                    start_pos = max(0, first_match_start - 1000)
                    end_pos = min(len(para), first_match_start + 3000)
                    
                    truncated = "[Content truncated] " + para[start_pos:end_pos] + " [Content truncated]"
                    matched_paragraphs.append(truncated.strip())
                else:
                    matched_paragraphs.append("[Content truncated] " + para.strip() + " [Content truncated]")
            else:
                matched_paragraphs.append("[Content truncated] " + para.strip() + " [Content truncated]")
    
    return '\n\n'.join(matched_paragraphs)

def get_files_below_threshold(directory_path: pathlib.Path, char_threshold: int) -> list[pathlib.Path]:
    """
    Returns a list of markdown files in the directory that have fewer characters than the threshold.
    """
    if not directory_path.exists():
        print(f"Directory not found: {directory_path}")
        return []
        
    md_files = list(directory_path.glob('*.md'))
    files_below_threshold = []
    
    for md_file in md_files:
        try:
            content = md_file.read_text(encoding='utf-8')
            if len(content) < char_threshold:
                files_below_threshold.append(md_file)
        except Exception as e:
            print(f"Error reading {md_file.name}: {e}")
            
    return files_below_threshold


