import ast


SAMPLE = "a=1;\nb=2;"
SAMPLE = """

class Banana:

    def banana(self, x):
        inner_var = 3 
        self.y = x

"""

ast_root = ast.parse(SAMPLE)
print(ast.dump(ast_root, indent=2))

for node in ast.walk(ast_root):
    print(node)
    try:
        # print(dir(node))
        print(node.value.id, "<<<<<<<<<")
        print(node.id)

    except:
        try:
            print(node.name)
        except:
            ...


exit(0)


print(ast_root.body[0].col_offset, ast_root.body[0].lineno)


exit()


class MyVisitor(ast.NodeVisitor):
    def visit_ClassDef(self, node):
        body = node.body
        for statement in node.body:
            if isinstance(statement, ast.Assign):
                if len(statement.targets) == 1 and isinstance(statement.targets[0], ast.Name):
                    print('class: %s, %s=%s' % (str(node.name), str(statement.targets[0].id), str(statement.value)))


tree = ast.parse(open('/home/dkravchenko/WORK/sources/Bitbucket/ttf_udp/base/udp_env.py').read(), '')
MyVisitor().visit(tree)
