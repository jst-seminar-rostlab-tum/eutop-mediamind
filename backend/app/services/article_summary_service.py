import uuid
from typing import Optional

from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import ChatOpenAI
from sqlmodel import Session

from app.core.config import configs
from app.models.article import Article
from app.repositories.article_repository import ArticleRepository


def summarize_text(text: str) -> str:
    """
    Summarizes the given text using a language model.

    Args:
        text (str): The text to summarize.

    Returns:
        str: The summarized text.
    """

    llm = ChatOpenAI(
        model="gpt-4o-mini", temperature=0, api_key=configs.OPENAI_API_KEY
    )

    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_text(text)

    docs = [Document(page_content=t) for t in texts]

    chain = load_summarize_chain(llm, chain_type="map_reduce")

    summary = chain.invoke(docs)
    return summary


def summarize_and_store(
    *, session: Session, article_id: uuid.UUID
) -> Optional[Article]:
    # 1. Artikel laden
    article = ArticleRepository.get_article_by_id(article_id)
    if not article:
        return None

    # 2. Zusammenfassen
    article.summary = summarize_text(article.content)

    # 3. Zusammenfassung speichern
    return ArticleRepository.update_article(article)


TEST_TEXT = r"""
### Das Europäische Parlament: Eine umfassende Betrachtung seiner Geschichte, Struktur, Aufgaben und Bedeutung

Das **Europäische Parlament (EP)** ist eine der zentralen Institutionen der Europäischen Union (EU) und spielt eine entscheidende Rolle in der Gesetzgebung, politischen Kontrolle und der Repräsentation der Bürger der EU. Es ist das einzige Organ der EU, dessen Mitglieder direkt von den Bürgern der Mitgliedsstaaten gewählt werden. Im folgenden Artikel gehen wir detailliert auf die Geschichte, Struktur, Aufgaben und Bedeutung des Europäischen Parlaments ein und betrachten, wie es die politische Landschaft der EU beeinflusst.

#### 1. **Die Geschichte des Europäischen Parlaments**

Die Entwicklung des Europäischen Parlaments ist eng mit der Entstehung der Europäischen Union und ihren Vorläufern verbunden. Der Ursprung des Parlaments liegt in der Schaffung der Europäischen Gemeinschaft für Kohle und Stahl (EGKS) im Jahr 1951. Diese Organisation, die als Vorläufer der Europäischen Union betrachtet wird, war ein erster Schritt hin zu einer engeren politischen und wirtschaftlichen Zusammenarbeit in Europa nach dem Zweiten Weltkrieg.

**1952**: Die erste Parlamentarische Versammlung der Europäischen Gemeinschaften wurde gegründet. Diese bestand aus Abgeordneten, die von den nationalen Parlamenten der Mitgliedstaaten entsandt wurden. Diese Versammlung hatte lediglich eine beratende Funktion und keine legislativen Befugnisse.

**1979**: Ein historischer Wendepunkt kam mit den ersten **direkten Wahlen** zum Europäischen Parlament. Bis zu diesem Zeitpunkt wurden die Abgeordneten weiterhin von den nationalen Parlamenten entsandt. Mit den Wahlen 1979 erhielten die Bürger der Mitgliedstaaten erstmals die Möglichkeit, ihre Vertreter im Europäischen Parlament direkt zu wählen. Dies stärkte die demokratische Legitimation des Parlaments erheblich.

**1992 - Vertrag von Maastricht**: Mit dem Vertrag von Maastricht wurden die Befugnisse des Europäischen Parlaments erheblich erweitert. Es erlangte ein Mitentscheidungsrecht, das es ihm ermöglichte, in vielen Bereichen, insbesondere bei der Gesetzgebung, gleichwertig mit dem **Rat der Europäischen Union** zu entscheiden. Der Vertrag von Maastricht war somit ein entscheidender Schritt hin zu einem stärker parlamentarischen System in der EU.

**2009 - Vertrag von Lissabon**: Der Vertrag von Lissabon verstärkte die Macht des Europäischen Parlaments weiter, indem er das Mitentscheidungsverfahren auf fast alle Politikbereiche ausdehnte. Außerdem erhielt das Parlament mehr Mitspracherechte bei der Wahl der Europäischen Kommission und ihren Präsidenten.

#### 2. **Die Struktur des Europäischen Parlaments**

Das Europäische Parlament ist ein internationales, supranationales Organ, das aus Abgeordneten besteht, die die Bürger der Europäischen Union vertreten. Es ist eine einzigartige Institution, da seine Mitglieder direkt gewählt werden und es somit die Interessen der europäischen Bürger im Gesetzgebungsprozess vertritt. Die Struktur des Europäischen Parlaments ist wie folgt:

1. **Abgeordnete**: Das Europäische Parlament setzt sich aus 705 Abgeordneten zusammen, die alle fünf Jahre gewählt werden. Die Zahl der Abgeordneten eines Landes richtet sich nach der Bevölkerungsgröße des Landes, wobei größere Länder mehr Abgeordnete haben. Deutschland hat beispielsweise 96 Abgeordnete, während kleinere Länder wie Malta nur 6 Abgeordnete entsenden. Die Abgeordneten vertreten die politischen Interessen ihrer jeweiligen Staaten, aber auch überparteilich als Mitglieder politischer Fraktionen.

2. **Fraktionen**: Im Europäischen Parlament organisieren sich die Abgeordneten nicht nach Nationalität, sondern nach politischen Fraktionen, die auf gemeinsamen ideologischen Prinzipien basieren. Die größten Fraktionen sind:

   * **Europäische Volkspartei (EVP)**: Eine konservative und christlich-demokratische Fraktion.
   * **Progressive Allianz der Sozialisten und Demokraten (S\&D)**: Eine sozialdemokratische Fraktion.
   * **Renew Europe (RE)**: Eine liberale Fraktion.
   * **Die Grünen / Europäische Freie Allianz (Greens/EFA)**: Eine Fraktion, die sich auf Umweltschutz und soziale Gerechtigkeit konzentriert.
   * **Identität und Demokratie (ID)**: Eine rechte, nationalistische Fraktion.
   * **Europäische Konservative und Reformisten (ECR)**: Eine Fraktion, die einen eher euroskeptischen Ansatz vertritt.

3. **Der Präsident des Europäischen Parlaments**: Der Präsident des Europäischen Parlaments wird alle zweieinhalb Jahre gewählt und übernimmt die Leitung der Plenarsitzungen. Er oder sie repräsentiert das Parlament in internationalen Angelegenheiten und stellt sicher, dass die parlamentarischen Abläufe korrekt und fair ablaufen.

4. **Ausschüsse**: Ein wichtiger Bestandteil des Parlaments sind die **Ausschüsse**. Diese Ausschüsse spielen eine entscheidende Rolle bei der Bearbeitung von Gesetzesvorschlägen und bei der Durchführung der parlamentarischen Kontrolle. Zu den bekanntesten Ausschüssen gehören der Ausschuss für auswärtige Angelegenheiten, der Wirtschaftsausschuss und der Umweltausschuss. Ausschüsse sind auch für die Erstellung von Berichten und Empfehlungen verantwortlich.

#### 3. **Die Aufgaben des Europäischen Parlaments**

Das Europäische Parlament hat eine Vielzahl von Aufgaben, die es zu einer der mächtigsten Institutionen der EU machen. Zu den wichtigsten Aufgaben gehören:

1. **Gesetzgebung**: Eine der zentralen Aufgaben des Europäischen Parlaments ist die **Gesetzgebung**. Es teilt sich diese Verantwortung mit dem Rat der Europäischen Union, wobei in vielen Fällen das Parlament und der Rat die gleiche Entscheidungsbefugnis haben. Das Parlament arbeitet an der Ausarbeitung und Verabschiedung von EU-Gesetzen, die alle Mitgliedstaaten betreffen, und das Mitentscheidungsverfahren gibt dem Parlament in vielen Bereichen eine gleichwertige Rolle.

2. **Haushaltsrecht**: Das Europäische Parlament hat das Recht, den EU-Haushalt zu genehmigen und zu ändern. Der Parlamentarische Haushalt ist ein entscheidendes Instrument, um die finanziellen Prioritäten der EU festzulegen, und das Parlament hat bedeutende Macht, um die Verteilung von Geldern zu beeinflussen. Das Parlament kann Änderungen am Haushaltsvorschlag der Kommission vornehmen und den Haushalt in seiner Gesamtheit ablehnen.

3. **Politische Kontrolle**: Das Europäische Parlament hat auch eine **Kontrollfunktion**. Es überwacht die Arbeit der Europäischen Kommission, stellt Fragen und fordert Berichte an. Das Parlament hat das Recht, der Kommission das Vertrauen zu entziehen, was weitreichende Konsequenzen für die Kommission hätte. Ebenso kann das Parlament andere Institutionen der EU zur Rechenschaft ziehen.

4. **Wahlen des Kommissionspräsidenten**: Seit dem Vertrag von Lissabon hat das Parlament auch ein Mitspracherecht bei der Wahl des Präsidenten der Europäischen Kommission. Das Parlament stimmt dem Kandidaten, der von den Staats- und Regierungschefs der EU-Mitgliedstaaten nominiert wird, zu oder lehnt ihn ab.

5. **Genehmigung internationaler Abkommen**: Das Parlament muss viele internationale Verträge, die von der EU ausgehandelt werden, genehmigen. Dies gilt insbesondere für Handelsabkommen und internationale Vereinbarungen. Das Parlament hat so die Möglichkeit, die Außenpolitik der EU mitzugestalten und sicherzustellen, dass die Interessen der Bürger gewahrt bleiben.

6. **Förderung der Menschenrechte und Demokratie**: Das Europäische Parlament ist ein Verfechter von Menschenrechten, Demokratie und Rechtsstaatlichkeit weltweit. Es setzt sich regelmäßig für die Förderung dieser Werte sowohl innerhalb als auch außerhalb der EU ein und hat eine bedeutende Rolle in der Außenpolitik der Union.

#### 4. **Der Gesetzgebungsprozess im Europäischen Parlament**

Der Gesetzgebungsprozess im Europäischen Parlament folgt einem strukturierten Ablauf und umfasst mehrere wichtige Phasen:

1. **Vorschläge der Europäischen Kommission**: Die Europäische Kommission hat das Recht, Gesetzesvorschläge zu machen, die dann vom Parlament und dem Rat der EU geprüft werden. Der Kommissionsvorschlag dient als Grundlage für die parlamentarische Arbeit.

2. **Erste Lesung**: Nach Eingang des Vorschlags wird dieser in den zuständigen Ausschüssen des Parlaments erörtert. Der Ausschuss kann den Vorschlag ändern und gibt seine Stellungnahme dann dem Plenum zur Abstimmung.

3. **Zweite Lesung**: Wenn der Rat Änderungen am Vorschlag vornimmt, wird der Text erneut dem Parlament zur Diskussion und Abstimmung vorgelegt. Wenn das Parlament den geänderten Text ablehnt, wird ein „Trilog“ zwischen Parlament, Rat und Kommission durchgeführt, um einen Kompromiss zu finden.

4. **Verabschiedung**: Wenn alle drei Institutionen – das Parlament, der Rat und die Kommission – sich auf einen Text einigen, wird dieser Gesetzesvorschlag verabschiedet und tritt in Kraft.

#### 5. **Bedeutung des Europäischen Parlaments**

Das Europäische Parlament spielt eine Schlüsselrolle bei der Schaffung eines demokratischen und transparenten Entscheidungsprozesses in der Europäischen Union. Es sorgt für eine direkte Verbindung zwischen den Bürgern und den EU-Institutionen, da die Abgeordneten direkt gewählt werden. Damit ist das Parlament ein unverzichtbares Organ der EU, das die Interessen der Bürger auf europäischer Ebene vertritt.

Die politische Bedeutung des Parlaments wächst stetig, insbesondere seit den Vertragsreformen der letzten Jahrzehnten. Es hat mittlerweile weitreichende Gesetzgebungs- und Kontrollbefugnisse, die es ihm ermöglichen, eine zentrale Rolle bei der Gestaltung der EU-Politik zu spielen. Durch die Kontrolle des Haushalts und der Kommission hat das Parlament entscheidenden Einfluss auf die Ausrichtung der Union und ihre politischen Prioritäten.

#### Fazit

Das Europäische Parlament ist eine der bedeutendsten Institutionen der EU und hat eine zentrale Funktion im politischen Leben der Union. Mit seinen Gesetzgebungs-, Kontroll- und Haushaltsbefugnissen beeinflusst es maßgeblich die europäische Politik. Die direkte Wahl der Abgeordneten durch die Bürger macht das Parlament zu einer einzigartigen Institution und einem wichtigen demokratischen Organ der EU. Angesichts der fortwährenden politischen und wirtschaftlichen Herausforderungen bleibt das Europäische Parlament eine essentielle Institution, die maßgeblich an der Gestaltung der Zukunft Europas beteiligt ist.

"""

if __name__ == "__main__":
    x = summarize_text(text=TEST_TEXT)
    print(x)
    print("--------------------")
    print(x.output_text)
