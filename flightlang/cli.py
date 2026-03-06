from __future__ import annotations
import argparse, pathlib, sys
from .parser import Parser
from .typecheck import typecheck
from .codegen_python import generate

def main():
    ap = argparse.ArgumentParser(prog='flight', description='FlightLang PoC CLI')
    sub = ap.add_subparsers(dest='cmd', required=True)
    runp = sub.add_parser('run', help='Compile and run a .fl mission')
    runp.add_argument('source', help='Path to .fl')
    checkp = sub.add_parser('check', help='Parse and validate a .fl mission')
    checkp.add_argument('source', help='Path to .fl')
    buildp = sub.add_parser('build', help='Compile a .fl mission to Python')
    buildp.add_argument('source', help='Path to .fl')
    buildp.add_argument('-o','--out', help='Output .py file', default='out.py')

    args = ap.parse_args()
    src_path = pathlib.Path(args.source)
    if not src_path.exists():
        print(f'Source not found: {src_path}', file=sys.stderr); sys.exit(1)
    src = src_path.read_text(encoding='utf-8')
    prog = Parser(src).parse(); typecheck(prog)
    if args.cmd == 'check':
        print(f'OK: {src_path}')
    elif args.cmd == 'build':
        py_code = generate(prog)
        out = pathlib.Path(args.out); out.write_text(py_code, encoding='utf-8'); print(f'Wrote: {out}')
    elif args.cmd == 'run':
        py_code = generate(prog)
        g = {}; exec(py_code, g, g)
    else:
        ap.print_help()

if __name__ == '__main__':
    main()
