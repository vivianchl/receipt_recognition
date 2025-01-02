'''
This script provides a Receipt Generator for drogerie, which:
 consists of a random date generator function, a header, a body, a total and a footer.
 The body part contains a list of ordered items, which are also randomly selected from a list of predefined items in the corresponding generator. 
 The information in the header and footer parts is set according to different real data as templates. 
 The header part contains the name of the company, the address of the retail store and telepone number. 
 The footer shows the start and end time of the transaction, as well as the signature counter, etc. 
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
    "Shampoo", "Seife", "Duschgel", "Zahnpasta", "Deodorant", 
    "Handcreme", "Bodylotion", "Rasierer", "Wattepads",
    "Pflaster", "Desinfektionsmittel", "Augentropfen", "Nasenspray", "Ohrenstäbchen",
    "Haargel", "Haarspray", "Haarbürste", "Nagelschere", "Zahnbürste",
    "Mundwasser", "Gesichtscreme", "Make-up-Entferner", "Rasiergel", "After-Shave",
    "Enthaarungscreme", "Tampons", "Binden", "Körperlotion",
    "Gesichtsmaske", "Gesichtswasser", "Zahnseide", "Kontaktlinsenlösung", "Lippenpflege",
    "Sonnencreme", "Insektenschutz", "Wundsalbe", "Hustenbonbons", "Antibiotikasalbe"
]

total_price = 0
date = None

def _insert_text(draw: ImageDraw, x, y, text,
                 color='rgb(0, 0, 0)',
                 font_file='fonts/Arial.ttf',
                 font_size=12):
    text = str(text)
    font = ImageFont.truetype(font_file, size=font_size)
    draw.text((x, y), text, fill=color, font=font)
    return draw


def _combine_all_images_horizantally(images):
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
            '                            Drogerie Muster',
            '                            Holstenstraße 1-11',
            '                            24103 Kiel',
            '                            0431/123456789',
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

        global date
        date = generate_random_date()

        bag = []

        _image_line_item = _combine_all_images_horizantally([
                self._text_image(date.strftime('%d.%m.%Y'), font_size=12, size=(80, 0)),
                self._text_image('17:04', font_size=12, size=(60, 0)),
                self._text_image('1821/1', font_size=12, size=(60, 0)),
                self._text_image('312494/3', font_size=12, size=(60, 0)),
                self._text_image('7946', font_size=12, size=(60, 0)),
                                                                    ])
        bag.append(_image_line_item)
        bag.append(self._text_image('', font_size=12, size=(320, 0)))
        
        body_text_data = []

        loop_count = random.randint(1, 10)

        for i in range(loop_count):
            random_noun = faker.word(ext_word_list=german_groceries)
            random_price = round(random.uniform(0.5, 10.0), 2)
            formatted_price = '{:,.2f}'.format(random_price).replace('.', ',')
            body_text_data.append((random_noun, f'{formatted_price}'))
            total_price += random_price

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
            ('SUMME EUR', '', sum),
            ('BAR EUR', '', '-'+sum),
            ('Rückgeld EUR', '', '0,00'),
        ]

        bag = []

        for each_line in body_text_data:
            _image_line_item = _combine_all_images_horizantally([
                self._text_image(each_line[0], font_size=12, size=(160, 0)),
                self._text_image(each_line[1], font_size=12, size=(80, 0)),
                self._text_image(each_line[2], font_size=12, size=(80, 0)),
            ])
            bag.append(_image_line_item)
            self.receipt_text_data.append('{} {} {}'.format(*each_line))
        
        bag.append(self._text_image('', font_size=12, size=(320, 0)))
        self.total = _combine_all_images_vertically(bag)

    def generate_footer(self):
        sum = '{:,.2f}'.format(total_price).replace('.', ',')
        tax = '{:,.2f}'.format(total_price*0.07).replace('.', ',')
        sum_netto = '{:,.2f}'.format(total_price-(total_price*0.07)).replace('.', ',')
        tax2 = '{:,.2f}'.format(total_price*0.19).replace('.', ',')
        sum_netto2 = '{:,.2f}'.format(total_price-(total_price*0.19)).replace('.', ',')
        footer_text_data = [
            ('MwSt-Satz', 'Brutto', 'Netto', 'MwSt'),
            ('1=19,00%',sum, sum_netto2, tax2),
            ('2=7,00%', sum, sum_netto, tax),
        ]

        bag = []
        for each_line in footer_text_data:
            _image_text = _combine_all_images_horizantally([
                self._text_image(each_line[0], font_size=12, size=(80, 0)),
                self._text_image(each_line[1], font_size=12, size=(80, 0)),
                self._text_image(each_line[2], font_size=12, size=(80, 0)),
                self._text_image(each_line[3], font_size=12, size=(80, 0))
            ])
            bag.append(_image_text)
            self.receipt_text_data.append('{} {}'.format(*each_line))

        bag.append(self._text_image('**' * 24, font_size=14, size=self.image_size))

        
        footer_date_text = [
            ('Öffnungzeiten auf drogerie.de'),
             ('Steuer-Nr.: 1235/85486'),
        ]

        for each_line in footer_date_text:
            _image_text = _combine_all_images_horizantally([
                self._text_image('', font_size=12, size=(60, 0)),
                self._text_image(each_line, font_size=12, size=(260, 0)),

            ])
            bag.append(_image_text)
            self.receipt_text_data.append('{}'.format(each_line))


        bag.append(self._text_image('', font_size=14, size=self.image_size))
        bag.append(self._text_image('  ******* FISKALINFROMATIONEN (TSE) ******', font_size=14, size=self.image_size))
        footer_tse = [
            ('Start:',date.strftime('%Y-%m-%d') + ' 17:04:12'),
            ('Ende:',date.strftime('%Y-%m-%d') + ' 17:04:32'),
            ('SN-Kasse: FD158964','TA-Nummer: 1258965'),
            ('Signaturzähler: 854695', 'Signatur: 826966'),
        ]

        for each_line in footer_tse:
            _image_text = _combine_all_images_horizantally([
                self._text_image(each_line[0], font_size=12, size=(160, 0)),
                self._text_image(each_line[1], font_size=12, size=(160, 0)),

            ])
            bag.append(_image_text)
            self.receipt_text_data.append('{} {}'.format(*each_line))
        bag.append(self._text_image('564d5f64d56f4a56df4f564654561d65fdfd4dfa57ef==', font_size=12, size=self.image_size))
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
                self.total,
                self.footer,
            ]
        )
        self.final_output_image.save('tmp_output.png')
        #print(self.receipt_text_data)


if __name__ == '__main__':
    t = ReceiptGenerator()
    t.save_output()

