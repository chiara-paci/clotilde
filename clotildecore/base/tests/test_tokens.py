# -*- coding: utf-8 -*-

import unittest
import random
import json

from unittest import skip
from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError,PermissionDenied
from django.db.utils import IntegrityError
from sqlite3 import IntegrityError as S3IntegrityError

from . import common
from .. import tokens

class ConstantTest(common.BaseTestCase):
    def test_tokens_constant(self):
        for name,required,actual in [ 
                ("MARKERS",self.CONST_TOKENS["MARKERS"],tokens.MARKERS),
                ("NEW_LINES",self.CONST_TOKENS["NEW_LINES"],tokens.NEW_LINES),
        ]: 
            for n in range(0,len(required)):
                with self.subTest(const=name,n=n):
                    self.assertConstant(name,required[n],actual[n])
