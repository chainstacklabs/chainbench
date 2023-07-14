from inspect import stack
from random import Random


class RNG:
    def __init__(self, name: str, seed: int):
        self.seed = seed
        self.name = name
        self.random = Random(seed)


class RNGManager:
    def __init__(self, seed: int = 42):
        self._seed = seed
        self._rngs: dict[str, RNG] = {}

    def get_rng(self, name: str | None = None, seed: int | None = None):
        seed = seed if seed is not None else self._seed
        if name is not None:
            if name not in self._rngs.keys():
                self._rngs[name] = RNG(name, seed)
            return self._rngs[name]
        else:
            caller = stack()[1][3]
            if caller not in self._rngs.keys():
                self._rngs[caller] = RNG(caller, seed)
            return self._rngs[caller]


rng_manager = RNGManager()
get_rng = rng_manager.get_rng
