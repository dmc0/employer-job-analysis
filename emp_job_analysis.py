# -*- coding: utf-8 -*-
"""
Created on Mon Sep 14 15:20:56 2020

@author: david
"""

import os
import sys
import pandas as pd
from pathlib import Path

this = sys.modules[__name__]

this.word_categories = []
this.ignore_words = []
this.path_job_desc = Path('')

COL_LINE_NUM = 0
COL_WORD_NUM = 1
COL_IGNORE_WORD = 2
COL_SORT_ORDER = 3
COL_CATEGORY = 4
COL_WORD_ORIG = 5
COL_WORD = 6
COL_WORD_CONTEXT = 7

# <codecell> functions
def initialize(job_desc_folder, words_ignore_file, word_category_files):
    this.path_job_desc = Path(job_desc_folder)

    if this.path_job_desc.exists() == False:
        print(f'This path does not exist: {this.path_job_desc}')
        sys.exit()
    
    words_ignore_path = Path(words_ignore_file)
    
    if words_ignore_path.exists() == False:
        print(f'This file does not exist: {words_ignore_path}')
        sys.exit()
    
    with open(words_ignore_file, 'r', encoding='utf8') as f:  
        this.ignore_words = [l.strip() for l in f.readlines()]    

    prev_word_list = []
    prev_word_list.append([words_ignore_file, this.ignore_words])
    
    for sort_order, fn in enumerate(word_category_files, 1):
        cat_file = Path(fn)
    
        if cat_file.exists() == False:
            print(f'This file does not exist: {cat_file}')
            sys.exit()
        
        last_period_char = -1 * (fn[::-1].find('.') + 1)
        file_name = fn[:last_period_char]
        category = file_name.split('-')[1].strip()
        
        with open(fn, 'r', encoding='utf8') as f:  
            w_lines = [l.strip() for l in f.readlines()]  
    
        for pwl in prev_word_list:
            word_intersect = set(pwl[1]) & set(w_lines)
            if len(word_intersect) > 0:
                dup_words = ', '.join(word_intersect)
                print(f'The file {fn} contains words that are also in the {pwl[0]} file.  Words must be unique across all "words-" files.  These are the duplicate words: {dup_words}')
                sys.exit()
            
        this.word_categories.append([sort_order, category, w_lines])
    
        prev_word_list.append([fn, w_lines])

def process_surr_words(file_line_words, NUM_WORDS_BEFORE, NUM_WORDS_AFTER):
# Process words before and after the word being counted
    try:
        file_line_words_len = len(file_line_words)
        list_pos = 0

        while list_pos < file_line_words_len:
            words_after = ''
            words_before = ''
            word_pos = 0

            while word_pos <= NUM_WORDS_AFTER:
                if (list_pos + word_pos) < file_line_words_len:
                    words_after += file_line_words[list_pos + word_pos][COL_WORD_ORIG] + ' '
                    
                word_pos += 1

            word_pos = NUM_WORDS_BEFORE

            while word_pos > 0:  
                if (list_pos - word_pos) >= 0:
                    words_before += file_line_words[list_pos - word_pos][COL_WORD_ORIG] + ' '

                word_pos -= 1
                
            file_line_words[list_pos][COL_WORD_CONTEXT] = words_before + ' ' + words_after

            list_pos += 1            
    except:
        for e in sys.exc_info():
            print(e)
    else:
        return file_line_words
    
def process_phrase_matches(file_line_words):
    try:
        file_line_words_len = len(file_line_words)
        
        for wc in this.word_categories:
            keep_phrase_words = [x.split() for x in wc[2]]
                
            l_sort_order = wc[0]
            l_category = wc[1]
    
            for flw_num, flw in enumerate(file_line_words):
                for kp in keep_phrase_words:
                    phrase_match = 1
                    line_idx = flw_num
                    
                    for kpw in kp:
                        if line_idx >= file_line_words_len:
                            break
    
                        if kpw.lower() != file_line_words[line_idx][COL_WORD].lower():
                            phrase_match = 0
                            break
    
                        line_idx += 1
    
                    if phrase_match == 1:
                        file_line_words[flw_num][COL_WORD] = ' '.join(kp).strip()
                        # set 1 for phrase
                        file_line_words[flw_num][COL_CATEGORY] = l_category
                        file_line_words[flw_num][COL_SORT_ORDER] = l_sort_order
                        line_idx_2 = flw_num
                        
                        for kpw in kp:
                            if line_idx_2 == flw_num:
                                line_idx_2 += 1
                                continue
                            else:
                                file_line_words[line_idx_2][COL_WORD] = ''

        return file_line_words

    except:
        for e in sys.exc_info():
            print(e)


def process_chars(file_line_words, remove_chars):
    try:
        for flw_num, flw in enumerate(file_line_words):
            # don't process if it's a phrase
            if len(flw[COL_CATEGORY]) == 0:
                for c in remove_chars:
                    flw[COL_WORD] = flw[COL_WORD].replace(c, ' ')
                
                flw[COL_WORD] = flw[COL_WORD].strip()
                word_split = flw[COL_WORD].split()

                if len(word_split) > 1:
                    for w_num, w in enumerate(word_split):
                        if w_num == 0:
                            flw[COL_WORD] = w.strip()
                        else:
                            flw_new = [flw[0], flw[1], flw[2], flw[3], flw[4], flw[5], flw[6], flw[7]]     
    
                            flw_new[COL_WORD] = w.strip()                           
                            file_line_words.append(flw_new)
    
    except Exception as exc:
        fname = sys._getframe().f_code.co_name
        print(fname, ':', exc)
        raise
    else:
        return file_line_words

