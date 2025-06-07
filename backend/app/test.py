import json

import trafilatura

if __name__ == "__main__":
    html_content = trafilatura.fetch_url(
        "https://www.merkur.de/politik/trump-telefoniert-"
        "erneut-mit-putin-zum-ukraine-krieg-zr-93741274.html"
    )
    result = trafilatura.extract(
        html_content, output_format="json", with_metadata=True
    )
    a = json.loads(result)
    print(type(a))
