# -*- coding: utf-8 -*-
from .directives import HTTPExample

import os
import shutil


CSS_FILE = 'sphinxcontrib-httpexample.css'
JS_FILE = 'sphinxcontrib-httpexample.js'


def copy_assets(app, exception):
    if app.builder.name != 'html' or exception:
        return

    # CSS
    src = os.path.join(os.path.dirname(__file__), 'static', CSS_FILE)
    dst = os.path.join(app.builder.outdir, '_static', CSS_FILE)
    shutil.copyfile(src, dst)

    # JS
    src = os.path.join(os.path.dirname(__file__), 'static', JS_FILE)
    dst = os.path.join(app.builder.outdir, '_static', JS_FILE)
    shutil.copyfile(src, dst)


def setup(app):
    app.connect('build-finished', copy_assets)
    app.add_directive_to_domain('http', 'example', HTTPExample)
    app.add_js_file(JS_FILE)
    app.add_css_file(CSS_FILE)
    return {'version': '1.0'}
