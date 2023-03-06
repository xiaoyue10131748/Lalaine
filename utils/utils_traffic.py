import sys
import tldextract
from urllib.parse import urlparse, parse_qs

TRAFFIC_TEST_FLAG = False


class ParsedURL:
    def __init__(self, url: str):
        self.url = url
        self.domain = ""
        self.subdomain = ""
        self.suffix = ""
        self.netloc = ""
        self.path = ""
        self.fragment = ""
        self.args = {}

        if not isinstance(url, str):
            return

        ext = tldextract.extract(url)
        self.url = url
        self.domain = ext.domain
        self.subdomain = ext.subdomain
        self.suffix = ext.suffix

        parsed = urlparse(url)
        self.netloc = parsed.netloc
        self.path = parsed.path
        self.fragment = parsed.fragment

        # https://ad.doubleclick.net/ddm/activity/src=11229815;type=amgappco;cat=amgappco;ord=2953895867383;dc_rdid=00000000-0000-0000-0000-000000000000;dc_lat=1;u3=;u4=;u5=;u6=;u11=false;u14=undefined;u15=00000000-0000-0000-0000-000000000000;u16=;u13=false
        self.args = {}
        if url.count(';') >= 2:
            args_str = url.split('/')[-1]
            for i in args_str.split(';'):
                if '=' in i:
                    try:
                        k, v = i.split('=')
                    except ValueError:
                        continue
                    self.args[k] = v
            # modify path
            path = url.split(self.netloc)[1]
            path = path.split(args_str)[0]
            self.path = path
        else:
            args_str = parsed.query
            if not args_str:
                self.args = {}
            else:
                args = parse_qs(args_str)
                args = {k: v[0] for k, v in args.items()}
                self.args = args

    def get_arg_keys(self) -> list:
        if not self.args:
            return []
        return list(self.args.keys())

    def __repr__(self) -> str:
        repr = 'url: {}, domain: {}, suffix: {}, netloc: {}, path: {}, fragment: {}, args: {}'.format(
            self.url, self.domain, self.suffix, self.netloc, self.path, self.fragment, self.args)
        return repr


class ParsedHeader:
    def __init__(self, header: str):
        self.header = header
        self.kv = {}

        if not isinstance(header, str):
            return

        try:
            header = eval(header)
        except:
            print('[!] header eval error', header)
            return

        if not isinstance(header, list):
            print('[!] header is not list', self.header)
            return

        for i in header:
            self.kv[i['name']] = i['value']

    def get_content_length(self) -> int:
        if not self.kv:
            return 0
        if 'Content-Length' in self.kv:
            return int(self.kv['Content-Length'])
        if 'content-length' in self.kv:
            return int(self.kv['content-length'])
        return 0

    def get_content_type(self) -> str:
        if not self.kv:
            return ''
        if 'Content-Type' in self.kv:
            return self.kv['Content-Type']
        if 'content-type' in self.kv:
            return self.kv['content-type']
        return ''

    def get_keys(self) -> list:
        if not self.kv:
            return []
        return list(self.kv.keys())

    def get_featured_keys(self) -> list:
        keys = self.get_keys()
        #
        normal_keys = ['content-length', 'content-type', 'accept', 'accept-encoding', 'content-encoding', 'accept-language', 'language', 'accept-charset',
                       'cookie', 'user-agent', 'host', 'connection', 'cache-control', 'authorization', 'x-auth', 'x-timestamp', 'vary', 'server', 'x-powered-by', 'x-powered-by-plesk', 'date']
        featured_keys = []
        for i in keys:
            if i.lower() not in normal_keys:
                featured_keys.append(i)
        return featured_keys

    def __repr__(self) -> str:
        repr = 'header: {}, kv: {}'.format(self.header, self.kv)
        return repr


