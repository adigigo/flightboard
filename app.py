from jinja2 import Environment, FileSystemLoader
from html2image import Html2Image
import epd7in5_V2
from PIL import Image
import os
import time
import random
import sys

from utils import get_flight

ROOT_DIR = os.path.dirname(os.path.abspath(__name__))
env = Environment(loader=FileSystemLoader(f"{ROOT_DIR}/Projects/flightboard/templates"))
fboard_template = env.get_template("fboard.html")


flight = get_flight()


fboard_output = fboard_template.render(airline = flight['airline'],
                                        flight_no = flight['flight_no'],
                                        o_name = flight['o_name'],
                                        o_code = flight['o_code'],
                                        dep_time = flight['dep_time_utc'],
                                        d_name = flight['d_name'],
                                        d_code = flight['d_code'],
                                        arr_time = flight['arr_time_utc'],
                                        altitude = flight['altitude'],
                                        heading = flight['heading'],
                                        ground_speed = flight['ground_speed'],
                                        airline_icao = f"{ROOT_DIR}/Projects/flightboard/logos/{flight['airline_icao']}.png",
                                        aircraft = flight['aircraft'])

hti = Html2Image(size=(800, 480), custom_flags = ['--disable-gpu'],output_path = f"{ROOT_DIR}/Projects/flightboard")
hti.screenshot(html_str=fboard_output,save_as="fboard.png")


epd = epd7in5_V2.EPD()
epd.init()

Himage = Image.open(f'{ROOT_DIR}/Projects/flightboard/fboard.png')
Himage = Himage.resize((800,480),Image.LANCZOS)
Himage = Himage.convert("L",dither=Image.NONE)
epd.display(epd.getbuffer(Himage))

time.sleep(20)

random_quote=random.choice(os.listdir(f'{ROOT_DIR}/Projects/flightboard/quote_images/'))

Himage = Image.open(f'{ROOT_DIR}/Projects/flightboard/quote_images/{random_quote}')
Himage = Himage.resize((800,480),Image.LANCZOS)
Himage = Himage.convert("1",dither=Image.NONE)
epd.display(epd.getbuffer(Himage))

sys.exit(0)