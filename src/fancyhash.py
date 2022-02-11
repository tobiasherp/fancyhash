# -*- coding: utf-8 -*- äöü vim: ts=8 sts=4 sw=4 si et tw=79
"""\
fancyhash: user friendly hash calculation and checking

See:
../README.rst (English) resp. ../LIESMICH.rst (German) for a description
../HISTORY.rst (English) resp. ../HISTORIE.rst (German) for the release history
../TODO.rst (English) for things still to be done
"""
# TODO (siehe auch -> fancyhash.txt):
# [x] - --check (ok: v0.3+)
# [x]   - check files which contain just one line, containing the digest only
# [ ]   - " *" implies binary, "  " implies textual
# [ ]   - accompanied by (from md5sum):
# [ ]     --quiet     don't print OK for each successfully verified file
# [ ]     --status    don't output anything, status code shows success
#                     (output for read errors, no output for hash mismatch)
# [ ]     -w, --warn  warn about improperly formatted MD5 checksum lines:
# [ ]                 - '  ' lines, where --binary hash matches expected value
# [ ]                 - uppercase hexdigits
# [ ]                 - whatever else md5sum considers improperly formatted
# [x]   - in *.sha files, derive the algorithm from the hash length
# [x]   - support openssl input lines, e.g.
#         SHA(pip-1.3.1.tar.gz)= 44831088fcca253a37ca4ff70943d48ce7999e3d
#         SHA1(pip-1.3.1.tar.gz)= 7466be3ab27702b0738423e9d731b0175f101133
#         RIPEMD160(pip-1.3.1.tar.gz)= 979f820ea3966f09c7465c6cdeae19a070845b76
# [ ]   - support openssl output format, see above
# [ ]   - tell about the used algorithm, if chosen automatically
# [ ] - --binary/-b:
# [ ]   - accompany by --text/-t (taken from md5sum)
# [ ]     - textual checksums of LF, CRLF, mixed-EOL text files
# [ ] - read standard input, if no filenames given, and if redirected
# [ ] - read standard input, if no filenames given, and --check specified
# [ ] - elaborate verbosity:
# [ ]   - 0 - status code only (--status, or -qqq)
# [ ]   - 1 - errors only (--quiet, or -qq)
# [ ]   - 2 - all checked hashes; summary about others (-q)
# [ ]   - 3 - process information (default)
# [ ]   - 4 - total summary (-v)
# [ ]   - 5 - summary per list (-vv)
# [x] - --prompt option to prompt for <Enter> key before quitting
# [ ]   - implies verbose output, full summary
# [ ] - thebops.anypy.hashlib
# [ ] - working i18n/l10n

__author__ = "Tobias Herp <tobias.herp@gmx.net>"
VERSION = (0,
           3,  # --check
           4,  # --prompt
           'rev-%s' % '$Rev: 1114 $'[6:-2],
           )
__version__ = '.'.join(map(str, VERSION))
try:
    _
except NameError:
    def dummy(s):
        return s
    _ = dummy

from os import stat
from os.path import splitext
from hashlib import new, algorithms  # Python 2.7+
from time import time, sleep
from fractions import gcd            # Python 2.6+
from string import hexdigits
from collections import defaultdict  # Python 2.5+
from re import compile as compile_re

from thebops.optparse import OptionParser, OptionGroup
from thebops.shtools import GlobFileGenerator, FilenameGenerator, get_console
from thebops.termwot import generate_caterpillars
from thebops.counters import error as err, warning as warn, info, \
        fatal, check_errors
from thebops.opo import add_glob_options, add_help_option, \
        add_trace_option, DEBUG, \
        add_version_option, add_verbosity_options

digest_lengths = (
        # ermittelt aus hashlib:
        ('md5',       16),
        ('sha1',      20),  # also sha, rmd160
        ('sha224',    28),
        ('sha256',    32),
        ('sha384',    48),
        ('sha512',    64),  # also whirlpool
        # supported by openssl command:
        #  rmd160 -> RIPEMD160 (20)
        #  sha -> SHA (20)
        #  sha1 -> SHA1 (20)
        # more:
        # ('whirlpool', 64),
        )
