from email.mime.text import MIMEText

import random
import re
import string

from flask import Flask, Response, request, stream_with_context

content = string.printable
content_length = len(content)

app = Flask('rrex')


def make_sep():
    nonce = ''.join(random.choices(string.digits, k=20))
    return f'==============={nonce}=='


@app.route('/')
def get_content():
    response = Response()
    response.headers.add('Accept-ranges', 'bytes')

    rangeh = request.headers.get('Range')

    if rangeh:
        response.status = '206 Partial content'
        unit, ranges = rangeh.split('=')
        ranges = re.split(',\s*', ranges)
        spans = []

        for rspec in ranges:
            if mo := re.match('-(\d+)', rspec):
                rstart = content_length - int(mo.group(1))
                rend = content_length
                spans.append((rstart, rend))
            else:
                rstart, rend = rspec.split('-')
                rstart = int(rstart)
                rend = int(rend) if rend else content_length
                spans.append((rstart, rend))

        if len(spans) == 1:
            rstart, rend = spans[0]
            response.data = content[rstart:rend]
            response.headers.add('content-range', f'{rstart}-{rend}/{content_length}')
        else:
            sep = make_sep()
            parts = []

            for span in spans:
                rstart, rend = span
                part = MIMEText(content[rstart:rend])
                part.add_header('content-range', f'{rstart}-{rend}/{content_length}')
                part.add_header('content-length', str(rend-rstart))
                parts.append(f'--{sep}\n{part}')

            response.data = '\n\n'.join(parts)
    else:
        response.data = content

    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
