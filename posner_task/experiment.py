from pathlib import Path
import argparse
import json
from psychopy import visual, core, event
import numpy as np
from sequence import Block


root = Path(__file__).parent.absolute()
win = visual.Window(fullscr=True)
clock = core.Clock()
p = json.load(open(root / "parameters.json"))


def run_experiment(subject_id):
    subject = f"sub-{str(subject_id).zfill(2)}"
    subject_dir = root / "data" / subject
    if not subject_dir.exists():
        subject_dir.mkdir(parents=True)

    text = visual.TextStim(
        win,
        text="Welcome to the experiment! \n \n Look at the white fixation point in the middle of the screen. \n \n When a black dot appears, indicate if it is on the left or right using the arrow keys. \n \n Respond as fast as possible! \n \n Press space to continue",
    )
    text.draw()
    win.flip()
    event.waitKeys(keyList=["space"])

    for i_block in range(p["n_blocks"]):
        text = visual.TextStim(
            win, text=f"Press space to start block {i_block+1} of {p['n_blocks']}"
        )
        text.draw()
        win.flip()
        event.waitKeys(keyList=["space"])

        block_sequence = Block(p["n_trials"], p["p_valid"])
        run_block(block_sequence)
        block_sequence.save(subject_dir / f"{subject}_block{i_block+1}.csv")

    text = visual.TextStim(
        win,
        text=f"Thank you for participating in the experiment! \n \n Press space to exit.",
    )
    text.draw()
    win.flip()
    event.waitKeys(keyList=["space"])


def run_block(sequence):
    for position, valid in sequence:
        response, response_time = run_trial(position, valid)
        sequence.add_response(response, response_time)


def run_trial(position, valid):
    """
    Run a single trial of the Posner cueing task
    Arguments:
        position (str): Stimulus position, can be "left" or "right".
        valid (bool): Whether the cue is valid (i.e. points to the target).
    Returns:
        response (str): Subject's response, can be "left" or "right".
        response_times (float): Time passed between stimulus presentation and response.
    """
    draw_frames()
    draw_fixation()
    win.flip()

    core.wait(p["fixation_dur"])

    draw_frames()
    draw_fixation()
    if (position == "left" and valid) or (position == "right" and not valid):
        draw_frames(highlight="left")
    else:
        draw_frames(highlight="right")
    win.flip()

    core.wait(p["cue_dur"])

    draw_stimulus(position)
    win.flip()
    clock.reset()

    keys = event.waitKeys(keyList=["left", "right", "escape"])
    response = keys[0]
    response_time = clock.getTime()

    return response, response_time


def draw_frames(highlight=None):
    if highlight is not None and highlight not in ["left", "right"]:
        raise ValueError("highlight must be None, 'left' or 'right'!")
    for side, x_pos in zip(["left", "right"], [-0.5, 0.5]):
        if side == highlight:
            color = "red"
        else:
            color = "white"
        frame = visual.Rect(win, lineColor=color, pos=(x_pos, 0))
        frame.draw()


def draw_fixation():
    fixation = visual.Circle(  # size adjusts scaling for screen size
        win, radius=0.01, size=(1 * 1 / win.aspect, 1), fillColor="white"
    )
    fixation.draw()


def draw_stimulus(side):
    if side == "left":
        x_pos = -0.5
    elif side == "right":
        x_pos = 0.5
    else:
        raise ValueError("Side must be 'left' or 'right'!")
    stimulus = visual.Circle(
        win,
        pos=[x_pos, 0],
        radius=0.02,
        size=(1 * 1 / win.aspect, 1),
        fillColor="black",
        lineColor=None,
    )
    stimulus.draw()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("subject_id", type=int)
    args = parser.parse_args()
    run_experiment(args.subject_id)
    win.close()
