#!pip install -U sentence-transformers
#!pip install ftfy


import pandas as pd
import numpy as np
import random
from pathlib import Path
import io


from sklearn.neighbors import NearestNeighbors
import PIL
from PIL import Image
import matplotlib.pyplot as plt
from sentence_transformers import SentenceTransformer

from utils import add_carriage_return


class CLIPSearcher():
    # class for searching similar CLIP embeddings in data in dataframe df
    def __init__(self, df, clip_model=None):
        if clip_model:
            # model to generate embeddings
            self.clip_model = clip_model
        else:
            # create instance if none
            self.clip_model = SentenceTransformer('clip-ViT-B-32')

        # columns of df that will be returned in the queries
        self.result_df_cols = ['ItemId', 'ItemName', 'ShopName', 'NumReviews', 'IsBestseller', 'NumberOfTags', 'Tags', 'Description']
        # dataframe where embeddings of images, tags and item names are
        #make sure that df indexes are sequential
        # they have to match with numy array embeddings indexes
        self.df = df
        self.df.reset_index(drop=True, inplace=True)

        
        # path where dataset of images is
        #self.images_path = images_path

        # shows if the last input embedding generated by gen_query()
        # is text or image
        self.query_embedding_type = None
        # stores last generated embedding
        self.query_embedding = None

        search_algorithm = 'brute'
        # create nearest neighbors model for image embeddings search
        self.NN_images = NearestNeighbors(n_neighbors=10,
                         metric='cosine',
                         algorithm=search_algorithm,
                         n_jobs=-1)
        # fit to image embeddings in dataframe
        self.NN_images.fit(self.df.loc[:,'IE000':'IE511'].values)

        # create nearest neighbors model for item name embeddings search
        self.NN_it_name = NearestNeighbors(n_neighbors=10,
                         metric='cosine',
                         algorithm=search_algorithm,
                         n_jobs=-1)
        # fit to image embeddings in dataframe
        self.NN_it_name.fit(self.df.loc[:,'NE000':'NE511'].values)

        # create nearest neighbors model for tags embeddings search
        self.NN_tags = NearestNeighbors(n_neighbors=10,
                         metric='cosine',
                         algorithm=search_algorithm,
                         n_jobs=-1)
        # fit to image embeddings in dataframe
        self.NN_tags.fit(self.df.loc[:,'TE000':'TE511'].values)
    
    def gen_query(self, query):
        # takes text or PIL image and generates its embeddings vector
        if isinstance(query, Image.Image):
            self.query_embedding_type = 'image'
        elif isinstance(query, str):
            self.query_embedding_type = 'text'
        else:
            self.query_embedding_type = None
            return
        # encode input
        self.query_embedding = self.clip_model.encode([query])

    def _search_with_model(self, model, k=5):
        # search for the top k similar embeddings in 
        # with specified model
        emb_dist, emb_idxs = model.kneighbors(X=self.query_embedding,
                                                n_neighbors=k, 
                                                return_distance=True)
        #return df rows matching the numpy embeddings indexes
        df_result = self.df.loc[emb_idxs[0],self.result_df_cols]
        # add distances values to df_result
        df_result['Distance'] = emb_dist[0]
        return df_result


    def search_in_images(self, k=5):
        # search the top k similar images embeddings in dataset
        # for the las generated query embedding
        return self._search_with_model(self.NN_images, k)

    def search_in_names(self, k=5):
        # search the top k similar item names embeddings in dataset
        # for the las generated query embedding
        return self._search_with_model(self.NN_it_name, k)

    def search_in_tags(self, k=5):
        # search the top k similar tags embeddings in dataset
        # for the las generated query embedding
        return self._search_with_model(self.NN_tags, k)



#------------------


