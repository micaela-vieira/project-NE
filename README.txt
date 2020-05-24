Authors:
Paula Mahler
Micaela Alexandra Ribeiro Vieira, 13-760-285
Tim Schluchter
Karin Thommen



Purpose:
Command line interface to get NEs from Horizon texts



Usage:
1)
First of all, we have to choose the input for the program. We have four possible inputs:
	-u URL		<-- a single url from a Horizon webpage. Note that this will also build txt files containing the texts scraped from the web
	-f FOLDER	<-- a single folder containing ONLY three txt files, one for every language of the Horizon article
	-t TEXTFILE	<-- a txt file containing several Horizon-urls, one for every line. This allows to grasp multiply urls at the same time. Note that this will also build txt files containing the texts scraped from the web
	-p PARENT_DIR	<-- a parent directory containing several subdirectories having the three txt file, one for every language
2)
Then, we have to choose the process we want to execute:
	-at METHOD	<-- build a txt file where the tokens are annotated with NEs. Method can be spacy, nltk, or stanford
	-ax METHOD	<-- build a xml file where the tokens are annotated with NEs. Method can be spacy, nltk, or stanford
	-l METHOD	<-- build a list containing the different NEs in alphabetical order. Method can be spacy, nltk, stanford or combination (i.e. all three methods together)



Examples:
These are possible examples of commands to execute:
python project_NE.py -u https://www.horizons-mag.ch/2020/03/05/the-sea-of-faith-in-an-ocean-of-science/ -at stanford
python project_NE.py -f Horizons_projectfiles/text-files/issue_109/article_a1/ -ax stanford -l stanford
python project_NE.py -t url_list.txt -l stanford -ax stanford
python project_NE.py -p Horizons_projectfiles/text-files/ -l stanford



Still missing:
- check if spacy works with de and fr (for some strange reason, spacy works only with en for me)
- find a way to build nltk for de and fr
- provide #NE/#Nouns statistics
- modifile function to build xml files
- find a way to merge the single xml files (see project-NE-combine.py)
- optimization with classes (if both -a and -l are called, the list of NE is calculated two times --> find way to have single call)
- ...
