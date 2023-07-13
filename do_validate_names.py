import ast
import os
import keyword
import builtins

import numpy as np
from sklearn.cluster import AffinityPropagation
import distance

PATH = os.environ.get("NAME_VALIDATION_PATH", "/home/dkravchenko/WORK/ON_THE_ROAD/CODE/NOT_MY/ttf_udp")
EXCLUDE_NAMES = keyword.kwlist + [i for i in dir(builtins) if not i.startswith("__")]

# TODO Variable like self.smth, cls.smth, in-class defi

########################################################################################################################


class GeneralNode:

    def __init__(self, node):

        self.general_name = getattr(node, 'id', None) or getattr(node, 'name', None) or getattr(node, 'attr', None)

        if self.general_name:
            self.name_type = ('id',
                              'name',
                              'attr')[[idx for idx, val in enumerate([hasattr(node, 'id'),
                                                                      hasattr(node, 'name'),
                                                                      hasattr(node, 'attr')]) if val is True][0]]
        else:
            self.name_type = None

        self.instance = node

    def is_considered(self):

        if not self.general_name or not self.general_name:
            return False

        if not isinstance(self.instance, (ast.Name, ast.Attribute)):
            return False

        if isinstance(getattr(self.instance, 'ctx', None), ast.Load):
            return False

        if self.name_type in ('id', 'name'):
            if self.general_name in EXCLUDE_NAMES:
                return False

        return True


########################################################################################################################


def _get_names(root):
    res = []
    for node in ast.walk(root):
        general_node = GeneralNode(node)
        if general_node.is_considered():
            res.append(general_node.general_name)
    return sorted(set(res))


def _get_name_nodes(root):
    res = []
    for node in ast.walk(root):
        general_node = GeneralNode(node)
        if general_node.is_considered():
            res.append(general_node.instance)
    return res

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

            names = _get_names(ast_root)
            name_nodes = _get_name_nodes(ast_root)

            max_name_length = max([len(i) for i in names] if names else [0])
            max_func_length = max([len(f.name) for f in function_nodes] if function_nodes else [0])

            # Group variable names by clusters (https://en.wikipedia.org/wiki/Affinity_propagation)
            grouped_names = []
            if names:
                words = np.asarray(names)
                lev_similarity = -1 * np.array([[distance.levenshtein(w1, w2) for w1 in words] for w2 in words],
                                               dtype=float)
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
                filtered_name_nodes = sorted([GeneralNode(node) for node in name_nodes
                                              if (getattr(node, 'id', None) or getattr(node, 'attr', None)) in cluster],
                                             key=lambda x: getattr(x.instance, 'id', None) or getattr(x.instance,
                                                                                                      'attr', None))

                for general_node in filtered_name_nodes:
                    if not general_node.general_name:
                        continue
                    print(str(general_node.general_name).ljust(max_name_length, " "),
                          str(general_node.instance.lineno).ljust(6, " "),
                          content_lines[general_node.instance.lineno - 1])

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



