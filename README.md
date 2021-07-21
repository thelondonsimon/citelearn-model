# CiteLearn Model Development

The CiteLearn models and training data described here attempt to provide predictions as to whether a sentence is in need of a citation.

The models are served as part of the [CiteLearn](https://github.com/thelondonsimon/citelearn) project developed by the University of Technology, Sydney (UTS).

## Training Data Set

In addition to training models using the original [Citation Needed](https://github.com/mirrys/citation-needed-paper) data sets, the [training-data/parseWikiArticles.py](training-data/parseWikiArticles.py) script provides an alternate method for harvesting data from [Wikipedia's *Featured Articles*](https://en.wikipedia.org/wiki/Wikipedia:Featured_articles).

The list of Featured Articles is subject to change (articles can be added and removed), and the training data set compiled here is based on the same set of 5,259 articles which were used for the Citation Needed model. The Wikipedia identifiers for these articles are at [training-data/fa-article-ids.txt](training-data/fa-article-ids.txt).

The training data input is based on discrete sentences. To obtain this input, the script process each featured article by:

* Downloading and parsing the HTML for each Featured Article
* Splitting each article into sentences
* Identifying the H2 and H3 level headings which each sentence falls under
* Detecting if each sentence either has a citation or has a *citation needed* flag
* Identifying if each sentence's preceding and subsequent sentences each has a citation
* Identifying if the paragraph which the sentence is part of has any citations

The last two items aim to capture some of the contextual considerations as to whether a sentence requires a citation. If a citation is provided in a neighbouring sentence, it likely lowers the likelihood that a citation is required.

The output of the parser is a TSV with the following information for each discrete sentence:

* **Article ID**: The Wikipedia article identifier
* **H2 Heading**: The H2-level heading label for the sentence
* **H3 Heading**: The H3-level heading label for the sentence
* **H2 #**: The sequential index for the sentence's H2 heading (zero indicates no H2 heading)
* **H3 #**: The sequential index for the sentence's H3 heading (zero indicates no H3 heading)
* **Paragraph #**: The sequential index for the sentence's paragraph in the current heading block
* **Sentence #**: The sequential index of the sentence in its paragraph
* **Sentence**: The sentence to be analysed
* **Has Citation**: Whether the sentence has (or needs) a citation
* **Paragraph Has Citation**: Whether the paragraph the sentence is in has any citations
* **Previous Sentence Has Citation**: Whether the preceding sentence (in the same paragraph) has a citation
* **Next Sentence Has Citation**: Whether the subsequent sentence (in the same paragraph) has a citation

## Model Training

TensorFlow was used to train the model using BERT word embeddings.

The model training scripts are published as Google Colab notebooks:

* [notebooks/citelearn-model-fa-cldata.ipynb](notebooks/citelearn-model-fa-cldata.ipynb): Trains a model using the revised Featured Article dataset described above
* [notebooks/citelearn-model-fa-cndata.ipynb](notebooks/citelearn-model-fa-cndata.ipynb): Trains a model using the original Featured Article dataset from the Citation Needed project
