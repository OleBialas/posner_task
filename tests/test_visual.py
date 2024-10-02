from unittest import mock
from psychopy import visual
from posner.experiment import draw_fixation, draw_text


def test_draw_fixation(mock_window, mock_circle):
    draw_fixation(mock_window)


def test_draw_text(mock_window, mock_text):
    draw_text(mock_window, message="hello")
    mock_window.flip.assert_called_once()
