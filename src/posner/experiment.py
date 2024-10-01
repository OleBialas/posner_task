import argparse
import json
import numbers
import random
import csv
import shutil
from pathlib import Path
from unittest.mock import patch
from typing import Literal, Tuple, List
from psychopy import visual, core, event


def test_experiment(subject_id: int, config: str, overwrite: bool = False):

    def mock_waitKeys(keyList):
        return [random.choice(keyList)]

    with patch("posner.experiment.event.waitKeys", side_effect=mock_waitKeys):
        run_experiment(subject_id, config, overwrite)

    # clean up
    root = json.load(open(config))["root"]
    sub_dir = Path(root) / "data" / f"sub-{str(subject_id).zfill(2)}"
    shutil.rmtree(sub_dir)


def run_experiment(subject_id: int, config: str, overwrite: bool = False):

    root, fix_dur, cue_dur, n_blocks, n_trials, p_valid = load_config(config)
    subject_dir = create_subject_dir(root, subject_id, overwrite)
    win = visual.Window(fullscr=True)
    clock = core.Clock()

    draw_text(win, "hello")
    event.waitKeys(keyList=["space"])

    for i_block in range(n_blocks):
        draw_text(win, f"block {i_block+1} of {n_blocks}")
        event.waitKeys(keyList=["space"])
        side, valid, response, response_time = run_block(
            win, clock, n_trials, p_valid, fix_dur, cue_dur
        )
        write_csv(subject_dir, i_block, side, valid, response, response_time)

    draw_text(win, "goodbye")
    event.waitKeys(keyList=["space"])

    win.close()


def run_block(
    win: visual.Window,
    clock: core.Clock,
    n_trials: int,
    p_valid: float,
    fix_dur: float,
    cue_dur: float,
) -> Tuple[
    List[Literal["left", "right"]],
    List[bool],
    List[Literal["left", "right"]],
    List[float],
]:

    side, valid = make_sequence(n_trials, p_valid)
    response, response_time = [], []
    for s, v in zip(side, valid):
        r, rt = run_trial(win, clock, s, v, fix_dur, cue_dur)
        response.append(r)
        response_time.append(rt)
    return side, valid, response, response_time


def run_trial(
    win: visual.Window,
    clock: core.Clock,
    side: Literal["left", "right"],
    valid: bool,
    fix_dur: float,
    cue_dur: float,
) -> Tuple[bool, float]:

    draw_frames(win, highlight=None)
    draw_fixation(win)
    win.flip()

    core.wait(fix_dur)

    draw_frames(win, highlight=None)
    draw_fixation(win)
    if (side == "left" and valid) or (side == "right" and not valid):
        draw_frames(win, highlight="left")
    else:
        draw_frames(win, highlight="right")
    win.flip()

    core.wait(cue_dur)

    draw_stimulus(win, side)
    win.flip()
    clock.reset()

    keys = event.waitKeys(keyList=["left", "right"])
    response_time = clock.getTime()
    response = keys[0]

    return response, response_time


def make_sequence(
    n_trials: int, p_valid: float
) -> Tuple[List[Literal["left", "right"]], List[bool]]:
    side, valid = [], []
    if n_trials / 2 * p_valid % 1 != 0:
        raise ValueError("Trials can't be evenly divided between conditions!")

    for s in ["left", "right"]:
        n = int(n_trials / 2)
        side += [s] * n
        n_valid = int(n * p_valid)
        valid += [True] * n_valid + [False] * (n - n_valid)
    idx = list(range(n_trials))
    random.shuffle(idx)

    return [side[i] for i in idx], [valid[i] for i in idx]


def draw_frames(win: visual.Window, highlight: Literal["left", "right", None]) -> None:
    for side, x_pos in zip(["left", "right"], [-0.5, 0.5]):
        if side == highlight:
            color = "red"
        else:
            color = "white"
        frame = visual.Rect(win, lineColor=color, pos=(x_pos, 0))
        frame.draw()


def draw_fixation(win: visual.Window) -> None:
    fixation = visual.Circle(
        win, radius=0.01, size=(1 * 1 / win.aspect, 1), fillColor="white"
    )
    fixation.draw()


