import pytest
from posner.experiment import load_config, Config


def test_load_config(write_config):
    config_dict1, config_fname = write_config
    config_dict2 = load_config(config_fname)
    assert config_dict1 == config_dict2


def test_config_not_found():
    with pytest.raises(FileNotFoundError):
        load_config("")


def test_missing_key_is_detected(create_config):
    for key in create_config.keys():
        wrong_config = create_config.copy()
        del wrong_config[key]
        Config(**wrong_config)


def test_wrong_types_are_detected(create_config):
    for key, value in zip(
        ["fix_dur", "cue_dur", "n_blocks", "n_trials"], ["hi", -2, 0.5, 20.0]
    ):
        wrong_config = create_config.copy()
        wrong_config[key] = value
        Config(**wrong_config)


def test_probability_validation(create_config):

    for key, value in zip(["n_trials", "p_valid"], [9, 1.1]):
        wrong_config = create_config.copy()
        wrong_config[key] = value
        Config(**wrong_config)
