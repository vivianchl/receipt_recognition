'''
A Simple Experimental Receipt Generator
'''

from PIL import Image, ImageDraw, ImageFont, ImageOps
from faker import Faker
import random
from datetime import datetime, timedelta

def generate_random_date():
    # Convert start_date and end_date to datetime objects
    start_date = '2000-01-01'  # Example start date
    end_date = '2024-12-31'    # Example end date
    start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
    end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Generate a random timedelta within the range
    random_timedelta = timedelta(days=random.randint(0, (end_datetime - start_datetime).days))
    
    # Add the random timedelta to start_date
    random_date = start_datetime + random_timedelta
    
    return random_date

german_groceries = [
    "Apfel","Banane","Orange","Karotte","Kartoffel","Tomate","Salat","Brot","Milch","Käse","Eier","Joghurt","Mehl","Zucker","Butter",
    "Paprika","Zwiebel","Gurke","Schokolade","Wasser","Kaffee","Tee","Reis","Nudeln","Huhn","Rindfleisch","Schweinefleisch","Fisch",
    "Öl","Essig","Marmelade","Honig","Müsli","Kekse","Zitrone","Limette","Ananas","Melone","Erdbeere","Himbeere","Blaubeere","Birne",
    "Pfirsich","Traube","Kiwi","Mango","Avocado","Spinat","Brokkoli","Blumenkohl","Lauch","Knoblauch","Petersilie","Basilikum","Thymian",
    "Rosmarin","Oregano","Salz","Pfeffer","Senf","Ketchup","Mayonnaise","Sojasauce","Wurst","Schinken","Speck","Joghurtdrink","Frischkäse",
    "Quark","Schlagsahne","Sauerrahm","Buttermilch","Eiscreme"
]

total_price = 0

def _insert_text(draw: ImageDraw, x, y, text,
                 color='rgb(0, 0, 0)',
                 font_file='fonts/Roboto-Bold.ttf',
                 font_size=12):
    text = str(text)
    font = ImageFont.truetype(font_file, size=font_size)
    draw.text((x, y), text, fill=color, font=font)
    return draw


def _combine_all_images_horizantally(images):
    # images = map(Image.open, sys.argv[1:-1])
    w = sum(i.size[0] for i in images)
    mh = max(i.size[1] for i in images)

    result = Image.new("RGBA", (w, mh))

    x = 0
    for i in images:
        result.paste(i, (x, 0))
        x += i.size[0]
    return result


def _combine_all_images_vertically(images):
    # images = map(Image.open, sys.argv[1:-1])
    w = max(i.size[0] for i in images)
    mh = sum(i.size[1] for i in images)

    result = Image.new("RGBA", (w, mh))

    x = 0
    for i in images:
        result.paste(i, (0, x))
        x += i.size[1]
    return result


