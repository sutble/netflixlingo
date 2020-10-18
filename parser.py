import xmltodict
from collections.abc import Mapping
import es_core_news_sm
import random
from googletrans import Translator
from  spanish_dict.dictdlib import DictDB
import json 


class SpanishTutor:
    def __init__(self,read_path, write_path):
        self.read_file = open(read_path)
        self.write_file = open(write_path,"w+")
        self.doc = xmltodict.parse(self.read_file.read())
        self.nlp = es_core_news_sm.load()
        self.translator = Translator()
        self.spanish_text = ''
        self.translation_text = ''
        self.paragraphs = []
        self.spanish_dict = json.load(open('spanish_dict.json'))

    def make_noun_equals_caption(self,spanish_text,translated_text,tagged_words):
        nouns = []
        for word in tagged_words:
            if word.pos_ == 'NOUN':
                nouns.append(word.text)

        for noun in nouns:
            lowered_noun = noun.lower()
            if lowered_noun not in self.spanish_dict:
                print(noun, " NOT IN MAIN DICTIONARY")
                definitions = [self.translator.translate(lowered_noun,dest='en').text]
                self.spanish_dict[lowered_noun] = definitions
            else:
                definitions = self.spanish_dict[lowered_noun]

            for definition in definitions: 
                if definition.lower() in translated_text.lower():
                    return_str = " " + noun + " = " + definition + " |"
                    print(return_str)
                    return return_str
                else:
                    print(definition, "NOT IN TEXT ", translated_text)
            return_str = " " + noun + " = " + definitions[0] + " |"
            print(return_str)
            return return_str
        

    def make_caption(self,spanish_text,translated_text):
        return self.make_hangman_caption(spanish_text,translated_text)

    
    def translate_word(self,chosen_word,translated_text):
        if chosen_word not in self.spanish_dict:
            definitions = [self.translator.translate(chosen_word,dest='en').text]
            self.spanish_dict[chosen_word] = definitions
        else:
            definitions = self.spanish_dict[chosen_word]
        for definition in definitions:
            if definition.lower() in translated_text.lower():
                return definition
        return definitions[0]

    def make_hangman_caption(self,spanish_text,translated_text):
        tagged_words = self.nlp(spanish_text)
        part_of_speeches = [word.pos_ for word in tagged_words]
        nouns = []
        verbs = []
        punctuation = []
        for word in tagged_words:
            if word.pos_ == 'NOUN':
                nouns.append(word.text)
            if word.pos_ == 'VERB':
                verbs.append(word.text)
            if word.pos_ == 'PUNCT':
                punctuation.append(word.text)
        word_list = []
        if nouns:
            word_list = nouns
        else:
            word_list = verbs
        if not word_list:
            #print("NO NOUNS OR VERBS?")
            return " "
        chosen_word = random.choice(word_list)
        translated_word = self.translate_word(chosen_word,translated_text)
        caption = ''
        substring_starting_index = spanish_text.find(chosen_word)
        substring_ending_index = substring_starting_index + len(chosen_word)
        for i in range(0,len(spanish_text)):
            char = spanish_text[i]
            if i >= substring_starting_index and i < substring_ending_index:
                caption += char
            elif char in punctuation:
                caption += char
            else:
                caption += '_'
        caption = caption[:substring_ending_index] + "(" + translated_word + ")" + caption[substring_ending_index:]
        #print(caption)
        return caption


    def populate_spanish_and_translation_text(self):
            paragraphs = self.doc['tt']['body']['div']['p']
            for paragraph in paragraphs:
                span = paragraph['span']
                if isinstance(span, Mapping):
                    span = [span]
                
                for order_d in span:
                    self.spanish_text += order_d['#text'] + ' '
                self.spanish_text += '\n'
            chunk = 10000
            for i in range(0, len(self.spanish_text), chunk):
                self.translation_text += self.translator.translate(self.spanish_text[i:i+chunk],dest='en').text


    def transform_doc(self):
        paragraphs = self.doc['tt']['body']['div']['p']
        translated_lines = self.translation_text.splitlines()
        for i in range(len(paragraphs)):
            paragraph = paragraphs[i]
            span = paragraph['span']
            if isinstance(span, Mapping):
                span = [span]
            
            for order_d in span:
                order_d['#text'] = self.make_caption(order_d['#text'],translated_lines[i]) 



    def main(self):
        
        self.populate_spanish_and_translation_text()
        self.transform_doc()
        self.write_file.write(xmltodict.unparse(self.doc))
        self.read_file.close()
        self.write_file.close()  
        import pdb; pdb.set_trace()
        json_dict = json.dumps(self.spanish_dict)
        f = open("spanish_dict.json","w+")
        f.write(json_dict)
        f.close()


        
         




if __name__ == "__main__":
    SpanishTutor('subtitles/s1e1spanish.xml','subtitles/hangman_efficient.xml').main()
