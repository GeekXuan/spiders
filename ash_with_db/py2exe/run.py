#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyInstaller.__main__ import run

if __name__ == '__main__':
    opts = ['ash_spider_db.py', '-F']
    # opts = ['performance_appraisal.py', '-F','--upx-dir','upx394w']
    # opts = ['performance_appraisal.py', '-F', '-w']
    # opts = ['face_gui.py', '-F', '-w','--upx-dir','upx394w']
    # opts = ['face_gui.py', '-F', '-w', '--icon=tubiao.ico','--upx-dir','upx394w']
    run(opts)
