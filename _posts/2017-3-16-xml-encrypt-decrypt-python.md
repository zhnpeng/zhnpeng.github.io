---
layout: post
title: xml加密解密
tags: python,xml,加密,解密
datetime: 2017-3-16 15:36
---

{{ page.title }}
================

使用python库<a href="https://github.com/mehcode/python-xmlsec"><strong>xmlsec</strong>进行加密解密

# 流程
使用rsa cert将xml的特定element加密,加密后明文的element被EncryptData element代替,
解密的时候使用rsa cert对应的私钥进行解密.

# 代码
{% highlight python %}
from os import path
import xmlsec
from lxml import etree

# Generating a self signed rsa cert run:
# openssl req  -nodes -new -x509  -keyout rsa.key -out rsa.cert

# rsa_cert is content of rsa.cert
rsa_cert = '''
-----BEGIN CERTIFICATE-----
MIICsDCCAhmgAwIBAgIJAIwKX7oCGsACMA0GCSqGSIb3DQEBBQUAMEUxCzAJBgNV
BAYTAkFVMRMwEQYDVQQIEwpTb21lLVN0YXRlMSEwHwYDVQQKExhJbnRlcm5ldCBX
aWRnaXRzIFB0eSBMdGQwHhcNMTcwMzE2MDcwODEyWhcNMTcwNDE1MDcwODEyWjBF
MQswCQYDVQQGEwJBVTETMBEGA1UECBMKU29tZS1TdGF0ZTEhMB8GA1UEChMYSW50
ZXJuZXQgV2lkZ2l0cyBQdHkgTHRkMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKB
gQCo7z5I2ltfBmo++NUOHwtkyh4g8ORJ4imh9W3yh/8eE4ojaIminJ/Zd3+T8hqW
tmndOxtdmThZfXHhcscNRS/8zTsi97CaV0apkx93IVht8SCvb/MPd87tSIBuVbUa
JHzHvA9ah5z6TPtFFOf/tDQlJvAaJZgvkMjFlpD4nNiWNQIDAQABo4GnMIGkMB0G
A1UdDgQWBBR4dBejPLF7Yd94FI+YBDNveellZTB1BgNVHSMEbjBsgBR4dBejPLF7
Yd94FI+YBDNveellZaFJpEcwRTELMAkGA1UEBhMCQVUxEzARBgNVBAgTClNvbWUt
U3RhdGUxITAfBgNVBAoTGEludGVybmV0IFdpZGdpdHMgUHR5IEx0ZIIJAIwKX7oC
GsACMAwGA1UdEwQFMAMBAf8wDQYJKoZIhvcNAQEFBQADgYEAkcAi44vq0pJLoZmd
v7odtGg5+aHnzY4BlHexj/zwuWFLt1r+GbK9sIp2tuuSn/Jbv5g8m25kDSc+xmVn
NdRo+wAnIdSX1dhXgsghM6Hog8h4wJDI1dS55xdJsIKCXbJdh6ECTvOoNT/p/q7v
YvfewGUx7p9C07TB+/do2J8Oln0=
-----END CERTIFICATE-----
'''

# content of rsa.key
rsa_private_key_pem = '''
-----BEGIN RSA PRIVATE KEY-----
MIICWwIBAAKBgQCo7z5I2ltfBmo++NUOHwtkyh4g8ORJ4imh9W3yh/8eE4ojaImi
nJ/Zd3+T8hqWtmndOxtdmThZfXHhcscNRS/8zTsi97CaV0apkx93IVht8SCvb/MP
d87tSIBuVbUaJHzHvA9ah5z6TPtFFOf/tDQlJvAaJZgvkMjFlpD4nNiWNQIDAQAB
AoGAVh2fIoQtD8O1ZWRzNz+cD0T5FtG1jfQ8RNNXuMqawjozsNkZUEuHMNQ5tLE1
3J4gWSZITO5OS1AnPUXFMn6SdvghPC9EKlqB+YwTdGUBWnNBP6sqUI/n7vHpE6+3
uTYuTo4Fvshau9gbfdEqNgYsuD5ibdjWNAQ+gCQuUvu/oAECQQDRMoyfdTu+sGwt
BHEtRqePZKBu/+uKz8SHRHWH2XAKfr0pIT+5innU1v3H5SEHqaU74evInzLBTFE3
mu/OsD9lAkEAzrqzJy/kvInTXDKPVEVF+oiqIIFlMjQiLmoHU6fbSEeRd80l+gPB
y9Mw48EZJ17dQiVh5MnO/6aY4wTQkyoWkQJAMW9vmbL7dll8hrrY/+kFabZOz0w8
3iWw/IIp//tbJa/DhbestmzJ04kmmZlEz+m/+UGvFU7BkLo3Kxu69a3inQJAbbtW
Sy+154n1IhRIVj/rFEAkpdppP8vCdQac2v/XerdadM/1H4+M98cjRVGDK43EPk8f
dlTUxojE0IQGvobxsQJAZ2Vabrbr+BUU7TkAJyGcBWLBYnD34PL9tD7sTM8jOFec
PVJJoLR12myTPUZaZG2GD2Fd9ruEcim78VJe0Z7E1A==
-----END RSA PRIVATE KEY-----
'''

