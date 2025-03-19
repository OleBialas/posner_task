import argparse
import json
import random
from pathlib import Path
from unittest.mock import patch
from typing import Literal, Tuple, List, Union, Optional
from pydantic import BaseModel, field_validator, model_validator
import pandas as pd
from psychopy import visual, core, event
import pygame

class Pos(BaseModel):
    left: Tuple[float, float]
    right: Tuple[float, float]

    @model_validator(mode="after")
    def sides_are_correct(values):
        assert values.left[0] < values.right[0]
        return values


class Config(BaseModel):
    root_dir: Path
    input_method: Literal["Keyboard", "Controller"]
    max_wait: Union[int, float]
    fix_dur: Union[int, float]
    cue_dur: Union[int, float]
    fix_radius: float
    fix_color: str
    stim_radius: float
    stim_color: str
    n_blocks: int
    n_trials: int
    p_valid: float
    pos: Pos

    @field_validator("input_method")
    @staticmethod
    def check_controler_works(value: str) -> Union[str, pygame.joystick.JoystickType]:
        if value == "Controller":
            pygame.init()
            pygame.joystick.init()
            joystick_count = pygame.joystick.get_count()
            if joystick_count == 0:
                raise ValueError("No joystick detected")
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
            return joystick
        else:
            return value

    @field_validator("root_dir")
    @staticmethod
    def root_dir_exists(value: Path) -> Path:
        assert value.exists()
        return value

    @field_validator("p_valid")
    @staticmethod
    def p_valid_is_percentage(value: float) -> float:
        assert 0 <= value <= 1
        return value

    @field_validator("fix_dur", "cue_dur")
    @staticmethod
    def durations_are_positive(value: Union[int, float]) -> float:
        assert 0 <= value <= 1
        return float(value)

    @model_validator(mode="after")
    def conditions_can_be_divided_into_n_trials(values):
        print("hi")
        assert (values.n_trials / 2) * values.p_valid % 1 == 0
        return values


def test_experiment(subject_id: str, config: str, overwrite: bool = False, screen: int = 0):

    def mock_waitKeys(keyList):
        return [random.choice(keyList)]

    with patch("posner.experiment.event.waitKeys", side_effect=mock_waitKeys):
        run_experiment(subject_id, config, overwrite, screen)


def run_experiment(subject_id: str, config_file: str, overwrite: bool = False, screen: int = 0):

    config = load_config(config_file)
    subject_dir = create_subject_dir(config.root_dir, subject_id, overwrite)
    win = visual.Window(fullscr=True, screen=screen)
    clock = core.Clock()

    draw_text(win, "hello", config)
    wait_for_response(config, clock)

    for i_block in range(config.n_blocks):
        draw_text(win, f"block {i_block+1} of {config.n_blocks}", config)
        (config, clock)
        df = run_block(win, clock, config)
        df.to_csv(subject_dir / f"block_{i_block+1}.csv", index=False)

    draw_text(win, "goodbye", config)
    wait_for_response(config, clock)

    win.close()


def run_block(
    win: visual.Window,
    clock: core.Clock,
    config: Config,
) -> pd.DataFrame:

    side, valid = make_sequence(config.n_trials, config.p_valid)
    df = pd.DataFrame()
    for s, v in zip(side, valid):
        r, rt = run_trial(win, clock, s, v, config)
        row = pd.DataFrame(
            [{"side": s, "valid": v, "response": r, "response_time": rt}]
        )
        df = pd.concat([df, row])
    return df


def run_trial(
    win: visual.Window,
    clock: core.Clock,
    side: Literal["left", "right"],
    valid: bool,
    config: Config,
) -> Tuple[bool, float]:

    draw_frames(win, config)
    draw_fixation(win, config)
    win.flip()

    core.wait(config.fix_dur)

    draw_frames(win, config)
    draw_fixation(win, config)
    if (side == "left" and valid) or (side == "right" and not valid):
        draw_frames(win, config, highlight="left")
    else:
        draw_frames(win, config, highlight="right")
    win.flip()

    core.wait(config.cue_dur)

    draw_frames(win, config)
    draw_stimulus(win, config, side)
    win.flip()

    response, response_time = wait_for_response(config, clock, keys=["left", "right"])
    if response == side:
        response = True
    else:
        response = False
    return response, response_time

