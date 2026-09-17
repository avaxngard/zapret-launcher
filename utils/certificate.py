# Zapret Launcher - Bypass restrictions
# Copyright (C) 2026 avaxngard corp
#
# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU GPL v3 or any later version.
#
# Distributed WITHOUT ANY WARRANTY.

import base64
import hashlib
_CERT_B64 = "MIIDBDCCAeygAwIBAgIQboWHtN2RXKZGEPVFHVgaHjANBgkqhkiG9w0BAQsFADAaMRgwFgYDVQQDDA9aYXByZXQgTGF1bmNoZXIwHhcNMjYwOTE3MDQ0MDUwWhcNMjkwOTE3MDQ1MDUwWjAaMRgwFgYDVQQDDA9aYXByZXQgTGF1bmNoZXIwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQCuRgDrZSZIiShJ1+G1YizPMMSdkeWL7IZGm4unCwUEvpjusYZGXIzA93w3nU7cKgErSOG7ctEh9+2p80zELn8Cadj16q5bIERfuA9rjA2Grl2QuCb2nv4A3OQC6Gh5gT/NyeolnKGEisH6/wkpWwXlWXVAmKaNmLoJp2xeZxy9oQOMtjHXbfoREGBCvL/OgSnMPWFYdW0esmAkEvycsdRhu3Xa2ZL6weJEWlyjZdxP1nalJiHlW1cwH13Vn9/HhPW0CVcHt1mQCNvKJsUduhAvgKJ58cVhomgH6UnMKIo2yj6e3sxmcXi/C77yiN4Se7P94csNZMsEH67pLT7c8ytpAgMBAAGjRjBEMA4GA1UdDwEB/wQEAwIHgDATBgNVHSUEDDAKBggrBgEFBQcDAzAdBgNVHQ4EFgQUvOsgCIgGCyDgvjX5su37M/kvHUgwDQYJKoZIhvcNAQELBQADggEBAIhY4FtdXFEjqoSQrTCW8A8r7thbe5f9H103dhzPg9+ERTnhgPKxRLAVkEsYNv8ZFU5qaoAcDb8pI//643qGwzLdde2pH3rl3Z6bwgj2Pm52DXPsIG/DBYVIXFqhXnrhZqlZ9ib1PY8Xuz2yAb5qHgZAUMwXCDhUd6V8XU8+nmTVQ9dLT1OlgRDfzhoyC2jYMGM+W63khCgLeWHIrrLGpQ9z+h+QzdtiBN4bsb5czYnK+FrUQZbVSwsrby/kHANpkhQjAO50ZrRu0S2pGSeQosPFSPRvYy/8SHcMzBGe0eLcLxlW68u6JPL087+y4Y9Mwqx/Is+f7Sly6x/KKZQNYIc="

def get_certificate_bytes() -> bytes:
    return base64.b64decode(_CERT_B64)

def get_certificate_sha256() -> str:
    return hashlib.sha256(get_certificate_bytes()).hexdigest()

def get_certificate_fingerprint() -> str:
    digest = hashlib.sha256(get_certificate_bytes()).hexdigest().upper()
    return ":".join(digest[i:i+2] for i in range(0, len(digest), 2))
