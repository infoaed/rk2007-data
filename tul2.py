#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import random
import requests
import bs4
import string
import csv
import json
import time
import re
import bisect

import roman

j=0

dists = {}

urls = []

cand_norm = []
cand_ext = {}

for i in range(1,4):
    urls.append(("http://vvk.ee/varasemad/r07/tulemus/10%d0000.html") % i)

for i in range (2,11):
    urls.append(("http://vvk.ee/varasemad/r07/tulemus/%d000000.html") % i)
    
for url in urls:
    j+=1
    #if j>10: break
    
    #print(url)
    succ = 1
    while succ > 0:
        try:
            page = requests.get(url)
            page.encoding = page.apparent_encoding
            succ = 0
        except requests.exceptions.RequestException as e:
            print(e)
            succ += 1
            time.sleep(succ)
    
    #print(page.text)
    #exit(1)
    
    soup = bs4.BeautifulSoup(page.text, 'lxml')
    x = soup.find_all("table")[8]
    distnr = int(str(x.find("span", {"class", "head"})).split("Valimisringkond nr ")[1].split("<")[0])
    tr = x.find_all("table")[2].find_all("tr")
    kvoot = None
    run = False
    head = []
    for z in tr:
        ddd = z.find_all("td")
        ht = ddd[0].text.strip()
        if not run:
            if ht != "I": continue
            else: run = 1
        print(roman.toRoman(run), "?=", ht)
        if roman.toRoman(run) == ht:
            head.append({
                "nr": run,
                "altnr": ht,
                "title": ddd[1].text.strip()
            }
            )
            if len(ddd[2].text.strip())>0:
                head[-1]["eligible"] = int(ddd[2].text.strip())
            if len(ddd[3].text.strip())>0:
                head[-1]["votes"] = int(ddd[3].text.strip())
            run += 1
                
        print(run, z)
        print("------")

    print(head)

    kvoot = tr[-1].text.strip()
    #print(kvoot)
    #ehstring = soup.find("div", {"class", "dataTableWrap"}).text.split("E-hääled")[0].split(" ")[-1]
    dists[distnr] = {"m": int(kvoot.split("/")[1].split("=")[0].strip()), "arr": head, "c": {}}
    #print(distnr, kvoot)

    dist = soup.find_all("table")[8].find_all("table")

    #print(dist)
#    ringkond = dist[0].text.split(" ")[-1]
#    candname = soup.find_all("span", {"class", "uppercase"})
#    nimi = candname[0].text.title()

    dist.remove(dist[0])
    dist.remove(dist[0])
    dist.remove(dist[0])

    #heads = []

    #table = dist[0].find('tbody')
    #print(table)
    #hhh = table.find_all("td")
    #for h in hhh:
    #    heads.append(h.text)

    #print(heads[-1], ehstring)

    #exit(1)
   
    for di in dist:
        table = di.find(name='tbody')
        rrr = di.find_all("tr")
        rows = 0
        party = ""
        for r in rrr:
            if rows == 0:
                ddd = r.find_all("td")
                party = ddd[0].text.strip().upper()
                rows +=1
                continue
            #print(r)
            if r.text.find("Nimekiri KOKKU") < 0 and  r.text.find("Üksikkandidaadid KOKKU") < 0:
                #print(r)
                td = 0
                res = []
                ddd = r.find_all("td")
                if len(ddd) < 3:
                    #print(ddd)
                    rows=0
                    continue
                else:
                    #print(ddd)
                    print(ddd[1].text, ddd[2].text, ddd[4].text, ddd[-1].text)

                    cand_norm.append(
                    {
                        "number": int(ddd[1].text),
                        "name": ddd[2].text,
                        "votes": int(ddd[4].text.replace("=","").replace(" ","")),
                        "electronic": int(ddd[-1].text.replace("+","").replace(" ","")),
                        "district": distnr,
                        "party": party
                    }
                    )

                    cand_ext[int(ddd[1].text)] = {
                        "number": int(ddd[1].text),
                        "name": ddd[2].text,
                        "votes": int(ddd[4].text.replace("=","").replace(" ","")),
                        "electronic": int(ddd[-1].text.replace("+","").replace(" ","")),
                        "district": distnr,
                        "party": party,
                        "arr": []
                    }
                    
                    ce = cand_ext[int(ddd[1].text)]["arr"]
                    kokku = int(ddd[4].text.replace("=","").replace(" ",""))
                    
                    hc = 0
                    for arr in head:
                        ce.append({
                            "title": arr["title"],
                            "nr": arr["nr"],
                            "altnr": arr["altnr"],
                            "votes": int(ddd[6+hc*2].text.replace("+","").replace(" ",""))
                            })
                        hc += 1
                        #if "eligible" in arr:
                        #    ce[arr["title"]]["e"] = arr["eligible"]
                        
                    if party not in dists[distnr]["c"]:
                        dists[distnr]["c"][party] = [cand_norm[-1]["number"]]
                    else:
                        bisect.insort(dists[distnr]["c"][party], cand_norm[-1]["number"])
                    
                    res.append(ddd[1].text)
                    res.append(ddd[2].text)
                    res.append(kokku)
                    res.append(ddd[-3].text.replace("+","").replace(" ",""))
                    res.append(ddd[-1].text.replace("+","").replace(" ",""))
                    with open('rk2007-tulemused.csv', 'a') as csv_file:
                        writer = csv.writer(csv_file)
                        writer.writerow(res)
                    csv_file.close()

print(cand_ext)

with open("res2007.json", 'w') as outfile:
    json.dump(cand_norm, outfile, sort_keys=True, indent=4)
    
with open("res2007-ext.json", 'w') as outfile:
    json.dump(cand_ext, outfile, sort_keys=True, indent=4)

with open("dists2007.json", 'w') as outfile:
    json.dump(dists, outfile, sort_keys=True, indent=4)
