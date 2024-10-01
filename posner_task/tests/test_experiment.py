import os
import json
from pathlib import Path
import tempfile
from unittest.mock import patch
import random
import experiment


def mock_waitKeys(keyList):
    return [random.choice(keyList)]


def test_run_experiment():
    with tempfile.TemporaryDirectory() as tmpdir:
        config = {
            "root": tmpdir,
            "fix_dur": 0.01,
            "cue_dur": 0.01,
            "n_blocks": 1,
            "n_trials": 20,
            "p_valid": 0.5,
        }
        config_file = os.path.join(tmpdir, "sample_config.json")
        json.dump(config, open(config_file, "w"))

        subject_id = random.randint(90, 99)
        with patch("experiment.event.waitKeys", side_effect=mock_waitKeys):
            experiment.run_experiment(subject_id, config_file)

        sub_dir = Path(config["root"] / "data" / f"sub-{str(subject_id).zfill(2)}")
        assert sub_dir.exists()
        out_files = list(sub_dir.glob("*"))
        assert len(out_files) == config["n_blocks"]
