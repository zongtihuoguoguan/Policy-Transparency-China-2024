POLICY TRANSPARENCY CHINA

This repository contains all the code and datasets collected and processed for the POLICY TRANSPARENCY CHINA project, to be published in an academic journal soon (tm). It primarily relies on Python and Jupyter Notebooks. It is provided to the public for reuse and review.

**Installing and running**

Each script has been tested to run on a Windows machine with the Anaconda environment file supplied. 
-- CheckDeletion.py: checks from a dataset whether or not the documents are still available today. The sample used for the paper can be found in "Dataset for Fig_5.xlsx". 
-- CheckGeoblocking.py: takes in the files "local_websites.xlsx"  and "national_websites.xlsx" to check whether the websites can be accessed from multiple locations across the world. Generates the file needed for figures 6-8. 
-- CreateCrossReferencedDataset.py: takes in a dataset of policy documents ("data.xlsx", not provided here) and creates the file needed for Tables 1-2, and Figure 4. 

The analysis files are subdivided by the figures/tables they correspond with.

**Datasets**

The repository contains the following datasets:

- A dataset containing multiple Excel sheets (under Document number datasets), retrieved from the official websites of the organs concerned in Summer 2023. It consists of the following parameters:
--- url: URL of the document 
--- pub_date_parsed: Publishing dates of the documents, extracted from the page of the URL
--- doc_number: The document number or 文号 in Chinese

- A dataset of referenced titles (Dataset for Table_1_2, Fig_4.xlsx). This has been generated using CreateCrossReferencedDataset.py and consists of the following parameters:
--- title: The title of the document being referred to (original)
--- cleaned_title: The title of the document being referred to (stripped down to only Chinese characters and numbers)
--- referral_date: the publishing date of the document making the referral
--- referred_in: the url of the document making the referral
--- fulltext_released_to_public: binary TRUE/FALSE whether or not the script was able to find the fulltext of the referred-to document
--- fulltext_pub_date: year that the referred-to document was found
--- fulltext_url: URL of the referred-to document

- A dataset of policies on Open Government Information (Dataset for Fig_1.xlsx). This has been scraped from official government websites. See the paper for more details. It consists of the following parameters:
--- Database: source website
--- Date: issuing date of the policy
--- Year: issuing year of the policy
--- Link: URL of the document
--- Title: original title of the document
--- Body: body text of the document (in some cases, shows an "error" or "nan" if no content was found, e.g. if the content was in image format)

- The results of the test for deletion of documents (Dataset for Fig_5.xlsx). This is generated through CheckDeletion.py. The parameters are:
--- Database: source website
--- Link: URL of the document
--- Result: HTTP status code 

- The results of the test for geoblocking (Dataset for Fig_6_7_8.xlsx). This is generated through CheckGeoblocking.py. It displays the result per server by displaying its HTTP status code. 

Not included in this repository are one dataset and one code file:
-- Dataset: data.xlsx
-- Code: the Scraper.py used to collect the data.xlsx