length2algo = defaultdict(lambda: [])
for tup in digest_lengths:
    algo, L = tup
    length2algo[L * 2].append(algo)
openssl2algo = {}
for key in [tup[0]
            for tup in digest_lengths
            ] + ['sha',
            ]:
    openssl2algo[key.upper()] = key
# openssl2algo['RIPEMD160'] = 'rmd160'


class FancyhashException(Exception):
    """
    Root of exception classes
    """


class HashtypeDetectionError(FancyhashException):
    "Could not detext hash type"


class NotAHexDigest(HashtypeDetectionError, ValueError):
    "The value is not a hex. digest"


# not yet used:
class UnknownHexdigestLength(HashtypeDetectionError, ValueError):
    "according to digest_lengths"


class FancyhashMismatch(FancyhashException):
    "hash doesn't match expected value"


def createParser():
    p = OptionParser(usage='%prog [Options]',
                     add_help_option=False)
    p.set_description(_('Compute cryptographic hashes, especially for large'
        ' files; during calculation, some screen output is displayed'
        ' (unless switched off via --quiet).'
        ))
    g = OptionGroup(p, "Important options")
    g.add_option('--check', '-c',
                 action='store_true',
                 default=False,
                 help=_('Read a file containing hash values'
                 ' ("abc...123def *filename" lines)'
                 ', and check whether the hashes match the actual '
                 'files.'
                 ' For hash files containing only the hash value, guess '
                 'the file name from the hash file name.'
                 ))
    g.add_option('--algorithm',
                 action='store',
                 metavar='|'.join(algorithms),
                 help=_('the algorithm to use'
                 ', unless guessed by length of given digest'
                 ' (--check/-c option)'
                 '; also --%s etc.'
                 ) % (algorithms[0],))
    g.add_option('--prompt',
                 action='store_true',
                 help=_('Prompt for [Return] before quitting'
                 ' (useful when called by a graphical shell)'
                 ))
    p.add_option_group(g)

    g = OptionGroup(p, _("Argument evaluation"))
    add_glob_options(g)
    p.add_option_group(g)

    h = OptionGroup(p, "hidden options")
    for alg in algorithms:
        h.add_option('--' + alg,
                     action='store_const',
                     dest='algorithm',
                     const=alg)
    add_trace_option(h)  # -T[TT]

    g = OptionGroup(p, _("Screen output"))
    add_verbosity_options(g, default=2)
    g.add_option('--refresh-interval',
                 dest='refresh_interval',
                 action='store',
                 type='float',
                 default=0.25,
                 metavar='0.25[seconds]',
                 help=_('the time [seconds] between screen updates, '
                 'default: %default'
                 ' (unless disabled by --quiet)'
                 ))
    p.add_option_group(g)

    g = OptionGroup(p, _("Everyday options"))
    add_version_option(g, version=VERSION)
    add_help_option(g)
    p.add_option_group(g)
    return p


def parse(p):
    o, a = p.parse_args()
    if not a:
        err(_('No files given!'))
        # err('Keine Dateien angegeben')
    if o.algorithm is None:
        if not o.check:
            o.algorithm = 'md5'
    if 0 and not o.algorithm in algorithms:
        # err(u'Nicht unterstützter Algorithmus: "%s"'
        err('Unsupported algorithm: "%s"'
            % (o.algorithm,))
    check_errors()
    return o, a


