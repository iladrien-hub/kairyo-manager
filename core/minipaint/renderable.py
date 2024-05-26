import abc
from typing import Optional

import numpy as np


class Renderable(abc.ABC):

    @abc.abstractmethod
    def getRGBA(self) -> Optional[np.ndarray]:
        raise NotImplementedError()
