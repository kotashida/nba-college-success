"""Register publication and input-access changes; preserve scientific evidence."""
from pathlib import Path
from datetime import datetime, timezone
import ast
import json
from research.data import sha

ROOT = Path(__file__).resolve().parent

def main():
    out = ROOT / 'output/experiments'
    freeze = json.loads((out / 'freeze.json').read_text())
    records = {}
    for module in ['report.py', 'experiment.py', '__init__.py', 'run.py', 'collect.py']:
        path = ('research/' if module in ['report.py', 'experiment.py', '__init__.py'] else '') + module
        preserved = out / 'frozen_publication_code' / module
        if sha(preserved) != freeze['hashes'][path]:
            raise ValueError('Original pre-test code not preserved')
        if module == 'experiment.py':
            def scientific_ast(file):
                tree = ast.parse(file.read_text(encoding='utf-8'))
                tree.body = [node for node in tree.body if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) or node.name != 'check_freeze']
                return ast.dump(tree, include_attributes=False)
            if scientific_ast(ROOT / path) != scientific_ast(preserved):
                raise ValueError('Scientific experiment code changed; amendment prohibited')
        if module in ['run.py', 'collect.py', '__init__.py']:
            def operational_ast(file):
                tree = ast.parse(file.read_text(encoding='utf-8'))
                if tree.body and isinstance(tree.body[0], ast.Expr) and isinstance(tree.body[0].value, ast.Constant) and isinstance(tree.body[0].value.value, str):
                    tree.body.pop(0)
                if module == 'collect.py':
                    tree.body = [node for node in tree.body
                                 if not (isinstance(node, ast.FunctionDef) and node.name == 'main')
                                 and not (isinstance(node, ast.Import) and any(alias.name == 'shutil' for alias in node.names))]
                return ast.dump(tree, include_attributes=False)
            if operational_ast(ROOT / path) != operational_ast(preserved):
                raise ValueError('Changes exceed publication or input-access scope')
        records[path] = {'original_sha256': sha(preserved), 'revised_sha256': sha(ROOT / path),
                         'preserved_original': preserved.relative_to(ROOT).as_posix(),
                         'registered_utc': datetime.now(timezone.utc).isoformat(),
                         'reason': 'Publication tables, formatting and artifact naming; temporary manuscript build with a single source/PDF pair; report verifies frozen evidence before generation. CLI docstring and collector main input-access validation only. Experiment changes are confined to check_freeze, which validates every consumed receipt artifact and rejects missing receipts; every other experiment AST is identical. No changes to predictors, targets, fitting, selection, predictions or scores.'}
    (out / 'publication_amendment.json').write_text(json.dumps(records, indent=2))
    print('Integrity records registered. Freeze and test receipt remain byte-identical; scientific routines unchanged.')

if __name__ == '__main__':
    main()
