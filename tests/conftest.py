import os
import json
import tempfile
import pytest


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
def write_config(create_config):
    with tempfile.TemporaryDirectory() as tmpdir:
        config_fname = os.path.join(tmpdir, "sample_config.json")
        json.dump(create_config, open(config_fname, "w"))
        yield create_config, config_fname
