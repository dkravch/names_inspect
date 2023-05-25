import ast


SAMPLE = "a=1;\nb=2;"

ast_root = ast.parse(SAMPLE)

print(ast.dump(ast_root, indent=2))
print(ast_root.body[0].col_offset, ast_root.body[0].lineno)
