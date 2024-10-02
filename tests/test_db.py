import csv
import pytest
from posner.experiment import create_subject_dir, write_csv


def test_subject_dir_creation(create_temp_subject_dir):
    assert create_temp_subject_dir.exists()


def test_subject_dir_overwriting(create_temp_subject_dir):
    _ = create_subject_dir(create_temp_subject_dir, 1, True)
    with pytest.raises(FileExistsError):
        _ = create_subject_dir(create_temp_subject_dir, 1, False)


def test_write_csv(create_temp_subject_dir):
    side, valid, response, response_time = ["left"], [True], ["left"], [0.6]
    fname = write_csv(create_temp_subject_dir, 1, side, valid, response, response_time)
    with open(fname, newline="") as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=" ")
        for i, row in enumerate(csv_reader):
            if i == 0:
                assert row == ["side,valid,response,response_time"]
            elif i == 1:
                assert row == ["left,True,left,0.6"]
