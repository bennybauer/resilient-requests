import unittest
import requests
# import requests_mock
# import responses
from httpretty import httpretty
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter


class MyTestCase(unittest.TestCase):
    def test_successful_request(self):
        res = requests.get('http://httpbin.org/status/200')
        self.assertEqual(200, res.status_code)

    def test_failed_request(self):
        res = requests.get('http://httpbin.org/status/400')
        self.assertEqual(400, res.status_code)

    def test_timeout_request(self):
        with self.assertRaises(requests.exceptions.RequestException):
            requests.get('http://httpbin.org/delay/2', timeout=1)

    def test_retry_failure(self):
        httpretty.enable()
        url = 'http://example.com/api/foo'
        httpretty.register_uri(httpretty.GET, url,
                               responses=[
                                   httpretty.Response(body='error', status=500),
                                   httpretty.Response(body='error', status=500),
                                   httpretty.Response(body='second response', status=200),
                               ])

        s = requests.Session()
        # should fail because it has only 1 retry
        retries = Retry(total=1,
                        backoff_factor=0.1,
                        status_forcelist=[500, 502, 503, 504])
        s.mount(url, HTTPAdapter(max_retries=retries))
        with self.assertRaises(requests.exceptions.RetryError) as e:
            s.get(url)

        self.assertRegexpMatches(str(e.exception), r'.* Max retries exceeded .*')

    def test_retry_success(self):
        httpretty.enable()
        url = 'http://example.com/api/foo'
        httpretty.register_uri(httpretty.GET, url,
                               responses=[
                                   httpretty.Response(body='error', status=500),
                                   httpretty.Response(body='second response', status=200),
                               ])

        s = requests.Session()
        retries = Retry(total=2,
                        backoff_factor=0.1,
                        status_forcelist=[500, 502, 503, 504])
        s.mount(url, HTTPAdapter(max_retries=retries))
        res = s.get(url)
        self.assertEqual(200, res.status_code)
        httpretty.disable()

    # @responses.activate
    # def test_retry_success_with_responses(self):
    #     with responses.RequestsMock(assert_all_requests_are_fired=True) as rsps:
    #         url = 'http://example.com/api/foo'
    #         rsps.add(responses.GET, url, status=500)
    #         rsps.add(responses.GET, url,
    #                  body='{}', status=200,
    #                  content_type='application/json')
    #
    #         # res = requests.get(url)
    #         # self.assertEqual(500, res.status_code)
    #         # res = requests.get(url)
    #         # self.assertEqual(200, res.status_code)
    #
    #         s = requests.Session()
    #         retries = Retry(total=1,
    #                         backoff_factor=0.1,
    #                         status_forcelist=[500, 502, 503, 504])
    #         s.mount(url, HTTPAdapter(max_retries=retries))
    #         res = s.get(url)
    #         self.assertEqual(200, res.status_code)


    # @requests_mock.mock()
    # def test_retry_success_with_requests_mock(self):
    #     adapter = requests_mock.Adapter()
    #     s = requests.Session()
    #     s.mount('mock', adapter)
    #     url = 'mock://example.com/api/foo'
    #     adapter.register_uri('GET', url, [{'text': 'resp1', 'status_code': 500},
    #                                       {'text': 'resp2', 'status_code': 200}])
    #
    #     retries = Retry(total=2,
    #                     backoff_factor=0.1,
    #                     status_forcelist=[500, 502, 503, 504])
    #     s.mount(url, HTTPAdapter(max_retries=retries))
    #     res = s.get(url)
    #     self.assertEqual(200, res.status_code)

    # Usage:
    # requests.get(url, timeout=(connect, read), retry=(total, backoff_factor, status_forcelist))


if __name__ == '__main__':
    unittest.main()