def process_ignore_words(file_line_words):
    try:
        for flw in file_line_words: 
            # if it's not a phrase
            if len(flw[COL_CATEGORY]) == 0:
                if (flw[COL_WORD].strip().lower() in this.ignore_words) or (len(flw[COL_WORD].strip()) <= 1):
                    flw[COL_IGNORE_WORD] = 1

        return file_line_words
    except:
        for e in sys.exc_info():
            print(e)
            
def process_file(lines, split_chars, NUM_WORDS_BEFORE, NUM_WORDS_AFTER, remove_chars):
    try:
        file_line_words_surr = []
        file_line_words = []

        for line_num, fl in enumerate(lines):
            for word_num, lw in enumerate(fl.split()):                
                file_line_words_surr.append([line_num, word_num, 0, 99, '', lw.strip(), lw.strip(), ''])

        file_line_words_surr = process_surr_words(file_line_words_surr, NUM_WORDS_BEFORE, NUM_WORDS_AFTER)
        
        for line_num, flws in enumerate(file_line_words_surr):
            for c in split_chars:
                flws[COL_WORD] = flws[COL_WORD].replace(c, ' ')                
            
            for w in flws[COL_WORD].split():                
                file_line_words.append([flws[0], flws[1], flws[2], flws[3], flws[4], flws[5], w.strip(), flws[7]]) 
        
        file_line_words = process_phrase_matches(file_line_words)
                
        file_line_words = process_chars(file_line_words, remove_chars)

        file_line_words = process_ignore_words(file_line_words)
        
        # check again for phrase matches after punctuation has been removed
        file_line_words = process_phrase_matches(file_line_words)

        return file_line_words

    except:
        for e in sys.exc_info():
            print(e)
              

# <codecell> Process Files
def process_files(split_chars, NUM_WORDS_BEFORE, NUM_WORDS_AFTER, remove_chars):
    df_job_desc = pd.DataFrame(columns=['job_id', 'line_num', 'word_pos', 'sort_order', 'category', 'word_lc', 'word', 'word_context'])
    df_company_position = pd.DataFrame(columns=['job_id', 'company_name', 'position'])
    
    for job_id, fn in enumerate(this.path_job_desc.glob('*.txt'), 1):
        try:
            file_name = str(fn)
            print(f'file_name = {file_name}')
        
            file_name = os.path.basename(file_name)
            file_name = file_name[:len(file_name) - 4]
            company_name = file_name.split('-')[0].strip()
            position = file_name.split('-')[1].strip()
        
            df_company_position = df_company_position.append({'job_id': job_id, 'company_name' : company_name, 'position': position}, ignore_index=True)
        
            file_lines = []    
            
            # Ignoring errors does not halt the particular file's processing.  
            # It skips the characters that cannot be decoded.
            with open(fn, 'r', encoding='utf8', errors='ignore') as f:  # , errors='ignore'
                file_lines = f.readlines()
            
            words_final = process_file(file_lines, split_chars, NUM_WORDS_BEFORE, NUM_WORDS_AFTER, remove_chars)
    
            for word_pos, w in enumerate(words_final):
                if w[COL_IGNORE_WORD] != 1:
                    df_job_desc = df_job_desc.append({\
                    'job_id': job_id, \
                    'line_num': w[COL_LINE_NUM], \
                    'word_pos': w[COL_WORD_NUM], \
                    'sort_order': w[COL_SORT_ORDER], \
                    'category': w[COL_CATEGORY], \
                    'word_lc': w[COL_WORD].lower(), \
                    'word': w[COL_WORD], \
                    'word_context': w[COL_WORD_CONTEXT]}, ignore_index=True)                   
                        
            #break
        except:
            for e in sys.exc_info():
                print(e)
            print(f'company_name = {company_name}, position = {position}')
            break
        
    return process_reports(df_company_position, df_job_desc)
    

# <codecell> Load DataFrames
def process_reports(df_company_position, df_job_desc):  
    df_jobs = df_job_desc.set_index('job_id').join(df_company_position.set_index('job_id'), on='job_id', how='inner', rsuffix='_company')
    
    df_jobs = df_jobs.reset_index()
    
    df_word_counts = df_jobs[['sort_order', 'category', 'word_lc', 'word']].groupby(['sort_order', 'category', 'word_lc']).count()
    df_word_counts = df_word_counts.rename(columns={'word': 'word_count'})
    df_word_counts = df_word_counts.sort_values(by=['sort_order', 'word_count'], ascending=[True, False])
    
    
    df_jobs_sorted = df_jobs[['sort_order', 'category', 'word_lc', 'word', 'word_context', 'company_name', 'position', 'job_id', 'line_num', 'word_pos']]
    
    
    df_jobs_sorted = df_jobs_sorted.sort_values(by=['sort_order', 'category', 'word_lc', 'word_context'], ascending=[True, True, True, True])
    
    df_word_counts.to_csv('word_counts.csv')
    df_jobs_sorted.to_csv('df_job_desc_words.csv', index=False)
    
    return df_word_counts, df_jobs_sorted