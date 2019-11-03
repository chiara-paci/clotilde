from django.test import TestCase

import random
import string

class BaseTestCase(TestCase):
    
    databases = settings.DATABASES

    # def setUp(self):  
    #     self.user=self.create_random_user()
    #     self.client.login(username=self.user.username,password=self.user.password)

    def random_string(self,size=0,with_spaces=True,max_size=10,min_size=3,only_chars="",add_chars=""):
        if not size:
            size=random.choice(range(min_size,max_size))
        if only_chars:
            chars=only_chars
        else:
            chars=string.ascii_lowercase +string.ascii_uppercase + string.digits
            chars+=add_chars
            if with_spaces:
                chars+="    "
        S=''.join(random.choice(chars) for _ in range(size))
        if with_spaces:
            S=S.strip()
            S=" ".join(S.split())
        return S


