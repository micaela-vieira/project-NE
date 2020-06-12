import en_core_web_sm
import fr_core_news_sm
import de_core_news_sm
import os

class Tagger:
    def __init__(self):
        #variables for english
        self._total_noun_en = 0

        self._GPE_spacy_en = 0
        self._ORG_spacy_en = 0
        self._PERS_spacy_en = 0

        self._GPE_stanford_en = 0
        self._ORG_stanford_en = 0
        self._PERS_stanford_en = 0

        self._NE_spacy_en = 0
        self._NE_stanford_en = 0

        #variables for french
        self._total_noun_fr = 0

        self._GPE_spacy_fr = 0
        self._ORG_spacy_fr = 0
        self._PERS_spacy_fr = 0

        self._GPE_stanford_fr = 0
        self._ORG_stanford_fr = 0
        self._PERS_stanford_fr = 0

        self._NE_spacy_fr = 0
        self._NE_stanford_fr = 0

        #variables for german
        self._total_noun_de = 0

        self._GPE_spacy_de = 0
        self._ORG_spacy_de = 0
        self._PERS_spacy_de = 0

        self._GPE_stanford_de = 0
        self._ORG_stanford_de = 0
        self._PERS_stanford_de = 0

        self._NE_spacy_de = 0
        self._NE_stanford_de = 0


        # go through all folders and files with the articles we like to analyze.
        root = '/Users/Karin/Desktop/Project_NE'
        os.chdir(root)

        for issue in range(109, 113):
            os.chdir('{}/issue_{}'.format(root,issue))

            for article in os.listdir(os.getcwd()):

                if article == '.DS_Store':
                    continue

                else:
                    print(os.getcwd())
                    os.chdir('{}/{}'.format(os.getcwd(), article))
                    path = os.getcwd()

                    self._en_text = path+'/en.txt'
                    self._ne_list_en_spacy = path+'/ne_list_all_en_spacy.txt'
                    self._ne_list_en_stanford = path+'/ne_list_all_en_stanford.txt'

                    self._fr_text = path+'/fr.txt'
                    self._ne_list_fr_spacy = path + '/ne_list_all_fr_spacy.txt'
                    self._ne_list_fr_stanford = path + '/ne_list_all_fr_stanford.txt'

                    self._de_text = path+'/de.txt'
                    self._ne_list_de_spacy = path + '/ne_list_all_de_spacy.txt'
                    self._ne_list_de_stanford = path + '/ne_list_all_de_stanford.txt'



                    self.get_results(issue, article)

                    os.chdir('issue_{}'.format(issue))

    def get_results(self, issue, article):

        os.chdir('/Users/Karin/Desktop/Project_NE')

        #get English results: Words and nouns
        self._en = self.get_nouns(self._en_text, 'en', issue, article)
        self._en_nouns = self._en[0] #number of nouns
        self._total_noun_en += self._en_nouns
        self._en_words = self._en[1] #number of words

        with open('evaluation_english.txt', 'a+') as eval:
            # write English results
            eval.write('\n\n____________________________________')
            eval.write('\nEvaluation of the English issue_{}, {}:\n'.format(issue, article))
            eval.write('Number of nouns (en): {}'.format(self._en_nouns))
        self.analyze(self._ne_list_en_spacy ,'english', 'spacy') # results of spacy

        self.analyze(self._ne_list_en_stanford, 'english', 'stanford') # write English Stanford Results



        #get French results: Words and nouns
        self._fr = self.get_nouns(self._fr_text, 'fr', issue, article)
        self._fr_nouns = self._fr[0] #number of nouns
        self._fr_words = self._fr[1] #number of words
        self._total_noun_fr += self._fr_nouns


        with open('evaluation_french.txt', 'a+') as eval:
            # write French results
            eval.write('\n\n____________________________________')
            eval.write('\nEvaluation of the French issue_{}, {}:\n'.format(issue, article))
            eval.write('Number of nouns (fr): {}'.format(self._fr_nouns))
        self.analyze(self._ne_list_fr_spacy ,'french', 'spacy') # results of spacy

        self.analyze(self._ne_list_fr_stanford, 'french', 'stanford') # write French Stanford Results


        #get German results: Words and nouns
        self._de = self.get_nouns(self._de_text, 'de', issue, article)
        self._de_nouns = self._de[0] #number of nouns
        self._de_words = self._de[1] #number of words
        self._total_noun_de += self._de_nouns


        with open('evaluation_german.txt', 'a+') as eval:
            # write French results
            eval.write('\n\n____________________________________')
            eval.write('\nEvaluation of the German issue_{}, {}:\n'.format(issue, article))
            eval.write('Number of nouns (de): {}'.format(self._de_nouns))

        self.analyze(self._ne_list_de_spacy ,'german', 'spacy') # results of spacy

        self.analyze(self._ne_list_de_stanford, 'german', 'stanford')  # write French Stanford Results


    def get_nouns(self, text, lang, issue, article):

        self.annotations_list = []

        if lang == 'en':
            nlp = en_core_web_sm.load()

        elif lang == 'de':
            nlp = de_core_news_sm.load()

        elif lang == 'fr':
            nlp = fr_core_news_sm.load()

        with open(text, 'r', encoding='utf-8') as file:
            for line in file.readlines():
                text = nlp(line)
                for token in text:
                    annotation = token.tag_
                    tuple = (token.text, annotation)
                    self.annotations_list.append(tuple)

        count_nouns = 0
        words = 0

        for tuple in self.annotations_list:
            if tuple[1].startswith('NN') or tuple[1].startswith('NE') or tuple[1].startswith('NOUN') or tuple[1].startswith('PROPN'):
                count_nouns += 1
                words += 1
            else:
                words += 1

        # save nouns into file if needed for later analysis
        with open('Words/words_{}_issue_{}_{}.txt'.format(lang, issue, article), 'w+') as nouns:
            nouns.write('\n'.join('{} \t {}'.format(tuple[0], tuple[1]) for tuple in self.annotations_list))

        return count_nouns, words


    def analyze(self, list, lang, tagger):
        self.count = Calculations.count_ne(Calculations, list)
        self.NE = self.count[0] # number of NE
        self.ORG = self.count[1] # number of ORG
        self.PERSON = self.count[2] # number of Person
        self.GPE = self.count[3] # number of GPE

        #get percentages
        self.percentage_gpe = Calculations.gpe_per_ne(Calculations, self.NE, self.GPE)
        self.percentage_org = Calculations.org_per_ne(Calculations, self.NE, self.ORG)
        self.percentage_person = Calculations.person_per_ne(Calculations, self.NE, self.PERSON)

        #write output
        with open('evaluation_{}.txt'.format(lang), 'a+') as eval:
            eval.write('\n-{}: Number of Named Entities in {}: {}'.format(tagger, lang, self.NE))
            eval.write('\n\t {}: Number of GPE: {}'.format(tagger, self.GPE))
            eval.write('\n\t {}: Percentage GPE per NE: {}'.format(tagger, self.percentage_gpe))

            eval.write('\n\t {}: Number of Organisation: {}'.format(tagger, self.ORG))
            eval.write('\n\t {}: Percentage ORG per NE: {}'.format(tagger, self.percentage_org))

            eval.write('\n\t {}: Number of Person: {}'.format(tagger, self.PERSON))
            eval.write('\n\t {}: Percentage Person per NE: {}'.format(tagger, self.percentage_person))

        if tagger == 'spacy' and lang == 'english':
            self._GPE_spacy_en += self.GPE
            self._ORG_spacy_en += self.ORG
            self._PERS_spacy_en += self.PERSON
            self._NE_spacy_en += self.NE

        elif tagger == 'stanford' and lang == 'english':
            self._GPE_stanford_en += self.GPE
            self._ORG_stanford_en += self.ORG
            self._PERS_stanford_en += self.PERSON
            self._NE_stanford_en += self.NE


        elif tagger == 'spacy' and lang == 'french':
            self._GPE_spacy_fr += self.GPE
            self._ORG_spacy_fr += self.ORG
            self._PERS_spacy_fr += self.PERSON
            self._NE_spacy_fr += self.NE

        elif tagger == 'stanford' and lang == 'french':
            self._GPE_stanford_fr += self.GPE
            self._ORG_stanford_fr += self.ORG
            self._PERS_stanford_fr += self.PERSON
            self._NE_stanford_fr += self.NE

        elif tagger == 'spacy' and lang == 'german':
            self._GPE_spacy_de += self.GPE
            self._ORG_spacy_de += self.ORG
            self._PERS_spacy_de += self.PERSON
            self._NE_spacy_de += self.NE

        elif tagger == 'stanford' and lang == 'german':
            self._GPE_stanford_de += self.GPE
            self._ORG_stanford_de += self.ORG
            self._PERS_stanford_de += self.PERSON
            self._NE_stanford_de += self.NE


