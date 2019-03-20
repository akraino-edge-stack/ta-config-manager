# Copyright 2019 Nokia

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


class CMHTTPErrors(object):
    # response for a successful GET, PUT, PATCH, DELETE,
    # can also be used for POST that does not result in creation.
    HTTP_OK = 200
    # response to a POST which results in creation.
    HTTP_CREATED = 201
    # response to a successfull request that won't be returning any body like a DELETE request
    HTTP_NO_CONTENT = 204
    # used when http caching headers are in play
    HTTP_NOT_MODIFIED = 304
    # the request is malformed such as if the body does not parse
    HTTP_BAD_REQUEST = 400
    # when no or invalid authentication details are provided.
    # also useful to trigger an auth popup API is used from a browser
    HTTP_UNAUTHORIZED_OPERATION = 401
    # when authentication succeeded but authenticated user doesn't have access to the resource
    HTTP_FORBIDDEN = 403
    # when a non-existent resource is requested
    HTTP_NOT_FOUND = 404
    # when an http method is being requested that isn't allowed for the authenticated user
    HTTP_METHOD_NOT_ALLOWED = 405
    # indicates the resource at this point is no longer available
    HTTP_GONE = 410
    # if incorrect content type was provided as part of the request
    HTTP_UNSUPPORTED_MEDIA_TYPE = 415
    # used for validation errors
    HTTP_UNPROCESSABLE_ENTITY = 422
    # when request is rejected due to rate limiting
    HTTP_TOO_MANY_REQUESTS = 429
    # Other errrors
    HTTP_INTERNAL_ERROR = 500

    @staticmethod
    def get_ok_status():
        return '%d OK' % CMHTTPErrors.HTTP_OK

    @staticmethod
    def get_object_created_successfully_status():
        return '%d Created' % CMHTTPErrors.HTTP_CREATED

    @staticmethod
    def get_request_not_ok_status():
        return '%d Bad request' % CMHTTPErrors.HTTP_BAD_REQUEST

    @staticmethod
    def get_resource_not_found_status():
        return '%d Not found' % CMHTTPErrors.HTTP_NOT_FOUND

    @staticmethod
    def get_unsupported_content_type_status():
        return '%d Unsupported content type' % CMHTTPErrors.HTTP_UNSUPPORTED_MEDIA_TYPE

    @staticmethod
    def get_validation_error_status():
        return '%d Validation error' % CMHTTPErrors.HTTP_UNPROCESSABLE_ENTITY

    @staticmethod
    def get_internal_error_status():
        return '%d Internal error' % CMHTTPErrors.HTTP_INTERNAL_ERROR
