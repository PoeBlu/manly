"""usage: manly [command] [options for that command]"""

import sys
import subprocess
import re


_ANSI_BOLD = '\033[1m{}\033[0m'


def parse_flags(raw_flags):
    '''Split concatenated flags (eg. ls' -la) into individual flags
    (eg. '-la' -> '-l', '-a').

    Args:
        raw_flags (list): The flags as they would be given normally.

    Returns:
        flags (list): The disassembled concatenations of flags, and regular
            verbose flags as given.
    '''
    flags = []
    for flag in raw_flags:
        if flag.startswith('--'):
            flags.append(flag)
        elif flag.startswith('-'):
            for char in flag[1:]:
                flags.append('-' + char)
    return flags


def section_is_for_arg(section, section_top, arg):
    first_line = section_top[0].split(',')
    try:
        header = section_top[1].strip().startswith(arg)
    except IndexError:
        header = False

    section = re.sub(
            r'(^|\s){}'.format(arg),
            _ANSI_BOLD.format(arg),
            section
    ).rstrip()

    if header:
        return section

    for seg in first_line:
        if seg.strip().startswith(arg):
            return section
    return False


def parse_manpage(page, args):
    '''Scan the manpage for blocks of text, and check if the found blocks
    have sections that match the general manpage-flag descriptor style.

    Args:
        page (str): The utf-8 encoded manpage.
        args (iter): An iterable of flags passed to check against.

    Returns:
        output (list): The blocks of the manpage that match the given flags.
    '''
    current_section = []
    output = []

    for line in page.splitlines():
        line = line + '\n'
        if line != '\n':
            current_section.append(line)
            continue

        section = ''.join(current_section)
        section_top = section.strip().split('\n')[:2]

        for arg in args:
            formatted_section = section_is_for_arg(section, section_top, arg)
            if formatted_section:
                output.append(formatted_section)
                continue
        current_section = []
    return output


def main():
    try:
        command = sys.argv[1]
    except IndexError:
        print(__doc__)
        sys.exit(0)
    if len(sys.argv) == 2:
        print('Please supply flags. Type just `manly` for help.')
        sys.exit(2)
    flags = parse_flags(sys.argv[2:])
    try:
        manpage = subprocess.check_output(['man', command]).decode('utf-8')
    except subprocess.CalledProcessError:
        sys.exit(16)  # because that's the exit status that `man` uses.

    title = _ANSI_BOLD.format(
            re.search(r'(?<=^NAME\n\s{7}).+', manpage, re.MULTILINE).group(0))
    output = parse_manpage(manpage, flags)

    print('\nSearching for:', command, *flags, end='\n\n')
    if output:
        print(title)
        print('=' * (len(title) - 8), end='\n\n')
        for flag in output:
            print(flag, end='\n\n')
    else:
        print('No flags found.')
    print()


if __name__ == '__main__':
    main()
