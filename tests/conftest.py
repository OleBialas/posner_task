import os
import json
from unittest import mock
import pytest
from psychopy import visual
from posner.experiment import create_subject_dir


@pytest.fixture
def create_config():
    return {
        "root_dir": "",
        "fix_dur": 0.1,
        "cue_dur": 0.2,
        "n_blocks": 1,
        "n_trials": 30,
        "p_valid": 0.5,
    }


@pytest.fixture
def write_config(create_config, tmpdir):
    config_fname = os.path.join(tmpdir, "sample_config.json")
    json.dump(create_config, open(config_fname, "w"))
    yield config_fname


@pytest.fixture
def create_temp_subject_dir(tmpdir):
    subject_dir = create_subject_dir(tmpdir, 1, False)
    return subject_dir


@pytest.fixture
def mock_window():
    with mock.patch.object(visual, "Window") as MockWin:
        MockWin.flip.return_value = None
        yield MockWin


@pytest.fixture
def mock_circle():
    with mock.patch.object(visual, "Circle") as MockCircle:
        yield MockCircle


@pytest.fixture
def mock_text():
    with mock.patch.object(visual, "TextStim") as MockText:
        yield MockText
