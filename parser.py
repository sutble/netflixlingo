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
        self.spanish_dict = DictDB()
        self.cached_spanish_dict = {}

    def make_noun_equals_caption(self,spanish_text,translated_text,tagged_words):
        nouns = []
        for word in tagged_words:
            if word.pos_ == 'NOUN':
                nouns.append(word.text)

        for noun in nouns:
            lowered_noun = noun.lower()
            if not self.spanish_dict.hasdef(lowered_noun):
                print(noun, " NOT IN MAIN DICTIONARY")
                if lowered_noun in self.cached_spanish_dict:
                    definitions = self.cached_spanish_dict[lowered_noun]
                else:
                    print(noun, " NOT IN CACHED DICTIONARY")
                    definitions = [self.translator.translate(lowered_noun,dest='en').text]
                    self.cached_spanish_dict[lowered_noun] = definitions
            else:
                definitions = self.spanish_dict.getdef(lowered_noun)

            for definition in definitions: 
                if definition.lower() in translated_text.lower():
                    return_str = " " + noun + " = " + definition + "|"
                    print(return_str)
                    return return_str
                else:
                    print(definition, "NOT IN TEXT ", translated_text)                
        return " "
        

    def make_caption_efficient(self,spanish_text,translated_text):
        tagged_words = self.nlp(spanish_text)
        return self.make_noun_equals_caption(spanish_text,translated_text,tagged_words)

    def make_caption(self,spanish_text,translated_text):
        tagged_words = self.nlp(spanish_text)
        part_of_speeches =  [word.pos_ for word in tagged_words]
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
        if nouns:
            word_list = nouns
        else:
            word_list = verbs
        if not word_list:
            return " "
        chosen_word = random.choice(word_list)
        translated_word = self.translator.translate(chosen_word,dest='en').text
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
        caption = caption[:substring_ending_index] + " (" + translated_word + ")" + caption[substring_ending_index:]
        print(caption)
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


        json_dict = json.dumps(dict)
        f = open("spanish_dict.json","w+")
        f.write(json_dict)
        f.close()
        self.read_file.close()
        self.write_file.close()  


        
         




if __name__ == "__main__":
    SpanishTutor('subtitles/s1e1spanish.xml','subtitles/hangman.xml').main()
