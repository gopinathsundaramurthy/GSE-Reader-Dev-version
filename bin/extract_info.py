import os
import sys
sys.path.append('../lib')
import csv
import glob
import logging
import ipdb
import argparse # for versions < 2.7
                # please get the module from
                # https://code.google.com/p/argparse/
from gse_parser import GSEFileParser, ensure_dir
from config_file_manager import ConfigFileManager

logging.basicConfig(level = logging.DEBUG,
                    format = '%(levelname)s: %(message)s',
                    filemode = 'w')


class ExtractInfo ():
    # Extracts information from GSE files based on
    # Configuration file and deposits it into the
    # output folder
    def __init__(self, base_path, gse_filename):
        self.base_path = base_path
        self.gse_filename = gse_filename

    def parse_data_attr(self, data_list, needed_attr):
        # Parses data blocks for Platform and Sample information
        # and converts them into lists.
        out_data_list = []
        data_attr_names = data_list[0].split('\t')
        needed_list = [data_attr in needed_attr
                       for data_attr in data_attr_names]
        for data_line in data_list:
            part_values = data_line.split('\t')
            if len(part_values)!= len(needed_list):
                # Ill-formed data line, skip
                continue
            selected_attrs = []
            for val, needed in zip(part_values, needed_list):
                if needed:
                    # Retains user selected attributes
                    selected_attrs.append(val)
            out_data_list.append(selected_attrs)
        return out_data_list

    def get_selected_attr(self, attr_dict, needed_attr):
        opt_attr_dict = {}
        for attr, info in attr_dict.iteritems():
            if attr in needed_attr:
                # Retains user selected attributes
                opt_attr_dict[attr] =  info
        return opt_attr_dict

    def write_blocks(self, gse_parser_blocks, config, output_path):
        platform_outputdir = os.path.join(output_path, 'platform')
        ensure_dir(platform_outputdir)
        samples_outputdir = os.path.join(output_path, 'samples')
        ensure_dir(samples_outputdir)

        for block_type, all_blocks in gse_parser_blocks.iteritems():
            if block_type != 'PLATFORM' and block_type != 'SAMPLE':
                continue

            if block_type == 'PLATFORM':
                # Selects output directory based on Block type
                # Samples are deposited into Samples folder
                # Platform Information are deposited in platform folder
                output_dir = platform_outputdir
            else:
                output_dir = samples_outputdir

            for block_id, ind_block in all_blocks.iteritems():
                file_info = open(os.path.join(output_dir,
                                              block_type + '_' + block_id + '.info'),'w+')
                file_data = open(os.path.join(output_dir,
                                              block_type + '_' + block_id + '.data'),'w+')

                # Write out data
                data_writer = csv.writer(file_data, delimiter=',')
                opt_data = self.parse_data_attr(ind_block.data, config['INFO'])
                data_writer.writerows(opt_data)

                # Write out attributes
                selected_attr = self.get_selected_attr(ind_block.attr,
                                                       config['ATTR'])
                for attr, info in selected_attr.iteritems():
                    file_info.write('%s:%s\n' % (attr, info))

                file_data.close()
                file_info.close()

    def process (self):
        # Describes the step necessary for extracting relevant information. 
        gp = GSEFileParser()
        gse_parser_blocks = gp.parse(self.gse_filename)
        series_id = gse_parser_blocks['SERIES'].keys()[0]
        conf_filename = os.path.join(self.base_path, 'conf', 'gse_%s_blockinfo.conf' % series_id)

        cm = ConfigFileManager()
        config = cm.read(conf_filename)

        series_output_path = os.path.join(self.base_path, 'output', series_id)
        ensure_dir(series_output_path)

        self.write_blocks(gse_parser_blocks, config, series_output_path)

        return (series_id, series_output_path)


if __name__ == '__main__':
    # GSE - http://www.mathworks.com/help/bioinfo/ref/geoseriesread.html
    logging.info('Initializing GSE Configuration Parser')
    parser = argparse.ArgumentParser(description = 'Extract relevant features from a GSE file and dumps them in a folder for manual cleanup of fields')
    parser.add_argument('--base_path', dest = 'base_path',
                        help = 'base path for all files')
    parser.add_argument('--gse_file', dest = 'gse_file',
                        help = 'Absolute Configuration filename')
    args = parser.parse_args()

    if not os.path.isfile(args.gse_file):
        logging.error('No input GSE file found.... exiting')
        sys.exit(1)

    ExtractInfo(args.base_path, args.gse_file).process()
    logging.info('Done processing GSE file')
