import argparse
import json
import numbers
from pathlib import Path
from typing import Literal, Tuple, Optional
from psychopy import visual, core, event
from sequence import Block


def run_experiment(subject_id: int, config: str):

    root, fixation_dur, cue_dur, n_blocks, n_trials, p_valid = read_config(config)
    subject_dir = create_subject_dir(root, subject_id)
    win = visual.Window(fullscr=True)
    clock = core.Clock()

    draw_text(win, "hello")
    event.waitKeys(keyList=["space"])

    for i_block in range(n_blocks):
        draw_text(win, f"block {i_block+1} of {n_blocks}")
        event.waitKeys(keyList=["space"])
        run_block(win, clock, n_trials, p_valid, fixation_dur, cue_dur)
        # block_sequence.save(subject_dir / f"{subject_dir.name}_block{i_block+1}.csv")

    draw_text(win, "goodbye")
    event.waitKeys(keyList=["space"])

    win.close()


def run_block(win, clock, n_trials, p_valid, fixation_dur, cue_dur):

    sequence = Block(n_trials, p_valid)
    for position, valid in sequence:
        response, response_time = run_trial(
            win, clock, position, valid, fixation_dur, cue_dur
        )
        sequence.add_response(response, response_time)


def run_trial(
    win: visual.Window,
    clock: core.Clock,
    position: Literal["left", "right"],
    valid: bool,
    fixation_dur: float,
    cue_dur: float,
) -> Tuple[bool, float]:

    draw_frames(win, highlight=None)
    draw_fixation(win)
    win.flip()

    core.wait(fixation_dur)

    draw_frames(win, highlight=None)
    draw_fixation(win)
    if (position == "left" and valid) or (position == "right" and not valid):
        draw_frames(win, highlight="left")
    else:
        draw_frames(win, highlight="right")
    win.flip()

    core.wait(cue_dur)

    draw_stimulus(win, position)
    win.flip()
    clock.reset()

    keys = event.waitKeys(keyList=["left", "right"])
    response_time = clock.getTime()
    response = keys[0]

    return response, response_time


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
        text = (
            f"Thank you for participating in the experiment! \n \n Press space to exit.",
        )
    else:
        text = f"Press space to start {message}"
    text_stim = visual.TextStim(win, text=text)
    text_stim.draw()
    win.flip()


def create_subject_dir(root: Path, subject_id: int) -> Path:
    subject = f"sub-{str(subject_id).zfill(2)}"
    if not root.exists():
        raise FileNotFoundError(
            f"Directorty {root} not found! Create directory or edit configuration!"
        )
    else:
        subject_dir = Path(root) / "data" / subject
        if not subject_dir.exists():
            subject_dir.mkdir(parents=True)
    return subject_dir


def read_config(config: str) -> Tuple[Path, float, float, int, int, float]:
    if not Path(config).exists():
        raise FileNotFoundError(f"Couldn't find config file at {config}")
    cfg = json.load(open(config))
    root = Path(cfg["root"])
    if not root.exists():
        raise FileNotFoundError(
            f"Couldn't find root directory {root}. Create it or edit the configuration!"
        )
    assert all(
        [isinstance(cfg[key], numbers.Number) for key in ["fixation_dur", "cue_dur"]]
    ), "fixation_dur and cue_dur must be scalar values!"
    fixation_dur, cue_dur = float(cfg["fixation_dur"]), float(cfg["cue_dur"])

    assert all(
        [isinstance(cfg[key], int) for key in ["n_blocks", "n_trials"]]
    ), "n_blocks and n_trials must be integers!"
    n_blocks, n_trials = cfg["n_blocks"], cfg["n_trials"]

    p_valid = cfg["p_valid"]
    assert 1 > p_valid > 0, "p_calid must be a value between 0 and 1!"
    return (root, fixation_dur, cue_dur, n_blocks, n_trials, p_valid)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("subject_id", type=int)
    parser.add_argument("config", type=str)
    args = parser.parse_args()
    run_experiment(args.subject_id, args.config)
