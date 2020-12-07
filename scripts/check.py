# -*- coding: utf-8 -*-

# @Version : 1.0
# @Time    : 2019/09/16 18:12
# @Author  : lework
# @File    : check.py
# @Desc    : 用于检查指定开源软件的最新版本

import os
import sys
import json
import time
import requests
import threading
from datetime import datetime

##source-product.json
source_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'source-product.json')
data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../static/data/data.json')
docs_data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../docs/static/data/data.json')
tags_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../static/data/tags.json')
docs_tags_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../docs/static/data/tags.json')

token = os.environ.get('GITHUB_TOKEN', '')
if token == '':
    print('[Error] not found token.')
    sys.exit(1)

headers = {"Content-Type": 'application/json; charset=utf-8', "Authorization": "token %s" % token}

result = {
    "updated_at": "",
    "total": 0,
    "data": []
}

tags_result = {}

def sort_time(stime):
    data = None
    try:
        if '.' in stime :
            datetime.datetime.utcfromtimestamp(stime)
            data = datetime.strptime(stime, "%Y-%m-%dT%H:%M:%S.%fZ")
            return data
        data = datetime.strptime(stime, "%Y-%m-%dT%H:%M:%S%z")
    except Exception as e:
        print(stime, e)
        data = datetime.strptime("1970-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    return data


def get_github_latest_release(pro):
    data = {}
    resp = {}
    tag = False
    latest_url = "https://api.github.com/repos/%s/releases/latest" % pro['repo']

    if "version" in pro and pro['version'] == 'tag':
        tag = True
    else:
        resp = requests.get(latest_url, headers=headers, timeout=60)
        if resp.status_code == 404:
            tag = True

    if tag:
        graphql_url = "https://api.github.com/graphql"
        post_data = {
            "query": """
{
  repository(owner: "%s", name: "%s") {
    refs(refPrefix: "refs/tags/", first: 25, orderBy: {field: TAG_COMMIT_DATE, direction: DESC}) {
      edges {
        node {
          name
          target {
            commitUrl
            ... on Tag {
              message
              commitUrl
              tagger {
                date
              }
              target {
                ... on Commit {
                  message
                  commitUrl
                  committedDate
                }
              }
            }
          }
        }
      }
    }
  }
}""" % (pro['repo'].split('/')[0], pro['repo'].split('/')[1])}
        #print('repo', pro['repo'])
        resp = requests.post(graphql_url, headers=headers, data=json.dumps(post_data), timeout=60)
        try:
            tags=[]
            for last in resp.json()['data']['repository']['refs']['edges']:
                if len(tags) >= 10:
                    break
                nameTmp = last['node']['name'].lower()
                if ("rc" in nameTmp) or ("alpha" in nameTmp) or ("beta" in nameTmp):
                    continue
                last_data = last['node']
                data_tmp = {}
                data_tmp['tag_name'] = last_data['name']
                if 'target' in last_data['target'] and last_data['target']['target']:
                    commit_url = last_data['target']['target']['commitUrl'].replace('/github.com/','/api.github.com/repos/').replace('/commit/', '/commits/')
                    data_tmp['created_at'] = last_data['target']['target']['committedDate']
                    data_tmp['body'] = last_data['target']['target']['message']
                    data_tmp['html_url'] = commit_url
                else:
                    commit_url = last_data['target']['commitUrl'].replace('/github.com/', '/api.github.com/repos/').replace('/commit/', '/commits/')
                    commit = requests.get(commit_url, headers=headers)
                    commit_data = commit.json()

                    if 'commit' in commit_data and commit.status_code == 200:
                        data_tmp['created_at'] = commit_data['commit']['committer']['date']
                        data_tmp['body'] = commit_data['commit']['message']
                        data_tmp['html_url'] = commit_data['html_url']
                    else:
                        data_tmp['created_at'] = last_data['target']['tagger']['date']
                        data_tmp['body'] = last_data['target']['message']
                        data_tmp['html_url'] = commit_url
                tags.append(data_tmp)
            #print('tags', pro['repo'],tags)
            tags_result[pro['repo']] = tags
            data = tags[0]
        except Exception as e:
            print(pro['repo'], e)
            print(json.dumps(resp.headers))
            print(json.dumps(resp.json()))
    else:



        
        data = resp.json()
        ##获取最近十个release版本
        recent_ten = 'https://api.github.com/repos/%s/releases?per_page=25' % pro['repo']
        resp = requests.get(recent_ten, headers=headers, timeout=60)
        tags = []
        for res in resp.json():
            if len(tags) >= 10:
                break
            nameTmp = res['tag_name'].lower()
            if ("rc" in nameTmp) or ("alpha" in nameTmp) or ("beta" in nameTmp) or (("latest" in nameTmp) and (pro['repo'].find('vsftpd') == -1)) or ('trunk' in nameTmp):
                continue
            tmp = {
                "name": res.get('name', ''),
                "tag_name": res.get('tag_name', ''),
                "html_url": res.get('html_url', ''),
                "repo_url": "https://github.com/%s" % pro['repo'],
                "body": res.get('body', ''),
                "created_at": res.get('created_at', '')
            }
            tags.append(tmp)
        tags_result[pro['repo']] = tags
    data['repo_url'] = "https://github.com/%s" % pro['repo']

    if 'message' in data:
        print(data)
        return None
    return data


def get_latest_release(pro):
    latest_data = {}
    print("[Repo] %s" % pro['project'])
    if pro['hosting'] == 'github':
        latest_data = get_github_latest_release(pro)

    if pro['hosting'] == 'dockerhub':
        latest_data = get_dockerhub_latest_release(pro)

    if latest_data:
        data = {
            "name": latest_data.get('name', ''),
            "tag_name": latest_data.get('tag_name', ''),
            "html_url": latest_data.get('html_url', ''),
            "repo_url": latest_data.get('repo_url', ''),
            "body": latest_data.get('body', ''),
            "created_at": latest_data.get('created_at', '')
        }
        data.update(pro)
        result['data'].append(data)

def get_dockerhub_latest_release(pro):
    request_url = "https://hub.docker.com/v2/repositories/%s/tags?page_size=50&page=1" % pro['repo']
    data = {}
    resp = {}
    try:
        resp = requests.get(request_url, headers={"Content-Type": 'application/json; charset=utf-8'}, timeout=60)
        #print( resp.json())
        tags=[]
        for result_item in resp.json()['results']:
            if len(tags) >= 10:
                break
            nameTmp = result_item["name"].lower()
            data_tmp = {}
            if ("rc" in nameTmp) or ("alpha" in nameTmp) or ("beta" in nameTmp) or (("latest" in nameTmp) and (pro['repo'].find('vsftpd') == -1)) or ('trunk' in nameTmp):
                continue
            data_tmp['tag_name'] = result_item["name"]
            data_tmp['name'] = result_item["name"]
            data_tmp['html_url'] = "https://hub.docker.com/r/%s/tags" % pro['repo']
            data_tmp['repo_url'] = "https://hub.docker.com/r/%s" % pro['repo']
            data_tmp['created_at'] = result_item['last_updated']
            data_tmp['body'] = result_item['last_updated']
            tags.append(data_tmp)
        tags_result[pro['repo']] = tags
        data = tags[0]
    except Exception as e:  
        print(pro['repo'], e)
        print(request_url)
        print(json.dumps(resp.json()))
    return data


threads = []
thread_num = 5
pos = -1
now = datetime.now()
print("[开始时间] %s" % now)

with open(source_file, 'r', encoding='UTF-8') as f:
    source_data = json.load(f)

print("[总数] %s" % len(source_data))

for i in source_data:
    pos += 1
    t = threading.Thread(target=get_latest_release,
                         args=(i,))
    threads.append(t)
    if len(threads) == thread_num or pos == len(source_data) - 1:
        for t in threads:
            # time.sleep(30)
            t.start()
        for t in threads:
            t.join()
        threads = []

#print("[tag] %s" % tags_result)
result['data'].sort(key=lambda item: sort_time(item['created_at']), reverse=True)
result['total'] = len(result['data'])
result['updated_at'] = datetime.utcfromtimestamp(time.mktime(now.timetuple())).isoformat() + 'Z'

if result['data']:
    dumps_result = json.dumps(result)
    with open(data_file, 'w', encoding='UTF-8') as f:
        f.write(dumps_result)
    with open(docs_data_file, 'w', encoding='UTF-8') as f:
        f.write(dumps_result)

if tags_result:
    dumps_tags = json.dumps(tags_result)
    with open(tags_file, 'w', encoding='UTF-8') as f:
        f.write(dumps_tags)
    with open(docs_tags_file, 'w', encoding='UTF-8') as f:
        f.write(dumps_tags)

end = datetime.now()
print("[结束时间] %s" % end)
print("[程序耗时] %s" % str(end - now))
