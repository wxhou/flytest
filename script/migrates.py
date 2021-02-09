#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import sys
import subprocess


def main():
    win = sys.platform.startswith('win')
    steps = ['flask db migrate -m "update"', 'flask db upgrade']
    for step in steps:
        subprocess.run('call ' + step if win else step, shell=True)


if __name__ == '__main__':
    main()
