import urllib
import urllib.request
import json
from tqdm import tqdm
from os.path import isfile, join, sep, getsize, exists
from os import listdir, makedirs
import re
from fuzzywuzzy import fuzz

import config

DIR_FINAL = join("scripts", "final")


tmdb_api_key = config.tmdb_api_key
omdb_api_key = config.omdb_api_key

movielist = [join(DIR_FINAL, f) for f in listdir(DIR_FINAL) if isfile(
    join(DIR_FINAL, f)) and getsize(join(DIR_FINAL, f)) > 3000]

mapping = {}

def camel_case_split(str):
    return re.findall(r'([A-Z0-9]+|[A-Z0-9]?[a-z]+)(?=[A-Z0-9]|\b)', str)

def search_name(name):
    name = " ".join(name.split("-"))
    if re.sub(r"(\d{4})", "", name).strip() != "":
        name = re.sub(r"(\d{4})", "", name)
    name = " ".join(camel_case_split(re.sub(r'\([^)]*\)', '', name))).lower()
    name = name.replace('transcript', "").replace(
        'script', "").replace("early draft", "").replace(
            "first draft", "").replace('transcript', "").replace(
            'production', "").replace("final draft", "").replace(
            'unproduced', "").replace("pdf", "").replace(
            'html', "").replace("doc", "").replace(
            'the ', "").replace(" the", "").strip()
    if name.endswith('final'):
        name = name.replace('final', "").strip()
    if name.endswith('early'):
        name = name.replace('early', "").strip()
    if name.endswith('shoot'):
        name = name.replace('shoot', "").strip()
    if name.endswith('shooting'):
        name = name.replace('shooting', "").strip()
    name = ' '.join(name.split())
    return name

# for movie in tqdm(movielist):
#     name = search_name(movie.split(sep)[-1].split('.txt')[0])
#     response = urllib.request.urlopen(
#         "https://api.themoviedb.org/3/search/movie?api_key=" + 
#         tmdb_api_key + "&language=en-US&query=" + urllib.parse.quote(name)
#         +"&page=1")
#     html = response.read()
#     jres = json.loads(html)
#     if jres['total_results'] > 0:
#         mapping[movie.split(sep)[-1].split('.txt')[0]] = jres['results']
#     else:
#         name = movie.split(sep)[-1].split('.txt')[0]
#         response = urllib.request.urlopen(
#             "https://api.themoviedb.org/3/search/movie?api_key=" +
#             tmdb_api_key + "&language=en-US&query=" + urllib.parse.quote(name)
#             + "&page=1")
#         html = response.read()
#         jres = json.loads(html)
#         if jres['total_results'] > 0:
#             mapping[movie.split(sep)[-1].split('.txt')[0]] = jres['results']
#         else:
#             name = " ".join(movie.split(sep)[-1].split('.txt')[0].split("-"))
#             name = " ".join(camel_case_split(name))
#             response = urllib.request.urlopen(
#                 "https://api.themoviedb.org/3/search/movie?api_key=" +
#                 tmdb_api_key + "&language=en-US&query=" + urllib.parse.quote(name)
#                 + "&page=1")
#             html = response.read()
#             jres = json.loads(html)
#             if jres['total_results'] > 0:
#                 mapping[movie.split(sep)[-1].split('.txt')[0]] = jres['results']
#             else:
#                 mapping[movie.split(sep)[-1].split('.txt')[0]] = []

    
#     # print(name)

# json_object = json.dumps(mapping)

# with open(join("metadata", "metadata.json"), "w") as outfile:
#     outfile.write(json_object)

with open(join("metadata", "metadata.json"), 'r') as f:
  mapping = json.load(f)

