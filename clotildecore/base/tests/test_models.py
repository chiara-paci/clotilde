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
from .. import models

class CasePairModelTest(common.BaseTestCase):
    def _create_random_object(self):
        return models.CasePair.objects.create(lower=self.random_string(),upper=self.random_string())

    def test_casepair_has_lower_field(self):
        obj=self._create_random_object()
        self.assertTrue(hasattr(obj,"lower"))
