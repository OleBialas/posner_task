import tempfile
import os
import json
import pytest
import experiment


def create_sample_config(tmpdir):
    config = {
        "root": tmpdir,
        "fix_dur": 0.1,
        "cue_dur": 0.2,
        "n_blocks": 1,
        "n_trials": 20,
        "p_valid": 0.5,
    }
    fname = os.path.join(tmpdir, "sample_config.json")
    json.dump(config, open(fname, "w"))
    return config, fname


def test_config_exists():
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dict1, fname = create_sample_config(tmpdir)
        config_dict2 = experiment._read_config(fname)
        assert config_dict1 == config_dict2
    with pytest.raises(FileNotFoundError):
        experiment._read_config(fname)


def test_config_has_all_keys():
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dict, _ = create_sample_config(tmpdir)
        experiment._check_config_dict(config_dict)
        for key in config_dict.keys():
            deficient_config_dict = config_dict.copy()
            del deficient_config_dict[key]
            with pytest.raises(KeyError):
                experiment._check_config_dict(deficient_config_dict)


def test_config_types():
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dict, _ = create_sample_config(tmpdir)
        for key, value in zip(
            ["fix_dur", "cue_dur", "n_blocks", "n_trials"], ["hi", -2, 0.5, 20.0]
        ):
            wrong_dict = config_dict.copy()
            wrong_dict[key] = value
            with pytest.raises(TypeError):
                experiment._check_config_dict(wrong_dict)


def test_config_valid():
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dict, _ = create_sample_config(tmpdir)
        for key, value in zip(["n_trials", "p_valid"], [9, 1.1]):
            wrong_dict = config_dict.copy()
            wrong_dict[key] = value
            with pytest.raises(ValueError):
                experiment._check_config_dict(wrong_dict)
