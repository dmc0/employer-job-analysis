# -*- coding: utf-8 -*-
"""
Requirements
1. Python 3.7 or higher

Created on Thu Sep  3 15:20:12 2020

@author: David McNamara
"""

import string
import pandas as pd
from pathlib import Path
import os
import sys
import time

job_desc_folder = 'D://data//employment//description//LinkedIn//'
keep_phrases = set(['SQL Server', 'global leader', 'data ingestion', 'C', 'C++', 'C#', 'R', 'F#', '.NET'])
ignore_words = set(['the', 'a', 'an', 'i', 'he', 'she', 'they', 'to', 'of', 'it', 'from', 'and', 'in', 'with', 'for', 'or', 'on', 'as', 'is', 'our', 'are', 'will', 'that', 'you', 'this', 'be', 'at', 'by', 'e.g.'])
    
num_words_before = 0
num_words_after = 5

remove_chars = set(string.punctuation)

c_col_word = 2
c_col_word_lc = 3
c_col_phrase = 4
c_col_line = 5

t_start = time.perf_counter()

p = Path(job_desc_folder)

if p.exists() == False:
    print(f'This path does not exist: {p}')
    sys.exit()
    
def process_phrase_matches(file_line_words, keep_phrases):
    try:
        file_line_words_len = len(file_line_words)
        keep_phrase_words = [x.split() for x in keep_phrases]
        
        for flw_num, flw in enumerate(file_line_words):
            for kp in keep_phrase_words:
                phrase_match = 1
                word_pos = flw_num
                for kpw in kp:
                    if word_pos >= file_line_words_len:
                        break
                    
                    if kpw.lower() != file_line_words[word_pos][c_col_word_lc]:
                        phrase_match = 0
                        break
                    
                    word_pos += 1
                    
                if phrase_match == 1:
                    file_line_words[flw_num][c_col_word_lc] = ' '.join(kp) 
                    # set 1 for phrase
                    file_line_words[flw_num][c_col_phrase] = 1
                    word_pos_2 = flw_num
                    for kpw in kp:
                        if word_pos_2 == flw_num:
                            word_pos_2 += 1
                            continue
                        else:
                            file_line_words[word_pos_2][c_col_word_lc] = '' 
                            
        return file_line_words
                            
    except:
        for e in sys.exc_info():
            print(e)

def process_file(file_lines, keep_phrases, remove_chars, num_words_before, num_words_after):
    file_line_words = []
    
    try:
        for line_num, fl in enumerate(file_lines):
            for word_num, lw in enumerate(fl.split()):
                file_line_words.append([line_num, word_num, lw, lw.lower(), 0, ''])
                
        file_line_words = process_phrase_matches(file_line_words, keep_phrases)
    
        file_line_words_pos = len(file_line_words)
        
        for flw_num, flw in enumerate(file_line_words):
            for c in remove_chars:
                flw[c_col_word_lc] = flw[c_col_word_lc].replace(c, ' ')
            
            # don't process if it's a phrase
            if flw[c_col_phrase] != 1:
                word_split = flw[c_col_word_lc].split()
                    
                if len(word_split) > 1:
                    for w_num, w in enumerate(word_split):
                        if w_num > 0:                    
                            flw_new = flw
                            flw_new[c_col_word_lc] = w
                            file_line_words.insert(file_line_words_pos, flw_new)
                            file_line_words_pos += 1
    
        file_line_words_pos = len(file_line_words)
        
        while file_line_words_pos > 0:
            file_line_words_pos -= 1
            flw = file_line_words[file_line_words_pos][c_col_word_lc]
            
            # if it's not a phrase
            if file_line_words[file_line_words_pos][c_col_phrase] != 1:
                if (flw in ignore_words) or (len(flw.strip()) <= 1):
                    del file_line_words[file_line_words_pos]
                    
        file_line_words_len = len(file_line_words)
        list_pos = 0
        
        while list_pos < file_line_words_len:
            words_surr = ''
            word_pos = 0
            
            while word_pos < num_words_after:
                if (list_pos + word_pos) < file_line_words_len:
                    words_surr += file_line_words[list_pos + word_pos][c_col_word] + ' '
                    
                word_pos += 1            
            
            flw = file_line_words[list_pos][c_col_line] = words_surr
            
            list_pos += 1
        
    except:
        for e in sys.exc_info():
            print(e)

        
     
    return file_line_words
            
df_job_desc =  pd.DataFrame(columns=['job_id', 'line_num', 'word_pos', 'word', 'word_lc', 'line'])
df_company_position = pd.DataFrame(columns=['job_id', 'company_name', 'position'])
# print(chars_to_remove)

for job_id, fn in enumerate(p.glob('*.txt'), 1):       
    file_name = str(fn)
    print(f'file_name = {file_name}')
    
    file_name = os.path.basename(file_name)
    file_name = file_name[:len(file_name) - 4]
    company_name = file_name.split('-')[0].strip()
    position = file_name.split('-')[1].strip()
    
    df_company_position = df_company_position.append({'job_id': job_id, 'company_name' : company_name, 'position': position}, ignore_index=True)
    
    with open(fn, 'r') as f:        
        try:
            file_lines = f.readlines()
             
            words_final = process_file(file_lines, keep_phrases, remove_chars, num_words_before, num_words_after)
            
            if len(words_final) == 0:
                continue

            for word_pos, w in enumerate(words_final):
                df_job_desc = df_job_desc.append({'job_id': job_id, 'line_num': w[0], 'word_pos': w[1], 'word': w[c_col_word], 'word_lc': str(w[c_col_word_lc]), 'line': w[c_col_line]}, ignore_index=True)

        except:
            for e in sys.exc_info():
                print(e)
            print(f'company_name = {company_name}, position = {position}')
            break
    
    break

    
df_jobs = df_job_desc.set_index('job_id').join(df_company_position.set_index('job_id'), on='job_id', how='inner', rsuffix='_company')
df_jobs = df_jobs.reset_index()
# df_word_counts = df_jobs['word'].value_counts(sort=True)

df_word_counts = df_jobs[['word_lc', 'word']].groupby(['word_lc']).count()
df_word_counts = df_word_counts.rename(columns={'word': 'word_count'})
df_word_counts = df_word_counts.sort_values(by='word_count', ascending=False)
df_word_counts.to_csv('word_counts.csv')

df_jobs_sorted = df_jobs.sort_values(by=['word_lc', 'line'])
df_jobs_sorted.to_csv('df_job_desc_words.csv')

t_stop = time.perf_counter()
print(f'Elapsed time (secs) = {t_stop - t_start}')
