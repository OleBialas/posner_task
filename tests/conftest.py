import os
import json
import pytest
from posner.experiment import create_subject_dir


@pytest.fixture
def create_config():
    return {
        "root": "",
        "fix_dur": 0.1,
        "cue_dur": 0.2,
        "n_blocks": 1,
        "n_trials": 20,
        "p_valid": 0.5,
    }


@pytest.fixture
def write_config(create_config, tmpdir):
    config_fname = os.path.join(tmpdir, "sample_config.json")
    json.dump(create_config, open(config_fname, "w"))
    yield create_config, config_fname


@pytest.fixture
def create_temp_subject_dir(tmpdir):
    subject_dir = create_subject_dir(tmpdir, 1, False)
    return subject_dir
