from charmhelpers.core import hookenv, templating
import subprocess


class WeechatHelper():
    def __init__(self):
        self.charm_config = hookenv.config()
        self.service_file = '/lib/systemd/system/weechat.service'
        self.fifo_file = '/home/weechat/.weechat/weechat_fifo'

    def install_systemd(self):
        templating.render('weechat.service',
                          self.service_file,
                          context={})

    def weechat_command(self, command):
        cmd = "*{}".format(command)
        result = subprocess.check_output('echo {} > {}'.format(cmd, self.fifo_file))
        return result.decode()

    def action_function(self):
        ''' An example function for calling from an action '''
        return
