#Import libraries
import numpy as np
import pandas as pd
import requests
import json
import re
import math
from bs4 import BeautifulSoup


def get_all_page_metas(response, config, debug=False):
    '''
    Retrieve metadata from a web page according to specific configuration.
    Expected values:
    page = full url
    config = {
        // Main content description selector
        'description_selector' : se

        // These two go together
        'value_in_element' : 'sibling' OR 'meta'
        ,'meta_selector' : 'div#band_stats dl dt'

        'class_to_check' :
        ETC...
    }

    '''

    metas = {}
    title = ""

    try:
        if debug: print(page)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Title
            title_selector = config.get('title_selector')

            if title_selector:
                title = soup.select(title_selector)[0].text

            # Word count in description
            description_selector = config.get('description_selector')

            if description_selector:
                block_description = soup.select(description_selector)

                # Paragraphs or no
                if description_selector[-1:] == 'p':
                    clean_description = ""
                    for p in block_description:
                        clean_description = clean_description + p.text
                else:
                    clean_description = str(block_description[0].text)

                char_count = len(clean_description)
                word_count = len(clean_description.split(" "))
            else:
                char_count = -1
                word_count = -1

            # Get config elements
            value_in_element = config.get('value_in_element')
            class_to_check = config.get('class_to_check')
            meta_selector = config.get('meta_selector')

            # Look for meta elements using the provided css selector
            if meta_selector:

                if debug: print('meta_selector')
                items = soup.select(meta_selector)
                metaText = class_to_check

                value = []
                for item in items:
                    if debug: print(items)

                    # Some specitic hard-coded use cases
                    # Accepted values: sibling, meta

                    if value_in_element == 'sibling':
                        metaText = item.text.split(":")[0]
                        value = item.find_next_sibling().text

                        metaText = metaText.strip()
                        value = value.strip()

                        if debug: print('item:' + str(metaText) + ': ' + str(value))

                    elif value_in_element == 'meta':
                        metaText = class_to_check
                        temp = item.text.split(":")[0]
                        if debug: print(temp)
                        value.append(str(temp))

                    metas.update({metaText: value})
            else:
                print('error: missing attribute meta_selector')

            metas.update({'char_count': char_count,
                          'word_count': word_count,
                          'description': clean_description,
                          'title': title})
        else:

            if debug:
                print("status code not 200: " + str(response.status_code))

            metas.update({'title': "N/A"})

        metas.update({'status_code': response.status_code})

        return metas

    except Exception as e:
        print(e)
        return


# PUBLIC TEST CASE 1 (description doesn't work)
page = 'https://www.metal-archives.com/bands/Trollfest/20648'
config = {
        'value_in_element': 'sibling'
        , 'meta_selector': 'div#band_stats dl dt'
        , 'description_selector': 'div.band_comment'
        , 'title_selector': 'h1.band_name'
    }

print(get_all_page_metas(page, config, debug = False))