
Things to Do
============

- Input lines:

  - `` \*`` implies binary, "  " implies textual
  - accompanied by (from md5sum):

    ``--quiet``     don't print OK for each successfully verified file
    ``--status``    don't output anything, status code shows success
                (output for read errors, no output for hash mismatch)

    ``-w``, ``--warn``  warn about improperly formatted MD5 checksum lines:

                - '  ' lines (containing two blanks),
                  where ``--binary`` hash matches expected value
                - uppercase hexdigits
                - whatever else md5sum considers improperly formatted

  - support openssl output format (like already supported for input)
  - tell about the used algorithm, if chosen automatically

- ``--binary``/``-b``:

  - accompany by ``--text``/``-t`` (taken from md5sum)

    - textual checksums of LF, CRLF, mixed-EOL text files

- read standard input, if no filenames given, and if redirected

- read standard input, if no filenames given, and ``--check`` specified

- elaborate verbosity:

  - 0 - status code only (--status, or -qqq)
  - 1 - errors only (--quiet, or -qq)
  - 2 - all checked hashes; summary about others (-q)
  - 3 - process information (default)
  - 4 - total summary (-v)
  - 5 - summary per list (-vv)
  - implies verbose output, full summary

- working i18n/l10n
