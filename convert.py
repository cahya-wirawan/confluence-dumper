from pathlib import Path
from markdownify import markdownify
import argparse
import re
import lxml.html
import lxml.html.clean


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output_dir', default="markdown")
    args = parser.parse_args()

    output_dir = args.output_dir
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    # find html files in export directory using pathlib module
    export_dir = Path("export")
    for file in export_dir.glob("**/*.html"):
        # if filename contains only numbers, skip it
        if file.stem.isnumeric() or file.stat().st_size < 1024:
            continue
        with open(file, "r", encoding="utf-8", errors='ignore') as f:
            print(f"Converting {file}")
            html = f.read()
            md_file = Path(re.sub(r'^export', f"{output_dir}", str(file)))
            md_file = md_file.with_suffix(".md")
            md_file.parent.mkdir(parents=True, exist_ok=True)
            if md_file.exists():
                continue
            html = html.replace("&#160;", " ")
            cleaner = lxml.html.clean.Cleaner(style=True)
            doc = lxml.html.fromstring(html)
            doc = cleaner.clean_html(doc)
            # doc = doc.text_content()
            doc = lxml.html.tostring(doc, encoding='unicode')
            md = markdownify(doc, heading_style="ATX")
            md = md[:md.find("## Attachments")]
            md_len = len(md)
            if md_len < 1024:
                continue
            md = md[md.find("# "):]
            md_file.write_text(md)

    print("Done")


if __name__ == "__main__":
    main()