from enum import Enum


class Capability(str, Enum):
    EXECUTE_COMMAND = "execute_command"
    READ_FILES = "read_files"
    WRITE_FILES = "write_files"
    USE_CLOUD_LLM = "use_cloud_llm"