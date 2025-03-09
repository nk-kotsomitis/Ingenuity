# Copyright (C) 2025 Ingenuity
# Licensed under the GNU General Public License v3.0

# Node schema
node_schema = {
    'attributes': {
        'conversion': None,
    },
        'inputs':
            {'a1':
                {'type': None,
                 'shape': None,
                 'q_params':
                     {'scale': None,
                      'zero': None,
                      'min': None,
                      'max': None
                      }
                 },
             'weights':
                 {
                     'type': None,
                     'shape': None,
                     'q_params':
                         {
                             'scale': None,
                             'zero': None,
                             'min': None,
                             'max': None
                         },
                     'buffer': None
                 },
             'bias':
                 {
                     'type': None,
                     'shape': None,
                     'q_params':
                         {
                             'scale': None,
                             'zero': None,
                             'min': None,
                             'max': None
                         },
                     'buffer': None
                 }
             },
        'outputs':
            {'a2':
                 {
                     'type': None,
                     'shape': None,
                     'q_params':
                         {
                             'scale': None,
                             'zero': None,
                             'min': None,
                             'max': None
                         },
                     'actf': None
                 }
            }
        }