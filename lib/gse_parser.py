import os
import sys
import logging
import argparse  # for versions < 2.7 please get the module
                 # from https://code.google.com/p/argparse/
import traceback
from enum import Enum


logging.basicConfig(level=logging.DEBUG,
                    format='%(levelname)s: %(message)s',
                    filemode='w')


def ensure_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)


class LineType(Enum):
    block = 1
    attr = 2
    info = 3
    data = 4


class Block:
    def __init__(self, block_name, block_id):
        self.name = block_name
        self.block_id = block_id
        self.attr = {}
        self.info = {}
        self.data = []

    def add_feature(self, feature_type, key, value):
        if feature_type == LineType.attr:
            self.attr[key] = value
        elif feature_type == LineType.info:
            self.info[key] = value
        else:
            self.data.append(value)

    def __str__(self):
        return 'Name:' + self.name + ' BlockID:' + self.block_id + ' Attr:' + str(self.attr) + ' Info:' + str(self.info) + ' Data:' + str(self.data)


class GSEFileParser():
    def __init__(self):
        self.line_types = {
                '^': LineType.block,
                '!': LineType.attr,
                '#': LineType.info,
        }

    def parse_line(self, line):
        '''
            Returns (success, line_type, key, value)
            for line_type==LineType.data, key=None, value = line of data
        '''
        # Determine line type
        line_type = self.line_types.get(line[0], LineType.data)
        # Parse line
        if line_type != LineType.data:
            parts = line[1:].split(' = ')
            if len(parts) != 2:
                logging.warning('### Unexpected line format: %s' % line)
                success = False
                key = None
                value = None
                sys.exit(1)
            else:
                success = True
                key = parts[0].strip()
                value = parts[1].strip()
        else:
            success = True
            key = None
            value = line
        return (success, line_type, key, value)

    def parse(self, filename):
        blocks = {}
        this_block = None
        skip_until_next_block = False
        try:
            for line in open(filename, 'r'):
                line = line.strip('\n')
                if line in ('!platform_table_begin', '!platform_table_end',
                            '!sample_table_begin', '!sample_table_end'):
                    continue
                (success, line_type, key, value) = self.parse_line(line)
                if not success and line_type == LineType.block:
                    # If we were unable to parse a new block header,
                    # discard all lines until next header
                    skip_until_next_block = True
                    continue
                if not success:
                    # Unable to parse this line, skip
                    continue
                if skip_until_next_block and line_type != LineType.block:
                    # Skip line if part of an ill-formatted block
                    continue
                if line_type == LineType.block:
                    # Encountered a new block
                    skip_until_next_block = False
                    this_block = Block(key, value)
                    if this_block.name not in blocks:
                        blocks[this_block.name] = {}
                    blocks[this_block.name][this_block.block_id] = this_block
                else:
                    # Encountered a new feature
                    this_block.add_feature(line_type, key, value)
        except:
            # Unable to parse input file
            print traceback.format_exc()
            blocks = {}
            logging.warning('Unable to parse file ' + filename)
        finally:
            return blocks


if __name__ == "__main__":
    logging.info('Initializing GSE Reader')

    parser = argparse.ArgumentParser(description=
                'Extract relevant data from a GSE file and dumps them in a folder')
    parser.add_argument('--file', dest = 'filename',
                        help = 'file to parse')
    args = parser.parse_args()

    if not args.filename:
        logging.error('No input files found provided')
        print args.usage()

    try:
        gp = GSEFileParser()
        blocks = gp.parse(args.filename)
        print 'Successfully parsed file:', args.filename
    except:
        print traceback.format_exc()
        print 'Error parsing file:', args.filename
