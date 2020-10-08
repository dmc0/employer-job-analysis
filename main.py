# <codecell> Description
# -*- coding: utf-8 -*-
"""
Cells should work in Spyder and Jupyter notebooks IDEs
Requirements
1. Python 3.7 or higher

Created on Thu Sep  3 15:20:12 2020

@author: David McNamara
"""

# <codecell> Imports
import time
import string
import emp_job_analysis as eja

# <codecell> User defined variables
job_desc_folder = 'D://data//employment//description//LinkedIn//'

words_ignore_file = 'words-ignore.txt'

# Analysis results will also be sorted in this order
word_category_files = ['words-key.txt', 'words-softskills.txt']

NUM_WORDS_BEFORE = 5
NUM_WORDS_AFTER = 5

# -1 = process all files.  Set it to a specific number for debugging.
NUM_FILES_TO_PROCESS = -1

remove_chars = set(string.punctuation)
remove_chars.add('’')

split_chars_arr = ['!','&', '(', ')', '=', '{', '[', '}', ']', '|', ';', ':', '"', ',', '<', '.', '>', '?', '’']
split_chars = str(split_chars_arr) 

# <codecell> variable loading and setup

t_start = time.perf_counter()

eja.initialize(job_desc_folder, words_ignore_file, word_category_files)

df_word_counts, df_jobs_sorted = eja.process_files(split_chars, NUM_WORDS_BEFORE, NUM_WORDS_AFTER, remove_chars, NUM_FILES_TO_PROCESS)

t_stop = time.perf_counter()
print(f'Elapsed time (secs) = {t_stop - t_start}')

# %%
