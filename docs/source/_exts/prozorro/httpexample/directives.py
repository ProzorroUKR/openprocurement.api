# -*- coding: utf-8 -*-
from docutils import nodes
from docutils.statemachine import StringList
from docutils.parsers.rst import directives
from sphinx.directives.code import CodeBlock
from . import utils

import os


class HTTPExample(CodeBlock):

    required_arguments = 1
    option_spec = {
        # Unused. Just to skip removing of all existing :code: options
        'code': directives.unchanged,
    }

    def run(self):
        config = self.state.document.settings.env.config

        # Load external file
        cwd = os.path.dirname(self.state.document.current_source)
        if self.arguments:
            response = utils.resolve_path(self.arguments[0], cwd)
            with open(response) as fp:
                self.content = StringList(
                    list(map(str.rstrip, fp.readlines())), response)

        # Enable 'http' language for http part
        self.arguments = ['http']

        # split the request and optional response in the content.
        # The separator is two empty lines followed by a line starting with
        # 'HTTP/' or 'HTTP '
        request_content = StringList()
        response_content = None
        emptylines_count = 0
        in_response = False
        for i, line in enumerate(self.content):
            source = self.content.source(i)
            if in_response:
                response_content.append(line, source)
            else:
                if emptylines_count >= 2 and \
                        (line.startswith('HTTP/') or line.startswith('HTTP ')):
                    in_response = True
                    response_content = StringList()
                    response_content.append(line, source)
                elif line == '':
                    emptylines_count += 1
                else:
                    request_content.extend(
                        StringList([''] * emptylines_count, source))
                    request_content.append(line, source)

                    emptylines_count = 0

        # reset the content to just the request
        self.content = request_content

        # Wrap and render main directive as 'http-example-http'
        klass = 'http-example-http'
        container = nodes.container('', classes=[klass])
        container.append(nodes.caption('', 'Request' if response_content else 'Example'))
        container.extend(super(HTTPExample, self).run())

        # Init result node list
        result = [container]

        # Append optional response
        if response_content:
            options = self.options.copy()
            options.pop('name', None)
            options.pop('caption', None)

            block = CodeBlock(
                'code-block',
                ['http'],
                options,
                response_content,
                self.lineno,
                self.content_offset,
                self.block_text,
                self.state,
                self.state_machine
            )

            # Wrap and render main directive as 'http-example-response'
            klass = 'http-example-response'
            container = nodes.container('', classes=[klass])
            container.append(nodes.caption('', 'Response'))
            container.extend(block.run())

            # Append to result nodes
            result.append(container)

        # Final wrap
        container_node = nodes.container('', classes=['http-example'])
        container_node.extend(result)

        return [container_node]
