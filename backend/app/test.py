from newsplease import NewsPlease
from newspaper import Article


if __name__ == "__main__":
    a = NewsPlease.from_url(
        "https://www.sueddeutsche.de/politik/krieg-in-der-ukraine-schwere-kaempfe-vor-neuen-ukraine-friedensgespraechen-dpa.urn-newsml-dpa-com-20090101-250601-930-616267")
    print(a.maintext)