def make_sequence(
    n_trials: int, p_valid: float
) -> Tuple[List[Literal["left", "right"]], List[bool]]:
    side, valid = [], []
    for s in ["left", "right"]:
        n = int(n_trials / 2)
        side += [s] * n
        n_valid = int(n * p_valid)
        valid += [True] * n_valid + [False] * (n - n_valid)
    idx = list(range(n_trials))
    random.shuffle(idx)

    return [side[i] for i in idx], [valid[i] for i in idx]

def wait_for_response(
        config:Config, clock:core.Clock, keys:Union[None, List[str]] = None
) -> Tuple[Union[str,None], float]:
    clock.reset()
    response = None
    if config.input_method == "Keyboard":
        keys = event.waitKeys(keyList=["left", "right"], maxWait=config.max_wait)
        response = keys[0]
    elif isinstance(config.input_method, pygame.joystick.JoystickType):
        response = None
        while response is None and clock.getTime().real < config.max_wait:
            pygame.event.pump()
            button_states = [
                config.input_method.get_button(i) for i in range(config.input_method.get_numbuttons())
            ]
            if button_states[0]: # A button on 8BitDo
                response = "right"
            if button_states[4]:
                response = "left" # Y button on 8BitDo
    else:
        raise ValueError("No valid input method found!")
    response_time = clock.getTime()
    return response, response_time

def draw_frames(
    win: visual.Window,
    config: Config,
    highlight: Optional[Literal["left", "right"]] = None,
) -> None:
    for side, pos in zip(["left", "right"], [config.pos.left, config.pos.right]):
        if side == highlight:
            color = config.stim_color
        else:
            color = "white"
        frame = visual.Rect(win, lineColor=color, pos=pos)
        frame.draw()


def draw_fixation(win: visual.Window, config: Config) -> None:
    fixation = visual.Circle(
        win, radius=config.fix_radius, size=(1 / win.aspect, 1), fillColor=config.fix_color
    )
    fixation.draw()


def draw_stimulus(
    win: visual.Window, config: Config, side: Literal["left", "right"]
) -> None:
    if side == "left":
        pos = config.pos.left
    elif side == "right":
        pos = config.pos.right
    stimulus = visual.Circle(
        win,
        pos=pos,
        radius=config.stim_radius,
        size=(1 / win.aspect, 1),
        fillColor=config.stim_color,
        lineColor=None,
    )
    stimulus.draw()


def draw_text(win: visual.Window, message: str, config:Config) -> None:
    if message == "hello":
        text = f"Welcome to the experiment! \n \n Look at the white fixation point in the middle of the screen. \n \n When a {config.stim_color} dot appears, indicate if it is on the left or right using the arrow keys. \n \n Respond as fast as possible! \n \n Press space to continue"
    elif message == "goodbye":
        text = "Thank you for participating! \n \n Press space to exit."
    else:
        text = f"Press space to start {message}"
    text_stim = visual.TextStim(win, text=text)
    text_stim.draw()
    win.flip()
    core.wait(1)


def create_subject_dir(root: Path, subject_id: str, overwrite: bool) -> Path:
    subject_dir = Path(root) / "data" / subject_id
    if subject_dir.exists():
        if overwrite is True:
            pass
        else:
            raise FileExistsError(
                f"Folder for {subject_id} already exists! \n Change the subject ID or use the --overwrite flag!"
            )
    else:
        subject_dir.mkdir(parents=True)
    return subject_dir


def load_config(config_file: str) -> Config:
    if not Path(config_file).exists():
        raise FileNotFoundError(f"Couldn't find config file at {config_file}")
    config_dict = json.load(open(config_file))
    return Config(**config_dict)


def main_cli():
    parser = argparse.ArgumentParser(description="A Python implementation of the Posner attention cueing task built on PsychoPy")
    parser.add_argument("subject_id", type=str, help="Subject ID used to name files and folders")
    parser.add_argument("config", type=str, help="Path to the JSON file with the experiments configuration")
    parser.add_argument("--screen", type=int, default=0, help="Number of the screen where window is displayed (defaults to 0)")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing data for this subject")
    parser.add_argument("--test", action="store_true", help="Run an automated test of the experiment")
    args = parser.parse_args()
    if args.test is False:
        run_experiment(args.subject_id, args.config, args.overwrite, args.screen)
    else:
        test_experiment(args.subject_id, args.config, args.overwrite, args.screen)


if __name__ == "__main__":
    main_cli()
