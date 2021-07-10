# -*- coding: utf-8 -*-
import os
from pytest import approx, raises, fixture
import shutil

from py3dtiles import convert_to_ecef
from py3dtiles.convert import convert, SrsInMissingException


fixtures_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')


@fixture()
def tmp_dir():
    yield './tmp'
    shutil.rmtree('./tmp', ignore_errors=True)


def test_convert_to_ecef():
    # results tested with gdaltransform
    [x, y, z] = convert_to_ecef(-75.61200462622627,
                                40.03886513981721,
                                2848.448771114095,
                                4326)
    approx(x, 1215626.30684538)
    approx(y, -4738673.45914053)
    approx(z, 4083122.83975827)


def test_convert(tmp_dir):
    # just
    convert(os.path.join(os.path.dirname(os.path.abspath(__file__)), './ripple.las'), outfolder=tmp_dir)
    assert os.path.exists(os.path.join(tmp_dir, 'tileset.json'))
    assert os.path.exists(os.path.join(tmp_dir, 'r0.pnts'))


def test_convert_without_srs(tmp_dir):
    with raises(SrsInMissingException):
        convert(os.path.join(fixtures_dir, 'without_srs.las'),
                outfolder=tmp_dir,
                srs_out='4978')
    assert not os.path.exists(os.path.join(tmp_dir))

    convert(os.path.join(fixtures_dir, 'without_srs.las'),
            outfolder=tmp_dir,
            srs_in='3949',
            srs_out='4978')
    assert os.path.exists(os.path.join(tmp_dir, 'tileset.json'))
    assert os.path.exists(os.path.join(tmp_dir, 'r.pnts'))


def test_convert_with_srs(tmp_dir):
    convert(os.path.join(fixtures_dir, 'with_srs.las'),
            outfolder=tmp_dir,
            srs_out='4978')
    assert os.path.exists(os.path.join(tmp_dir, 'tileset.json'))
    assert os.path.exists(os.path.join(tmp_dir, 'r.pnts'))
