from datetime import datetime, timezone, timedelta

from jwt import JWT, jwk_from_dict
from jwt.utils import get_int_from_datetime

JWT_SIGNING_KEY = jwk_from_dict(
    {
        'kty': 'RSA',
        'e': 'AQAB',
        'n': 'n7iNo3l8WIL87NI1h_UL11xXgxC9fQpa5WEigkiOyLwv6K6Y9xu52k4pUeZPOh3bwBXevQhDTy1nbAkJMUtOhL7S08DwjaqCR1oD-2CIZHrVFodwGSufBEAKSjGl3g5HQ7MsfIusfGwuEG_dFYd72Ci2QvG6C2SWiVZG5LxY9KVD4XmO7csK62SUZxw1yGJt2UB82fPCB7fQTOTeFzFTinVFxCk-rZxTO3ygVXBcakHkyLo80INBCJSifzOcr8ndZ7oQ96rtOExMxLdEQdlBLHaashgBAR8I7M8wloX3ZW2zEVCKJW5HCfaHLe4eN8r7oXuuXsdXPmZc1t_mhA5lWQ',
        'd': 'br9G5q0b_TuGKKdxGr5c4Y1T2LtIyGTfteDuTqwE5UcnaQ13XxBIhAhiOjmZgdCmSMBhW21ZTpNK_OwfBaET5pNyGAXWRkSOZO8Th7_dkt5g1mg-4BURA59sAxn9ysTXwSeBlzI5_WP9ZMRL5du1kaJZDn4R5Ehw4PWD3qKCg87jl4kZWtLSXjDpwWn5-WLytdv9S4k6NJBjcCDrOMrYnNB6JMmn2DMA1FqsZAWgzLqv_zHcrTVw70bhhbSefuCBXbeKRSY-xz_7j9zzMAVvQ6WuNFI3Vpk1KqgQ2lrPoiSrglQZHiOpqLfvJFbXfqhZxMKM0OFUgG6js_3mPtk6aQ'
    }
)
jwt_util = JWT()

def get_jwt_token(claims):
    """
    Creates a JWT token

    :param claims: dict of claims like email, role etc
    :returns token: jwt token
    """
    claims['iat'] = get_int_from_datetime(datetime.now(timezone.utc))
    claims['exp'] = get_int_from_datetime(
        datetime.now(timezone.utc) + timedelta(hours=6)
    )

    token = jwt_util.encode(claims, JWT_SIGNING_KEY, alg='RS256')
    return token


def decode_jwt_token(token):
    """
    Decodes a jwt token

    :param token: jwt token in str
    :returns claims: dict of claims email, role etc
    """
    try:
        claims = jwt_util.decode(token, JWT_SIGNING_KEY, do_time_check=True)
        return claims
    except Exception:
        return None
