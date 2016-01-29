#!/usr/bin/env python
#
# Create test certificates:
#
#  ca.pem
#  server.pem
#  recipient.pem
#  signer.pem
#  x509.pem
#
from __future__ import print_function

import hashlib
import os
import os.path
import sys
import time

from M2Crypto import ASN1, EVP, RSA, X509, m2

t = long(time.time()) + time.timezone
before = ASN1.ASN1_UTCTIME()
before.set_time(t)
after = ASN1.ASN1_UTCTIME()
after.set_time(t + 60 * 60 * 24 * 365 * 10)  # 10 years

serial = 1


def callback(self, *args):
    return ' '


def gen_identifier(cert, dig='sha1'):
    instr = cert.get_pubkey().get_rsa().as_pem()
    h = hashlib.new(dig)
    h.update(instr)
    digest = h.hexdigest().upper()

    return ":".join(digest[pos: pos + 2] for pos in range(0, 40, 2))

def make_subject(cn=None, email=None):
    sub = X509.X509_Name()
    sub.C = 'US'
    sub.ST = 'California'
    sub.O = 'M2Crypto'
    if cn is not None:
        sub.CN = cn
    else:
        sub.CN = 'Heikki Toivonen'
    if email is not None:
        sub.Email = email
    return sub


def req(name):
    rsa = RSA.load_key(name + '_key.pem')
    pk = EVP.PKey()
    pk.assign_rsa(rsa)
    reqqed = X509.Request()
    reqqed.set_pubkey(pk)
    reqqed.set_subject(make_subject())
    reqqed.sign(pk, 'sha1')
    return reqqed, pk


def saveTextPemKey(cert, name, with_key=True):
    with open(name + '.pem', 'wb') as f:
        for line in cert.as_text():
            f.write(line)
        for line in cert.as_pem():
            f.write(line)
        if with_key:
            for line in open(name + '_key.pem', 'rb'):
                f.write(line)


def issue(request, ca, capk):
    global serial

    pkey = request.get_pubkey()
    sub = request.get_subject()

    cert = X509.X509()
    cert.set_version(2)
    cert.set_subject(sub)
    cert.set_serial_number(serial)
    serial += 1

    issuer = ca.get_subject()
    cert.set_issuer(issuer)

    cert.set_pubkey(pkey)

    cert.set_not_before(before)
    cert.set_not_after(after)

    ext = X509.new_extension('basicConstraints', 'CA:FALSE')
    cert.add_ext(ext)

    ext = X509.new_extension('subjectKeyIdentifier',
                             gen_identifier(cert))
    cert.add_ext(ext)

    # auth = X509.load_cert('ca.pem')
    # auth_id = auth.get_ext('subjectKeyIdentifier').get_value()
    # ext = X509.new_extension('authorityKeyIdentifier', 'keyid:%s' % auth_id)
    # # cert.add_ext(ext)

    cert.sign(capk, 'sha1')

    assert cert.verify(capk)

    return cert


def mk_ca():
    r, pk = req('ca')
    pkey = r.get_pubkey()
    sub = r.get_subject()

    cert = X509.X509()
    cert.set_version(2)
    cert.set_subject(sub)
    cert.set_serial_number(0)

    issuer = X509.X509_Name()
    issuer.C = sub.C
    issuer.ST = sub.ST
    issuer.O = sub.O
    issuer.CN = sub.CN
    cert.set_issuer(issuer)

    cert.set_pubkey(pkey)

    cert.set_not_before(before)
    cert.set_not_after(after)

    ext = X509.new_extension('basicConstraints', 'CA:TRUE')
    cert.add_ext(ext)

    ski = gen_identifier(cert)
    ext = X509.new_extension('subjectKeyIdentifier', ski)
    cert.add_ext(ext)

    #ext = X509.new_extension('authorityKeyIdentifier', 'keyid:%s' % ski)
    # cert.add_ext(ext)

    cert.sign(pk, 'sha1')

    saveTextPemKey(cert, 'ca')

    return cert, pk


def mk_server(ca, capk):
    r, _ = req('server')
    r.set_subject(make_subject(cn='localhost'))
    cert = issue(r, ca, capk)
    saveTextPemKey(cert, 'server')


def mk_x509(ca, capk):
    r, _ = req('x509')
    r.set_subject(make_subject(cn='X509'))
    cert = issue(r, ca, capk)
    saveTextPemKey(cert, 'x509')

    with open('x509.der', 'wb') as derf:
        derf.write(cert.as_der())


def mk_signer(ca, capk):
    r, _ = req('signer')
    r.set_subject(make_subject(cn='Signer', email='signer@example.com'))
    cert = issue(r, ca, capk)

    saveTextPemKey(cert, 'signer', with_key=False)


def mk_recipient(ca, capk):
    r, _ = req('recipient')
    r.set_subject(make_subject(cn='Recipient', email='recipient@example.com'))
    cert = issue(r, ca, capk)
    saveTextPemKey(cert, 'recipient')

if __name__ == '__main__':
    names = ['ca', 'server', 'recipient', 'signer', 'x509']

    os.chdir(os.path.dirname(sys.argv[0]))

    for key_name in names:
        genned_key = RSA.gen_key(1024, m2.RSA_F4)
        genned_key.save_key('%s_key.pem' % key_name, None)

    ca_bits, pk_bits = mk_ca()
    mk_server(ca_bits, pk_bits)
    mk_x509(ca_bits, pk_bits)
    mk_signer(ca_bits, pk_bits)
    mk_recipient(ca_bits, pk_bits)
