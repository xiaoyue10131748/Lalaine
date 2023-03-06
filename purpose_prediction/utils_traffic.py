import re
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
        self.fragment = ""

        if not isinstance(url, str):
            return

        ext = tldextract.extract(url)
        self.domain = ext.domain
        self.subdomain = ext.subdomain
        self.suffix = ext.suffix

        parsed = urlparse(url)
        self.netloc = parsed.netloc
        self._path = parsed.path
        self._query = parsed.query
        self.fragment = parsed.fragment

    @property
    def path(self) -> str:
        if not isinstance(self.url, str):
            return ""
        # https://ad.doubleclick.net/ddm/activity/src=11229815;type=amgappco;cat=amgappco;ord=2953895867383;dc_rdid=00000000-0000-0000-0000-000000000000;dc_lat=1;u3=;u4=;u5=;u6=;u11=false;u14=undefined;u15=00000000-0000-0000-0000-000000000000;u16=;u13=false
        if self.url.count(';') >= 2:
            args_str = self.url.split('/')[-1]
            # modify path
            path = self.url.split(self.netloc)[1]
            path = path.split(args_str)[0]
            return path
        else:
            return self._path

    @property
    def args(self) -> dict:
        if not isinstance(self.url, str):
            return {}
        # https://ad.doubleclick.net/ddm/activity/src=11229815;type=amgappco;cat=amgappco;ord=2953895867383;dc_rdid=00000000-0000-0000-0000-000000000000;dc_lat=1;u3=;u4=;u5=;u6=;u11=false;u14=undefined;u15=00000000-0000-0000-0000-000000000000;u16=;u13=false
        if self.url.count(';') >= 2:
            args = {}
            args_str = self.url.split('/')[-1]
            for i in args_str.split(';'):
                if '=' in i:
                    try:
                        k, v = i.split('=')
                    except ValueError:
                        continue
                    args[k] = v
                    return args
        else:
            args_str = self._query
            if not args_str:
                return {}
            else:
                args = parse_qs(args_str)
                args = {k: v[0] for k, v in args.items()}
                return args
        return {}

    @property
    def arg_keys(self) -> list:
        return list(self.args.keys())

    @property
    def main_url(self) -> str:
        if self.domain:
            if self.suffix:
                return self.domain + '.' + self.suffix
            else:
                return self.domain
        return ''

    def __str__(self) -> str:
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

    @property
    def content_length(self) -> int:
        if not self.kv:
            return 0
        if 'Content-Length' in self.kv:
            return int(self.kv['Content-Length'])
        if 'content-length' in self.kv:
            return int(self.kv['content-length'])
        return 0

    @property
    def content_type(self) -> str:
        if not self.kv:
            return ''
        if 'Content-Type' in self.kv:
            return self.kv['Content-Type']
        if 'content-type' in self.kv:
            return self.kv['content-type']
        return ''

    @property
    def user_agent(self) -> str:
        if not self.kv:
            return ''
        if 'User-Agent' in self.kv:
            return self.kv['User-Agent']
        if 'user-agent' in self.kv:
            return self.kv['user-agent']
        return ''

    @property
    def keys(self) -> list:
        if not self.kv:
            return []
        return list(self.kv.keys())

    @property
    def featured_keys(self) -> list:
        keys = self.keys
        #
        normal_keys = ['content-length', 'content-type', 'accept', 'accept-encoding', 'content-encoding', 'accept-language', 'language', 'accept-charset',
                       'cookie', 'user-agent', 'host', 'connection', 'cache-control', 'authorization', 'x-auth', 'x-timestamp', 'vary', 'server', 'x-powered-by', 'x-powered-by-plesk', 'date']
        featured_keys = []
        for i in keys:
            if i.lower() not in normal_keys:
                featured_keys.append(i)
        return featured_keys

    def __str__(self) -> str:
        repr = 'header: {}, kv: {}, content_length: {}, content_type: {}, user_agent: {}'.format(
            self.header, self.kv, self.content_length, self.content_type, self.user_agent)
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

    def clean_keys(func):
        def wrapper(self, *args, **kwargs):
            forbidden_list = ['<?xml version', '"']
            ret = func(self, *args, **kwargs)
            if TRAFFIC_TEST_FLAG:
                print('[!] clean keys', ret)
            cleaned_keys = []
            for i in ret:
                if not i.isascii():
                    continue
                for j in forbidden_list:
                    if j in i:
                        continue
                # \x00-\x1f
                if re.search(r'[\x00-\x1f]', i):
                    continue
                cleaned_keys.append(i.lstrip('$'))
            return cleaned_keys
        return wrapper

    @property
    @clean_keys
    def keys(self) -> list:
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

    @property
    def size(self) -> int:
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

    def __str__(self) -> str:
        repr = 'body: {}'.format(self.body)
        return repr


if __name__ == '__main__':
    TRAFFIC_TEST_FLAG = True
    url = 'https://toblog.ctobsnssdk.com/service/2/log_settings/?sdk_version=3.2.10&version_code=2.4.0&app_version_minor=3&language=en&user_agent=StarsFun-mobile%202.4.0%20rv:3%20(iPhone;%20iOS%2013.4.1;%20en_US)&app_name=starskiller_ios&app_version=2.4.0&vid=BB2A8FDE-745D-4B5F-9D96-3AB44D193F4B&is_upgrade_user=0&device_id=3716782181331003&tz_offset=-14400&mcc_mnc=&channel=AppStore&app_region=US&resolution=640*1136&aid=190150&os=iOS&ssid=b6afa5de-5271-4a0f-a1b6-3a13ef8961bd&openudid=32da002631ec0c9d601c4dd96aba7a4a8b1fb2be&ac=&timezone=-4&os_version=13.4.1&tz_name=America/Indiana/Indianapolis&mc=02:00:00:00:00:00&is_jailbroken=1&device_platform=iphone&app_language=en&device_type=iPhone%20SE&iid=3699190317453984&idfa=F270BCAF-13C0-4D1C-B91F-6F446E24A380'

    p = ParsedURL(url)
    print(p)
    print(p.arg_keys)

    header = open('./test/header.txt').read()
    p = ParsedURL(header)
    print(p)

    body = open('./test/body.txt', 'r').read()
    p = ParsedBody(body)
    print(p.keys)