def average_ratio(n, m):
    return ((fuzz.token_sort_ratio(n,  m) + fuzz.token_sort_ratio(m,  n)) // 2)

not_found = []

count = 0
movie_info = {}


for key in mapping:
    if len(mapping[key]) == 0:
        count += 1
        n = key.split('.txt')[0]
        not_found.append(n)
        # print(search_name(key.split('.txt')[0])," : ", n)
        movie_info[key] = {}
    elif len(mapping[key]) > 1:
        name = re.sub(r'\([^)]*\)', '',
                      " ".join(key.split('.txt')[0].replace("transcript", "").split("-"))).lower()
        m = mapping[key][0]['title'].replace(
            '\'', '').replace(",", '').replace(
            '.', '').replace('&', 'and').lower()
        m2 = mapping[key][1]['title'].replace(
            '\'', '').replace(",", '').replace(
            '.', '').replace('&', 'and').lower()
        m = re.sub(r'\([^)]*\)', '', m)
        m2 = re.sub(r'\([^)]*\)', '', m2)
        if average_ratio(name, m) < average_ratio(name, m2) and abs(average_ratio(name, m) - average_ratio(name, m2)) > 10:
            m = m.split(":", 1)[0]
            m2 = m2.split(":", 1)[0]
            if average_ratio(name, m) < average_ratio(name, m2) and abs(average_ratio(name, m) - average_ratio(name, m2)) > 10:
                # print(key.split('.txt')[0], " : ", mapping[key]
                #     [0]['title'], " | ", mapping[key][1]['title'])
                movie_info[key] = mapping[key][1]
            else: 
                movie_info[key] = mapping[key][0]

        else:
            movie_info[key] = mapping[key][0]
            
    elif len(mapping[key]) == 1:
        movie_info[key] = mapping[key][0]
    else:
        print("what???")

# print(count)


json_object = json.dumps(movie_info, indent=4)

with open(join("metadata", "info.json"), "w") as outfile:
    outfile.write(json_object)

with open(join("metadata", "info.json"), 'r') as f:
  movie_info = json.load(f)

not_matched = []

count = 0
for key in movie_info:
    if movie_info[key]:
        name = re.sub(r'\([^)]*\)', '',
                      " ".join(key.split('.txt')[0].replace("transcript", "").split("-"))).lower().replace("the ", "").replace(" the", "")
        m = movie_info[key]['title'].replace(
            '\'', '').replace(",", '').replace(
            '.', '').replace('&', 'and').lower().replace("the ", "").replace(" the", "")
        m = re.sub(r'\([^)]*\)', '', m)
        m_join = "".join(m.split())
        name = re.sub(r'\([^)]*\)', '', name)
        m_rem = m.replace(":", "")
        m_split = m.split(":", 1)[0]
        m_alt = m.split(":", 1)[1] if len(
            m.split(":", 1)) != 1 else m_split
        if average_ratio(name, m) < 80 and average_ratio(name, m_rem) < 80 and average_ratio(name, m_rem) < 80 and (average_ratio(name, m_split) < 80) and (average_ratio(name, m_alt) < 80) and (average_ratio(name, m_join) < 80) and fuzz.partial_ratio(name, m) < 80 and fuzz.partial_ratio(m, name) < 80:
            m_original = movie_info[key]['original_title'].replace(
                '\'', '').replace(",", '').replace(
                '.', '').replace('&', 'and').lower().replace("the ", "").replace(" the", "")
            m_original = re.sub(r'\([^)]*\)', '', m_original)
            if average_ratio(name, m_original) < 80:

                # print(key.split('.txt')[0], " : ", movie_info[key]
                #       ['title'], ' , ', average_ratio(name, m))
                not_matched.append(key)
                count += 1

print(len(not_matched) + len(not_found))
        

omdb_info = {}

for movie in tqdm(not_matched):
    name = search_name(movie.split(sep)[-1].split('.txt')[0])
    response = urllib.request.urlopen(
        "http://www.omdbapi.com/?apikey=" +
        omdb_api_key + "&t=" + urllib.parse.quote(name)
        + "&plot=full")
    html = response.read()
    jres = json.loads(html)
    if jres['Response'] != "False":
        omdb_info[movie.split(sep)[-1].split('.txt')[0]] = jres
    else:
        name = movie.split(sep)[-1].split('.txt')[0]
        response = urllib.request.urlopen(
            "http://www.omdbapi.com/?apikey=" +
            omdb_api_key + "&t=" + urllib.parse.quote(name)
            + "&plot=full")
        html = response.read()
        jres = json.loads(html)
        if jres['Response'] != "False":
            omdb_info[movie.split(sep)[-1].split('.txt')[0]] = jres
        else:
            name = " ".join(movie.split(sep)[-1].split('.txt')[0].split("-"))
            name = " ".join(camel_case_split(name))
            response = urllib.request.urlopen(
                "http://www.omdbapi.com/?apikey=" +
                omdb_api_key + "&t=" + urllib.parse.quote(name)
                + "&plot=full")
            html = response.read()
            jres = json.loads(html)
            if jres['Response'] != "False":
                omdb_info[movie.split(sep)[-1].split('.txt')[0]]=jres
            else:
                omdb_info[movie.split(sep)[-1].split('.txt')[0]]={}


    # print(name)

json_object = json.dumps(omdb_info, indent=4)

with open(join("metadata", "omdb_unmatched_metadata.json"), "w") as outfile:
    outfile.write(json_object)
