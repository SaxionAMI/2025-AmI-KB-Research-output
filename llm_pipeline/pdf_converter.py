import pathlib
import logging
import pymupdf4llm

def convert_pdf_to_markdown(pdf_path: str, output_dir: pathlib.Path) -> pathlib.Path:
    pdf_file = pathlib.Path(pdf_path)
    pdf_stem = pdf_file.stem
    
    out_md = output_dir / f"{pdf_stem}.md"
    
    if out_md.exists():
        return out_md
    
    # Conversion
    md_text = pymupdf4llm.to_markdown(pdf_path)
    out_md.write_text(md_text, encoding="utf-8")
    return out_md

def convert_with_logging(pdf_path: str, output_dir: pathlib.Path):
    try:
        md_path = convert_pdf_to_markdown(pdf_path, output_dir)
        return str(md_path)
    except Exception as e:
        logging.warning(f"Failed to convert {pdf_path}: {e}")
        return None