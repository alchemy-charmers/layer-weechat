import pytest
from juju.model import Model

# Treat tests as coroutines
pytestmark = pytest.mark.asyncio

series = ['bionic']


@pytest.fixture
async def model():
    model = Model()
    await model.connect_current()
    yield model
    await model.disconnect()


@pytest.mark.parametrize('series', series)
async def test_weechat_deploy(model, series):
    weechat = await model.deploy('.', series=series)
    await model.deploy('cs:~chris.sanders/haproxy', series='xenial')
    await model.block_until(lambda: weechat.status == 'active')
    assert weechat.status == 'active'


async def test_running(run_command):
    cmd = 'runuser -l weechat -c "screen -list"'
    result = await run_command(cmd, 'weechat/0')
    assert 'There is a screen' in result['Stdout']


async def test_relation(model):
    weechat = model.applications['weechat']
    haproxy = model.applications['haproxy']
    await weechat.add_relation('reverseproxy', 'haproxy:reverseproxy')
    await model.block_until(lambda: haproxy.status == 'active')
# def test_example_action(self, deploy, unit):
#     uuid = unit.run_action('example-action')
#     action_output = deploy.get_action_output(uuid, full_output=True)
#     print(action_output)
#     assert action_output['status'] == 'completed'