class ParsedBody:
    def __init__(self, body: str):
        self.body = ''

        if not isinstance(body, str):
            return

        body = body.replace('\\\\\\\\/', '/').replace('\\\\/', '/')
        body = body.replace('\\\\\\\\"', '"').replace('\\\\"', '"')
        self.body = body

    def _try_get_key(self, colon_index: int) -> str:
        # find two "
        end = self.body.rfind('"', 0, colon_index)
        if end == -1:
            return ''
        begin = self.body.rfind('"', 0, end)
        if begin == -1:
            return ''

        forbidden_seps = ['{', '}', ':', ';', '\n', '\t', ',', '\\', ]
        for i in forbidden_seps:
            if i in self.body[end+1:colon_index]:
                return ''

        ret = self.body[begin+1:end]
        # if contain non-ascii, return empty
        if not ret.isascii():
            return ''
        forbidden_strs = [':', ';', ',', '\n', '\r',
                          '\t', '\\', '/', '{', '}', '[', ']']
        for i in forbidden_strs:
            if i in ret:
                return ''
        return ret

    def _try_get_keys_from_params(self) -> list:
        if TRAFFIC_TEST_FLAG:
            print('[!] try get keys from params')
        try:
            body = eval(self.body)
        except:
            if TRAFFIC_TEST_FLAG:
                print('[!] eval error')
            return []
        if not isinstance(body, dict):
            if TRAFFIC_TEST_FLAG:
                print('[!] body is not list', type(body))
            return []
        if 'params' not in body:
            if TRAFFIC_TEST_FLAG:
                print('[!] no params')
            return []
        params = body['params']
        ret = []
        for h in params:
            if not isinstance(h['name'], str):
                continue
            ret.append(h['name'])
        return ret

    def get_keys(self) -> list:
        if not self.body:
            return []
        if not isinstance(self.body, str):
            return []
        ret = []
        if "'params':" in self.body:
            ret = self._try_get_keys_from_params()
            if ret:
                return ret
        colon_index = self.body.find(':')
        while colon_index != -1:
            if colon_index+2 < len(self.body):
                if self.body[colon_index+1:colon_index+3] == '//':
                    colon_index = self.body.find(':', colon_index+3)
                    continue
            key = self._try_get_key(colon_index)
            if key:
                ret.append(key)
            colon_index = self.body.find(':', colon_index+1)
        return ret

    def get_size(self) -> int:
        if "'size':" not in self.body:
            return 0
        # all digits after "'size':"
        start = self.body.find("'size':") + 7
        while start < len(self.body) and not self.body[start].isdigit():
            start += 1
        if start >= len(self.body):
            return 0
        end = start
        while end < len(self.body) and self.body[end].isdigit():
            end += 1
        return int(self.body[start:end])

    def __repr__(self) -> str:
        repr = 'body: {}'.format(self.body)
        return repr


if __name__ == '__main__':
    TRAFFIC_TEST_FLAG = True
    url = 'https://pagead2.googleadservices.com/pagead/adview?ai=CrAhGMABoYtS1KYb3BdfOjogNxZrY6mnt9PHs1w_AjbcBEAEg3t7xLWDJ5qaI9KPAEKABtvSwqQKoAwGqBOoBT9AqYseNmotlJO4A0nrKsCUKelrIyQSnWR2Y_ZxoKWcWMniH5x08_RVC2XR5yC5fNCx60MkaqTZHzdP842KopFHbXDkZvw-xcH0tl7UExXlkXp_PR7MNCI2AE1WPT7LNf-mE_qftfh-gwAeNE04mOc7Ak8Dc4I_vyxbcWy-uuoafi3_mBpkaGX5PtqSkUIr2nuoX6zACXyxLH3W2tA2gPt5dH-U0-rcJF9KSq0MJsWVKOWcVXpPN1kVAI-VXT7k5DvFEpkW5AIVqP8wK9aQi_6XiQ1YxGaXjdL9NZsIWHZpkqR8zRRKEh7KUwAT-qMWD_gOIBb-2wcM_kAYBoAYagAeyi8_WAZgHAagHzZuxAqgHmZ2xAqgHpr4bqAfVyRuoB6EBqAetyhuoB67NG6gH_p6xAqgH89EbqAeW2BuoB6qbsQKoB9-fsQKoB47cG6gHyZyxArgHq_-2reCNy4jbAcAH5tgD2AcB-gcRY29tLmJlZWp1Zy5Hb2x3aXqYCAGgCKuJPrAIArgIAdIIBwiAYRABGB2xCa0AOFVxyJYagAoDkAsFmAydgNnU-QO4E-ECghQZGhdtb2JpbGVhcHA6OjEtMTQ4NjE1MTQ4ONAVAZgWAcoWOQoKMTU5NDU1MTM5ORolCKHyo-ant5OFXhCmhdy8nIeZ0dkBGAAgACoKMTQ4NjE1MTQ4OCD1_AMoAfgWAYAXAbIXGgoYCAASFHB1Yi00MzA3MTAwNzY3Mzc2MDIz&sigh=4MZjM01lZTk&cid=CAQShgEAjSKyzLv3GrAqLaLv6DkDJRR6u2PIHIpt8H6H67bQzk61raqYcZnOdVGzSiozRdE8WwE4erBJIfePLKIL0cxWIPO9XeIQMUfdqIiKD0KGdrVLFLPxMg4fhyltJqjdBbxp4eQDlKedWho6rZR6r8_75y1afmftNCPu-1hjPm0e4C64o3kMww&gvr=1&fbs_aeid=-897417868342707321&ms=eYNLvr1gQ2sZsXAmho9_krWLf3UjiVwY2qgN4zchmsfrH6UZm1g8isVmym33FZoKHXufuwvZZB8PtiK0iBw2SGM5AY6TNTJBlr-xB2JHYKyMEkENDFOXIOfCuxt7ylvB73Q-HMptS6M-82o94lbK9JRoaH-IS1PpcNymLFX0H4OapBQmB_ee1BKduEu7O-VyQ95uPMMpE4hbIjRsiV-q9sErqis7ggoWvnXZI0qUbYCc5Zn6eK0VTErsh_L_J8ovdqtPc3vltj8nl4jaX5h7hlNcEtSxDlxtV93l_brja2QrmJQVjRl8VV-Uem2_WJSUzoBzaGan9mQ4EMFhACwCew'

    p = ParsedURL(url)
    print(p.args.keys())

    #body = open('./test/body.txt', 'r').read()
    #p = ParsedBody(body)
    #print(p.get_keys())
