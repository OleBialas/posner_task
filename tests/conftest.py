import os
import json
from unittest import mock
import random
import pytest
from psychopy import visual
from posner.experiment import make_subject_dir, Config


@pytest.fixture
def config_dict():
    return {
        "root_dir": "",
        "input_method": "Keyboard",
        "max_wait": 2.0,
        "fix_dur": 0.5,
        "cue_dur": 0.5,
        "fix_radius": 0.025,
        "fix_color": "white",
        "stim_radius": 0.05,
        "stim_color": "red",
        "n_blocks": 2,
        "n_trials": 10,
        "p_valid": 0.8,
        "pos": {"left": (-0.5, 0), "right": (0.5, 0)},
    }


@pytest.fixture
def create_config(config_dict):
    return Config(**config_dict)


@pytest.fixture
def write_config(config_dict, tmp_path):
    config_dict["root_dir"] = str(tmp_path)
    config_fname = os.path.join(tmp_path, "sample_config.json")
    json.dump(config_dict, open(config_fname, "w"))
    yield config_fname


@pytest.fixture
def create_temp_subject_dir(tmp_path, config_dict):
    config_dict["root_dir"] = str(tmp_path)
    config = Config(**config_dict)
    subject_dir = make_subject_dir(config, "1")
    return subject_dir


@pytest.fixture
def mock_window():
    with mock.patch.object(visual, "Window") as MockWin:
        MockWin.flip.return_value = None
        MockWin.aspect = 2
        yield MockWin


@pytest.fixture
def mock_circle():
    with mock.patch.object(visual, "Circle") as MockCircle:
        yield MockCircle


@pytest.fixture
def mock_rect():
    with mock.patch.object(visual, "Rect") as MockRect:
        yield MockRect


@pytest.fixture
def mock_text():
    with mock.patch.object(visual, "TextStim") as MockText:
        yield MockText


@pytest.fixture
def mock_waitKeys():
    with mock.patch("posner.experiment.event.waitKeys") as mock_waitKeys:
        mock_waitKeys.side_effect = lambda keyList: [random.choice(keyList)]
        yield mock_waitKeys
