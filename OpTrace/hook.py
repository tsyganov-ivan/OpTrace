import sys

from importlib.machinery import SourceFileLoader
from importlib.abc import MetaPathFinder

from OpTrace.wrapper import Wrapper
from OpTrace.reporter import CommonReporter
from OpTrace.wrapped_opcode import FileOpcode


_REAL_PATHFINDER = next((
    item
    for item in sys.meta_path
    if getattr(item, '__name__', None) == 'PathFinder'
), None)

assert _REAL_PATHFINDER is not None, 'Original PathFinder not found.'

_PATHFINDER_INDEX = sys.meta_path.index(_REAL_PATHFINDER)


class OpTraceHook:
    def __init__(self, modules, debug=False):
        self.target_modules = modules
        self.module_opcodes = dict()
        self.debug = debug

    def log(self, *args):
        if self.debug:
            print(*args)

    def make_marker(self, module, source):
        self.module_opcodes[module] = FileOpcode(module, source)
        def mark(codeobj_id, opcode):
            self.module_opcodes[module].add(codeobj_id, opcode.offset, opcode)
            self.log(
                ' mark {}_{} {}'.format(codeobj_id, opcode.offset, repr(opcode)))
        return mark

    def make_visitor(self, module):
        def visit(codeobj_id, opcode):
            self.module_opcodes[module].visit(codeobj_id, opcode.offset, opcode)
            self.log(' visit {}_{} {}'.format(
                codeobj_id, opcode.offset, repr(opcode)))
        return visit

    def report(self):
        reporter = CommonReporter(self.module_opcodes)
        reporter.report()

    def make_loader(self):
        class OpTraceLoader(SourceFileLoader):
            def get_code(_, module_name):
                code = super().get_code(module_name)
                if module_name in self.target_modules:
                    source = super().get_source(module_name).splitlines()
                    wrapper = Wrapper(
                        trace_func=self.make_visitor(module_name),
                        mark_func=self.make_marker(module_name, source)
                    )
                    new_code = wrapper.wrap_code(code)
                    del wrapper
                    return new_code
                return code
        return OpTraceLoader

    def make_finder(self):
        class OpTraceFinder(MetaPathFinder):
            @classmethod
            def find_module(cls, fullname, path=None):
                self.log('find module ', fullname)
                spec = _REAL_PATHFINDER.find_spec(fullname, path)
                if not spec:
                    if not hasattr(self, 'find_spec'):
                        return
                    found = self.find_spec(fullname, path)
                    return found.loader if found is not None else None
                loader = spec.loader
                loader.__class__ = self.make_loader()
                return loader
        return OpTraceFinder

    def setup_hook(self):
        sys.meta_path[_PATHFINDER_INDEX] = self.make_finder()

    def teardown_hook(self):
        sys.meta_path[_PATHFINDER_INDEX] = _REAL_PATHFINDER
