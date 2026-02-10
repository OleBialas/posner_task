import csv
import pytest
from posner.experiment import make_subject_dir


def test_subject_dir_creation(create_temp_subject_dir):
    assert create_temp_subject_dir.exists()


def test_subject_dir_overwriting(tmp_path, config_dict):
    config_dict["root_dir"] = str(tmp_path)
    from posner.experiment import Config
    config = Config(**config_dict)
    subject_dir = make_subject_dir(config, "1")
    assert subject_dir is not None
    # Try to create the same subject dir again - should return None
    result = make_subject_dir(config, "1")
    assert result is None
