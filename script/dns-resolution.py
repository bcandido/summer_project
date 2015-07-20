#!/usr/bin/python

import pexpect
import sys

IP = sys.argv[1]

child = pexpect.spawnu( 'dig -x '+IP+' +short')
child.expect(pexpect.EOF, timeout=None)

print child.before.strip(),