count = defaultdict(int)
def main():
    aborted = False
    # DEBUG()
    p = createParser()
    o, a = parse(p)

    try:
        INTERVAL = o.refresh_interval
        console = get_console()

        if o.verbose >= 1:
            fancy = generate_caterpillars(width=FANCYWIDTH).__iter__()
        else:
            fancy = None
        gen = (o.glob
               and GlobFileGenerator
               or  FilenameGenerator
               )(*a).__iter__()
        for fn in gen:
            try:
                if o.check:
                    check_hashes(fn, algorithm=o.algorithm,
                                 fancy=fancy, console=console,
                                 verbose=o.verbose)
                else:
                    compute_hash(fn, algorithm=o.algorithm,
                                 fancy=fancy, console=console,
                                 verbose=o.verbose)
            except OSError, e:
                err(e)
                count['readerrors'] += 1
    except KeyboardInterrupt:
        DEBUG()
        print >> console
        print >> console, '\r%*s\r%s' % (FANCYWIDTH + 10 + len(fn),
                                       '',
                                       _('... aborted.')
                                       ),
        aborted = True
    finally:
        # TODO: establish an option to accept missing files
        #       (and use info instead of warn)
        #       as long as at least one hash was successfully checked
        if count['readerrors']:
            warn(_('%(readerrors)d of %(total)d files could not be read')
                 % count)
            count['total'] -= count['readerrors']
        if count['mismatch']:
            warn(_('%(mismatch)d of %(total)d computed checksums did NOT match')
                 % count)
        DEBUG()
        if o.prompt:
            print >> console, _('Press [Return] key to quit: '),
            raw_input()
        elif aborted:
            raise SystemExit(99)
        ## no tell argument yet:
        # check_errors(text=False, tell=False)
        if count['readerrors'] or count['mismatch']:
            fatal(count=False, tell=False)


HEXDIGITS = set(hexdigits)
def default_algo(digest, listname=None):
    """
    digest - hex-Darstellung des gegebenen Hashwerts (--check)
    listname - Dateiname der Listendatei; derzeit nicht verwendet
    """
    wrong = set(digest).difference(HEXDIGITS)
    if wrong:
        raise NotAHexDigest(wrong)
    return length2algo[len(digest)][0]


FANCYWIDTH = 20
FANCYMASK = '\r%%%ds %%s (%%.2f%%%%)' % FANCYWIDTH
def fancyline(fancy, fn, total, pos):
    if pos >= total:
        proz = 100
    elif total:
        proz = pos * 100.0 / total
    else:
        proz = 0
    return (FANCYMASK
            % (fancy.next(),
               fn,
               proz
               ))


INTERVAL = 0.2
AUTOGROW = False
NULLSTRING_HASHES = {}
def compute_hash(fn, algorithm=None, digest=None, fancy=None, console=None,
                 verbose=0):
    """
    Berechne den Hash-Wert der übergebenen Datei

    algorithm - der Algorithmus; optional, wenn <digest> angegeben
    digest - hex-Darstellung des gegebenen Hashwerts (--check)
    fancy - ein Generator für Textausgaben
    console - Gerät zur Ausgabe der Textausgaben
    """
    if fancy is not None:
        if console is None:
            console = get_console()
    if algorithm is None:
        if digest is not None:
            algorithm = default_algo(digest)
            if verbose > 2:
                info('Computing %(algorithm)s for %(fn)s'
                     ' (guessed from digest length)'
                     % locals())
        # otherwise set to 'md5' by default
    elif verbose > 2:
        info('Computing %(algorithm)s for %(fn)s'
             % locals())
    count['total'] += 1
    total = stat(fn).st_size
    fo = open(fn, 'rb', 0)
    DEBUG()
    HASH = new(algorithm)
    if algorithm not in NULLSTRING_HASHES:
        NULLSTRING_HASHES[algorithm] = HASH.hexdigest()
    ochunk = chunk = lcm(HASH.block_size, 512 * 2 ** 5)
    pos = 0
    try:
        if fancy is not None:
            ptime = time()
            print >> console, fancyline(fancy, fn, total, pos),
            while True:
                HASH.update(fo.read(chunk))
                pos += chunk
                now = time()
                lap = now - ptime
                if pos >= total:
                    break
                elif lap > INTERVAL:
                    print >> console, fancyline(fancy, fn, total, pos),
                    ptime = now
                elif AUTOGROW:
                    chunk += ochunk
        else:
            while True:
                HASH.update(fo.read(chunk))
                pos += chunk
                if pos >= total:
                    break
    finally:
        fo.close()
        newdigest = HASH.hexdigest()
        del HASH, fo
        if fancy is not None:
            print >> console, '\r%*s\r' % (FANCYWIDTH + 10 + len(fn),
                                           '',
                                           ),
        if digest is None:
            print '%s *%s' % (newdigest, fn)
            return True
        elif newdigest == digest.lower():
            print '%s (%s): ok' % (fn, algorithm)
            return True
        else:
            err(_('%(fn)s: Error!\n'
                  '  expected: %(digest)s\n'
                  '  got:      %(newdigest)s'
                  ) % locals())
            return False


