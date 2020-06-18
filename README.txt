AUTHORS:
Paula Mahler, 17-712-381
Micaela Alexandra Ribeiro Vieira, 13-760-285
Tim Schluchter, 16-725-277
Karin Thommen, 16-580-011



PURPOSE:
Command line interface to get NEs from Horizon webpages/texts


HELP:
For help, type python project_NE.py -h

USAGE:
1)
First of all, we have to choose the input for the program. We have four possible inputs:
	-u URL		<-- a single url from a Horizon webpage. Note that this will also build txt files containing the texts scraped from the web
	-f FOLDER	<-- a single folder containing ONLY three txt files, one for every language of the Horizon article
	-t TEXTFILE	<-- a txt file containing several Horizon-urls, one for every line. This allows to grasp multiply urls at the same time. Note that this will also build txt files containing the texts scraped from the web
	-p PARENT_DIR	<-- a parent directory containing several subdirectories having the three txt file, one for every language
2)
Secondly, we have to choose the method to use to get the NEs. We have two possibilities:
-m stanford		<-- use Stanford nlp
-m spacy		<-- use spaCy
3)
We have to choose the processes we want to execute (multiple processes are allowed):
-la			<-- write in a txt file the pairs (token-NE) for all NEs found in the text. In the txt file we will have one pair per line, in order of appearance
-ld			<-- write in a txt file the pairs (token-NE) for all different NEs found in the text. In the txt file we will have one pair per line, in alphabetical order. Note that it is possible that a single token is assigned to multiple NE tags; if this is the case, all of them will be listed
-pc			<-- write in a txt file and build bar plots of the various percentages of NE tags with respect to the total amount of nouns and literals (only for EN) of the text
-at			<-- build a txt file where the tokens are annotated with NEs
-ax			<-- build a xml file where the tokens are annotated with NEs

EXAMPLES:
These are possible examples of commands to execute:
1)	python project_NE.py -u https://www.horizons-mag.ch/2020/03/05/the-sea-of-faith-in-an-ocean-of-science/ -m stanford -ld
2)	python project_NE.py -f Horizons_projectfiles/text-files/issue_113/article_a35/ -m stanford -la -ld -pc -at -ax
3)	python project_NE.py -t url_list.txt -m stanford -ax -la
4)	python project_NE.py -p Horizons_projectfiles/text-files/issue_115 -m stanford -la -ld -pc -at -ax
Examples 2) and 4) are the ones that have been used to produce the output in the folders article_a35 and issue 115