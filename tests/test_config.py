import pytest
from posner.experiment import load_config, Config
from pydantic import ValidationError


def test_load_config(write_config):
    config_fname = write_config
    load_config(config_fname)


def test_config_not_found():
    with pytest.raises(FileNotFoundError):
        load_config("")


def test_missing_key_is_detected(create_config):
    for key in create_config.keys():
        wrong_config = create_config.copy()
        del wrong_config[key]
        with pytest.raises(ValidationError):
            Config(**wrong_config)


def test_wrong_types_are_detected(create_config):
    for key, value in zip(
        ["fix_dur", "cue_dur", "n_blocks", "n_trials"], ["hi", -2, 0.5, 19]
    ):
        wrong_config = create_config.copy()
        wrong_config[key] = value
        with pytest.raises(ValidationError):
            Config(**wrong_config)


def test_probability_is_valid(create_config):
    for p in range(1, 20):
        create_config["p_valid"] = p / 10
        if create_config["p_valid"] <= 1:
            Config(**create_config)
        else:
            with pytest.raises(ValidationError):
                Config(**create_config)
