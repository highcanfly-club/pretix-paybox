import base64
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from urllib.parse import parse_qs, urlparse


def verify_response(response_message):

    #  Hard coded paybox public key
    PAYBOX_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDe+hkicNP7ROHUssGNtHwiT2Ew
HFrSk/qwrcq8v5metRtTTFPE/nmzSkRnTs3GMpi57rBdxBBJW5W9cpNyGUh0jNXc
VrOSClpD5Ri2hER/GcNrxVRP7RlWOqB1C03q4QYmwjHZ+zlM4OUhCCAtSWflB4wC
Ka1g88CjFwRw/PB9kwIDAQAB
-----END PUBLIC KEY-----"""
    """Verifies the Paybox certificate, authenticity and alteration.
    If everything goes well, returns True. Otherwise raise an Error

    :message: (str), the full url with its args
    :signature: (str), the signature of the message, separated from the url

    Flow:
        - The signature is decoded base64
        - The signature is removed from the message
        - The Paybox pubkey is loaded from an external file
        - it's validity is checked
        - The message is digested by SHA1
        - The SHA1 message is verified against the binary signature
    """

    url_parsed = urlparse(response_message)  # object
    message = url_parsed.query  # string
    query = parse_qs(message)  # dictionnary
    signature = query["signature"][0]
    # detach the signature from the message
    message_without_sign = message.split("&signature=")[0]
    # decode base64 the signature
    binary_signature = base64.b64decode(signature)
    # create a pubkey object
    key = RSA.importKey(PAYBOX_PUBLIC_KEY)
    # digest the message
    h = SHA.new(bytes(message_without_sign, encoding="utf8"))
    # and verify the signature
    verifier = PKCS1_v1_5.new(key)
    assert verifier.verify(
        h, binary_signature), "Signature Verification Failed"

    return True
