from typing import Any, Dict, Optional


class RangeDict(dict):
    def __init__(self, d: Optional[Dict] = None):
        if d is None:
            return

        for k, v in d.items():
            self[k] = v

    def __getitem__(self, key: Any) -> Any:
        if key is None:
            raise KeyError

        for k, v in self.items():
            if k[0] <= key <= k[1]:
                return v
        raise KeyError(
            "Key '%s' is not between any values in the RangeDict" % key
        )

    def __setitem__(self, key: Any, value: Any) -> None:
        try:
            if len(key) == 2:
                if key[0] <= key[1]:
                    dict.__setitem__(self, (key[0], key[1]), value)
                else:
                    raise RuntimeError(
                        "First element of a RangeDict key "
                        "must be less than or equal to the "
                        "second element"
                    )
            else:
                raise ValueError(
                    "Key of a RangeDict must be an iterable " "with length two"
                )
        except TypeError:
            raise TypeError(
                "Key of a RangeDict must be an iterable " "with length two"
            )

    def __contains__(self, key: Any) -> bool:
        try:
            return bool(self[key]) or True
        except KeyError:
            return False
