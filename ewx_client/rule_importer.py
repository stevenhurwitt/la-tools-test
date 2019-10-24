from energyworx_jgscm import GoogleStorageContentManager
from energyworx_client import _create_path
from energyworx_public.rule import RuleResult, AbstractRule

import sys
import imp
import os
import logging

RULE_LIB_DIRECTORY = 'rule_lib'

logger = logging.getLogger()

class RuleImporter(object):
    def __init__(self):
        logger.info('Initialize importer')
        self.gcs_manager = GoogleStorageContentManager(skip_syncing=True)

    def _import_code(self, code, name, add_to_sys_modules=False):
        """ code can be any object containing code -- string, file object, or
           compiled code object. Returns a new module object initialized
           by dynamically importing the given code and optionally adds it
           to sys.modules under the given name.
        """
        import imp
        module = imp.new_module(name)
        if add_to_sys_modules:
            import sys
            sys.modules[name] = module
        exec code in module.__dict__
        return module

    def load_module(self, package, module):
        logger.info('Finding module %s in package %s', module, package)        
        # namespace-energyworx_org/edwinpoot/rule_lib/validation/totalizer_completeness_check.py
        result = self.gcs_manager.get('{}/rule_lib/{}/{}.py'.format(os.environ['EWX_USERNAME'], package, module))
        logger.info('find_result: %s', result)
        if not result:
            return None
        fullname = "{}.{}".format(package, module)
        logger.info('Importing module %s', fullname)
        return self._import_code(result['content'], fullname, True)