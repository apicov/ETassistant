
from PIL import Image
import io
import base64

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
