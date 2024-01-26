# -*- coding: utf-8 -*-
"""
NOTE: The dataset used here is not released to the public
as it is owned by a third party. The code is only released for re-use on 
other datasets or for peer review.
"""

# imports
import pandas as pd
import re
import progressbar as pb
import numpy as np
from functools import partial
from multiprocessing import Pool, Process

# set this to max processor cores your system can dedicate to this task
num_processes = 5

class CrossReference():
    def __init__(self, data_to_check, full_data, i):
        """
        Checks whether documents in a dataframe have been released to the public by cross-referencing
        each document with the dataset of released documents. Saves it to an Excel file to be stitched
        back together after multiprocessing is done

        Parameters
        ----------
        data_to_check : Pandas DataFrame
            Contains all the document titles you want to check if they have been released to the public.
        full_data : Pandas DataFrame
            Contains all published documents you want to check against.
        i : Int
            The number of the process, used to save the dataframe and stich them back together later.

        """
        
        exists = []
        dates = []
        links = []
        shortened_t = []

        def find_doc(t, df):
            """
            Checks a title against the full dataframe to see if it exists

            Parameters
            ----------
            t : String
                Title to check.
            df : Pandas DataFrame
                Contains all published documents you want to check against.

            Returns
            -------
            bool
                True if document has been published, else False.
            Int or NoneType
                The year a document was published, or NoneType if not published.
            String or NoneType
                The url of the published document, or NoneType if not published.

            """
            
            
            for k in range(len(df)):
                # check exact match of title 
                if t == df["title_clean"][k]:
                    return True, df["Year"][k], df["Link"][k]
                # check non-exact match of title
                elif (t in str(df["title_clean"][k])) and df["doc_type"][k] not in ["新闻", "解读"]:
                    return True, df["Year"][k], df["Link"][k]
            return False, None, None

        for j in range(len(data_to_check)):
            title = data_to_check["title"][j]
            t = re.sub("[^\u4e00-\u9FFF\d]", "", title)
            e, d, l = find_doc(t, full_data)
            exists.append(e)
            dates.append(d)
            links.append(l)
            shortened_t.append(t)

        data_to_check["fulltext_released_to_public"] = exists
        data_to_check["fulltext_pub_date"] = dates
        data_to_check["fulltext_url"] = links
        data_to_check["cleaned_title"] = shortened_t
        data_to_check.to_excel(f".//data_{str(i)}.xlsx")


if __name__ == "__main__":
    # load data, sort by date, filter to date >= 2008
    df = pd.read_excel(".\\data.xlsx").sort_values(by=["Publishing date"], ascending=True)
    df = df.loc[df["Year"].astype(int) >= 2008].reset_index(drop=True)
    # strip title down to only characters and numbers
    df["title_clean"] = df["Title"].str.replace(r'[\u4e00-\u9FFF\d]', "", regex=True)
    # only national level documents
    df = df.loc[df["administrative_level"] == "Central"].reset_index(drop=True)

    def parse_referred_titles(df):
        """
        Extracts all referenced titles from a dataset

        Parameters
        ----------
        df : Pandas DataFrame
            Contains all documents to be extracted from.

        Returns
        -------
        data : Pandas DataFrame
            Contains all extracted titles with their information.

        """
        
        list_of_titles = []
        list_of_referral_dates = []
        list_of_referral_urls = []
        
        # progressbar as script can take long to finish (+= 15 mins on 300k documents)
        widgets = [f' Parsing {str(len(df))} documents', pb.Percentage(), ' ',pb.Bar(marker=pb.RotatingMarker()), ' ', pb.ETA()]
        timer = pb.ProgressBar(widgets=widgets, maxval=len(df)).start()
        
        # iterate through each document in database
        for i in range(len(df)):
            # regex for referred-titles
            # note: this also extracts self-references and references to e.g., attachments
            x = re.findall("[《〈][^》]{7,60}[》〉]", str(df["Body"][i]))
            for string in x:
                # only append if not already in list
                if string[1:-1] not in list_of_titles:
                    list_of_titles.append(string[1:-1])
                    list_of_referral_dates.append(df["Publishing date"][i])
                    list_of_referral_urls.append(df["Link"][i])
            timer.update(i)
        timer.finish()
        
        data = pd.DataFrame({"title": list_of_titles, "referral_date": list_of_referral_dates, "referred_in": list_of_referral_urls})
        return data
            
    data = parse_referred_titles(df)
    
    # break dataframes up in chunks for multiprocessing    
    dataframes = np.array_split(data, num_processes)
    checked_data = pd.DataFrame()
    func = partial(CrossReference)
    processes = []
    
    # execute processes
    for i in range(num_processes):
        print(f"process {str(i)} starting")
        process_data = dataframes[i].reset_index(drop=True)
        process = Process(target=func, args=(process_data, df, i))
        processes.append(process)
        process.start()    
    for process in processes:
        process.join() 
    
    # stich partial dataframes back together
    cross_referenced = pd.DataFrame()
    for i in range(num_processes):
        df = pd.read_excel(f".//data_{str(i)}.xlsx")
        cross_referenced = pd.concat([cross_referenced, df])
    cross_referenced.to_excel(".//cross_referenced.xlsx")





