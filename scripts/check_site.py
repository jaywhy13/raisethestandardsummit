"""Basic checks for the static site: tag nesting and local asset references."""
import os
import re
import sys
from html.parser import HTMLParser

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "source", "track", "wbr"}
SITE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


class NestingChecker(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append((tag, self.getpos()))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if self.stack and self.stack[-1][0] == tag:
            self.stack.pop()
        else:
            self.errors.append(f"unexpected </{tag}> at line {self.getpos()[0]}")


def main():
    path = os.path.join(SITE, "index.html")
    with open(path, encoding="utf-8") as f:
        html = f.read()

    errors = []

    checker = NestingChecker()
    checker.feed(html)
    errors.extend(checker.errors)
    errors.extend(f"unclosed <{tag}> opened at line {pos[0]}" for tag, pos in checker.stack)

    refs = set(re.findall(r'(?:src|href)="([^"#?]+)"', html))
    for ref in sorted(refs):
        if ref.startswith(("http://", "https://", "//", "mailto:")):
            continue
        if not os.path.exists(os.path.join(SITE, ref)):
            errors.append(f"missing local file referenced: {ref}")

    for err in errors:
        print(f"ERROR: {err}")
    print(f"checked {path}: {len(refs)} references, {len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
