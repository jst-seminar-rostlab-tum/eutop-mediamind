export interface NewsArticle {
  id: string;
  title: string;
  content: string;
  url: string;
  author: string;
  published_at: string;
  language: string;
  category: string;
  summary: string;
  subscription_id: string;
  status: string;
  crawled_at: string;
  scraped_at: string;
}

export const getArticle = (): NewsArticle => {
  return {
    id: "a7a02941-0fee-4865-9ff6-d03fc0bc9a4b",
    title:
      "Deutschland erneut Jodmangelgebiet: Warum das für die Gesundheit gefährlich ist",
    content:
      "Jodmangel ist in Deutschland zurück – laut WHO mit ernsten Folgen. Besonders betroffen: die Schilddrüse und das Hormonsystem. Viele heutige Schilddrüsenprobleme gehen auf starken Jodmangel vor den 1980er Jahren zurück, bevor die Jodmangel-Prophylaxe eingeführt wurde. Die Jodversorgung verbesserte sich damals deutlich durch jodiertes Speisesalz und jodiertes Tierfutter. Anfang der 2000er Jahre galt das Problem weitgehend als gelöst. Doch die WHO weist darauf hin, dass der Trend zu einer Ernährung ohne tierische Produkte und der steigende Anteil an Bioprodukten, die meist weniger Jod enthalten als konventionelle Lebensmittel, zu einem erneuten Anstieg des Jodmangels beitragen. Das kann gesundheitliche Folgen haben. Studien des Robert-Koch-Instituts zeigen, dass 32 Prozent der Erwachsenen und 44 Prozent der Kinder und Jugendlichen in Deutschland ein erhöhtes Risiko für Jodmangel haben. Die Weltgesundheitsorganisation WHO stuft Deutschland inzwischen wieder als Jodmangelgebiet ein. Dies kann erhebliche gesundheitliche Folgen haben. Jodmangel in Deutschland: Unterversorgung kann Schilddrüse schaden Da der Körper Jod nicht selbst herstellen kann, ist das Spurenelement lebenswichtig, wie ARD Gesund betont. Es wird benötigt, um Schilddrüsenhormone zu produzieren. Die T3- und T4-Hormone steuern viele wichtige Körperfunktionen: Sie beeinflussen Herz und Kreislauf, regulieren den Blutdruck, fördern das Gewebewachstum und die Zellteilung. Zudem sind sie für die gesunde Funktion von Gehirn und Nervensystem unerlässlich und spielen eine Rolle bei der Regulierung des Körpergewichts. Ein Jodmangel kann langfristig zu einer Vergrößerung der Schilddrüse führen. Im schlimmsten Fall entstehen Knoten, die selten bösartig sind, aber auf Schilddrüsenkrebs hinweisen können. Häufig zeigt sich eine sichtbare Vergrößerung der Schilddrüse, der sogenannte Kropf oder Struma. Außerdem kann Jodmangel depressive Verstimmungen, Konzentrationsschwäche, Lernprobleme sowie Symptome wie Schwitzen, Schlafstörungen, Durchfall und Gewichtsverlust verursachen. Besonders kritisch ist ein Jodmangel während Schwangerschaft und Stillzeit, da er bei Kindern dauerhafte Entwicklungs- und Funktionsstörungen hervorrufen kann. Gesundheitliche Folgen: Jodmangel kann bei Frauen besonders gefährlich sein Eine verbesserte Jodversorgung wäre vor allem für Frauen wichtig. Laut ARD Gesund sind Frauen deutlich häufiger von Schilddrüsenerkrankungen betroffen als Männer. Die genauen Ursachen sind noch nicht abschließend erforscht, doch hormonelle Veränderungen – etwa durch Schwangerschaft, hormonelle Verhütung oder die Wechseljahre – können die empfindliche Schilddrüsenfunktion stören. Zudem ist das Immunsystem von Frauen in der Regel stärker aktiv, was sie zwar besser vor Infektionen schützt, sie aber gleichzeitig anfälliger für Autoimmunerkrankungen macht. Dazu gehören Schilddrüsenerkrankungen wie Hashimoto-Thyreoiditis oder Morbus Basedow. Vorschläge gegen Jodmangel: Jodsalz in Lebensmittelindustrie kann Jodmangel Bekämpfen In den letzten zehn Jahren haben sich die Ernährungsgewohnheiten der Deutschen deutlich gewandelt. Immer mehr Menschen greifen vermehrt zu pflanzlichen Lebensmitteln. Eine Ernährung mit weniger Fleisch und Milchprodukten sowie der verstärkte Konsum von Bioprodukten hat viele Vorteile – deswegen müsse sich die Industrie anpassen. Die Jodierung von Speisesalz bleibt weiterhin die wichtigste Maßnahme zur Sicherstellung einer ausreichenden Jodversorgung. Gauden Galea, strategischer Berater des Regionaldirektors im Rahmen der WHO-Sonderinitiative für nichtübertragbare Krankheiten und Innovation (SNI), erklärt in einer Mitteilung der WHO: „In Anbetracht der veränderten Ernährungsgewohnheiten muss auch eine angemessene Anreicherung von alternativen Milch- und Molkereiprodukten mit Jod sichergestellt werden. Zudem seien verbindliche Vorgaben zur Verwendung von jodiertem Speisesalz in verarbeiteten Lebensmitteln nötig, um den Jodmangel europaweit zu bekämpfen.",
    url: "https://www.merkur.de/welt/deutschland-erneut-jodmangelgebiet-warum-das-fuer-die-gesundheit-gefaehrlich-ist-zr-93774187.html",
    author: "John Doe",
    published_at: "2025-06-06 18:06:41.000000",
    language: "German",
    category: "Newspaper Online",
    summary:
      "Iodine deficiency has re-emerged in Germany, posing serious risks to thyroid health and the hormonal system, as highlighted by the WHO. Despite improvements in iodine intake through iodized salt and animal feed, a shift towards plant-based diets and organic products, which often contain less iodine, has led to increased deficiency rates. Studies show that 32% of adults and 44% of children in Germany are at risk, prompting the WHO to classify the country as iodine-deficient. Iodine is crucial for thyroid hormone production, and deficiency can result in health issues such as goiter, depression, and developmental disorders in children, particularly during pregnancy and breastfeeding. Women are especially vulnerable due to higher rates of thyroid diseases. To combat this, experts recommend enhancing iodine levels in the food industry, including iodizing alternative dairy products and enforcing regulations for iodized salt in processed foods.",
    subscription_id: "44d4555a-9ed1-42bb-8973-9b1c0ef9f4ed",
    status: "SCRAPED",
    crawled_at: "2025-06-07 08:34:53.810000",
    scraped_at: "2025-06-07 08:37:40.688000",
  };
};
