import time

import boto3
import pytest
from moto import mock_aws

from utec_logger import Level, Logger
from utec_logger import logger as logger_module


@pytest.fixture
def new_logger(tmp_path, monkeypatch):
    """Crea un Logger nuevo (es singleton) que escribe en un directorio temporal."""
    monkeypatch.chdir(tmp_path)
    Logger._instance_ = None

    def factory():
        return Logger()

    yield factory

    Logger._instance_ = None


@pytest.fixture
def no_cloud_watch(monkeypatch):
    for name in ('CLOUD_WATCH_GROUP', 'CLOUD_WATCH_STREAM'):
        monkeypatch.delenv(name, raising=False)


@pytest.fixture
def cloud_watch_env(monkeypatch):
    monkeypatch.setenv('AWS_ACCESS_KEY_ID', 'testing')
    monkeypatch.setenv('AWS_SECRET_ACCESS_KEY', 'testing')
    monkeypatch.setenv('AWS_REGION', 'us-east-1')
    monkeypatch.setenv('CLOUD_WATCH_GROUP', 'test-group')
    monkeypatch.setenv('CLOUD_WATCH_STREAM', 'test-stream')


def test_singleton(new_logger, no_cloud_watch):
    assert new_logger() is new_logger()


def test_writes_formatted_line_to_file(new_logger, no_cloud_watch, tmp_path):
    log = new_logger()
    log.warning('mensaje de prueba')

    files = list((tmp_path / 'logs').glob('log-test_logger-*.log'))
    assert len(files) == 1

    line = files[0].read_text(encoding='utf-8').strip()
    parts = line.split(' | ')
    assert parts[1] == 'WARNING'
    assert parts[2].startswith('test_logger.py:')
    assert parts[3] == 'mensaje de prueba'


def test_all_levels(new_logger, no_cloud_watch, tmp_path):
    log = new_logger()
    log.info('a')
    log.warning('b')
    log.error('c')
    log.critical('d')
    log.log('e', level=Level.ERROR)

    content = next((tmp_path / 'logs').glob('*.log')).read_text(encoding='utf-8')
    levels = [line.split(' | ')[1] for line in content.strip().splitlines()]
    assert levels == ['INFO', 'WARNING', 'ERROR', 'CRITICAL', 'ERROR']


@pytest.fixture
def session_calls(monkeypatch):
    """Registra las llamadas a boto3.Session sin contactar AWS."""
    calls = []

    def fake_session(*args, **kwargs):
        calls.append(kwargs)
        raise RuntimeError('AWS disabled in tests')

    monkeypatch.setattr(logger_module, 'Session', fake_session)
    return calls


def test_no_aws_calls_without_cloud_watch_config(new_logger, no_cloud_watch, session_calls):
    log = new_logger()
    log.info('solo local')

    assert session_calls == []
    assert log.cloud_watch is None


def test_creating_logger_does_not_contact_aws(new_logger, cloud_watch_env, session_calls):
    new_logger()

    assert session_calls == []


@mock_aws
def test_sends_events_to_cloud_watch(new_logger, cloud_watch_env):
    log = new_logger()

    before = int(time.time() * 1000)
    log.error('fallo en el pago')
    after = int(time.time() * 1000)

    events = boto3.client('logs', region_name='us-east-1').get_log_events(
        logGroupName='test-group',
        logStreamName='test-stream',
    )['events']

    assert len(events) == 1
    assert events[0]['message'].startswith('ERROR | test_logger.py:')
    assert events[0]['message'].endswith('| fallo en el pago')
    assert before <= events[0]['timestamp'] <= after


@mock_aws
def test_cloud_watch_failure_does_not_raise(new_logger, cloud_watch_env, capsys):
    log = new_logger()
    log.info('inicializa CloudWatch')

    boto3.client('logs', region_name='us-east-1').delete_log_group(logGroupName='test-group')

    log.info('el grupo ya no existe')

    assert 'CloudWatch error' in capsys.readouterr().out
