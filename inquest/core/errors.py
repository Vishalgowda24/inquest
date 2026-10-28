"""Actionable errors for configuration, contracts, stages, and artifacts."""


class InquestError(Exception):
    def __init__(self, message: str, stage: str | None = None, input_path: str | None = None) -> None:
        super().__init__(message)
        self.stage = stage
        self.input_path = input_path


class IngestError(InquestError):
    pass


class ContractError(InquestError):
    pass


class StageError(InquestError):
    pass


class ArtifactError(InquestError):
    pass


class ConfigurationError(InquestError):
    pass


class VerificationError(InquestError):
    pass
