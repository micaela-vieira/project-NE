#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 24 16:21:59 2020
"""

import os


def combine_files(directory: str, extension: str, language: str, method: str):
    """function to merge initial txt files, annotated txt files and annotated
    xml files"""
    #find all files corresponding to the criteria and save the path into a list
    paths = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if method != '':
                if file.endswith(language + '_' + method + '.' + extension):
                    paths.append(os.path.join(root, file))
            else: 
                if file.endswith(language + '.' + extension):
                    paths.append(os.path.join(root, file))
    #merge txt
    if extension == 'txt':
        if method == '':
            outfile_name = 'merge_' + language + '.txt'
        else: 
            outfile_name = 'merge_annotation' + language + '_' + method + '.txt'
        with open(outfile_name, 'w') as outfile:
            for file in paths:
                with open(file) as infile:
                    for line in infile:
                        outfile.write(line)
                    outfile.write('\n\n--------------------------------------------------------------------------\n\n\n')
    #merge xml
    elif extension == 'xml':
        """TO WRITE"""
        
    return 

combine_files('prova', 'xml', 'en', 'stanford')
#combine_files('prova', 'txt', 'en', '')
#combine_files('prova', 'txt', 'en', 'stanford')