class Calculations:
    def __init__(self):
        pass

    def ne_per_nouns(self, ne, nouns):
        return (ne/nouns) * 100

    def nouns_per_words(self, nouns, words):
        return (nouns/words) * 100

    def gpe_per_ne(self, ne, gpe):
        return (gpe/ne) * 100

    def org_per_ne(self, ne, org):
        return (org/ne) * 100

    def person_per_ne(self, ne, person):
        return (person/ne) * 100

    def count_ne(self, file):
        GPE = 0
        PERSON = 0
        ORG = 0
        NE = 0

        with open(file, 'r', encoding='utf-8', errors='replace') as file:
            for line in file.readlines():
                NE += 1

                if 'ORG' in line:
                    ORG += 1

                elif 'PER' in line or 'PERSON' in line:
                    PERSON += 1

                elif 'GPE' in line or 'LOC' in line:
                    GPE += 1

        return NE, ORG, PERSON, GPE


def main():
    evaluation = Tagger()


    ''' do evaluation over all files'''
    root = '/Users/Karin/Desktop/Project_NE'
    os.chdir(root)

    with open('evaluation_overall.txt', 'a+') as all:

        # write English Evaluation
        all.write('________________\n')
        all.write('Evaluation for English:\n')
        all.write('Total nouns English: {}\n'.format(evaluation._total_noun_en))
        all.write('Total named English Entities spacy: {}\n'.format(evaluation._NE_spacy_en))
        all.write('- % NE spacy: {:.2f}%\n'.format((evaluation._NE_spacy_en/evaluation._total_noun_en)*100))

        all.write('- GPE spacy: {:.2f}\n'.format(evaluation._GPE_spacy_en))
        all.write('- % GPE spacy: {:.2f}%\n'.format((evaluation._GPE_spacy_en/evaluation._NE_spacy_en)*100))

        all.write('- Organizations spacy: {}\n'.format(evaluation._ORG_spacy_en))
        all.write('- % ORG spacy: {:.2f}%\n'.format((evaluation._ORG_spacy_en/evaluation._NE_spacy_en)*100))


        all.write('- Person spacy: {}\n'.format(evaluation._PERS_spacy_en))
        all.write('- % PERS spacy: {:.2f}%\n'.format((evaluation._PERS_spacy_en/evaluation._NE_spacy_en)*100))


        all.write('Total named Entities stanford: {}\n'.format(evaluation._NE_stanford_en))
        all.write('- % NE stanford: {:.2f}%\n'.format((evaluation._NE_stanford_en/evaluation._total_noun_en)*100))

        all.write('- GPE stanford: {}\n'.format(evaluation._GPE_stanford_en))
        all.write('- % PE stanford: {:.2f}%\n'.format((evaluation._GPE_stanford_en/evaluation._NE_stanford_en)*100))

        all.write('- Organizations stanford: {}\n'.format(evaluation._ORG_stanford_en))
        all.write('- % PERS stanford: {:.2f}%\n'.format((evaluation._ORG_stanford_en/evaluation._NE_stanford_en)*100))

        all.write('- Person stanford: {}\n'.format(evaluation._PERS_stanford_en))
        all.write('- % PERS stanford: {:.2f}%\n'.format((evaluation._PERS_stanford_en/evaluation._NE_stanford_en)*100))


        all.write('________________\n')
        all.write('Evaluation for French:\n')
        all.write('Total nouns French: {}\n'.format(evaluation._total_noun_fr))
        all.write('Total named French Entities spacy: {}\n'.format(evaluation._NE_spacy_fr))
        all.write('- % NE spacy: {:.2f}%\n'.format((evaluation._NE_spacy_fr/evaluation._total_noun_fr)*100))

        all.write('- GPE spacy: {}\n'.format(evaluation._GPE_spacy_fr))
        all.write('- % GPE spacy: {:.2f}%\n'.format((evaluation._GPE_spacy_fr/evaluation._NE_spacy_fr)*100))

        all.write('- Organizations spacy: {}\n'.format(evaluation._ORG_spacy_fr))
        all.write('- % ORG spacy: {:.2f}%\n'.format((evaluation._ORG_spacy_fr/evaluation._NE_spacy_fr)*100))

        all.write('- Person spacy: {}\n'.format(evaluation._PERS_spacy_fr))
        all.write('- % PERS spacy: {:.2f}%\n'.format((evaluation._PERS_spacy_fr/evaluation._NE_spacy_fr)*100))


        all.write('Total named French Entities stanford: {}\n'.format(evaluation._NE_stanford_fr))
        all.write('- % NE stanford: {:.2f}%\n'.format((evaluation._NE_stanford_fr/evaluation._total_noun_fr)*100))

        all.write('- GPE stanford: {}\n'.format(evaluation._GPE_stanford_fr))
        all.write('- % GPE stanford: {:.2f}%\n'.format((evaluation._GPE_stanford_fr/evaluation._NE_stanford_fr)*100))

        all.write('- Organizations stanford: {}\n'.format(evaluation._ORG_stanford_fr))
        all.write('- % ORG stanford: {:.2f}%\n'.format((evaluation._ORG_stanford_fr/evaluation._NE_stanford_fr)*100))

        all.write('- Person stanford: {}\n'.format(evaluation._PERS_stanford_fr))
        all.write('- % PERS stanford: {:.2f}%\n'.format((evaluation._PERS_stanford_fr/evaluation._NE_stanford_fr)*100))


        all.write('________________\n')
        all.write('Evaluation for German:\n')
        all.write('Total nouns German: {}\n'.format(evaluation._total_noun_de))
        all.write('Total named German Entities spacy: {}\n'.format(evaluation._NE_spacy_de))
        all.write('- % NE spacy: {:.2f}%\n'.format((evaluation._NE_spacy_de/evaluation._total_noun_de)*100))

        all.write('- GPE spacy: {}\n'.format(evaluation._GPE_spacy_de))
        all.write('- % GPE spacy: {:.2f}%\n'.format((evaluation._GPE_spacy_de/evaluation._NE_spacy_de)*100))

        all.write('- Organisations spacy: {}\n'.format(evaluation._ORG_spacy_de))
        all.write('- % ORG spacy: {:.2f}%\n'.format((evaluation._ORG_spacy_de/evaluation._NE_spacy_de)*100))

        all.write('- Person spacy: {}\n'.format(evaluation._PERS_spacy_de))
        all.write('- % PERS spacy: {:.2f}%\n'.format((evaluation._PERS_spacy_de/evaluation._NE_spacy_de)*100))


        all.write('Total named German Entities stanford: {}\n'.format(evaluation._NE_stanford_de))
        all.write('- % NE stanford: {:.2f}%\n'.format((evaluation._NE_stanford_de/evaluation._total_noun_de)*100))

        all.write('- GPE stanford: {}\n'.format(evaluation._GPE_stanford_de))
        all.write('- % GPE stanford: {:.2f}%\n'.format((evaluation._GPE_stanford_de/evaluation._NE_stanford_de)*100))

        all.write('- Organisations stanford: {}\n'.format(evaluation._ORG_stanford_de))
        all.write('- % ORG stanford: {:.2f}%\n'.format((evaluation._ORG_stanford_de/evaluation._NE_stanford_de)*100))

        all.write('- Person stanford: {}\n'.format(evaluation._PERS_stanford_de))
        all.write('- % PERS stanford: {:.2f}%\n'.format((evaluation._PERS_stanford_de/evaluation._NE_stanford_de)*100))



if __name__ == "__main__":
    main()