import urllib
import urllib2
import json




# Begin using data like the following



class SolrInterface(object):
    def __init__(self, url):
        self.url = url
        self.update_path = 'solr/update/json'
        self.search_path = 'solr/select/?indent=on&{query}&wt=python&hl=true&hl.fl=*&hl.simple.pre=<em>&hl.simple.post=</em>&hl.snippets=100&hl.fragsize=0'
        self.delete_path = 'solr/update?stream.body=<delete><query>id:{id}</query></delete>'

    def add(self, document):
        # print self.to_json(document.__dict__)
        url_path = '{url}/{path}'.format(url=self.url, path=self.update_path)
        jjson = '[' + self.to_json(document) + ']'
        print '*********************************************'
        print url_path
        print jjson
        print '*********************************************'
        req = urllib2.Request(url=url_path)
        req.add_data(jjson)
        req.add_header('Content-type', 'application/json')
        f = urllib2.urlopen(req)
        print f.read()

    def commit(self):
        req = urllib2.Request(url='{url}/{path}?commit=true'.format(url=self.url,path=self.update_path).format(url=self.url))
        req.add_header('Content-type', 'application/json')
        f = urllib2.urlopen(req)
        print f.read()

    def to_json(self, document):
        return json.dumps( document.__dict__ )
        # return '{"id" : "TestDoc1", "title" : "test1"}, {"id" : "TestDoc2", "title" : "another test"}'

    def search(self, query):
        url_path = '{url}/{path}'.format(url=self.url, path=self.search_path.format(query=urllib.urlencode({'q' : query })))
        print 'SEARCH *********************************************'
        print url_path
        req = urllib2.Request(url=url_path)
        f = urllib2.urlopen(req)
        response = eval(f.read())
        print response['response']['numFound'], "documents found."
        print '*********************************************'
        return response

    def delete(self, asset_id):
        url_path = '{url}/{path}'.format(url=self.url, path=self.delete_path.format(id=asset_id))
        print 'DELETE *********************************************'
        print url_path
        req = urllib2.Request(url=url_path)
        f = urllib2.urlopen(req)
        response = f.read()
        print response
        print '*********************************************'
        return response
