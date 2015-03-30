#################################################################################
#                        GSE PARSER MODULES                                     #                                                          #   written by Gopinath Sundaramurthy                                           #
#   Date: Jan 11, 2015                                                          #
#                                                                               #
################################################################################# 

GSE Parser modules is part of my larger expression analysis platform. It parses through expression data to identify and extract relevant 

information. The GSE module was designed specifically extract information from Gene Expression Omnibus's GSE files stored in 'SOFT' 

format. Some of the information extracted from these files are listed below.  
1) Sample Information
2) Sample Expression values
3) Platforms used
4) Probe Information
5) Series Information
6) Experimental Information
These information are subsequently used by other modules in the expression analysis platform  
The code has been modified to ensure it can be run independently.

Python Package Requirements:
-None

Input :
-GEO GSE SOFT files

Output:

Configuration (Conf) Folder
  |
  ---- GSE Specific Configuration file (Editable): The configuration file can be edited by adding '#' before attributes that are not 

required to be extracted.  

Output Folder
  |
  |
  ---- Samples - (.data) Sample Expression Values   
  |            - (.info) Sample Information
  |
  |
  ---- Platform - (.info) Platform Information
                - (.data) Platform probe Information 

Files:
- config_dump.py: Reads GSE soft file to create configaration file in the 'conf' directory. This file can be edited if needed before the next step.  
  usage: python config_dump.py --base_path "path" --gse_file "GSE File path"
  example:  python config_dump.py --base_path=../ --gse_file=../data/GSE30070_family.soft
 
- extract_info.py: Reads the GSE soft file and the configaration file to create output directories which are used by subsequent modules. 
  usage: python extract_info.py --base_path "path" --gse_file "GSE File path"
  