def draw_stimulus(win: visual.Window, side: Literal["left", "right"]) -> None:
    if side == "left":
        x_pos = -0.5
    elif side == "right":
        x_pos = 0.5
    stimulus = visual.Circle(
        win,
        pos=[x_pos, 0],
        radius=0.02,
        size=(1 * 1 / win.aspect, 1),
        fillColor="black",
        lineColor=None,
    )
    stimulus.draw()


def draw_text(win: visual.Window, message: str) -> None:
    if message == "hello":
        text = "Welcome to the experiment! \n \n Look at the white fixation point in the middle of the screen. \n \n When a black dot appears, indicate if it is on the left or right using the arrow keys. \n \n Respond as fast as possible! \n \n Press space to continue"
    elif message == "goodbye":
        text = "Thank you for participating! \n \n Press space to exit."
    else:
        text = f"Press space to start {message}"
    text_stim = visual.TextStim(win, text=text)
    text_stim.draw()
    win.flip()


def create_subject_dir(root: Path, subject_id: int, overwrite: bool) -> Path:
    subject = f"sub-{str(subject_id).zfill(2)}"
    subject_dir = Path(root) / "data" / subject
    if subject_dir.exists():
        if overwrite is True:
            pass
        else:
            raise FileExistsError(
                f"Folder for subject {subject} already exists! \n Change the subject ID or use the --overwrite flag!"
            )
    else:
        subject_dir.mkdir(parents=True)
    return subject_dir


def load_config(config_file: str) -> Tuple[Path, float, float, int, int, float]:
    config_dict = _read_config(config_file)
    return _check_config_dict(config_dict)


def _read_config(config_file: str) -> dict:
    if not Path(config_file).exists():
        raise FileNotFoundError(f"Couldn't find config file at {config_file}")
    config_dict = json.load(open(config_file))
    return config_dict


def _check_config_dict(config_dict: dict) -> Tuple[Path, float, float, int, int, float]:

    for key in ["root", "fix_dur", "cue_dur", "n_blocks", "n_trials", "p_valid"]:
        if not key in config_dict.keys():
            raise KeyError(f"Config file does not contain {key}!")

    root = Path(config_dict["root"])
    if not root.exists():
        raise FileNotFoundError(
            f"Couldn't find root directory {root}. Create it or edit the configuration!"
        )

    if not (
        all(
            [
                isinstance(config_dict[key], numbers.Number)
                for key in ["fix_dur", "cue_dur"]
            ]
        )
        and all([config_dict[key] > 0 for key in ["fix_dur", "cue_dur"]])
    ):
        raise TypeError("fix_dur and cue_dur must be positive scalar values!")

    fix_dur, cue_dur = float(config_dict["fix_dur"]), float(config_dict["cue_dur"])

    if not all([isinstance(config_dict[key], int) for key in ["n_blocks", "n_trials"]]):
        raise TypeError("n_blocks and n_trials must be integers!")
    n_blocks, n_trials = config_dict["n_blocks"], config_dict["n_trials"]

    if not isinstance(config_dict["p_valid"], float):
        raise TypeError("p_valid must be a float!")

    if not 1 >= config_dict["p_valid"] > 0:
        raise ValueError("p_calid must be a value between 0 and 1!")
    p_valid = config_dict["p_valid"]

    try:
        make_sequence(n_trials, p_valid)
    except ValueError:
        raise ValueError(
            f"Can't generate sequence with n_trials={n_trials} and p_valid={p_valid}"
        )

    return (root, fix_dur, cue_dur, n_blocks, n_trials, p_valid)


def write_csv(
    subject_dir: Path,
    i_block: int,
    side: List[Literal["left", "right"]],
    valid: List[bool],
    response: List[Literal["left", "right"]],
    response_time: List[float],
) -> None:

    file_path = subject_dir / f"{subject_dir.name}_block{i_block+1}.csv"
    rows = zip(side, valid, response, response_time)
    with open(file_path, "w", newline="") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["side", "valid", "response", "response_time"])
        csvwriter.writerows(rows)


def main_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("subject_id", type=int)
    parser.add_argument("config", type=str)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--test", action="store_true")
    args = parser.parse_args()
    if args.test is False:
        run_experiment(args.subject_id, args.config, args.overwrite)
    else:
        test_experiment(args.subject_id, args.config, args.overwrite)


if __name__ == "__main__":
    main_cli()
