'''
Created on Jun 3, 2015

@author: agutierrez
'''
from __future__ import unicode_literals
from argparse import ArgumentParser
import logging
import os
import sys

from madmex import setup
import madmex
from madmex.configuration import SETTINGS


logger = logging.getLogger(__name__)

class CommandError(Exception):
    '''
    Exception class indicating a problem while executing a management
    command.
    '''
    pass

class SystemCheckError(CommandError):
    '''
    Exception class indicating a problem while executing a management
    command.
    '''
    pass

class CommandParser(ArgumentParser):
    """
    Customized ArgumentParser class to prevent
    SystemExit in several occasions, as SystemExit is unacceptable when a
    command is called programmatically.
    """
    def __init__(self, cmd, **kwargs):
        self.cmd = cmd
        super(CommandParser, self).__init__(**kwargs)

    def error(self, message):
        if self.cmd._called_from_command_line:
            super(CommandParser, self).error(message)
        else:
            raise CommandError("Error: %s" % message)

def handle_default_options(options):
    """
    Include any default options that all commands should accept here
    so that ManagementUtility can handle them before searching for
    user commands.

    """
    if getattr(options, 'settings'):
        os.environ['MADMEX_SETTINGS_MODULE'] = options.settings
        SETTINGS.reload()
        setup()
        logger.info('Settings loaded from %s.' % options.settings)
    if getattr(options, 'pythonpath'):
        sys.path.insert(0, options.pythonpath)
        logger.info('%s was added to the PYTHONPATH.' % options.settings)
    logger.debug('Default options had been handled.')

class BaseCommand(object):
    '''
    This is the class that all commands should inherit. It defines
    methods to be implemented by descendants. All commands should be
    defined in the commands package beneath this module.
    '''

    help = ''
    args = ''
    _called_from_command_line = False
    def __init__(self):
        '''
        Constructor
        '''
        self.stdout = sys.stdout
        self.stderr = sys.stderr
    def usage(self, subcommand):
        '''
        Return a brief description of how to use this command, by
        default from the attribute ``self.help``.
        '''
        usage = '%%prog %s [options] %s' % (subcommand, self.args)
        if self.help:
            return '%s\n\n%s' % (usage, self.help)
        else:
            return usage
    def create_parser(self, prog_name, subcommand):
        '''
        Create and return the ``ArgumentParser`` which will be used to
        parse the arguments to this command.
        '''
        parser = CommandParser(
            self,
            prog="%s %s" % (os.path.basename(prog_name), subcommand),
            description=self.help or None
        )
        parser.add_argument(
            '--version',
            action='version',
            version=madmex.get_version()
        )
        parser.add_argument(
            '-v',
            '--verbosity',
            action='store',
            dest='verbosity',
            default='1',
            type=int,
            choices=[0, 1, 2, 3],
            help='Verbosity level; 0=minimal output, 1=normal output, 2=verbose '
                 'output, 3=very verbose output'
        )
        parser.add_argument(
            '--settings',
            help=(
                'The Python path to a SETTINGS module, e.g. '
                '"myproject.SETTINGS.main". If this isn\'t provided, the '
                'DJANGO_SETTINGS_MODULE environment variable will be used.'
            ),
        )
        parser.add_argument(
            '--pythonpath',
            help='A directory to add to the Python path, e.g. '
                 '"/home/djangoprojects/myproject".'
        )
        parser.add_argument(
            '--traceback',
            action='store_true',
            help='Raise on CommandError exceptions'
        )
        parser.add_argument(
            '--no-color',
            action='store_true',
            dest='no_color',
            default=False,
            help="Don't colorize the command output."
        )
        if self.args:
            # Keep compatibility and always accept positional 
            # arguments, like optparse when args is set
            parser.add_argument('args', nargs='*')
        self.add_arguments(parser)
        return parser
    def add_arguments(self, parser):
        '''
        Entry point for subclassed commands to add custom arguments.
        '''
        pass
    def print_help(self, prog_name, subcommand):
        '''
        Print the help message for this command, derived from
        ``self.usage()``.

        '''
        parser = self.create_parser(prog_name, subcommand)
        parser.print_help()
    def run_from_argv(self, argv):
        '''
        Will execute this command with the given arguments from the command line
        interface.
        '''
        self._called_from_command_line = True
        parser = self.create_parser(argv[0], argv[1])
        options = parser.parse_args(argv[2:])
        cmd_options = vars(options)
        handle_default_options(options)  
        try:
            self.execute(**cmd_options)
        except CommandError as exception:
            if options.traceback or not isinstance(exception, CommandError):
                raise

            # SystemCheckError takes care of its own formatting.
            if isinstance(exception, SystemCheckError):
                self.stderr.write(str(exception), lambda x: x)
            else:
                self.stderr.write('%s: %s' % (exception.__class__.__name__, exception))
            sys.exit(1)
        finally:
            pass
    def execute(self, **options):
        '''
        This method will implement necessary system checks in case they are needed.
        '''
        try:
            self.handle(**options)
        finally:
            pass
    def handle(self, **options):
        '''
        The actual logic of the command. Subclasses must implement
        this method.
        '''
        raise NotImplementedError('Subclasses of BaseCommand must provide a handle() method')
