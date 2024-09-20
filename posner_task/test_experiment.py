from pathlib import Path
from unittest.mock import patch
import shutil
import random
import experiment

root = Path(__file__).parent.absolute()


def mock_waitKeys(keyList=None):
    return [random.choice(keyList)]


def test_run_experiment():
    experiment.p["fixation_dur"] = 0.1
    experiment.p["cue_dur"] = 0.1
    experiment.p["n_blocks"] = random.randint(1, 5)
    subject_id = random.randint(90, 99)
    with patch("experiment.event.waitKeys", side_effect=mock_waitKeys):
        experiment.run_experiment(subject_id)
    out_dir = root / "data" / f"sub-{str(subject_id).zfill(2)}"
    assert out_dir.exists()
    out_files = list(out_dir.glob("*"))
    assert len(out_files) == experiment.p["n_blocks"]
    shutil.rmtree(out_dir)
