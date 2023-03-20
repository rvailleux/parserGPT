# parserGPT

# Scrap a subdomain
```shell
# Will scrap all links of the URL passed in argument reccursively éfor each link below that contains the URL
# -d is for debug
# It will put scraped content into files under the /content/<URL_DOMAIN> folder
python3 scraper.py -u https://example.com/subfolder -d
```

# Process the scraped content and turn it into embeddings
```shell
python3 process.py -u https://example.com/subfolder -d
```

# Start an endpoint
```shell
python3 endpoint.py
```

Exposed endpoints:
- `/answer?question=Question&userid=20202` returns the GPT 3.5 answer to the `question`. All conversations are stored into the /messages/ folder
- `/public/*` returns all the fils of the public/ folder
- `/chatbot` returns the chatbot template file