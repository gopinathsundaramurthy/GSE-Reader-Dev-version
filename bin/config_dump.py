import os
import sys
sys.path.append('../lib')
import logging
import glob
import argparse  # for versions < 2.7 please
                 # get the module from
                 # https://code.google.com/p/argparse/
from gse_parser import GSEFileParser
from config_file_manager import ConfigFileManager

logging.basicConfig(level = logging.DEBUG,
                    format = '%(levelname)s: %(message)s',
                    filemode = 'w')


class GSEFileConfig():
    # Reads GSE file and identifies all attributes that present in the GSE.
    # Output is a configuration file deposited in the 'conf' folder.
    # Configuration File can be edited by adding '#' for all attributes
    # that not required.
    def __init__(self, base_path, filename):
        self.base_path = base_path
        self.conf_path = os.path.join(base_path, 'conf')
        self.gse_filename = filename

    def read_gsefile(self):
        # Parser to read the GSE file to create a dict with all attributes. 
        blocks_dict = {}
        gp = GSEFileParser()
        gse_parser_blocks = gp.parse(self.gse_filename)
        for block_type, all_blocks in gse_parser_blocks.iteritems():
            for block_id, ind_block in all_blocks.iteritems():
                if block_type not in blocks_dict.keys():
                    blocks_dict[block_type] = {'attr': ind_block.attr,
                                                'info': ind_block.info,
                                                'block_id': block_id}
                else:
                    common_attr_keys = list(set(blocks_dict[block_type]['attr']
                            .keys()).intersection(set(ind_block.attr.keys())))
                    common_info_keys = list(set(blocks_dict[block_type]['info']
                            .keys()).intersection(set(ind_block.info.keys())))
                    updated_attr = {}
                    for ind_attr_key in common_attr_keys:
                        updated_attr[ind_attr_key] = blocks_dict[
                            block_type]['attr'][ind_attr_key]
                    updated_info = {}
                    for ind_info_key in common_info_keys:
                        updated_info[ind_info_key] = blocks_dict[
                            block_type]['info'][ind_info_key]
                    blocks_dict[block_type] = {'attr': updated_attr,
                                                'info': updated_info,
                                                'block_id': block_id}
        return blocks_dict

    def write_config(self, blocks, series_id):
        conf_filename = os.path.join(self.conf_path,
                                     'gse_%s_blockinfo.conf' % series_id)
        cm = ConfigFileManager()
        cm.write(conf_filename, blocks, attr_set=('attr', 'info'))
        return conf_filename

    def process(self):
        gse_blocks_dict = self.read_gsefile()
        series_id = None
        series_id = gse_blocks_dict['SERIES']['block_id']
        if not series_id:
            logging.warning('Parser cannot identify Unique Series ID.')
            sys.exit(1)
        conf_filename = self.write_config(gse_blocks_dict, series_id)
        return series_id, conf_filename

if __name__ == '__main__':
    # GSE - http://www.mathworks.com/help/bioinfo/ref/geoseriesread.html
    logging.info('Initializing GSE Configuration Parser')
    parser = argparse.ArgumentParser(description =
                'Extract relevant features from a GSE file and dumps them in a folder for manual cleanup of fields')
    parser.add_argument('--base_path', dest = 'base_path',
                        help = 'base path for all files')
    parser.add_argument('--gse_file', dest = 'gse_file',
                        help = 'GSE file path')
    args = parser.parse_args()

    if not os.path.isfile(args.gse_file):
        logging.error('GSE input file not found in path %s' % args.gse_file)
        sys.exit(1)

    gp = GSEFileParser()
    gse_config = GSEFileConfig(args.base_path, args.gse_file)
    series_id, conf_filename = gse_config.process()
    logging.info('Processed file ' + args.gse_file + ' (Series: ' + series_id + ') into ' + conf_filename)
    logging.info('Processed all available files')
### ADDRESS AND GET RID OF ALL ### COMMENTS
