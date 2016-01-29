import unittest
import jsonschema
import json
from _ucoinpy_test.api.webserver import WebFunctionalSetupMixin, web, asyncio
from ucoinpy.api.bma.wot import Lookup, Members, CertifiedBy, CertifiersOf


class Test_BMA_Wot(WebFunctionalSetupMixin, unittest.TestCase):
    def test_bma_wot_lookup(self):
        json_sample = {
            "partial": False,
            "results": [
                {
                    "pubkey": "HsLShAtzXTVxeUtQd7yi5Z5Zh4zNvbu8sTEZ53nfKcqY",
                    "uids": [
                        {
                            "uid": "udid2;c;TOCQUEVILLE;FRANCOIS-XAVIER-ROBE;1989-07-14;e+48.84+002.30;0;",
                            "meta": {
                                "timestamp": 1409990782
                            },
                            "self": "J3G9oM5AKYZNLAB5Wx499w61NuUoS57JVccTShUbGpCMjCqj9yXXqNq7dyZpDWA6BxipsiaMZhujMeBfCznzyci",
                            "others": [
                                {
                                    "pubkey": "9WYHTavL1pmhunFCzUwiiq4pXwvgGG5ysjZnjz9H8yB",
                                    "meta": {
                                        "timestamp": 1509991044
                                    },
                                    "signature": "42yQm4hGTJYWkPg39hQAUgP6S6EQ4vTfXdJuxKEHL1ih6YHiDL2hcwrFgBHjXLRgxRhj2VNVqqc6b4JayKqTE14r"
                                }
                            ]
                        }
                    ],
                    "signed": [
                        {
                            "uid": "snow",
                            "pubkey": "2P7y2UDiCcvsgSSt8sgHF3BPKS4m9waqKw4yXHCuP6CN",
                            "meta": {
                                "timestamp": 1509992000
                            },
                            "signature": "Xbr7qhyGNCmLoVuuKnKIbrdmtCvb9VBIEY19izUNwA5nufsjNm8iEsBTwKWOo0lq5O1+AAPMnht8cm2JjMq8AQ=="
                        },
                        {
                            "uid": "snow",
                            "pubkey": "2P7y2UDiCcvsgSSt8sgHF3BPKS4m9waqKw4yXHCuP6CN",
                            "meta": {
                                "timestamp": 1509992006
                            },
                            "signature": "HU9VPwC4EqPJwATPuyUJM7HLjfig5Ke1CKonL9Q78n5/uNSL2hkgE9Pxsor8CCJfkwCxh66NjGyqnGYqZnQMAg=="
                        },
                        {
                            "uid": "snow",
                            "pubkey": "7xapQvvxQ6367bs8DsskEf3nvQAgJv97Yu11aPbkCLQj",
                            "meta": {
                                "timestamp": 1609994000
                            },
                            "signature": "6S3x3NwiHB2QqYEY79x4wCUYHcDctbazfxIyxejs38V1uRAl4DuC8R3HJUfD6wMSiWKPqbO+td+8ZMuIn0L8AA=="
                        },
                        {
                            "uid": "cat",
                            "pubkey": "CK2hBp25sYQhdBf9oFMGHyokkmYFfzSCmwio27jYWAN7",
                            "meta": {
                                "timestamp": 1422890632
                            },
                            "signature": "AhgblSOdxUkLwpUN9Ec46St3JGaw2jPyDn/mLcR4j3EjKxUOwHBYqqkxcQdRz/6K4Qo/xMa941MgUp6NjNbKBA=="
                        }
                    ]
                }
            ]
        }
        jsonschema.validate(json_sample, Lookup.schema)

    def test_bma_wot_lookup_bad(self):
        async def handler(request):
            await request.read()
            return web.Response(body=b'{}', content_type='application/json')

        async def go():
            _, srv, url = await self.create_server('GET', '/pubkey', handler)
            lookup = Lookup(None, "pubkey")
            lookup.reverse_url = lambda scheme, path: url
            with self.assertRaises(jsonschema.exceptions.ValidationError):
                await lookup.get()

        self.loop.run_until_complete(go())

    def test_bma_wot_members(self):
        json_sample = {
            "results": [
                {"pubkey": "HsLShAtzXTVxeUtQd7yi5Z5Zh4zNvbu8sTEZ53nfKcqY", "uid": "cat"},
                {"pubkey": "9kNEiyseUNoPn3pmNUhWpvCCwPRgavsLu7YFKZuzzd1L", "uid": "tac"},
                {"pubkey": "9HJ9VXa9wc6EKC6NkCi8b5TKWBot68VhYDg7kDk5T8Cz", "uid": "toc"}
            ]
        }
        jsonschema.validate(Members.schema, json_sample)

    def test_bma_wot_members_bad(self):
        async def handler(request):
            await request.read()
            return web.Response(body=b'{}', content_type='application/json')

        async def go():
            _, srv, url = await self.create_server('GET', '/', handler)
            members = Members(None)
            members.reverse_url = lambda scheme, path: url
            with self.assertRaises(jsonschema.exceptions.ValidationError):
                await members.get()

        self.loop.run_until_complete(go())

    def test_bma_wot_cert(self):
        json_sample = {
            "pubkey": "HsLShAtzXTVxeUtQd7yi5Z5Zh4zNvbu8sTEZ53nfKcqY",
            "uid": "user identifier",
            "isMember": True,
            "certifications": [
                {
                    "pubkey": "9WYHTavL1pmhunFCzUwiiq4pXwvgGG5ysjZnjz9H8yB",
                    "uid": "certifier uid",
                    "cert_time": {
                        "block": 88,
                        "medianTime": 1509991044
                    },
                    "written": {
                        "number": 872768,
                        "hash": "D30978C9D6C5A348A8188603F039423D90E50DC5"
                    },
                    "isMember": True,
                    "signature": "42yQm4hGTJYWkPg39hQAUgP6S6EQ4vTfXdJuxKEHL1ih6YHiDL2hcwrFgBHjXLRgxRhj2VNVqqc6b4JayKqTE14r"
                },
                {
                    "pubkey": "9WYHTavL1pmhunFCzUwiiq4pXwvgGG5ysjZnjz9H8yB",
                    "uid": "certifier uid",
                    "cert_time": {
                        "block": 88,
                        "medianTime": 1509991044
                    },
                    "written": None,
                    "isMember": True,
                    "signature": "42yQm4hGTJYWkPg39hQAUgP6S6EQ4vTfXdJuxKEHL1ih6YHiDL2hcwrFgBHjXLRgxRhj2VNVqqc6b4JayKqTE14r"
                }
            ]
        }
        jsonschema.validate(json_sample, CertifiersOf.schema)
        jsonschema.validate(json_sample, CertifiedBy.schema)

    def test_bma_wot_certifiers_bad(self):
        async def handler(request):
            await request.read()
            return web.Response(body=b'{}', content_type='application/json')

        async def go():
            _, srv, url = await self.create_server('GET', '/pubkey', handler)
            certsof = CertifiersOf(None, 'pubkey')
            certsof.reverse_url = lambda scheme, path: url
            with self.assertRaises(jsonschema.exceptions.ValidationError):
                await certsof.get()

        self.loop.run_until_complete(go())

    def test_bma_wot_certifiers_inner_bad(self):
        async def handler(request):
            await request.read()
            return web.Response(body=bytes(json.dumps({
    "pubkey": "7Aqw6Efa9EzE7gtsc8SveLLrM7gm6NEGoywSv4FJx6pZ",
    "uid": "john",
    "isMember": True,
    "certifications": [
        {
            "pubkey": "FADxcH5LmXGmGFgdixSes6nWnC4Vb4pRUBYT81zQRhjn",
            "meta": {
                "block_number": 38580
            },
            "uids": [
                "doe"
            ],
            "isMember": True,
            "wasMember": True,
            "signature": "8XYmBdElqNkkl4AeFjJnC5oj/ujBrzH9FNgPZvK8Cicp8Du0PQa0yYFG95EQ46MJhdV0fUT2g5xyH8N3/OGhDA=="
        },
    ]
}), "utf-8"), content_type='application/json')

        async def go():
            _, srv, url = await self.create_server('GET', '/pubkey', handler)
            certsof = CertifiersOf(None, 'pubkey')
            certsof.reverse_url = lambda scheme, path: url
            with self.assertRaises(jsonschema.exceptions.ValidationError):
                await certsof.get()

        self.loop.run_until_complete(go())

    def test_bma_wot_certified_bad(self):
        async def handler(request):
            await request.read()
            return web.Response(body=b'{}', content_type='application/json')

        async def go():
            _, srv, url = await self.create_server('GET', '/pubkey', handler)
            certby = CertifiedBy(None, 'pubkey')
            certby.reverse_url = lambda scheme, path: url
            with self.assertRaises(jsonschema.exceptions.ValidationError):
                await certby.get()

        self.loop.run_until_complete(go())
