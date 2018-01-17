#! /usr/bin/env python3
import gnureadline as readline


class Command:
    def __init__(self, name, desc, func, *usage):
        self.name = name
        self.desc = desc
        self.func = func
        self.usage = usage

    def __call__(self, *s):
        options = []
        for usage in range(len(self.usage)):
            if usage < len(s):
                (worked, res) = self.usage[usage](s[usage])
                if worked:
                    options.append(res)
                else:
                    if self.usage[usage].optional:
                        break
                    else:
                        print(res)
                        print(self)
                        return False
            else:
                if self.usage[usage].optional:
                    break
                else:
                    print(self)
                    return False

        self.func(*options)

    def __repr__(self, *args):
        return 'Usage: ' + self.name + ' ' + ' '.join(str(u) for u in self.usage)


class Usage:
    def __init__(self, func, usage, optional=False):
        self.func = func
        self.usage = usage
        self.optional = optional

    def __call__(self, args):
        return self.func(args) # ret tuple (bool success, ret val)

    def __repr__(self):
        return ''.join(['<' if not self.optional else '[', self.usage, '>' if not self.optional else ']'])


class Completer(object):
    """
    This is an autocompleter to be used with the python readline class
    sample implementation and documentation is located at:
    http://stackoverflow.com/questions/5637124/tab-completion-in-pythons-raw-input
    """
    def __init__(self, commands):
        self.commands = commands
        self.re_space = re.compile('.*\s+$', re.M)

    def _listdir(self, root):
        res = []
        for name in os.listdir(root):
            path = os.path.join(root, name)
            if os.path.isdir(path):
                name += os.sep
            res.append(name)
        return res

    def _complete_path(self, path=None):
        if not path:
            return self._listdir('.')
        dirname, rest = os.path.split(path)
        tmp = dirname if dirname else '.'
        res = [os.path.join(dirname, p) for p in self._listdir(tmp) if p.startswith(rest)]
        # more than one match, or single match which does not exist (typo)
        if len(res) > 1 or not os.path.exists(path):
            return res
        # resolved to a single directory, so return list of files below it
        if os.path.isdir(path):
            return [os.path.join(path, p) for p in self._listdir(path)]
        # exact file match terminates this completion
        return [path + ' ']

    def complete_extra(self, args):
        if not args:
            return self._complete_path('.')
        # treat the last arg as a path and complete it
        return self._complete_path(args[-1])

    def complete(self, text, state):
        buffer = readline.get_line_buffer()
        line = readline.get_line_buffer().split()

        # show all commands
        if not line:
            return [c + ' ' for c in self.commands][state]
        # account for last argument ending in a space
        if self.re_space.match(buffer):
            line.append('')
        # resolve command to the implementation function
        cmd = line[0].strip()
        if cmd in self.commands:
            args = line[1:]
            if args:
                return (self.complete_extra(args) + [None])[state]
            return [cmd + ' '][state]
        results = [c + ' ' for c in self.commands if c.startswith(cmd)] + [None]
        return results[state]
