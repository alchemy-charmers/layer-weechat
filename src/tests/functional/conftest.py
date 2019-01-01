import juju
import pytest
from juju.errors import JujuError


@pytest.fixture
async def get_unit(model):
    '''Returns the requested <app_name>/<unit_number> unit'''
    async def _get_unit(name):
        try:
            (app_name, unit_number) = name.split('/')
            return model.applications[app_name].units[int(unit_number)]
        except (KeyError, ValueError):
            raise JujuError("Cannot find unit {}".format(name))
    return _get_unit


@pytest.fixture
async def run_command(get_unit):
    '''
    Runs a command on a unit.

    :param cmd: Command to be run
    :param target: Unit object or unit name string
    '''
    async def _run_command(cmd, target):
        unit = (
            target
            if type(target) is juju.unit.Unit
            else await get_unit(target)
        )
        action = await unit.run(cmd)
        return action.results
    return _run_command
