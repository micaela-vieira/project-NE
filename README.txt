AUTHORS:
Paula Mahler
Micaela Alexandra Ribeiro Vieira, 13-760-285
Tim Schluchter, 16-725-277
Karin Thommen



NOTE:
Feel free to change what you want!

PURPOSE:
Command line interface to get NEs from Horizon texts

STILL MISSING:
Check if spacy works with de and fr (for some strange reason, spacy works only with en for Micaela)

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
-m spacy		<-- use spacy
3)
We have to choose the processes we want to execute (multiple processes are allowed):
-la			<-- write in a txt file the pairs (token-NE) for all NEs found in the text. In the txt file we will have one pair per line, in order of appearance
-ld			<-- write in a txt file the pairs (token-NE) for all different NEs found in the text. In the txt file we will have one pair per line, in alphabetical order. Note that it is possible that a single token is assigned to multiple NE tags; if this is the case, all of them will be listed
-pc			<-- write in a txt file the various percentages of NE tags with respect to the total amount of nouns and literals of the text
-at			<-- build a txt file where the tokens are annotated with NEs
-ax			<-- build a xml file where the tokens are annotated with NEs

EXAMPLES:
These are possible examples of commands to execute:
<<<<<<< HEAD
1)	python project_NE.py -u https://www.horizons-mag.ch/2020/03/05/the-sea-of-faith-in-an-ocean-of-science/ -m stanford -ld
2)	python project_NE.py -f Horizons_projectfiles/text-files/issue_113/article_a35/ -m stanford -la -ld -pc -at -ax
3)	python project_NE.py -t url_list.txt -m stanford -ax -la
4)	python project_NE.py -p Horizons_projectfiles/text-files/issue_115 -m stanford -la -ld -pc -at -ax
Examples 2) and 4) are the ones that have been used to produce the output in the folders article_a35 and issue 115
=======
python project_NE.py -u https://www.horizons-mag.ch/2020/03/05/the-sea-of-faith-in-an-ocean-of-science/ -at stanford
python project_NE.py -f Horizons_projectfiles/text-files/issue_109/article_a1/ -ax stanford -l stanford
python project_NE.py -t url_list.txt -l stanford -ax stanford
python project_NE.py -p Horizons_projectfiles/text-files/ -l stanford



Still missing:
- check if spacy works with de and fr (for some strange reason, spacy works only with en for Micaela)
- find a way to build nltk for de and fr
- provide #NE/#Nouns statistics
- modifile function to build xml files
- find a way to merge the single xml files (see project-NE-combine.py)
- optimization with classes (if both -a and -l are called, the list of NE is calculated two times --> find way to have single call)
- ...
>>>>>>> ed0717c617c9b62f80692035f61f1a30a6431502