def plot_images(df, images_path, with_distance=True, rows=False):
    #plots images of items in dataframe
    #limit to a maximum number of 15 images
    nimages = min(15, df.shape[0])

    figsize = (40, 50) # width, height
    if rows:
        #plot images in a row
        fig, axarr = plt.subplots(1, nimages, figsize=figsize);
    else:
        #plot images in a column
        fig, axarr = plt.subplots(nimages, 1, figsize=figsize);

    for i, (df_index, row) in enumerate(df.iterrows()):
        # extract image path from shopname and itemid columns 
        image_path = images_path / (row['ShopName'] + '_' + str(row['ItemId']) + '.jpg')
        image = Image.open(image_path)

        axarr[i].imshow(image);
        axarr[i].axis('off');
        bestseller_mark = '*Bestseller*\n\n' if row['IsBestseller'] else ''

    
        out_message = f'''{bestseller_mark}Shop: {row['ShopName']}

ItemID: {row['ItemId']}

Title:
{add_carriage_return(row['ItemName'], char_limit=25)}

Reviews: {row['NumReviews']}

Distance: {row['Distance']:.4f}
'''
        
        axarr[i].annotate(out_message, xy=(1, 0.5), xycoords='axes fraction', fontsize=60,
                     horizontalalignment='left', verticalalignment='center')
        '''
        if with_distance:
            # Prints also embeddings distance in title
            axarr[i].set_title(
                f"{bestseller_mark}Shop: {row['ShopName']} ItemID:{row['ItemId']}\n{row['ItemName']}\nReviews: {row['NumReviews']} {row['Distance']:.4f}",
                 fontsize=60);
        else:
            axarr[i].set_title(
                f"{bestseller_mark}{row['ShopName']}\n{row['ItemId']}\n{row['ItemName'][:15]}\nrevs: {row['NumReviews']}",
                 fontsize=24);
        '''
            
    plt.tight_layout();

    # Return plot as a PIL image
    # render the plot onto a buffer
    buf = io.BytesIO()
    fig.savefig(buf,bbox_inches='tight', pad_inches=0)#, dpi=dpi)
    buf.seek(0)
    return PIL.Image.open(buf).convert('RGB')







'''
def plot_images(df, images_path, with_distance=True, rows=False):
    #plots images of items in dataframe
    #limit to a maximum number of 15 images
    nimages = min(15, df.shape[0])

    figsize = (40, 50) # width, height
    if rows:
        #plot images in a row
        fig, axarr = plt.subplots(1, nimages, figsize=figsize);
    else:
        #plot images in a column
        fig, axarr = plt.subplots(nimages, 1, figsize=figsize);

    for i, (df_index, row) in enumerate(df.iterrows()):
        # extract image path from shopname and itemid columns 
        image_path = images_path / (row['ShopName'] + '_' + str(row['ItemId']) + '.jpg')
        image = Image.open(image_path)

        axarr[i].imshow(image);
        axarr[i].axis('off');
        bestseller_mark = '*' if row['IsBestseller'] else ''
        
        if with_distance:
            # Prints also embeddings distance in title
            axarr[i].set_title(
                f"{bestseller_mark}Shop: {row['ShopName']} ItemID:{row['ItemId']}\n{row['ItemName']}\nReviews: {row['NumReviews']} {row['Distance']:.4f}",
                 fontsize=60);
        else:
            axarr[i].set_title(
                f"{bestseller_mark}{row['ShopName']}\n{row['ItemId']}\n{row['ItemName'][:15]}\nrevs: {row['NumReviews']}",
                 fontsize=24);
        
            
    plt.tight_layout();

    # set the figure with a specific size and dpi
    #output_width = 600
    #output_height = 1200
    #dpi = 200
    #output_width_inches = output_width / dpi
    #output_height_inches = output_height / dpi
    #plt.gcf().set_size_inches(output_width_inches, output_height_inches)

    # Return plot as a PIL image
    # render the plot onto a buffer
    buf = io.BytesIO()
    fig.savefig(buf,bbox_inches='tight', pad_inches=0)#, dpi=dpi)
    buf.seek(0)
    return PIL.Image.open(buf).convert('RGB')
    '''