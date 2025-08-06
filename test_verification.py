#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import importlib
import sys

# Force reload the module
if 'victoria2_main_modifier' in sys.modules:
    importlib.reload(sys.modules['victoria2_main_modifier'])

from victoria2_main_modifier import Victoria2Modifier

# Test verification function
modifier = Victoria2Modifier()
modifier.debug_mode = False
print('Loading file...')
modifier.load_file('China1836_02_20.v2')
print('Running verification...')
modifier.verify_ideology_modifications('China1836_02_20.v2')
