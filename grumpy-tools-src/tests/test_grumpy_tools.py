#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `grumpy_tools` package."""

import tempfile
import unittest

import pytest

from click.testing import CliRunner

from grumpy_tools import cli


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string


@pytest.mark.xfail
def test_command_line_interface(capfd):
    """Test the CLI."""
    runner = CliRunner()
    out, err = capfd.readouterr()

    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0

    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert '>>> ' in out, (result.output, out, err)


def test_run_input_inline(capfd):
    runner = CliRunner()
    result = runner.invoke(cli.main, ['run', '-c', "print('Hello World')",])
    out, err = capfd.readouterr()
    assert out == 'Hello World\n', (err, result.output)
    assert result.exit_code == 0


def test_run_input_stdin(capfd):
    runner = CliRunner()
    result = runner.invoke(cli.main, ['run'], input="print('Hello World')")

    out, err = capfd.readouterr()
    assert out == 'Hello World\n', (err, result.output)
    assert result.exit_code == 0


def test_run_input_file(capfd):
    runner = CliRunner()
    with tempfile.NamedTemporaryFile() as script_file:
        script_file.write("print('Hello World')")
        script_file.flush()

        result = runner.invoke(cli.main, ['run', script_file.name])

    out, err = capfd.readouterr()
    assert out == 'Hello World\n', (err, result.output)
    assert result.exit_code == 0
