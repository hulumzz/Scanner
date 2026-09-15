import numpy as np
import pytest
from app.core.exceptions import ScannerError
from app.services.quality_checker import inspect_quality

def test_low_resolution_rejected():
    with pytest.raises(ScannerError) as exc: inspect_quality(np.full((300,500,3),180,dtype=np.uint8))
    assert exc.value.code=='LOW_RESOLUTION'
