

class StageNameConflictException(Exception):
    pass


class MultipleSuppliersException(Exception):
    pass


class CyclicStagesException(Exception):
    pass


class UnsatisfiableStageException(Exception):
    pass


class PralinefileValidationException(Exception):
    pass


class CompilerInstantionException(Exception):
    pass


class NoSupportedCompilerFoundException(Exception):
    pass


class DirectUserMessageException(Exception):
    pass


class IllformedProjectException(DirectUserMessageException):
    pass


class ClangFormatConfigurationException(DirectUserMessageException):
    pass


class ServiceConfigurationException(DirectUserMessageException):
    pass


class PullDependenciesNoConnectionException(DirectUserMessageException):
    pass


class ProcessExecutionException(Exception):
    def __init__(self, status: int, stdout: bytes, stderror: bytes):
        self.status = status
        self.stdout = stdout
        self.stderror = stderror
        self.output = stdout + stderror

    def __str__(self):
        if self.status != 0 and len(self.output) > 0:
            return f"Command exited with return code {self.status} and output:\n{self.output.decode()}"
        elif self.status == 0 and len(self.stderror) > 0:
            return f"Command exited with output:\n{self.output.decode()}"
        elif self.status != 0 and len(self.output) == 0:
            return f"Command exited with return code {self.status}"
        else:
            return "Command execution error"


class MainProcessExecutionException(ProcessExecutionException, DirectUserMessageException):
    def __init__(self, status: int, stdout: bytes, stderror: bytes):
        super().__init__(status, stdout, stderror)


class TestProcessExecutionException(ProcessExecutionException, DirectUserMessageException):
    def __init__(self, status: int, stdout: bytes, stderror: bytes):
        super().__init__(status, stdout, stderror)

class PreprocessingException(ProcessExecutionException, DirectUserMessageException):
    def __init__(self, status: int, stderror: bytes):
        super().__init__(status, stdout=b'', stderror=stderror)


class CompilationException(ProcessExecutionException, DirectUserMessageException):
    def __init__(self, status: int, stdout: bytes, stderror: bytes):
        super().__init__(status, stdout, stderror)


class LinkingException(ProcessExecutionException, DirectUserMessageException):
    def __init__(self, status: int, stdout: bytes, stderror: bytes):
        super().__init__(status, stdout, stderror)
