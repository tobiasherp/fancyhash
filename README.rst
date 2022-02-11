======================================
FancyHash - calculate and check hashes
======================================

Fancyhash calculates all hashes supported by your Python interpreter.

On Linux systems, calculating hashes is not a big problem - there are programs
like md5sum, sha1sum etc. which are installed by default, or easily by
installing a well-known package.  Windows (tm) users have a harder time to find
the appropriate programs.

Besides, often you don't get a proper <progname>.md5 etc. file, which contains
proper <hash> \*<progname> lines, but rather the naked hash value, sometimes
even with uppercase hex digits.  Yes, you can fix this, and vim will transform
the uppercase hex digits to lowercase with the ~ command; but it is cumbersome.
You have downloaded the file, and you save the hash value to the same
directory; you click on the existing program file, and append the appropriate
extension - done: fancyhash will take it.  Just as gpg, it will guess the
filename by removing the last extension component.

And since some files are really big, and calculation takes some time, there can
as well be some entertainment ...


Features
========

We try to comply as narrowly as possible to the call conventions expected by the user.

- ``--check`` resp. ``-c`` option

  This should work as expected for "proper" hash files,
  e.g. ``.md5`` files containing ``<hash> *<filename>`` lines.

  Additionally, we allow
 
  - hash files which contain just one line, giving the digest value only
    (where the name of the checked file is the hash file name with the last
    extension stripped off)

  - openssl-style input lines, e.g.::

     SHA(pip-1.3.1.tar.gz)= 44831088fcca253a37ca4ff70943d48ce7999e3d
     SHA1(pip-1.3.1.tar.gz)= 7466be3ab27702b0738423e9d731b0175f101133
     RIPEMD160(pip-1.3.1.tar.gz)= 979f820ea3966f09c7465c6cdeae19a070845b76

- Algorithms

  Fancyhash supports all algorithms your Python's ``hashlib`` module knows,
  and perhaps some more.

  In ``*.sha`` files, we derive the algorithm variant from the hash length.

  We're not sure yet whether this is worth some kind of plugin mechanism;
  for now, we'd be willing to support algorithms which are provided by
  optionally installed packages.

- Output

  While processing large files (which to read and hash takes its time),
  we display some nice little progress indicator.
  If you don't like it, switch it off, using the ``-q`` option.

- ``--prompt`` option to prompt for `Enter` key before quitting