# 7466be3ab27702b0738423e9d731b0175f101133 *pip-1.3.1.tar.gz:
RE_HASHLINE = compile_re('^'
                         '(?P<digest>[a-fA-F0-9]+)'
                         r'(?P<switch>(  | \*| \b))'
                         '(?P<filename>.+)'
                         '$')
# SHA1(pip-1.3.1.tar.gz)= 7466be3ab27702b0738423e9d731b0175f101133:
RE_OPENSSLLINE = compile_re('^'
                            '(?P<ALGO>[A-Z0-9]+)'
                            '[(]'
                            '(?P<filename>.+)'
                            '[)]= '
                            '(?P<digest>[a-fA-F0-9]+)'
                            '$')
def parse_hashline(s):
    """
    >>> parse_hashline('abc123 *thefile')
    {'digest': 'abc123', 'filename': 'thefile', 'switch': ' *'}
    >>> parse_hashline('abc123')
    {'digest': 'abc123'}
    """
    mo = RE_HASHLINE.match(s)
    if mo:
        return mo.groupdict()
    mo = RE_OPENSSLLINE.match(s)
    if mo:
        return mo.groupdict()
    wrong = set(s).difference(HEXDIGITS)
    if not wrong:
        return {'digest': s}
    return


def check_hashes(fn, algorithm=None, digest=None, fancy=None, console=None,
                 verbose=0):
    """
    Prüfe die Hash-Werte aus der übergebenen Listendatei

    fn - die Listendatei
    algorithm - der Algorithmus; optional, wenn <digest> angegeben
    digest - hex-Darstellung des gegebenen Hashwerts (--check)
    fancy - ein Generator für Textausgaben
    console - Gerät zur Ausgabe der Textausgaben
    """
    try:
        fo = open(fn, 'rU')
    except IOError, e:
        err(e)
        return
    else:
        for line in fo:
            z = line.strip()
            if not z or z[0] in '#;':
                count['skipped'] += 1
                continue
            dic = parse_hashline(z)
            if not dic:
                count['invalid'] += 1
                continue
            ALGO = dic.get('ALGO')  # openssl style line
            if ALGO is not None:
                try:
                    algorithm = openssl2algo[ALGO]
                except KeyError:
                    count['invalid'] += 1
                    continue
            try:
                fname = dic.pop('filename')
            except KeyError:
                fname = splitext(fn)[0]
                if not fname or fname == fn:
                    raise ValueError(_('Couldn\'t guess a filename from'
                                       ' %(fn)s!'
                                       ) % locals())
            try:
                if compute_hash(fname, algorithm,
                                dic['digest'],
                                fancy, console,
                                verbose):
                    count['match'] += 1
                else:
                    count['mismatch'] += 1
            except OSError, e:
                err(e)
                count['readerrors'] += 1


def lcm(a, b):
    """
    least common multiple

    >>> lcm(4, 6)
    12
    """
    if a and b:
        return abs(a * b) / gcd(a, b)
    else:
        return 0


if __name__ == '__main__':
    main()
