import ast
import os
import keyword
import builtins

import numpy as np
from sklearn.cluster import AffinityPropagation
import distance

PATH = os.environ.get("BANANA", "/home/dkravchenko/WORK/sources/Bitbucket/ttf_udp")
EXCLUDE_NAMES = keyword.kwlist + [i for i in dir(builtins) if not i.startswith("__")]

########################################################################################################################

for root, dirs, files in os.walk(PATH, topdown=False):
    for name in files:
        if not name.endswith(".py"):
            continue
        full_path = os.path.join(root, name)
        f" [ {full_path} ] ".center(120, '-')
        print(f" [ {full_path} ] ".center(120, '-'))

        with open(full_path) as f:
            content = f.read()
            content_lines = content.split('\n')
            ast_root = ast.parse(content)

            function_nodes = [node for node in ast.walk(ast_root) if isinstance(node, ast.FunctionDef)]
            classes = [node.name for node in ast.walk(ast_root) if isinstance(node, ast.ClassDef)]
            import_nodes = [node for node in ast.walk(ast_root) if isinstance(node, (ast.Import, ast.ImportFrom))]

            names = sorted({node.id for node in ast.walk(ast_root)
                            if isinstance(node, ast.Name) and node.id not in EXCLUDE_NAMES
                            and not isinstance(node.ctx, ast.Load)})  # to only handle names assigned to, not used

            name_nodes = [node for node in ast.walk(ast_root)
                          if isinstance(node, ast.Name) and node.id not in EXCLUDE_NAMES
                          and not isinstance(node.ctx, ast.Load)]  # to only handle names assigned to, not used

            max_name_length = max([len(i) for i in names] if names else [0])
            max_func_length = max([len(f.name) for f in function_nodes] if function_nodes else [0])

            # Group variable names by clusters (https://en.wikipedia.org/wiki/Affinity_propagation)
            grouped_names = []
            if names:
                words = np.asarray(names)
                lev_similarity = -1 * np.array([[distance.levenshtein(w1, w2) for w1 in words] for w2 in words], dtype=float)
                affprop = AffinityPropagation(affinity="precomputed", damping=0.5)
                affprop.fit([list(item) for item in lev_similarity])

                for cluster_id in np.unique(affprop.labels_):
                    exemplar = words[affprop.cluster_centers_indices_[cluster_id]]
                    cluster = np.unique(words[np.nonzero(affprop.labels_ == cluster_id)])
                    cluster_str = ", ".join(cluster)
                    # print(" - *%s:* %s" % (exemplar, cluster_str))
                    grouped_names.append(list(cluster))

            print("\n(names, assigned to only, not used)")
            for cluster in grouped_names:
                # print(f"<<<< {cluster}")
                filtered_name_nodes = sorted([node for node in name_nodes if node.id in cluster],
                                             key=lambda x: x.id)
                for node in filtered_name_nodes:
                    if node.id not in cluster:
                        continue
                    print(str(node.id).ljust(max_name_length, " "),
                          str(node.lineno).ljust(6, " "), content_lines[node.lineno - 1])

            print("\n(functions)")
            for function in function_nodes:
                print(function.name.ljust(max_func_length, " "), content_lines[function.lineno - 1])

            print("\n(classes)")
            for class_ in classes:
                print(class_)

            print("\n(imports)")
            for import_ in import_nodes:
                for obj in import_.names:
                    print(obj.name)