doc_xml = '<?xml version="1.0" encoding="UTF-8"?><Envelope><Data>Hello, World!</Data></Envelope>'
root = etree.fromstring(doc_xml)

def encrypt_with_ras_cert():
    global root
    # Element to be encrypted
    data = root.find('./Data')
    # load key
    manager = xmlsec.KeysManager()
    key = xmlsec.Key.from_memory(rsa_cert, xmlsec.KeyFormat.CERT_PEM, None)
    manager.add_key(key)
    # Prepare for encryption
    enc_data = xmlsec.template.encrypted_data_create(
        root,
        xmlsec.Transform.AES128,
        type=xmlsec.EncryptionType.ELEMENT,
        ns='xenc'
    )
    xmlsec.template.encrypted_data_ensure_cipher_value(enc_data)
    key_info = xmlsec.template.encrypted_data_ensure_key_info(enc_data, ns="dsig")
    enc_key = xmlsec.template.add_encrypted_key(key_info, xmlsec.Transform.RSA_OAEP)
    xmlsec.template.encrypted_data_ensure_cipher_value(enc_key)
    # Encrypt
    enc_ctx = xmlsec.EncryptionContext(manager)
    enc_ctx.key = xmlsec.Key.generate(xmlsec.KeyData.AES, 128, xmlsec.KeyDataType.SESSION)
    enc_ctx.encrypt_xml(enc_data, data)

def decrpyt_with_rsa_private_key():
    # find EncryptedData element
    global root
    enc_data = xmlsec.tree.find_child(root, "EncryptedData", xmlsec.Namespace.ENC)
    # load rsa private key
    dec_manager = xmlsec.KeysManager()
    dec_key = xmlsec.Key.from_memory(rsa_private_key_pem, xmlsec.KeyFormat.PEM, None)
    dec_manager.add_key(dec_key)
    dec_ctx = xmlsec.EncryptionContext(dec_manager)
    # Decrypt
    dec_ctx.decrypt(enc_data)

print '================= Original XML ======================\n'
print etree.tostring(root, pretty_print=True)
encrypt_with_ras_cert()
print '================= After Encrypted =====================\n'
print etree.tostring(root, pretty_print=True)
decrpyt_with_rsa_private_key()
print '================= After Decrypted =====================\n'
print etree.tostring(root, pretty_print=True)
{% endhighlight %}

# 输出:
{% highlight shell %}
================= Original XML ======================

<Envelope>
  <Data>Hello, World!</Data>
</Envelope>

================= After Encrypted =====================

<Envelope>
  <xenc:EncryptedData xmlns:xenc="http://www.w3.org/2001/04/xmlenc#" Type="http://www.w3.org/2001/04/xmlenc#Element">
<xenc:EncryptionMethod Algorithm="http://www.w3.org/2001/04/xmlenc#aes128-cbc"/>
<dsig:KeyInfo xmlns:dsig="http://www.w3.org/2000/09/xmldsig#">
<xenc:EncryptedKey>
<xenc:EncryptionMethod Algorithm="http://www.w3.org/2001/04/xmlenc#rsa-oaep-mgf1p"/>
<xenc:CipherData>
<xenc:CipherValue>bv37IOrVxNO8FE++8v0gBgmpbbUu6d5LRA/ZeGTH7Ga3f4POTJo1pZHq6dNhgG/H
NvBieVw8avX44TCBHNCqITMVJQJLIjFCNUkDKJFJ+obccCI9lcfvZkzZK5K62xmw
QvMIwkbY9lkdsqVz1EKWWPo64wijq/kJNJ7gApa/iGU=</xenc:CipherValue>
</xenc:CipherData>
</xenc:EncryptedKey>
</dsig:KeyInfo>
<xenc:CipherData>
<xenc:CipherValue>Xgm7oR8KsgpSMTU5fQWiv7ECbjaEquel8z7dkjBURYTsWULjywwTfk/qyCNCCCCW</xenc:CipherValue>
</xenc:CipherData>
</xenc:EncryptedData>
</Envelope>

================= After Decrypted =====================

<Envelope>
  <Data>Hello, World!</Data>
</Envelope>
{% endhighlight %}
