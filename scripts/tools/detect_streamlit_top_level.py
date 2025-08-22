"""
Detect top-level Streamlit UI calls in the repository using AST.
This tool scans .py files and reports calls like st.title/st.header/st.subheader
that appear at module top-level (not nested inside functions/classes).

Run: python scripts/tools/detect_streamlit_top_level.py
"""
from pathlib import Path
import ast

ROOT = Path(__file__).resolve().parents[3]  # workspace root

STREAMLIT_ATTRS = {"title", "header", "subheader", "markdown", "set_page_config"}


class StreamlitTopLevelVisitor(ast.NodeVisitor):
    def __init__(self):
        self.top_level_calls = []

    def visit_Expr(self, node):
        # Look for Call expressions like st.title(...)
        value = node.value
        if isinstance(value, ast.Call):
            func = value.func
            if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
                if func.value.id == "st" and func.attr in STREAMLIT_ATTRS:
                    self.top_level_calls.append((func.attr, node.lineno))
        self.generic_visit(node)


def analyze_file(path: Path):
    try:
        src = path.read_text(encoding="utf-8")
        tree = ast.parse(src, filename=str(path))
    except Exception as e:
        return f"ERROR parsing {path}: {e}"

    visitor = StreamlitTopLevelVisitor()
    # Only visit top-level statements: iterate Module.body and check Expr/Assign/If etc.
    for node in tree.body:
        # If node is a simple Expr(Call) we can pass it to visitor
        if isinstance(node, ast.Expr):
            visitor.visit(node)
        # If it's an If at top-level, skip because it's guarded
        # If it's FunctionDef or ClassDef it's safe
    if visitor.top_level_calls:
        return visitor.top_level_calls
    return None


def main():
    py_files = list(ROOT.rglob("*.py"))
    results = {}
    for p in py_files:
        # skip venv, .git, __pycache__ and hidden folders
        if any(part.startswith('.') or part in ("__pycache__", "venv", ".venv", "env") for part in p.parts):
            continue
        res = analyze_file(p)
        if res:
            results[str(p.relative_to(ROOT))] = res

    if not results:
        print("No top-level Streamlit calls found.")
        return

    print("Top-level Streamlit calls detected:")
    for fname, calls in sorted(results.items()):
        print(f"\n- {fname}")
        if isinstance(calls, str):
            print(f"  {calls}")
        else:
            for attr, lineno in calls:
                print(f"  line {lineno}: st.{attr}(...)")


if __name__ == '__main__':
    main()
