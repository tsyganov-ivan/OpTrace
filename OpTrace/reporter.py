from collections import defaultdict
from OpTrace.opcode_resolver import OpcodeResolver


class FileReporter:
    def __init__(self, data):
        self.module = data.module
        self.opcodes = data.opcodes
        self.source = data.source

        self.resolve = OpcodeResolver().resolve

        self.missing_positions = defaultdict(list)
        self.cannot_represent = defaultdict(list)

    def log(self, *args):
        print(*args)

    def add_missing(self, opcode, line, source, prev_position):
        missing = self.resolve(opcode, line, source, prev_position)
        if missing:
            self.missing_positions[(missing.line, missing.comment)].extend(
                range(missing.start, missing.stop))
        else:
            self.cannot_represent[line].append(opcode)

    def analyze(self):
        line_lumber = 0
        line_source = self.source[line_lumber]
        prev_position = (0, 0)
        for key, opcode in sorted(self.opcodes.items()):
            if opcode.starts_line:
                line_lumber = opcode.starts_line-1
                line_source = self.source[line_lumber]

            if opcode.argrepr and opcode.argrepr in line_source:
                prev_position = (
                    line_lumber, line_source.index(opcode.argrepr)-1)

            if opcode.visited:
                continue

            self.add_missing(opcode, line_lumber, line_source, prev_position)

    def make_report_line(self, line, reason, indexes):
        num = '{: >4}:'.format(line)
        source = '{} {}'.format(num, self.source[line])
        underline = '{left_spaces} {underline} {reason}'.format(
            left_spaces=' ' * len(num),
            reason=reason,
            underline=''.join(
                '^' if index in indexes else ' '
                for index in range(len(self.source[line]))
            ).rstrip(),
        )
        return '{}\n{}'.format(source, underline)

    def report(self):
        self.analyze()
        self.log('----------- Report {} --------------'.format(self.module))
        for (line, reason), indexes in sorted(self.missing_positions.items()):
            self.log(self.make_report_line(line, reason, indexes))
        if self.cannot_represent:
            self.log('--- cannot represent ---')
            for line, opcodes in self.cannot_represent.items():
                self.log('Last known source line:')
                self.log(self.source[line])
                self.log('Opcodes:')
                for opcode in opcodes:
                    self.log(' - {}'.format(opcode))
                self.log('------------------------')

class CommonReporter:
    def __init__(self, module_opcodes):
        self.reporters = [
            FileReporter(data) for data in module_opcodes.values()
        ]

    def report(self):
        for reporter in self.reporters:
            reporter.report()
