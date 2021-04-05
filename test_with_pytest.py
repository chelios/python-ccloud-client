import argparse
import pytest
import urllib.request

from fetch_installer import parse_args, fetch_script


def test_parser_with_valid_params():
    ''' Test that function returns correct commandline parameters '''

    args = parse_args([
        '-a',  'ccloud',
        '-u', 'http://example .com',
        '-i', '/tmp/stuff',
        '-d',
        ])

    assert isinstance(args, argparse.Namespace)
    assert args.alias == 'ccloud'
    assert args.url == 'http://example .com'
    assert args.install_dir == '/tmp/stuff'
    assert args.disable_prompts is True


def test_parser_with_invalid_params():
    ''' Test that function exits when passed incorrect parameters'''

    with pytest.raises(SystemExit):
        args = parse_args(['-g',  'ccloud', ])


def test_parser_invalid_params_output(capsys):
    ''' Test that function returns correct commandline parameters '''
    try:
        parse_args(['-g',  'ccloud', ])
    except SystemExit:
        pass
    captured = capsys.readouterr()
    assert captured.err == "usage: pytest [-h] [-d] [-i INSTALL_DIR] [-a ALIAS] [-u URL]\npytest: error: unrecognized arguments: -g ccloud\n"


def test_usage_message_output(capsys):
    ''' Test that usage message is displayed when "-h" flag passed'''
    try:
        parse_args(['-h'])
    except SystemExit:
        pass
    captured = capsys.readouterr()
    assert 'Installer script' in captured.out


def test_fetch_script(tmpdir):
    ''' Test that the second stage script can be retrieved and saved as a file
        locally'''
    script_url = 'https://raw.githubusercontent.com/chelios/python-ccloud-client/master/ccloud-client-install.py'
    script_name = 'ccloud-client-install.py'
    file = tmpdir.join(script_name)
    fetch_script(script_url, file.strpath)  # or use str(file)
    assert "check_docker_exists()" in file.read()


def test_fetch_script_url_error(capsys):
    ''' Test that the second stage script can be retrieved and saved as a file
        locally'''
    script_url = 'https://raw.githubusercontent.com/chelios/python-ccloud-client/master/ccloud-client-install.sh'
    script_name = 'ccloud-client-install.py'
    try:
        fetch_script(script_url, script_name)
    except SystemExit:
        pass
    captured = capsys.readouterr()
    assert 'HTTP Error 404: Not Found' in captured.out


def test_fetch_script_file_error(capsys):
    ''' Test that the second stage script can be retrieved and saved as a file
        locally'''
    script_url = 'https://raw.githubusercontent.com/chelios/python-ccloud-client/master/ccloud-client-install.py'
    script_name = '/foo/ccloud-client-install.py'
    try:
        fetch_script(script_url, script_name)
    except SystemExit:
        pass
    captured = capsys.readouterr()
    assert 'Error writing script file' in captured.out
