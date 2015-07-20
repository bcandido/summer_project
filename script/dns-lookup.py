#!/usr/bin/python

import pexpect
import sys

DOMAIN = sys.argv[1]

child = pexpect.spawnu('dig +short '+domain)
child.expect(pexpect.EOF, timeout=None)

print child.before.strip()