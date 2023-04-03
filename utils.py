
from PIL import Image
import io
import base64
import random

def pil_to_base64(pil_im):
    # Convert the PIL image to a base64 encoded string
    buffer = io.BytesIO()
    pil_im.save(buffer, format="JPEG")
    img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return img_str

def base64_to_pil(img_str):
    # Convert the base64 encoded string back to a PIL image
    img_data = base64.b64decode(img_str)
    pil_img = Image.open(io.BytesIO(img_data))
    return pil_img


def add_carriage_return(s, char_limit=20):
    result = ''
    for i in range(0, len(s), char_limit):
        result += s[i:i + char_limit] + '\n'
    return result.strip()


def tags_from_df(df):
    # extract tags in dataframe and put them in a string
    str_tags = 'Items tags\n'
    for idx, row in df.iterrows():
        # #replace semicolon and space beween tags with a \n
        tags = row['Tags'].replace('; ','\n')
        str_tags += f"--------{row['ShopName']}--------\n{tags}\n"

    return str_tags
    
def etsy_sites_from_df(df):
    # create etsy url of every item in dataframe
    # and put them on a string
    sites = ''
    for i, (df_index, row) in enumerate(df.iterrows()):
        sites += f"{i+1}.- https://www.etsy.com/de-en/listing/{row['ItemId']}/\n\n"
    return sites


def get_first_n_tags(df, n):
    # take the n tag s of each item and 
    # put them in a list
    tags  = []
    for i, (df_index, row) in enumerate(df.iterrows()):
        #get first n tags of set of tags in item
        try: 
            first_tags = ' '.join(row['Tags'].split('; ')[:n])
        except KeyboardInterrupt:
            # Handle the KeyboardInterrupt separately, if needed
            print("\nCtrl+C detected. Exiting gracefully...")
            exit()
        except Exception as e:
            # Handle other exceptions here
            print(f"An unexpected error occurred: {e}")
            first_tags = ' '.join(row['Tags'].split('; '))

        tags.append(first_tags)
        
    return tags


def get_rnd_tags(df, n):
    # gets randomly n tags from all tags in all items in df
    # gets tags strings from df and remove semicolon, then joined them with a space
    tags_lists = df['Tags'].tolist()
    # split each tags string and put everything on a list
    tags_lists = [ x for i in tags_lists for x in i.split('; ')]
    try:
        # take n random samples from the list
        random_tags = random.sample(tags_lists, n)
    except KeyboardInterrupt:
        # Handle the KeyboardInterrupt separately, if needed
        print("\nCtrl+C detected. Exiting gracefully...")
        exit()
    except Exception as e:
        # there is fewer than n tags available
        random_tags = tags_lists
    
    # join them in a string
    random_tags = ' '.join(random_tags)
    return random_tags


def get_etsy_queries(df):
    # creates a set of queries for etsy from the tags in df
    base_url = 'https://www.etsy.com/de-en/search?q={}&ref=search_bar'
    # gets list of ntags from each item
    items_tags =  get_first_n_tags(df, 4)
    # get string of random tags gotten from all items in df
    rnd_tags = get_rnd_tags(df, 4)
    # add it to list of tags
    items_tags += [rnd_tags]
    # create string of etsy queries from tags
    etsy_queries = ''
    for i,tags in enumerate(items_tags):
        query = base_url.format(tags.replace(' ','+'))
        etsy_queries += f'{i+1}.- {query}\n\n'

    return etsy_queries


def get_item_names(df):
    # joins all item names in a string
    item_names = [ name for name in df['ItemName'].tolist()]
    str_names = '\n\n'.join(item_names)
    return str_names


def tags2string(df):
    # get all tags in df and put them in a string
    tags = df['Tags'].tolist()
    # join adding carriage return between tags
    tags_str = '\n'.join(tags)
    return tags_str


'''
def get_tags_for_etsy_query(df, n, only_first=True):
    # take the n tag s of each item and 
    # puts it in a url for etsy search
    base_url = 'https://www.etsy.com/de-en/search?q={}&ref=search_bar'
    tags  = []
    for i, (df_index, row) in enumerate(df.iterrows()):
        #get first n tags of set of tags in item
        try: 
            first_tags = ' '.join(row['Tags'].split('; ')[:n])
        except KeyboardInterrupt:
            # Handle the KeyboardInterrupt separately, if needed
            print("\nCtrl+C detected. Exiting gracefully...")
            exit()
        except Exception as e:
            # Handle other exceptions here
            print(f"An unexpected error occurred: {e}")
            first_tags = ''

        tags.append(first_tags)
        
        # if only first is true, only takes tags from  first item
        if only_first:
            break
        
    #join tags with a + separator for query
    jtags = '+'.join(tags)
    # replace extra spaces with +
    jtags = jtags.replace(' ','+')
    return base_url.format(jtags)
'''