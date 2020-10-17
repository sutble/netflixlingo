import xmltodict
from collections.abc import Mapping
import es_core_news_sm
import random
from googletrans import Translator


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

    def make_equals_caption(self,spanish_text,translated_text,tagged_words):
        nouns = []
        for word in tagged_words:
            if word.pos_ == 'NOUN':
                nouns.append(word.text)
        if not nouns:
            return " "
        chosen_word = random.choice(nouns)
        return_str = " " + chosen_word + " = " + translated_text + " "
        print(return_str)
        return return_str
        

    def make_caption(self,spanish_text,translated_text):
        import pdb; pdb.set_trace()
        tagged_words = self.nlp(spanish_text)
        return self.make_equals_caption(spanish_text,translated_text,tagged_words)

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


        
         




if __name__ == "__main__":
    SpanishTutor('s1e1spanish.xml','custom.xml').main()