class ReceiptGenerator():
    def __init__(self, size=None):
        self.header = None
        self.body = None
        self.total = None
        self.footer = None
        self.final_output_image = None
        self._debug_ = False # Debug Param

        self.image_size = size if size else (320, 480)
        self.image_line_sep = self._text_image('--' * 27, font_size=14, size=self.image_size)
        self.image_whitespace_sep = self._text_image(' ', font_size=14, size=self.image_size)

        self.receipt_text_data = []

    def _text_image(self, text, font_size=12, size=(320, 480)):
        width, height = size
       # _text = text.center(int(int(width / font_size) * 3.2))
        if self._debug_:
            _text = _text.replace(' ', '.')
        image = Image.new(mode="RGB", size=(width, font_size + 4), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        draw = _insert_text(draw=draw, x=0 + 4, y=0, text=text, font_size=font_size)
        if self._debug_:
            image = ImageOps.expand(image, border=2, fill='black')
        return image
    
    def generate_header(self):
        header_text_data = [
            '                            REWE Altenburg oHG',
            '                            Holstenstraße 1-11',
            '                            24103 Kiel',
            '                            UID Nr. : DE285532480',
            '                            Date: 12/12/2009'
        ]

        image1 = _combine_all_images_vertically([
            self._text_image(header_text_data[0], font_size=12, size=(320, 0)),
            self._text_image(header_text_data[1], font_size=12, size=(320, 0)),
            self._text_image(header_text_data[2], font_size=12, size=(320, 0)),
            self._text_image(header_text_data[3], font_size=12, size=(320, 0)),
        ]
        )
        self.receipt_text_data += header_text_data[:3]

       

        self.header = _combine_all_images_vertically([image1])


    def generate_body(self):
        faker = Faker('de_DE')
        global total_price
        total_price = 0
       
        body_text_data = [
            ('', 'EUR')
        ]

        loop_count = random.randint(1, 10)

        for i in range(loop_count):
            random_noun = faker.word(ext_word_list=german_groceries)
            random_price = round(random.uniform(0.5, 10.0), 2)
            formatted_price = '{:,.2f}'.format(random_price).replace('.', ',')
            body_text_data.append((random_noun, f'{formatted_price} B'))
            total_price += random_price


        bag = []

        for each_line in body_text_data:
            _image_line_item = _combine_all_images_horizantally([
                self._text_image(each_line[0], font_size=12, size=(160, 0)),
                self._text_image('', font_size=12, size=(80, 0)),
                self._text_image(each_line[1], font_size=12, size=(80, 0)),
            ])
            bag.append(_image_line_item)
            self.receipt_text_data.append('{} {}'.format(*each_line))

        image3 = _combine_all_images_vertically(bag)

        self.body = image3

    def generate_total(self):
        sum = '{:,.2f}'.format(total_price).replace('.', ',')
        body_text_data = [
            ('SUMME', 'EUR', sum),
            ('Geg. BAR', 'EUR', sum),
        ]

        bag = []

        for each_line in body_text_data:
            _image_line_item = _combine_all_images_horizantally([
                self._text_image(each_line[0], font_size=12, size=(160, 0)),
                self._text_image(each_line[1], font_size=12, size=(80, 0)),
                self._text_image(each_line[2], font_size=12, size=(80, 0)),
            ])
            bag.append(_image_line_item)
            if(len(bag) == 1):
                bag.append(self.image_line_sep)
            self.receipt_text_data.append('{} {} {}'.format(*each_line))

        self.total = _combine_all_images_vertically(bag)

    def generate_footer(self):
        sum = '{:,.2f}'.format(total_price).replace('.', ',')
        tax = '{:,.2f}'.format(total_price*0.07).replace('.', ',')
        sum_netto = '{:,.2f}'.format(total_price-(total_price*0.07)).replace('.', ',')
        footer_text_data = [
            ('Steuer %', 'Netto', 'Steuer', 'Brutto'),
            ('B= 7,0 %', sum_netto, tax,sum),
            ('Gesamtbetrag', sum_netto, tax,sum),
        ]

        bag = []
        for each_line in footer_text_data:
            _image_text = _combine_all_images_horizantally([
                self._text_image(each_line[0], font_size=10, size=(80, 0)),
                self._text_image(each_line[1], font_size=10, size=(80, 0)),
                self._text_image(each_line[2], font_size=10, size=(80, 0)),
                self._text_image(each_line[3], font_size=10, size=(80, 0))
            ])
            bag.append(_image_text)
            self.receipt_text_data.append('{} {}'.format(*each_line))

        bag.append(self._text_image(' ', font_size=14, size=self.image_size))

        date = generate_random_date()

        footer_tse = [
            ('TSE-Signatur:','AKJDFLKJFKLSDJSDFFDDFDLKFJSDK'),
            ('','KJGDFJLKFJDKLFJKLDJFKDJFDVNNN'),
            ('','DFDFDFDFLKDFJDLIFIDJFILDJFIDD'),
            ('','/KJDFLKJFKLSDJSDFFDDFLKFJSDK'),
            ('TSE-Signaturzähler', '2710643'),
            ('TSE-Transaktion', '1310826'),
            ('TSE-Start', date.strftime('%Y-%m-%d') + 'T17:12:07.000'),
            ('TSE-Stop', date.strftime('%Y-%m-%d') + 'T17:12:28.000'),
            ('Seriennummer Kasse', 'REWE:b4:e2:99:d9:b6:71:00'),
        ]

        for each_line in footer_tse:
            _image_text = _combine_all_images_horizantally([
                self._text_image(each_line[0], font_size=10, size=(120, 0)),
                self._text_image(each_line[1], font_size=10, size=(200, 0)),

            ])
            bag.append(_image_text)
            self.receipt_text_data.append('{} {}'.format(*each_line))


        footer_date_text = [
            (date.strftime('%d.%m.%Y'),'17:12', 'Bon-Nr. :4505'),
             ('Markt:5571','Kasse:4', 'Bed. :424242'),
        ]

        for each_line in footer_date_text:
            _image_text = _combine_all_images_horizantally([
                self._text_image('', font_size=12, size=(10, 0)),
                self._text_image(each_line[0], font_size=12, size=(100, 0)),
                self._text_image(each_line[1], font_size=12, size=(100, 0)),
                self._text_image(each_line[2], font_size=12, size=(100, 0)),
                self._text_image('', font_size=12, size=(10, 0)),
            ])
            bag.append(_image_text)
            self.receipt_text_data.append('{} {} {}'.format(*each_line))


        bag.append(self._text_image('**' * 24, font_size=14, size=self.image_size))





        self.footer = _combine_all_images_vertically(bag)

    def show_output(self):
        pass

    def save_output(self):
        self.generate_header()
        self.generate_body()
        self.generate_total()
        self.generate_footer()
        self.final_output_image = _combine_all_images_vertically(
            [
                self.image_whitespace_sep,
                self.header,
                self.image_whitespace_sep,
                self.body,
                self.image_line_sep,
                self.total,
                self.footer,
            ]
        )
        self.final_output_image.save('tmp_output.png')
        #print(self.receipt_text_data)


if __name__ == '__main__':
    t = ReceiptGenerator()
    t.save_output()

