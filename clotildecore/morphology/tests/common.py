from django.test import TestCase
from django.db.utils import IntegrityError
from sqlite3 import IntegrityError as S3IntegrityError

import random
import string
import abc

from .. import models
from base.tests import common as base_common

class BaseTestCase(base_common.CommonTestCase):
    app_name="morphology"
