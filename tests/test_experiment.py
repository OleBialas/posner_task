import time
from posner.experiment import run_trial, run_block, Config
from psychopy import core

WAITKEY_CALL_PER_TRIAL = 1
CIRCLE_CALL_PER_TRIAL = 3
RECT_CALL_PER_TRIAL = 6


def test_run_trial(mock_window, mock_circle, mock_rect, mock_waitKeys):
    fix_dur, cue_dur = 0, 0
    tic = time.time()
    clock = core.Clock()
    run_trial(
        mock_window, clock, side="left", valid=True, fix_dur=fix_dur, cue_dur=cue_dur
    )
    elapsed = time.time() - tic
    assert abs(elapsed - (fix_dur + cue_dur)) < 0.005
    assert mock_waitKeys.call_count == WAITKEY_CALL_PER_TRIAL
    assert mock_circle.call_count == CIRCLE_CALL_PER_TRIAL
    assert mock_rect.call_count == RECT_CALL_PER_TRIAL


def test_run_block(create_config, mock_window, mock_circle, mock_rect, mock_waitKeys):
    config = Config(**create_config)
    config.fix_dur, config.cue_dur = 0.01, 0.01
    clock = core.Clock()
    df = run_block(mock_window, clock, config)
    assert df.shape[0] == config.n_trials
    assert df["side"].isin(["left", "right"]).all()
