import pytest

from app.services.dusun_service import canonical_dusun


@pytest.mark.parametrize(('alamat', 'expected'), [
    ('DK BOJONGIRENG RT 001 RW 002', 'BOJONGIRENG'),
    ('Dusun Panumbangan, Desa Contoh', 'PANUMBANGAN'),
    ('SIMENDEM', 'SIMENDEM'),
    ('DK.SASAK', 'SASAK'),
    ('dusun mandelun', 'MANDELUN'),
    ('Jalan tanpa nama dusun', None),
    ('BOJONGIRENG PANUMBANGAN', None),
    (None, None),
])
def test_canonical_dusun_is_derived_only_from_supported_address_names(alamat, expected):
    assert canonical_dusun(alamat) == expected
