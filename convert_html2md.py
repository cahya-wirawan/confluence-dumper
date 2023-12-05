from pathlib import Path
from markdownify import markdownify
import argparse
import re
import lxml.html
import lxml.html.clean


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output_dir', default="markdown")
    parser.add_argument('-f', '--force', action=argparse.BooleanOptionalAction, default=False)
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
            if md_file.exists() and not args.force:
                continue
            html = html.replace("&#160;", " ")
            cleaner = lxml.html.clean.Cleaner(style=True)
            doc = lxml.html.fromstring(html)
            uls = doc.xpath("//td/ul")
            ps = doc.xpath("//td//p")
            for p in ps:
                p_string = lxml.html.tostring(p, encoding='unicode')
                p_string = p_string.replace("<p>", "").replace("</p>", "#br#")
                p_string = f"<div>{p_string}</div"
                td = p.getparent()
                td.remove(p)
                td.append(lxml.html.fromstring(p_string))
            for ul in uls:
                ul_string = lxml.html.tostring(ul, encoding='unicode')
                ul_string = ul_string.replace("<li>", "#li+").replace("</li>", "#li-").replace("<ul>", "#ul+").replace("</ul>", "#ul-")
                ul_string = f"<div>{ul_string}</div"
                td = ul.getparent()
                td.remove(ul)
                td.append(lxml.html.fromstring(ul_string))
            doc = cleaner.clean_html(doc)
            doc = lxml.html.tostring(doc, encoding='unicode')
            md = markdownify(doc, heading_style="ATX")
            md = md[:md.find("## Attachments")]
            md = md.replace("#li+", "<li>").replace("#li-", "</li>").replace("#ul+", "<ul>").replace("#ul-", "</ul>")
            md = md.replace("#br#", "<br>")
            md_len = len(md)
            if md_len < 1024:
                continue
            md = md[md.find("# "):]
            md = re.sub(r"!?\[([^]]*)]\([^)]+\)", r"\1", md)
            md = re.sub(r"\n\s+\n", "\n\n", md)
            md = re.sub(r"\n{3,}", "\n\n", md)
            md_file.write_text(md)

    print("Done")


if __name__ == "__main__":
    main()