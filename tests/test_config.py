import pytest
from posner import experiment


def test_read_config(write_config):
    config_dict1, config_fname = write_config
    config_dict2 = experiment._read_config(config_fname)
    assert config_dict1 == config_dict2


def test_config_not_found():
    with pytest.raises(FileNotFoundError):
        experiment._read_config("")


def test_config_is_valid(create_config):
    experiment._check_config_dict(create_config)


def test_config_is_missing_key(create_config):
    for key in create_config.keys():
        deficient_config_dict = create_config.copy()
        del deficient_config_dict[key]
        with pytest.raises(KeyError):
            experiment._check_config_dict(deficient_config_dict)


def test_config_values_are_correct_type(create_config):
    for key, value in zip(
        ["fix_dur", "cue_dur", "n_blocks", "n_trials"], ["hi", -2, 0.5, 20.0]
    ):
        wrong_config = create_config.copy()
        wrong_config[key] = value
        with pytest.raises(TypeError):
            experiment._check_config_dict(wrong_config)


def test_config_values_are_valid(create_config):
    for key, value in zip(["n_trials", "p_valid"], [9, 1.1]):
        wrong_config = create_config.copy()
        wrong_config[key] = value
        with pytest.raises(ValueError):
            experiment._check_config_dict(wrong_config)
