# autotestsmith/ast_index.py
import tree_sitter_python as tspython
from tree_sitter import Language, Parser

CONTROL_FLOW_TYPES = {
    "if_statement", "for_statement", "while_statement",
    "try_statement", "with_statement", "match_statement"
}

class AstIndex:
    def __init__(self, code: str, debug: bool = False):
        self.code = code
        self.debug = debug
        PY_LANGUAGE = Language(tspython.language())
        self.parser = Parser(PY_LANGUAGE)
        self.tree = self.parser.parse(code.encode())

    def _node_snippet(self, node, max_len: int = 60) -> str:
        text = self.code[node.start_byte:node.end_byte]
        single_line = " ".join(text.split())
        if len(single_line) > max_len:
            return single_line[:max_len] + "..."
        return single_line

    def _walk(self, node):
        yield node
        for i in range(node.child_count):
            yield from self._walk(node.child(i))

    def functions(self):
        # yields (name, node)
        root = self.tree.root_node
        for n in self._walk(root):
            if n.type == "function_definition":
                name_node = n.child_by_field_name("name")
                if name_node:
                    name = self.code[name_node.start_byte:name_node.end_byte]
                    if self.debug:
                        print(f"FUNCTION name={name} bytes=[{n.start_byte}:{n.end_byte}]")
                    yield (name, n)

    def nestedness(self, func_node):
        count = 0
        if self.debug:
            name_node = func_node.child_by_field_name("name")
            func_name = self.code[name_node.start_byte:name_node.end_byte] if name_node else "<?>"
            print(f"\n=== ASTIndex: nestedness walk for {func_name} ===")
        for n in self._walk(func_node):
            if n.type in CONTROL_FLOW_TYPES:
                count += 1
                if self.debug:
                    print(f"  CTRL {n.type} at [{n.start_byte}:{n.end_byte}] -> +1")
        if self.debug:
            print(f"  total nestedness={count}")
        return count

    def calls_in_func(self, func_node):
        # tree-sitter python: call nodes look like "call"
        # child_by_field_name("function") -> callee
        calls = []
        if self.debug:
            name_node = func_node.child_by_field_name("name")
            func_name = self.code[name_node.start_byte:name_node.end_byte] if name_node else "<?>"
            print(f"\n=== ASTIndex: call discovery for {func_name} ===")
        for n in self._walk(func_node):
            if n.type == "call":
                callee = n.child_by_field_name("function")
                if callee:
                    callee_name = self.code[callee.start_byte:callee.end_byte]
                    calls.append(callee_name)
                    if self.debug:
                        print(f"  CALL {callee_name} at [{n.start_byte}:{n.end_byte}]")
        if self.debug:
            print(f"  calls={calls if calls else []}")
        return calls


