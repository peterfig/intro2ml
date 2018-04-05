# Introductory Python Machine Learning Class #
## How do I run the notebooks?

## Method 0: pip install in your already crowded Python environment
  * `pip install pandas jupyter numpy nltk gensim pyLDAvis`
  * Clone this repo: `git clone https://github.com/peterfig/intro2ml.git`.  (Perhaps preceeded by `brew install git`.)
  * Move into the repo: `cd intro2ml`.
  * Launch the notebook server in the browser with `jupyter notebook`
  
## Method 1: run locally, using a new virtual environment

  * `mkvirtualenv nlpclass`.  (If you haven't installed `virtualenvwrapper`, try `sudo pip3 install virtualenvwrapper`.  For MacOS, see this [helpful video.](https://www.google.com/search?q=install+virtualenvwrapper+mac&oq=install+virtualenvwrapper+mac&aqs=chrome..69i57j0l5.5953j0j7&sourceid=chrome&ie=UTF-8#kpvalbx=1)
  * Clone this repo: `git clone https://github.com/peterfig/intro2ml.git`.  (Perhaps preceeded by `brew install git`.)
  * Move into the repo: `cd intro2ml`.
  * `pip install -r requirements.txt` to install the required Python libraries.
  * Install the Python kernel into IPython/Jupyter notebooks: ` python -m ipykernel install --user --name nlpclass --display-name "nlp class"`
  * Download the required data for use by `nltk`.
    * `python` from the command line
    * `import nltk`
    * `nltk.download()`.
    * This will bring up a GUI where you can download the `nltk` data.
  * Launch the notebook server in the browser with `jupyter notebook`

## Method 2: Run from Docker container
(under construction)
