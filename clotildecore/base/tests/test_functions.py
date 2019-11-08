# -*- coding: utf-8 -*-

from unittest import skip
from unittest import mock

import random

from . import common
from .. import functions

from django.utils.text import slugify as django_slugify

class FunctionTest(common.BaseTestCase):
    def test_function_slugify(self):
        S=self.random_string(add_chars="¶@&*\"'~%")
        S+="¶@&*\"'~%"
        expected=django_slugify(S)
        ret=functions.slugify(S)
        self.assertEqual(expected,ret)
