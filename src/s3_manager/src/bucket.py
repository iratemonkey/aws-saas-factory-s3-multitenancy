#!/usr/bin/env python3

# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
This script performs 2 operations:
PUT operation on objects into tenant-specific buckets.
GET operation to retrieve objects based on tenant context.
"""

import os
from http import HTTPStatus

import botocore

import constants
import helper


def put_object(sts_creds, req_header):
    """
    Uploads objects and tenant_id/user_id into separate bucket
        :param event:
        :param context:
        :return: 201 - Success
                 400 - Bad Request, 401 - Unauthorized
                 500 - Error, 502 - Service Unavailable
    """
    try:
        s3_client = helper.get_boto3_client("s3", sts_creds)
        helper.check_create_bucket(s3_client, req_header["bucket_name"])
        api_put_resp = s3_client.put_object(Bucket=req_header["bucket_name"],
                                            Key="{0}/{1}".format(req_header["user_id"],
                                                                 req_header["object_key"]),
                                            Body=req_header["object_value"])

        if api_put_resp and \
                api_put_resp["ResponseMetadata"]["HTTPStatusCode"] == HTTPStatus.OK:
            return helper.success_response(api_put_resp)
        else:
            return helper.failure_response("Operation failed. Please retry.",
                                           HTTPStatus.SERVICE_UNAVAILABLE)

    except Exception as ex:
        return helper.failure_response(helper.format_exception(ex))


def get_object(sts_creds, req_header):
    """
    Retrieve objects for tenant-specific bucket by AssumeRole()
        :param event:
        :param context:
        :return: 200 - Success
                 400 - Bad Request, 401 - Unauthorized
                 500 - Error, 503 - Unavailable
    """
    try:
        s3_client = helper.get_boto3_client("s3", sts_creds)
        api_list_resp = s3_client.list_objects_v2(Bucket=req_header["bucket_name"],
                                                  Prefix=req_header["user_id"])

        if api_list_resp and api_list_resp['KeyCount'] > 0:
            user_objects = [obj['Key'].rsplit('/', 1)[-1]
                            for obj in api_list_resp['Contents']]
            return helper.success_response(user_objects,
                                           HTTPStatus.OK)
        else:
            return helper.failure_response("Operation failed. Please retry.",
                                           HTTPStatus.SERVICE_UNAVAILABLE)

    except botocore.exceptions.ClientError as ex:
        return helper.failure_response_message(helper.format_exception(ex),
                                               ex.response["Error"]["Code"])

    except Exception as ex:
        return helper.failure_response(helper.format_exception(ex))


def populate_context(event):
    """
    Adds derived fields to support operations
        :param req_header:
    """
    req_header = helper.get_tenant_context(event)
    if "missing_fields" in req_header:
        return req_header

    bucket_name = "{0}-{1}-{2}".format(constants.BUCKET_NAME_BKT,
                                       req_header["tenant_id"].lower(),
                                       os.environ["AWS_ACCOUNT_ID"])
    req_header["bucket_name"] = bucket_name
    req_header["bucket_arn"] = "arn:aws:s3:::{0}".format(bucket_name)
    return req_header
