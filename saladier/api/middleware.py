#
# Copyright 2013 IBM Corp.
# Copyright 2012 New Dream Network, LLC (DreamHost)
#
# Author: Doug Hellmann <doug.hellmann@dreamhost.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
"""Middleware to replace the plain text message body of an error
response with one formatted so the client can parse it.

Based on pecan.middleware.errordocument
"""
import json

from lxml import etree
import webob

from saladier.openstack.common import log

LOG = log.getLogger(__name__)


class ParsableErrorMiddleware(object):
    """Replace error body with something the client can parse."""

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        # Request for this state, modified by replace_start_response()
        # and used when an error is being reported.
        state = {}

        def replacement_start_response(status, headers, exc_info=None):
            """Overrides the default response to make errors parsable."""
            try:
                status_code = int(status.split(' ')[0])
                state['status_code'] = status_code
            except (ValueError, TypeError):  # pragma: nocover
                raise Exception((
                    'ErrorDocumentMiddleware received an invalid '
                    'status %s' % status
                ))
            else:
                if (state['status_code'] / 100) not in (2, 3):
                    # Remove some headers so we can replace them later
                    # when we have the full error message and can
                    # compute the length.
                    headers = [(h, v)
                               for (h, v) in headers
                               if h not in ('Content-Length', 'Content-Type')
                               ]
                # Save the headers in case we need to modify them.
                state['headers'] = headers
                return start_response(status, headers, exc_info)

        app_iter = self.app(environ, replacement_start_response)
        if (state['status_code'] / 100) not in (2, 3):
            req = webob.Request(environ)
            # Find the first TranslationHook in the array of hooks and use the
            # translatable_error object from it
            error = None
            if (req.accept.best_match(['application/json', 'application/xml'])
               == 'application/xml'):
                try:
                    # simple check xml is valid
                    faultstr = '\n'.join(
                        [x.decode() for x in app_iter])
                    fault = etree.fromstring(faultstr)
                    # Add the translated error to the xml data
                    if error is not None:
                        for fault_string in fault.findall('faultstring'):
                            fault_string.text = error
                    body_str = ('<error_message>' +
                                etree.tostring(fault).decode() +
                                '</error_message>')
                    body = [body_str.encode()]
                except etree.XMLSyntaxError as err:
                    LOG.error('Error parsing HTTP response: %s' % err)
                    body_str = ('<error_message>%s</error_message>' %
                                state['status_code'])
                    body = [body_str.encode()]
                state['headers'].append(('Content-Type', 'application/xml'))
            else:
                try:
                    fault = json.loads(
                        '\n'.join([x.decode() for x in app_iter]))
                    if error is not None and 'faultstring' in fault:
                        fault['faultstring'] = error
                    body = [json.dumps({'error_message': fault}).encode()]
                except ValueError as err:
                    error = '\n'.join([x.decode() for x in app_iter])
                    body = [json.dumps({'error_message': error}).encode()]
                state['headers'].append(('Content-Type', 'application/json'))
            state['headers'].append(('Content-Length', str(len(body[0]))))
        else:
            body = app_iter
        return body
