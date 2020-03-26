#!/usr/bin/env python3

# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
Vends token based on header fields (TenantId, UserId)
"""


import packages.jwt as jwt

X_TOKEN = "x-token"
X_TENANT_ID = "x-tenant-id"
X_USER_ID = "x-user-id"


def vend(tenant_id, user_id, secret_key='aws-saas-factory'):
    """
    Vends token based on input fields. secret_key can be overriden
        :param tenant_id:
        :param user_id:
        :param secret_key='aws-saas-factory':
    """
    payload = {
        'tenant_id': tenant_id,
        'user_id': user_id
    }

    token = jwt.encode(payload=payload,
                       key=secret_key,
                       algorithm='HS256').decode('utf-8')
    return token


def get_header(event, secret_key='aws-saas-factory'):
    """
    Return tenant_id, user_id, token
        :param event:
        :param secret_key='aws-saas-factory':
    """
    if X_TOKEN in event:
        token = event[X_TOKEN]
        decoded_token = get_decoded_token(token)
        tenant_id = decoded_token.get("tenant_id")
        user_id = decoded_token.get("user_id")
    else:
        tenant_id = event.get(X_TENANT_ID)
        user_id = event.get(X_USER_ID)
        if not tenant_id or not user_id:
            return {}
        token = vend(tenant_id, user_id, secret_key)

    return {
        "token": token,
        "tenant_id": tenant_id,
        "user_id": user_id,
    }


def get_decoded_token(token, secret_key='aws-saas-factory'):
    """
    Decodes token using PyJWT library
        :param token:
        :param secret_key='aws-saas-factory':
    """
    return jwt.decode(jwt=token,
                      key=secret_key,
                      algorithm='HS256')


encoded_token = vend('tenantb', 'user1')
print("TenantA:" + encoded_token)
encoded_token = vend('tenantb', 'user2')
print("TenantA:" + encoded_token)