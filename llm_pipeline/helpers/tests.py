
import pathlib

def analyze_markdown_stats(directory_path: pathlib.Path, char_threshold: int = -1) -> None:
    """
    Iterate all .md files in that directory and calculate their number of characters.
    """
    if not directory_path.exists():
        print(f"Directory not found: {directory_path}")
        return
        
    md_files = list(directory_path.glob('*.md'))
    total_files = len(md_files)
    
    if total_files == 0:
        print(f"No markdown files found in {directory_path}")
        return
        
    total_chars = 0
    files_exceeding_threshold = []
    
    for md_file in md_files:
        try:
            content = md_file.read_text(encoding='utf-8')
            count = len(content)
            total_chars += count
            
            if char_threshold != -1 and count > char_threshold:
                files_exceeding_threshold.append((md_file.name, count))
        except Exception as e:
            print(f"Error reading {md_file.name}: {e}")
            
    avg_chars = total_chars / total_files if total_files > 0 else 0
    
    print(f"Total markdown files: {total_files}")
    print(f"Total characters: {total_chars}")
    print(f"Average characters per file: {avg_chars:.2f}")
    
    if char_threshold is not None and files_exceeding_threshold:
        print(f"\nFiles exceeding {char_threshold} characters:")
        for name, count in files_exceeding_threshold:
            print(f"  {name}: {count} chars")
