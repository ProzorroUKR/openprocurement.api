import os
import json
import re

from docutils import nodes
from docutils.parsers.rst import directives
from docutils.statemachine import StringList
from sphinx.directives.code import CodeBlock

from . import utils


class HTTPExample(CodeBlock):
    required_arguments = 1
    option_spec = {
        # Unused. Just to skip removing of all existing :code: options
        "code": directives.unchanged,
    }

    def is_json_content(self, content):
        """Check if content contains valid JSON."""
        if not content:
            return False
        
        # Find the JSON part after HTTP headers
        json_start = self._find_json_start(content)
        if json_start is None:
            return False
        
        # Extract JSON part
        json_lines = content[json_start:]
        text = '\n'.join(json_lines).strip()
        
        # Try to parse as JSON
        try:
            json.loads(text)
            return True
        except (json.JSONDecodeError, ValueError):
            return False

    def _find_json_start(self, content):
        """Find the starting line index of JSON content."""
        for i, line in enumerate(content):
            line = line.strip()
            # Look for empty line followed by JSON start
            if line == "" and i + 1 < len(content):
                next_line = content[i + 1].strip()
                if next_line.startswith('{') or next_line.startswith('['):
                    return i + 1
            # Or if line starts with JSON directly
            elif line.startswith('{') or line.startswith('['):
                return i
        return None

    def _extract_json_lines(self, content):
        """Extract only the JSON lines from content."""
        json_start = self._find_json_start(content)
        if json_start is None:
            return content
        return content[json_start:]

    def _extract_headers_lines(self, content):
        """Extract only the HTTP headers lines from content."""
        json_start = self._find_json_start(content)
        if json_start is None:
            return content
        return content[:json_start]

    def run(self):
        # Load external file
        cwd = os.path.dirname(self.state.document.current_source)
        if self.arguments:
            response = utils.resolve_path(self.arguments[0], cwd)
            with open(response) as fp:
                self.content = StringList(list(map(str.rstrip, fp.readlines())), response)

        # Enable 'http' language for http part
        self.arguments = ["http"]

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
                if emptylines_count >= 2 and (line.startswith("HTTP/") or line.startswith("HTTP ")):
                    in_response = True
                    response_content = StringList()
                    response_content.append(line, source)
                elif line == "":
                    emptylines_count += 1
                else:
                    request_content.extend(StringList([""] * emptylines_count, source))
                    request_content.append(line, source)

                    emptylines_count = 0

        # Check if request contains JSON
        request_is_json = False
        if request_content:
            request_list = [str(line) for line in request_content]
            request_is_json = self.is_json_content(request_list)

        # reset the content to just the request
        self.content = request_content

        # Wrap and render main directive as 'http-example-request'
        klass = "http-example-request"
        container = nodes.container("", classes=[klass])
        
        # Add folding controls for JSON content in request
        if request_is_json:
            # First show HTTP headers
            headers_lines = self._extract_headers_lines(request_content)
            if headers_lines:
                headers_content_list = StringList(headers_lines, source=self.content.source)
                headers_block = CodeBlock(
                    "code-block",
                    ["http"],
                    self.options.copy(),
                    headers_content_list,
                    self.lineno,
                    self.content_offset,
                    self.block_text,
                    self.state,
                    self.state_machine,
                )
                container.extend(headers_block.run())
            
            # Then show JSON content in foldable container
            foldable_container = nodes.container("", classes=["json-foldable"])
            
            # Add toggle button
            toggle_button = nodes.raw("", '<button class="json-fold-toggle">Expand</button>', format="html")
            foldable_container.append(toggle_button)
            
            # Wrap code content
            json_content = nodes.container("", classes=["json-content"])
            
            # Extract only the JSON part for highlighting
            json_lines = self._extract_json_lines(request_content)
            json_content_list = StringList(json_lines, source=self.content.source)
            
            # Create code block with only JSON content
            options = self.options.copy()
            options.pop("name", None)
            options.pop("caption", None)
            block = CodeBlock(
                "code-block",
                ["json"],
                options,
                json_content_list,
                self.lineno,
                self.content_offset,
                self.block_text,
                self.state,
                self.state_machine,
            )
            json_content.extend(block.run())
            foldable_container.append(json_content)
            
            container.append(foldable_container)
        else:
            container.extend(super().run())

        # Init result node list
        result = [container]

        # Append optional response
        if response_content:
            options = self.options.copy()
            options.pop("name", None)
            options.pop("caption", None)

            # Check if response contains JSON
            # Convert StringList to regular list for JSON detection
            response_list = [str(line) for line in response_content]
            is_json = self.is_json_content(response_list)
            
            # Wrap and render main directive as 'http-example-response'
            klass = "http-example-response"
            container = nodes.container("", classes=[klass])
            
            # Add folding controls for JSON content
            if is_json:
                # First show HTTP headers
                headers_lines = self._extract_headers_lines(response_content)
                if headers_lines:
                    headers_content_list = StringList(headers_lines, source=self.content.source)
                    headers_block = CodeBlock(
                        "code-block",
                        ["http"],
                        options,
                        headers_content_list,
                        self.lineno,
                        self.content_offset,
                        self.block_text,
                        self.state,
                        self.state_machine,
                    )
                    container.extend(headers_block.run())
                
                # Then show JSON content in foldable container
                foldable_container = nodes.container("", classes=["json-foldable"])
                
                # Add toggle button
                toggle_button = nodes.raw("", '<button class="json-fold-toggle">Expand</button>', format="html")
                foldable_container.append(toggle_button)
                
                # Wrap code content
                json_content = nodes.container("", classes=["json-content"])
                
                # Extract only the JSON part for highlighting
                json_lines = self._extract_json_lines(response_content)
                json_content_list = StringList(json_lines, source=self.content.source)
                
                # Create code block with only JSON content
                block = CodeBlock(
                    "code-block",
                    ["json"],
                    options,
                    json_content_list,
                    self.lineno,
                    self.content_offset,
                    self.block_text,
                    self.state,
                    self.state_machine,
                )
                json_content.extend(block.run())
                foldable_container.append(json_content)
                
                container.append(foldable_container)
            else:
                # Use HTTP highlighting for non-JSON content
                block = CodeBlock(
                    "code-block",
                    ["http"],
                    options,
                    response_content,
                    self.lineno,
                    self.content_offset,
                    self.block_text,
                    self.state,
                    self.state_machine,
                )
                container.extend(block.run())

            # Append to result nodes
            result.append(container)

        # Final wrap
        container_node = nodes.container("", classes=["http-example"])
        container_node.extend(result)

        return [container_node]
