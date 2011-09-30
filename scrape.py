import httplib
conn = httplib.HTTPConnection('www.ville.quebec.qc.ca', 80)
conn.request("GET", "/citoyens/loisirs_sports/tennis.aspx")
response = conn.getresponse()
html = response.read()
print html

