#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 12 15:15:49 2020

@authors: 
    Paula Mahler
    Micaela Alexandra Ribeiro Vieira, 13-760-285
    Tim Schluchter
    Karin Thommen

Version: 5

Purpose:
    TO WRITE

Still missing:
    - check if spacy works with de and fr (for some strange reason, spacy works only with en for me)
    - find a way to build nltk for de and fr
    - provide #NE/#Nouns statistics
    - modifile function to build xml files
    - find a way to merge the xml files
    - optimization with classes (if both -a and -l are called, the list of NE is calculated two times --> find way to have single call)
    - ...
"""

#import packages
import argparse
from bs4 import BeautifulSoup
from collections import defaultdict
import json 
from lxml import html, etree
from nltk import tokenize
from nltk import pos_tag, ne_chunk
from nltk.tree import Tree
import os
import requests
import spacy
import stanza
import sys
import threading
import time
from typing import List, Dict


###############################################################################
################################## functions ##################################
###############################################################################
def get_language_of_horizon_url(url_h: str) -> str:
    """Return the language of a horizon webpage"""
    if 'horizons-mag' in url_h:
        return 'en'
    elif 'horizonte-magazin' in url_h:
        return 'de'
    elif 'revue-horizons' in url_h:
        return 'fr'
    
def get_urls_other_two_languages(url_h: str) -> Dict:
    """Return the url of the other two languages"""
    #get path of our url
    html_root = html.fromstring(requests.get(url_h).content)
    #initialise a dictionary
    dict_two_lang = {}
    #depending on the language of url_h, get other two languages
    if get_language_of_horizon_url(url_h) == 'en':
        dict_two_lang['fr'] = html_root.xpath("//link[@rel='alternate' and @hreflang='fr-FR']/@href")[0]
        dict_two_lang['de'] = html_root.xpath("//link[@rel='alternate' and @hreflang='de-DE']/@href")[0]
    elif get_language_of_horizon_url(url_h) == 'de':
        dict_two_lang['fr'] = html_root.xpath("//link[@rel='alternate' and @hreflang='fr-FR']/@href")[0]
        dict_two_lang['en'] = html_root.xpath("//link[@rel='alternate' and @hreflang='en-US']/@href")[0]
    elif get_language_of_horizon_url(url_h) == 'fr':
        dict_two_lang['en'] = html_root.xpath("//link[@rel='alternate' and @hreflang='en-US']/@href")[0]
        dict_two_lang['de'] = html_root.xpath("//link[@rel='alternate' and @hreflang='de-DE']/@href")[0]
    return dict_two_lang


def save_horizon_to_txt(url_h: str):
    """Save main text of a horizon webpage into a txt file"""
    #get content of the page
    res = requests.get(url_h)
    html_page = res.content
    soup = BeautifulSoup(html_page, 'html.parser')
    text = soup.find_all(text = True)
    #initialise file to write the output. The name depends on the language of
    #the input url
    language = get_language_of_horizon_url(url_h)
    output_filename = language + '.txt'
    file = open(output_filename, 'w')
    #define counter for the abstract
    counter_abstract = 0
    #for every line in the page
    for t in text:
        if t.parent.name == 'title':
            file.write('Title: ' + t + '\n')
        if t.parent.name == 'script' and '"author"' in t:
            file.write('Author: ' + (((json.loads(str(t))).get('@graph'))[-1]).get('name') + '\n')
        #if the parent name is 'p' (get only text), the length of the line is 
        #greater than 2 (remove empty lines, and creative commons), the line is 
        #not the caption of an image (captions have |) and the amount of spaces 
        #in >0.5len(line) (to exclude lines not belonging to the main text)
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

def named_entity_stanford_nlp(sent: str, lang: str) -> List:
    """Get list containing (token, token_start, token_end, NE_category) of a 
    sentence by using Stanford nlp"""
    #possible languages: 'en', 'de', 'fr'
    stanza.download(lang, processors = 'tokenize,mwt,ner')
    nlp = stanza.Pipeline(lang, processors = 'tokenize,mwt,ner')
    #load file
    doc = nlp(sent)
    #build the output list
    named_entity_list = []
    for sentence in doc.ents:
        named_entity_list.append((sentence.text, sentence.start_char, 
                                  sentence.end_char, sentence.type))
    return named_entity_list

def named_entity_spacy(sent: str, lang: str) -> List:
    """Get list containing (token, token_start, token_end, NE_category) of a 
    sentence by using spacy"""
    #choose language
    if lang == 'en':
        lang_for_spacy = 'en_core_web_sm'
    elif lang == 'de':
        lang_for_spacy = 'de_core_news_sm'
    elif lang == 'fr':
        lang_for_spacy = 'fr_core_news_md'
    #load file and convert input string
    nlp = spacy.load(lang_for_spacy)
    doc = nlp(sent)
    #build the output list
    named_entity_list = []
    for ent in doc.ents:
        named_entity_list.append((ent.text, ent.start_char, ent.end_char, 
                                  ent.label_))
    return named_entity_list

def named_entity_nltk_chunk(sent: str, lang: str) -> List:
    """Get list containing (token, token_start, token_end, NE_category) of a 
    sentence by using nltk chunks"""
    #choose language
    if lang == 'en':
        lang_for_nltk = 'english'
    #for every words in the sentence, get POS and, if present, NE_category
    words = tokenize.word_tokenize(sent, language = lang_for_nltk)
    words_pos = pos_tag(words)
    words_pos_chunk = ne_chunk(words_pos)
    #build a list containing only tokens with NE_category
    only_NE = [i for i in words_pos_chunk if isinstance(i,Tree)]    
    #initialise a string and a counter -> useful for getting position of tokens
    copy_sent = sent
    index_rem = 0
    #initialise the output list
    named_entity_list = []
    for i in only_NE:
        #get indices and label of token
        start_index = copy_sent.index(i[0][0])+index_rem
        end_index = start_index+len(i[0][0])
        entity_label = i.label()
        #change label for organizations in order to have coherency with the 
        #other two methods
        if entity_label == 'ORGANIZATION':
            entity_label = 'ORG'
        #update copy_sent and index_rem
        copy_sent = sent[end_index:]
        index_rem = end_index
        #update the output list
        named_entity_list.append((i[0][0], start_index, end_index, entity_label))
    return named_entity_list

def save_ne_list_to_txt(lang: str, method: str):
    """
    PURPOSE
        Get NEs from a txt file and, by giving language and method, return a txt
        file containing the NE items with tags in alphabetical order
    PARAMETERS
        lang: language. en, de, fr
        method: method to use. stanford, spacy, nltk, combination (i.e. all 
                three previous methods together)
    """
    #initialise a dictionary
    named_entity_dict = defaultdict(list)
    #open txt file
    with open(lang + '.txt') as file:
        for paragraph in file:
            sentences = tokenize.sent_tokenize(paragraph)
            for sentence in sentences:
                #depending on the method, build a list with NE tags
                if method == 'stanford':
                    ne_list = named_entity_stanford_nlp(sentence, lang)
                elif method == 'spacy':
                    ne_list = named_entity_spacy(sentence, lang)
                elif method == 'nltk':
                    ne_list = named_entity_nltk_chunk(sentence, lang)
                elif method == 'combination':
                    ne_list_1 = named_entity_stanford_nlp(sentence, lang)
                    ne_list_2 = named_entity_spacy(sentence, lang)
                    ne_list_3 = named_entity_nltk_chunk(sentence, lang)
                    ne_list = ne_list_1 + ne_list_2 + ne_list_3
                #add NE tags to the dictionary
                for i in ne_list:
                    if i[0] not in named_entity_dict:
                        named_entity_dict[i[0]] = {i[3]}
                    #if the token is already present, check if NE is the same
                    else:
                        if i[3] in named_entity_dict.get(i[0]):
                            pass
                        #if not, add new NE to the values
                        else:
                            j = named_entity_dict.get(i[0])
                            j.add(i[3])
    #initialise file to write the output
    outfile = open(('ne_list_' + lang + '_' + method + '.txt'), 'w')
    #write to the output the items of the dictionary in alphabetical order
    for key,value in sorted(named_entity_dict.items()):
        value_str = '/'.join(sorted(value))
        outfile.write(key + '\t' + value_str + '\n')
    outfile.close()
    return

def save_annotated_text_to_txt(lang: str, method: str):
    """
    PURPOSE
        Get NEs from a txt file and, by giving language and method, return a txt
        file containing the original text with annotations written just after
        the tokens
    PARAMETERS
        lang: language. en, de, fr
        method: method to use. stanford, spacy, nltk
    """
    #initialise file to write the output
    outfile = open(('annotated_text_' + lang + '_' + method + '.txt'), 'w')
    #open txt file
    with open(lang + '.txt') as file:
        for paragraph in file:
            sentences = tokenize.sent_tokenize(paragraph)
            for sentence in sentences:
                #build lists with the ends of the tokens with NE and the NEs
                #the lists depend on the method chosen
                end_list = [0]
                ne_list = []
                if method == 'stanford':
                    for i in named_entity_stanford_nlp(sentence, lang):
                        end_list.append(i[2])
                        ne_list.append(i[3])
                elif method == 'spacy':
                    for i in named_entity_spacy(sentence, lang):
                        end_list.append(i[2])
                        ne_list.append(i[3])
                elif method == 'nltk':
                    for i in named_entity_nltk_chunk(sentence, lang):
                        end_list.append(i[2])
                        ne_list.append(i[3])
                #build new string
                new_string = ''
                for i in range(len(end_list)-1):
                    new_string += (sentence[end_list[i]:end_list[i+1]]+
                                   '<annotation class="'+ne_list[i]+'">')
                new_string += sentence[end_list[-1]:len(sentence)]
                #add new_string to outfile (for the Abstract line, put an additional newline)
                if new_string.startswith('Abstract'):
                    outfile.write(new_string + '\n\n')
                else:
                    outfile.write(new_string + '\n') 
    outfile.close()
    return

def save_annotated_text_to_xml(lang: str, method: str):
    """
    PURPOSE
        Get NEs from a txt file and, by giving language and method, return a xml
        file containing the original text with annotations written just after
        the tokens
    PARAMETERS
        lang: language. en, de, fr
        method: method to use. stanford, spacy, nltk
    """
    #initialise file to write the output
    outfile = open(('annotated_text_' + lang + '_' + method + '.xml'), 'w')
    #initialise xml
    annotated_doc = etree.Element('Annotated_document')
    #counter for xml
    counter_xml = 0
    main_text = ''
    #open txt file
    with open(lang + '.txt') as file:
        for paragraph in file:
            sentences = tokenize.sent_tokenize(paragraph)
            for sentence in sentences:
                #build lists with the ends of the tokens with NE and the NEs
                #the lists depend on the method chosen
                end_list = [0]
                ne_list = []
                if method == 'stanford':
                    for i in named_entity_stanford_nlp(sentence, lang):
                        end_list.append(i[2])
                        ne_list.append(i[3])
                elif method == 'spacy':
                    for i in named_entity_spacy(sentence, lang):
                        end_list.append(i[2])
                        ne_list.append(i[3])
                elif method == 'nltk':
                    for i in named_entity_nltk_chunk(sentence, lang):
                        end_list.append(i[2])
                        ne_list.append(i[3])
                #build new string
                new_string = ''
                for i in range(len(end_list)-1):
                    new_string += (sentence[end_list[i]:end_list[i+1]]+
                                   '<annotation class="'+ne_list[i]+'">')
                new_string += sentence[end_list[-1]:len(sentence)]
                #print title, author, abstract and main text differently to xml
                if counter_xml == 0:
                    title_text = etree.SubElement(annotated_doc, "Title")
                    title_text.text = new_string[6:]
                    counter_xml += 1
                elif counter_xml == 1:
                    author_text = etree.SubElement(annotated_doc, "Author")
                    author_text.text = new_string[7:]
                    counter_xml += 1
                elif counter_xml == 2:
                    abstract_text = etree.SubElement(annotated_doc, "Abstract")
                    abstract_text.text = new_string[9:]
                    counter_xml += 1      
                else: 
                    main_text += new_string + '\n'
    main_text_xml = etree.SubElement(annotated_doc, "Main_text")
    main_text_xml.text = main_text
    xml_bytes = etree.tostring(annotated_doc, encoding='UTF-8', pretty_print=True, xml_declaration=True)
    xml_str = xml_bytes.decode("utf-8")
    outfile.write(xml_str)
    outfile.close()
    return

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
    parser.add_argument('-l', '--list-ne', type=str, 
                        help='create a txt file with a list of the NE with the\
                        chosen method',
                        choices=['stanford', 'spacy', 'nltk', 'combination'])
    parser.add_argument('-at', '--annotated-txt', type=str, 
                        help='create an annotated txt file  with the chosen method',
                        choices=['stanford', 'spacy', 'nltk'])
    parser.add_argument('-ax', '--annotated-xml', type=str, 
                        help='create an annotated xml file with the chosen method',
                        choices=['stanford', 'spacy', 'nltk'])
           
    def provide_output():
        """Put everything in a function to print nice animation while waiting"""
        args = parser.parse_args()
        #convert args to a dictionary
        args_dict = {arg: value for arg, value in vars(args).items() if value is not None} 
        #initialise parameters for method_list, method_annotation_txt and method_annotation_xml
        method_list = None
        method_annotation_txt = None
        method_annotation_xml = None
        #if list_ne parameter is given, update the parameter with the method
        if 'list_ne' in args_dict:
            method_list = args_dict.pop('list_ne')
        #if annotated_txt is given, update the parameter eith the method
        if 'annotated_txt' in args_dict:
            method_annotation_txt = args_dict.pop('annotated_txt')
        if 'annotated_xml' in args_dict:
            method_annotation_xml = args_dict.pop('annotated_xml')
        #if we choose the url option
        if 'url' in args_dict:
            url = args_dict.pop('url')
            #get language of the provided url and store it in a dictionary
            languages_one_dict = {get_language_of_horizon_url(url) : url}
            #get links of other two languages
            languages_two_dict = get_urls_other_two_languages(url)
            #merge above dictionaries together
            languages_three_dict = {**languages_one_dict, **languages_two_dict}
            #for every language
            for i in languages_three_dict:
                #save main text of the horizon urls in txt files
                save_horizon_to_txt(languages_three_dict.get(i))
                if method_list != None:
                    #return txt files with the list of NEs
                    save_ne_list_to_txt(i, method_list)
                if method_annotation_txt != None:
                    #return txt files with annotated text
                    save_annotated_text_to_txt(i, method_annotation_txt)
                if method_annotation_xml != None:
                    #return xml files with annotated text
                    save_annotated_text_to_xml(i, method_annotation_xml)
        #if we choose the folder option
        elif 'folder' in args_dict:
            #go the the directory specified in folder
            folder = args_dict.pop('folder')
            os.chdir(folder)
            #for all three languages
            for i in ['en', 'de', 'fr']:
                if method_list != None:
                    #return txt files with the list of NEs
                    save_ne_list_to_txt(i, method_list)
                if method_annotation_txt != None:
                    #return txt files with annotated text
                    save_annotated_text_to_txt(i, method_annotation_txt)
                if method_annotation_xml != None:
                    #return xml files with annotated text
                    save_annotated_text_to_xml(i, method_annotation_xml)
        #if we choose the textfile option
        elif 'textfile' in args_dict:
            textfile = args_dict.pop('textfile')
            #initialise counter for folders
            url_nr = 1
            #for every line in the text_file
            for line in textfile:
                url = line.replace('\n', '')
                #get language of the provided url and store it in a dictionary
                languages_one_dict = {get_language_of_horizon_url(url) : url}
                #get links of other two languages
                languages_two_dict = get_urls_other_two_languages(url)
                #merge above dictionaries together
                languages_three_dict = {**languages_one_dict, **languages_two_dict}
                #build new directory and move into it
                os.mkdir('url_nr_'+str(url_nr))
                os.chdir('url_nr_'+str(url_nr))
                #for every language
                for i in languages_three_dict:
                    #save main text of the horizon urls in txt files
                    save_horizon_to_txt(languages_three_dict.get(i))
                    if method_list != None:
                        #return txt files with the list of NEs
                        save_ne_list_to_txt(i, method_list)
                    if method_annotation_txt != None:
                        #return txt files with annotated text
                        save_annotated_text_to_txt(i, method_annotation_txt)
                    if method_annotation_xml != None:
                        #return xml files with annotated text
                        save_annotated_text_to_xml(i, method_annotation_xml)
                #update counter for folders
                url_nr += 1
                os.chdir('..')
        elif 'parent_directory' in args_dict:
            parent_directory = args_dict.pop('parent_directory')
            #initialise list for good paths (i.e. the ones containing only txt files)
            good_paths = []
            #all paths
            all_paths = ([x[0] for x in os.walk(parent_directory)])
            for i in all_paths:
                #content of the paths
                content = os.listdir(i)
                #if there is a directory in the folder, then pass. Otherwise, add to list
                for j in content:
                    if not j.endswith('txt'):
                        pass
                    else:
                        good_paths.append(i)
                        break
            #for every good path
            for i in good_paths:
                #initialise a parameter containing the number of subdirectories of the path
                amount_subdirectories = 1 + i.count('/')
                #go to the directory
                os.chdir(i)
                #for all three languages
                for j in ['en', 'de', 'fr']:
                    if method_list != None:
                        #return txt files with the list of NEs
                        save_ne_list_to_txt(j, method_list)
                    if method_annotation_txt != None:
                        #return txt files with annotated text
                        save_annotated_text_to_txt(j, method_annotation_txt)
                    if method_annotation_xml != None:
                        #return xml files with annotated text
                        save_annotated_text_to_xml(j, method_annotation_xml)
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









