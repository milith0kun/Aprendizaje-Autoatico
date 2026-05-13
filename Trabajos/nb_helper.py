import nbformat as nbf
import sys
import json

def read_nb(path):
    with open(path, 'r', encoding='utf-8') as f:
        return nbf.read(f, as_version=4)

def write_nb(nb, path):
    with open(path, 'w', encoding='utf-8') as f:
        nbf.write(nb, f)

def add_cell(path, content, cell_type='code', index=None):
    nb = read_nb(path)
    if cell_type == 'code':
        new_cell = nbf.v4.new_code_cell(content)
    else:
        new_cell = nbf.v4.new_markdown_cell(content)
    
    if index is None:
        nb.cells.append(new_cell)
    else:
        nb.cells.insert(index, new_cell)
    
    write_nb(nb, path)
    print(f"Added {cell_type} cell at index {index if index is not None else 'end'}")

def list_cells(path):
    nb = read_nb(path)
    for i, cell in enumerate(nb.cells):
        print(f"[{i}] {cell.cell_type}: {cell.source[:50].replace('\\n', ' ')}...")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python nb_helper.py <command> <path> [args]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    path = sys.argv[2]
    
    if cmd == "list":
        list_cells(path)
    elif cmd == "add-code":
        content = sys.stdin.read()
        add_cell(path, content, 'code')
    elif cmd == "add-markdown":
        content = sys.stdin.read()
        add_cell(path, content, 'markdown')
