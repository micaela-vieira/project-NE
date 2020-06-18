#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 12 15:15:49 2020

@authors: 
    Paula Mahler, 17-712-381
    Micaela Alexandra Ribeiro Vieira, 13-760-285
    Tim Schluchter, 16-725-277
    Karin Thommen, 16-580-011
    
Purpose:
    CLI to extract and analyse NEs in Horizon articles
"""


#import packages
import argparse
from bs4 import BeautifulSoup
from collections import defaultdict
import json 
from lxml import html, etree
import matplotlib.pyplot as plt
from nltk import tokenize
import os
import requests
import spacy
import stanza
import sys
import threading
import time
from typing import List, Dict


###############################################################################
################################### classes ###################################
###############################################################################

class horizon_url:
    def __init__(self, url_h: str):
        self.url_h = url_h
        self.language = None
        self.get_language_of_horizon_url()
        self.languages_one_dict = {self.language : self.url_h}
        self.languages_two_dict = {}
        self.get_urls_other_two_languages()
        self.languages_three_dict = {**self.languages_one_dict, 
                                     **self.languages_two_dict}
        
    def get_language_of_horizon_url(self) -> str:
        """Get the language of a horizon webpage"""
        if 'horizons-mag' in self.url_h:
            self.language = 'en'
        elif 'horizonte-magazin' in self.url_h:
            self.language = 'de'
        elif 'revue-horizons' in self.url_h:
            self.language = 'fr'
    
    def get_urls_other_two_languages(self) -> Dict:
        """Every Horizon article is written in three languages: en, de, and fr.
        This function returns the url of the pages of the other two languages"""
        #get path of our url
        html_root = html.fromstring(requests.get(self.url_h).content)
        #depending on the language of url_h, get other two languages
        if self.language == 'en':
            self.languages_two_dict['fr'] = html_root.xpath("//link[@rel='alternate' and @hreflang='fr-FR']/@href")[0]
            self.languages_two_dict['de'] = html_root.xpath("//link[@rel='alternate' and @hreflang='de-DE']/@href")[0]
        elif self.language == 'de':
            self.languages_two_dict['fr'] = html_root.xpath("//link[@rel='alternate' and @hreflang='fr-FR']/@href")[0]
            self.languages_two_dict['en'] = html_root.xpath("//link[@rel='alternate' and @hreflang='en-US']/@href")[0]
        elif self.language == 'fr':
            self.languages_two_dict['en'] = html_root.xpath("//link[@rel='alternate' and @hreflang='en-US']/@href")[0]
            self.languages_two_dict['de'] = html_root.xpath("//link[@rel='alternate' and @hreflang='de-DE']/@href")[0]

    def save_horizon_to_txt(self):
        """Save main text of the three (one for each language) horizon webpages 
        into txt files"""
        #for every language
        for i in self.languages_three_dict:
            #get content of the page
            res = requests.get(self.languages_three_dict.get(i))
            html_page = res.content
            soup = BeautifulSoup(html_page, 'html.parser')
            text = soup.find_all(text = True)
            #initialise file to write the output. The name depends on the 
            #language of the input url
            output_filename = i + '.txt'
            file = open(output_filename, 'w')
            #define counter for the abstract
            counter_abstract = 0
            #for every line in the page
            for t in text:
                if t.parent.name == 'title':
                    file.write('Title: ' + t + '\n')
                if t.parent.name == 'script' and '"author"' in t:
                    file.write('Author: ' + 
                               (((json.loads(str(t))).get('@graph'))[-1]).get('name') + '\n')
                #if the parent name is 'p' (get only text), the length of the 
                #line is greater than 2 (remove empty lines, and creative 
                #commons), the line is not the caption of an image (captions 
                #have |) and the amount of spaces in >0.5len(line) (to exclude 
                #lines not belonging to the main text)
                if (t.parent.name == 'p' and len(t)>2 and '| ' not in t
                    and not sum(c.isspace() for c in t) > 0.5*len(t)):
                    #write line to txt file
                    if counter_abstract == 0:
                        file.write('Abstract: ' + t + '\n\n')
                        counter_abstract +=1
                    else:
                        file.write(t+'\n')
            file.close()
        return


class named_entity_methods_sentence:
    def __init__(self, sent: str, lang: str):
        self.sent = sent
        self.lang = lang
        self.named_entity_list = []
        self.amount_nouns_and_num = 0

    def named_entity_list_stanford_nlp(self) -> List:
        """Get list containing (token, token_start, token_end, NE_category) of a 
        sentence by using Stanford nlp. Possible languages: 'en', 'de', 'fr'"""
        stanza.download(self.lang, processors = 'tokenize,mwt,ner')
        #load file and convert input string
        nlp = stanza.Pipeline(self.lang, processors = 'tokenize,mwt,ner')
        doc = nlp(self.sent)
        #build the output list
        for sentence in doc.ents:
            #avoid that 'Abstract', 'Title' and 'Author' are counted between NEs
            if sentence.text != 'Abstract' and sentence.text != 'Title' and sentence.text != 'Author':
                self.named_entity_list.append((sentence.text, 
                                               sentence.start_char, 
                                               sentence.end_char, sentence.type))
        return self.named_entity_list
    
    def amount_nouns_and_numerals_stanford_nlp(self) -> int:
        """Get amount of nouns and numerals in a sentece by using Stanford nlp.
        Note: for en, we include numerals since it is the POS of NEs like time, 
        date or percent"""
        stanza.download(self.lang, processors = 'tokenize,mwt,pos')
        nlp = stanza.Pipeline(self.lang, processors = 'tokenize,mwt,pos')
        doc = nlp(self.sent)
        for sentence in doc.sentences:
            for word in sentence.words:
                #if the part of speech is a noun, a proper noun or a numeral 
                #(only for en) 
                if self.lang == 'en':
                    if word.upos == 'NOUN' or word.upos == 'PROPN' or word.upos == 'NUM':
                        self.amount_nouns_and_num += 1
                elif self.lang == 'de' or self.lang == 'fr':
                    if word.upos == 'NOUN' or word.upos == 'PROPN':
                        self.amount_nouns_and_num += 1
        return self.amount_nouns_and_num
    
    def named_entity_list_spacy(self) -> List:
        """Get list containing (token, token_start, token_end, NE_category) of a 
        sentence by using spacy"""
        #choose language
        if self.lang == 'en':
            lang_for_spacy = 'en_core_web_sm'
        elif self.lang == 'de':
            lang_for_spacy = 'de_core_news_sm'
        elif self.lang == 'fr':
            lang_for_spacy = 'fr_core_news_md'
        #load file and convert input string
        nlp = spacy.load(lang_for_spacy)
        doc = nlp(self.sent)
        #build the output list
        for ent in doc.ents:
            #avoid that 'Abstract', 'Title' and 'Author' are counted between NEs
            if ent.text != 'Abstract' and ent.text != 'Title' and ent.text != 'Author':
                self.named_entity_list.append((ent.text, ent.start_char, 
                                               ent.end_char, ent.label_))
        return self.named_entity_list

    def amount_nouns_and_numerals_spacy(self) -> int:
        """Get amount of nouns and numerals in a sentece by using spacy.
        Note: for en, we include numerals since it is the POS of NEs like time, 
        date or percent"""
        #choose language
        if self.lang == 'en':
            lang_for_spacy = 'en_core_web_sm'
        elif self.lang == 'de':
            lang_for_spacy = 'de_core_news_sm'
        elif self.lang == 'fr':
            lang_for_spacy = 'fr_core_news_md'
        nlp = spacy.load(lang_for_spacy)
        doc = nlp(self.sent)
        for word in doc:
            #if the part of speech is a noun, a proper noun or a numeral 
            #(only for en) 
            if self.lang == 'en':
                if word.pos_ == 'NOUN' or word.pos_ == 'PROPN' or word.pos_ == 'NUM':
                    self.amount_nouns_and_num += 1
            elif self.lang == 'de' or self.lang == 'fr':
                if word.pos_ == 'NOUN' or word.pos_ == 'PROPN':
                    self.amount_nouns_and_num += 1
        return self.amount_nouns_and_num


class named_entity_methods_text:
    def __init__(self, lang: str, method: str):
        self.lang = lang
        self.method = method
        self.named_entity_list_total = []
        self.amount_nouns_and_num_total = 0
        #call full_ne_list_and_pos_amount
        self.full_ne_list_and_pos_amount()
        
    def full_ne_list_and_pos_amount(self):
        """Extract and save into a list all NEs of a text and store in a
        variable the total amount of nouns and literals"""
        #open file
        with open(self.lang + '.txt') as file:
            for paragraph in file:
                sentences = tokenize.sent_tokenize(paragraph)
                for sentence in sentences:
                    #instance of the named_entity_methods_sentence class
                    inst = named_entity_methods_sentence(sentence, self.lang)
                    #save into a list all NEs of the text and update the total
                    #number of nouns and numerals
                    if self.method == 'stanford':
                        self.named_entity_list_total.append(inst.named_entity_list_stanford_nlp())
                        self.amount_nouns_and_num_total += inst.amount_nouns_and_numerals_stanford_nlp()
                    elif self.method == 'spacy':
                        self.named_entity_list_total.append(inst.named_entity_list_spacy())
                        self.amount_nouns_and_num_total += inst.amount_nouns_and_numerals_spacy()
        return
    
    def save_all_ne_as_list_to_txt(self):
        """Save a list of all NEs, in order of appearance and together with the
        NE tag, into a txt file"""
        #write the output
        outfile = open(('ne_list_all_' + self.lang + '_' + self.method +
                        '.txt'), 'w')
        for sublist in self.named_entity_list_total:
            for entry in sublist:
                outfile.write(entry[0]+'\t'+entry[3]+'\n')
        outfile.close()

    def save_different_ne_as_list_to_txt(self):
        """Save a list of different NEs, alphabetically and together with the 
        (possible several) NE tags, into a txt file"""        
        #initialise a dictionary
        different_ne_dict = defaultdict(list)
        #update dictionary
        for sublist in self.named_entity_list_total:
            for entry in sublist:
                if entry[0] not in different_ne_dict:
                        different_ne_dict[entry[0]] = {entry[3]}
                #if the token is already present, check if NE is the same
                else:
                    if entry[3] in different_ne_dict.get(entry[0]):
                            pass
                    #if not, add new NE to the values
                    else:
                        new_list_of_ne = different_ne_dict.get(entry[0])
                        new_list_of_ne.add(entry[3])
        #write the output
        outfile = open(('ne_list_different_' + self.lang + '_' + self.method +
                        '.txt'), 'w')
        for key,value in sorted(different_ne_dict.items()):
            value_str = '/'.join(sorted(value))
            outfile.write(key + '\t' + value_str + '\n')
        outfile.close()  
        return
    
    def save_percentages_to_txt(self):
        """Save NEs percentages into a txt file and build a plot of them"""
        #initialise a dictionary with the list of NEs taken from 
        #https://spacy.io/api/annotation
        if self.lang == 'en':
            named_entity_divided_per_type = {'PERSON':0, 'NORP':0, 'FAC':0, 
                                             'ORG':0, 'GPE':0, 'LOC':0, 
                                             'PRODUCT':0, 'EVENT':0, 
                                             'WORK_OF_ART':0, 'LAW':0, 
                                             'LANGUAGE':0, 'DATE':0, 'TIME':0, 
                                             'PERCENT':0, 'MONEY':0, 
                                             'QUANTITY':0, 'ORDINAL':0, 
                                             'CARDINAL':0}
        if self.lang == 'de' or self.lang == 'fr':
            named_entity_divided_per_type = {'PER':0, 'ORG':0, 'LOC':0, 
                                             'MISC':0}
        #define counter for total amount of NE
        amount_ne_total = 0
        #update the dictionary depending on the type of NE and update the 
        #counter
        for sublist in self.named_entity_list_total:
            for entry in sublist:
                old_amount = (named_entity_divided_per_type.get(entry[3]))
                named_entity_divided_per_type[entry[3]] = old_amount + 1
                amount_ne_total += 1
        #get percentages of the various NE types over the amount of nouns and 
        #numerals
        percentages = {}
        for i in named_entity_divided_per_type:
            percentages[i] = round(100*named_entity_divided_per_type.get(i)/self.amount_nouns_and_num_total,1)
        #write the output
        outfile = open(('percentages_' + self.lang + '_' + self.method + 
                        '.txt'), 'w')
        outfile.write('Method used: ' + self.method + '\n')
        outfile.write('----------------------------------------------\n')
        outfile.write('Amount NEs: '+ str(amount_ne_total) + '\n')
        outfile.write('Amount nouns and numerals: '+ 
                      str(self.amount_nouns_and_num_total) + '\n')
        outfile.write('----------------------------------------------\n')
        outfile.write('Percentages:\n')
        for i in percentages:
            outfile.write(i+'\t'+str(percentages.get(i)) + '%\n')
        outfile.close()
        #build the plot
        if self.lang == 'en':
            plt.figure(figsize=(12,6))
            plt.ylabel('#NE / #(NOUN,PROPN,NUM) [%]', fontsize=14)
        elif self.lang == 'de' or self.lang == 'fr':
            plt.figure(figsize=(2.5,6))
            plt.ylabel('#NE / #(NOUN,PROPN) [%]', fontsize=14)
        plt.bar(range(len(percentages)), list(percentages.values()), 
                align='center')
        plt.xticks(range(len(percentages)), list(percentages.keys()), 
                   fontsize=14, rotation='vertical')
        plt.title('Method: '+self.method+'\nLanguage: '+self.lang, fontsize=20)
        plt.savefig('percentages_'+self.lang+'_'+self.method, 
                    bbox_inches='tight')
        return

    def save_annotated_text_to_txt(self):
        """Save txt file, where NE types are written after the corresponding 
        tokens"""
        #initialise file to write the output
        outfile = open(('annotated_text_' + self.lang + '_' + self.method +
                        '.txt'), 'w')
        #counter for the sentences
        counter_sentence = 0
        #counter for the paragrafhs
        counter_paragraph = 0
        #open txt file
        with open(self.lang + '.txt') as file:
            for paragraph in file:
                sentences = tokenize.sent_tokenize(paragraph)
                for sentence in sentences:
                    #build lists with the ends of the tokens with NE and the NEs
                    end_list = [0]
                    end_list += [i[2] for i in 
                                 self.named_entity_list_total[counter_sentence]]
                    ne_list = [i[3] for i in 
                               self.named_entity_list_total[counter_sentence]]
                    counter_sentence += 1
                    #build new string
                    new_string = ''
                    for i in range(len(end_list)-1):
                        new_string += (sentence[end_list[i]:end_list[i+1]]+
                                       '<annotation class="'+ne_list[i]+'">')
                    new_string += sentence[end_list[-1]:len(sentence)]
                    #add new_string to outfile
                    outfile.write(new_string + '\n')
                #add additional space after abstract
                if counter_paragraph == 2:
                    outfile.write('\n') 
                counter_paragraph += 1
        outfile.close()
        return

    def save_annotated_text_to_xml(self):
        """Save xml file, where NE types are written after the corresponding 
        tokens"""
        #initialise file to write the output
        outfile = open(('annotated_text_' + self.lang + '_' + 
                        self.method + '.xml'), 'w')
        #initialise xml
        annotated_doc = etree.Element('Annotated_document')
        main_text = ''
        #counter for the sentences
        counter_sentence = 0
        #counter for the paragraphs
        counter_paragraph = 0
        #open txt file
        with open(self.lang + '.txt') as file:
            for paragraph in file:
                paragraph_string = ''
                sentences = tokenize.sent_tokenize(paragraph)
                for sentence in sentences:
                    #build lists with the ends of the tokens with NE and the NEs
                    end_list = [0]
                    end_list += [i[2] for i in 
                                 self.named_entity_list_total[counter_sentence]]
                    ne_list = [i[3] for i in 
                               self.named_entity_list_total[counter_sentence]]
                    counter_sentence += 1
                    #build new string
                    new_string = ''
                    for i in range(len(end_list)-1):
                        new_string += (sentence[end_list[i]:end_list[i+1]]+
                                       '<annotation class="'+ne_list[i]+'"/>')
                    new_string += sentence[end_list[-1]:len(sentence)]
                    paragraph_string += new_string+'\n'
                #print title, author, abstract and main text differently to xml
                if counter_paragraph == 0:
                    title_text = etree.SubElement(annotated_doc, "Title")
                    #add text to the node
                    init_text = "<text>{0}</text>".format(paragraph_string[6:])
                    fin_text = etree.fromstring(init_text)
                    title_text.append(fin_text)
                elif counter_paragraph == 1:
                    author_text = etree.SubElement(annotated_doc, "Author")
                    #add text to the node
                    init_text = "<text>{0}</text>".format(paragraph_string[7:])
                    fin_text = etree.fromstring(init_text)
                    author_text.append(fin_text)
                elif counter_paragraph == 2:
                    abstract_text = etree.SubElement(annotated_doc, "Abstract")
                    #add text to the node
                    init_text = "<text>{0}</text>".format(paragraph_string[9:])
                    fin_text = etree.fromstring(init_text)
                    abstract_text.append(fin_text)
                else: 
                    main_text += paragraph_string
                counter_paragraph += 1
        main_text_xml = etree.SubElement(annotated_doc, "Main_text")
        #add text to the node
        init_text = "<text>{0}</text>".format(main_text)
        fin_text = etree.fromstring(init_text)
        main_text_xml.append(fin_text)
        #convert and write to outfile
        xml_bytes = etree.tostring(annotated_doc, encoding='UTF-8', 
                                   pretty_print=True, xml_declaration=True)
        xml_str = xml_bytes.decode("utf-8")
        outfile.write(xml_str)
        outfile.close()
        return





###############################################################################
############################# animation functions #############################
###############################################################################

def waiting_animation():
    """Animation to show while waiting the output"""
    animation = ["[■□□□□□□□□□]","[■■□□□□□□□□]", "[■■■□□□□□□□]", "[■■■■□□□□□□]", 
                 "[■■■■■□□□□□]", "[■■■■■■□□□□]", "[■■■■■■■□□□]", "[■■■■■■■■□□]", 
                 "[■■■■■■■■■□]", "[■■■■■■■■■■]", "[□■■■■■■■■■]", "[□□■■■■■■■■]",
                 "[□□□■■■■■■■]", "[□□□□■■■■■■]", "[□□□□□■■■■■]", "[□□□□□□■■■■]",
                 "[□□□□□□□■■■]", "[□□□□□□□□■■]", "[□□□□□□□□□■]", "[□□□□□□□□□□]"
                 ]
    for i in range(len(animation)):
        time.sleep(0.2)
        sys.stdout.write("\r" + animation[i % len(animation)])
        sys.stdout.flush()

def loadingAnimation(process):
    """Display the animation while the process is still alive"""
    while process.isAlive():
        waiting_animation()





###############################################################################
################################ main function ################################
###############################################################################

def main():
    #define parser arguments
    parser = argparse.ArgumentParser(
        description='named entity recognition of Horizon webpage')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-u', '--url', type=str, help='url of the Horizon webpage')
    group.add_argument('-f', '--folder', type=str, help='folder where the Horizon files are stored')
    group.add_argument('-t', '--textfile', type=argparse.FileType(encoding='utf-8'), help='txt file containing one Horizon url per line')
    group.add_argument('-p', '--parent_directory', type=str, help='parent directory containing subfolder with Horizon files')
    parser.add_argument('-m', '--method', type=str, 
                        help='method to use in the process (default: spacy)',
                        choices=['stanford', 'spacy'],
                        default = 'spacy')
    parser.add_argument('-la', '--list-all', help='create a txt file with a list\
                        of all NEs with the chosen method', action='store_const', const=True)
    parser.add_argument('-ld', '--list-different', help='create a txt file with a list of different NEs with the\
                        chosen method', action='store_const', const=True)
    parser.add_argument('-pc', '--percentage', help='create a txt file with the percentages of NEs with the\
                        chosen method and build corresponding plots', action='store_const', const=True)
    parser.add_argument('-at', '--annotated-txt', help='create an annotated txt file with the chosen method', action='store_const', const=True)
    parser.add_argument('-ax', '--annotated-xml', help='(create an annotated xml file with the chosen method)', action='store_const', const=True)
    
    def provide_output():
        """Put everything in a function to print nice animation while waiting"""
        args = parser.parse_args()
        #convert args to a dictionary
        args_dict = {arg: value for arg, value in vars(args).items() if value 
                     is not None} 
        #store method into a variable
        method = args_dict.pop('method')
        def perform_operation():
            """Function to perform all operations requested by the user"""
            for k in ['en', 'de', 'fr']:
                inst = named_entity_methods_text(k, method)
                if 'list_all' in args_dict:
                    inst.save_all_ne_as_list_to_txt()
                if 'list_different' in args_dict:
                    inst.save_different_ne_as_list_to_txt()
                if 'percentage' in args_dict:
                    inst.save_percentages_to_txt()
                if 'annotated_txt' in args_dict:
                    inst.save_annotated_text_to_txt()
                if 'annotated_xml' in args_dict:
                    inst.save_annotated_text_to_xml()
            return
        #if we choose the url option
        if 'url' in args_dict:
            url = args_dict.pop('url')
            url = horizon_url(url)
            #save horizon pages into txt
            url.save_horizon_to_txt()
            #perform operations depending on the user input
            perform_operation()
        #if we choose the folder option
        elif 'folder' in args_dict:
            folder = args_dict.pop('folder')
            os.chdir(folder)
            #perform operations depending on the user input
            perform_operation()
        #if we choose the textfile option
        elif 'textfile' in args_dict:
            textfile = args_dict.pop('textfile')
            #initialise counter for folders
            url_nr = 1
            #for every line in the text_file
            for line in textfile:
                #build new directory and move into it
                os.mkdir('url_nr_'+str(url_nr))
                os.chdir('url_nr_'+str(url_nr))
                url = line.replace('\n', '')
                url = horizon_url(url)
                #save horizon pages into txt
                url.save_horizon_to_txt()
                #perform operations depending on the user input
                perform_operation()
                #update counter for folders
                url_nr += 1
                os.chdir('..')
        elif 'parent_directory' in args_dict:
            parent_directory = args_dict.pop('parent_directory')
            #initialise list for good paths (i.e. the ones containing only txt 
            #files)
            good_paths = []
            #all paths
            all_paths = ([x[0] for x in os.walk(parent_directory)])
            for i in all_paths:
                #content of the paths
                content = os.listdir(i)
                #if there is a directory in the folder, then pass. Otherwise, 
                #add to list
                for j in content:
                    if not j.endswith('txt'):
                        pass
                    else:
                        good_paths.append(i)
                        break
            #for every good path
            for i in good_paths:
                #initialise a parameter containing the number of subdirectories 
                #of the path
                amount_subdirectories = 1 + i.count('/')
                #go to the directory
                os.chdir(i)
                #perform operations depending on the user input
                perform_operation()
                #come back to the parent directory
                while amount_subdirectories > 0:
                    os.chdir('..')
                    amount_subdirectories -= 1
        #if no one among url, folder, textfile or parent_directory is provided, 
        #return an error and exit
        else: 
            raise TypeError('Either -u, -f, -t, or -p must be specified')
            exit(1)
           
    #provide animation while waiting
    loading_process = threading.Thread(target=provide_output)
    loading_process.start()
    loadingAnimation(loading_process)
    loading_process.join()


if __name__ == '__main__':
    main()