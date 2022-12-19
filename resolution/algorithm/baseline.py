
from dataclasses import dataclass

@dataclass
class Baseline:
    name: str
    full: bool = True

    def fit(self, data):
        raise NotImplementedError

    def infer(self, data):
        raise NotImplementedError
