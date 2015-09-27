import os.path
import logging

from google.appengine.ext import vendor


logger = logging.getLogger(__name__)
vendor_lib = os.path.join(os.path.dirname(__file__), 'site-packages')
vendor_lib = os.path.realpath(vendor_lib)
try:
    vendor.add(vendor_lib)
except Exception as e:
    logger.exception(e)
