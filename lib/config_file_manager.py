import os
import sys
import logging
sys.path.append('../lib')

logging.basicConfig(level=logging.DEBUG,
                    format='%(levelname)s: %(message)s',
                    filemode='w')


class ConfigFileManager:
    # Manages the writing and reading of configuration files.
    def __init__(self, delim=','):
        self.delim = delim
        self.comment_ch = '#'

    def read(self, filename):
        # Read Method manages the reading of configuration file
        config = {}
        fp = None
        try:
            fp = open(filename, 'r')
            for line in fp:
                if line[0] == self.comment_ch:
                    # commented line, skip
                    continue
                parts = line.strip('\n').split(self.delim)
                # line = attribute_type,attribute_name,example
                if len(parts) < 2:
                    # skip ill-formatted lines
                    continue
                [attr_type, attr_name] = parts[:2]
                config.setdefault(attr_type, []).append(attr_name)
        except:
            logging.warning('Unable to parse file:' + self.filename)
        finally:
            if fp:
                fp.close()
            return config

    def write(self, filename, data_dict, attr_set=None):
        # Manages the writing of configuration file
        fp = open(filename, 'w')
        for attr_type, attr_vals in data_dict.iteritems():
            fp.write('# %s INFORMATION\n' % attr_type.upper())
            attr_names = sorted(attr_vals.keys())
            for attr_name in attr_names:
                attr_data = attr_vals[attr_name]
                if attr_set and attr_name not in attr_set:
                    # Not an attribute we want to dump out
                    continue
                for ind_block, val in attr_data.iteritems():
                    fp.write('%s%s%s%sExample: %s\n' % (attr_name.upper(),
                                    self.delim, ind_block, self.delim, val))
