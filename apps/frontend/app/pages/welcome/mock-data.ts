export const profiles = [
  {
    id: "1",
    name: "Eutop",
    is_public: true,
    organization_emails: ["user@example.com"],
    profile_emails: ["user@example.com"],
    can_read_user_ids: ["1"],
    is_reader: true,
    can_edit_user_ids: ["1"],
    is_editor: true,
    owner_id: "1",
    is_owner: true,
    language: "en",
    topics: [
      {
        id: "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        name: "string",
        keywords: ["string"],
      },
    ],
    subscriptions: [
      {
        id: "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        name: "string",
        is_subscribed: true,
      },
    ],
    new_articles_count: 3,
  },
  {
    id: "2",
    name: "TUM",
    is_public: true,
    organization_emails: ["user@example.com"],
    profile_emails: ["user@example.com"],
    can_read_user_ids: ["1"],
    is_reader: true,
    can_edit_user_ids: ["2"],
    is_editor: false,
    owner_id: "2",
    is_owner: true,
    language: "en",
    topics: [
      {
        id: "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        name: "string",
        keywords: ["string"],
      },
    ],
    subscriptions: [
      {
        id: "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        name: "string",
        is_subscribed: true,
      },
    ],
    new_articles_count: 7,
  },
  {
    id: "3",
    name: "CSEE",
    is_public: false,
    organization_emails: ["user@example.com"],
    profile_emails: ["user@example.com"],
    can_read_user_ids: ["1"],
    is_reader: true,
    can_edit_user_ids: ["1"],
    is_editor: true,
    owner_id: "1",
    is_owner: true,
    language: "en",
    topics: [
      {
        id: "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        name: "string",
        keywords: ["string"],
      },
    ],
    subscriptions: [
      {
        id: "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        name: "string",
        is_subscribed: true,
      },
    ],
    new_articles_count: 7,
  },
];

export const matches = [
  {
    id: "1",
    relevance: 0.9,
    topics: [
      {
        id: "1",
        name: "Automotive",
        score: 0.95,
        keywords: [],
      },
    ],
    article: {
      article_url: "",
      headline: {
        en: "Cars: A Reliable Way to Get from A to B",
        de: "Autos: Eine zuverlässige Art, von A nach B zu kommen",
      },
      summary: {
        en: "Cars have long been a trusted method of transportation.\nThey offer flexibility, speed, and convenience.\nWhile public transport is growing, cars remain essential.\nMost families rely on at least one vehicle.\nInfrastructure continues to favor personal vehicles.",
        de: "Autos sind seit langem ein bewährtes Fortbewegungsmittel.\nSie bieten Flexibilität, Geschwindigkeit und Komfort.\nObwohl der öffentliche Verkehr zunimmt, bleiben Autos wichtig.\nDie meisten Familien besitzen mindestens ein Auto.\nDie Infrastruktur bevorzugt weiterhin den Individualverkehr.",
      },
      image_urls: ["https://picsum.photos/800/600?random=10"],
      date: "2025-07-16",
      source: "1",
    },
  },
  {
    id: "2",
    relevance: 0.88,
    topics: [
      {
        id: "2",
        name: "Environmental",
        score: 0.9,
        keywords: [],
      },
    ],
    article: {
      article_url: "",
      headline: {
        en: "Summer Temperatures Are on the Rise",
        de: "Die Sommertemperaturen steigen an",
      },
      summary: {
        en: "This summer has been one of the hottest on record.\nCities across the globe report increased heat waves.\nScientists link the rise to climate change.\nCitizens are encouraged to reduce energy use.\nGovernments are pushing for climate adaptation strategies.",
        de: "Dieser Sommer gehört zu den heißesten seit Beginn der Aufzeichnungen.\nStädte weltweit berichten von Hitzewellen.\nWissenschaftler sehen einen Zusammenhang mit dem Klimawandel.\nBürger sollen ihren Energieverbrauch senken.\nRegierungen fördern Anpassungsstrategien.",
      },
      image_urls: ["https://picsum.photos/800/600?random=9"],
      date: "2025-07-16",
      source: "2",
    },
  },
  {
    id: "3",
    relevance: 0.85,
    topics: [
      {
        id: "1",
        name: "Automotive",
        score: 0.88,
        keywords: [],
      },
    ],
    article: {
      article_url: "",
      headline: {
        en: "Electric Cars Gaining Popularity in Europe",
        de: "Elektroautos werden in Europa immer beliebter",
      },
      summary: {
        en: "More people are switching to electric cars every year.\nGovernment incentives are helping to lower costs.\nCharging infrastructure is expanding rapidly.\nAutomakers are releasing new models frequently.\nPublic perception of EVs is becoming more positive.",
        de: "Immer mehr Menschen steigen auf Elektroautos um.\nStaatliche Förderungen senken die Kosten.\nDie Ladeinfrastruktur wächst schnell.\nAutohersteller bringen regelmäßig neue Modelle heraus.\nDas öffentliche Bild von E-Autos verbessert sich.",
      },
      image_urls: ["https://picsum.photos/800/600?random=8"],
      date: "2025-07-08",
      source: "1",
    },
  },
  {
    id: "4",
    relevance: 0.86,
    topics: [
      {
        id: "2",
        name: "Environmental",
        score: 0.93,
        keywords: [],
      },
    ],
    article: {
      article_url: "",
      headline: {
        en: "Wind Energy Now Powers 20% of Local Grid",
        de: "Windenergie deckt nun 20 % des lokalen Stromnetzes",
      },
      summary: {
        en: "Wind turbines are generating a larger share of electricity.\nRural areas have seen major investment in renewables.\nMaintenance costs for wind farms are decreasing.\nLocal jobs are created through green energy projects.\nGrid upgrades improve renewable integration.",
        de: "Windkraft erzeugt einen immer größeren Teil des Stroms.\nLändliche Regionen profitieren von Investitionen.\nWartungskosten für Windparks sinken.\nGrüne Energie schafft neue Arbeitsplätze.\nNetzmodernisierungen erleichtern die Integration.",
      },
      image_urls: ["https://picsum.photos/800/600?random=7"],
      date: "2025-07-08",
      source: "3",
    },
  },
  {
    id: "5",
    relevance: 0.8,
    topics: [
      {
        id: "1",
        name: "Automotive",
        score: 0.82,
        keywords: [],
      },
    ],
    article: {
      article_url: "",
      headline: {
        en: "Routine Oil Changes Extend Engine Life",
        de: "Regelmäßiger Ölwechsel verlängert die Lebensdauer des Motors",
      },
      summary: {
        en: "Experts recommend changing oil every 10,000 km.\nClean oil helps engines run smoothly.\nDelaying oil changes can cause damage.\nMost manufacturers include oil change schedules.\nNewer cars have reminders for maintenance.",
        de: "Experten empfehlen einen Ölwechsel alle 10.000 km.\nSauberes Öl sorgt für einen reibungslosen Motorlauf.\nVerspätete Ölwechsel können Schäden verursachen.\nHersteller geben Wartungsintervalle vor.\nModerne Autos erinnern an den nächsten Ölwechsel.",
      },
      image_urls: ["https://picsum.photos/800/600?random=6"],
      date: "2025-07-02",
      source: "2",
    },
  },
  {
    id: "6",
    relevance: 0.84,
    topics: [
      {
        id: "2",
        name: "Environmental",
        score: 0.85,
        keywords: [],
      },
    ],
    article: {
      article_url: "",
      headline: {
        en: "Cities Invest in Urban Tree Planting",
        de: "Städte investieren in städtische Baumpflanzungen",
      },
      summary: {
        en: "Urban trees help cool cities and reduce pollution.\nMunicipalities are launching tree planting campaigns.\nTrees also improve mental well-being.\nGreen areas are linked to higher property values.\nCitizens are encouraged to volunteer for planting.",
        de: "Stadtbäume kühlen und verringern die Luftverschmutzung.\nKommunen starten Baumpflanzaktionen.\nBäume fördern auch das psychische Wohlbefinden.\nGrünflächen steigern Immobilienwerte.\nBürger sollen sich an Pflanzaktionen beteiligen.",
      },
      image_urls: ["https://picsum.photos/800/600?random=5"],
      date: "2025-06-16",
      source: "1",
    },
  },
  {
    id: "7",
    relevance: 0.75,
    topics: [
      {
        id: "1",
        name: "Automotive",
        score: 0.78,
        keywords: [],
      },
    ],
    article: {
      article_url: "",
      headline: {
        en: "The Future of Self-Driving Cars",
        de: "Die Zukunft selbstfahrender Autos",
      },
      summary: {
        en: "Self-driving technology is advancing quickly.\nMajor tech firms are investing heavily.\nSafety remains the top concern.\nLegal frameworks are under development.\nPilot programs are testing in urban areas.",
        de: "Selbstfahrende Technologie entwickelt sich schnell.\nGroße Technologiekonzerne investieren stark.\nSicherheit hat höchste Priorität.\nRechtliche Rahmenbedingungen entstehen.\nPilotprojekte testen in Städten.",
      },
      image_urls: ["https://picsum.photos/800/600?random=4"],
      date: "2025-06-10",
      source: "3",
    },
  },
  {
    id: "8",
    relevance: 0.83,
    topics: [
      {
        id: "2",
        name: "Environmental",
        score: 0.88,
        keywords: [],
      },
    ],
    article: {
      article_url: "",
      headline: {
        en: "Plastic Waste Still a Global Problem",
        de: "Plastikmüll bleibt ein globales Problem",
      },
      summary: {
        en: "Plastic continues to pollute oceans and landfills.\nRecycling rates are improving but remain low.\nSingle-use bans are gaining traction.\nNew materials offer eco-friendly alternatives.\nConsumers are shifting to reusable items.",
        de: "Plastik verschmutzt weiter Meere und Deponien.\nRecyclingquoten steigen langsam.\nVerbote von Einwegplastik nehmen zu.\nNeue Materialien bieten umweltfreundliche Optionen.\nVerbraucher greifen öfter zu wiederverwendbaren Produkten.",
      },
      image_urls: ["https://picsum.photos/800/600?random=3"],
      date: "2025-05-24",
      source: "2",
    },
  },
  {
    id: "9",
    relevance: 0.79,
    topics: [
      {
        id: "1",
        name: "Automotive",
        score: 0.76,
        keywords: [],
      },
    ],
    article: {
      article_url: "",
      headline: {
        en: "Tire Pressure Impacts Fuel Economy",
        de: "Reifendruck beeinflusst den Kraftstoffverbrauch",
      },
      summary: {
        en: "Proper tire pressure improves mileage.\nUnderinflated tires cause drag and waste fuel.\nDrivers should check pressure monthly.\nMost cars now include tire pressure sensors.\nMaintaining correct pressure extends tire life.",
        de: "Richtiger Reifendruck verbessert den Verbrauch.\nZu wenig Luft erhöht den Rollwiderstand.\nRegelmäßige Kontrolle wird empfohlen.\nModerne Autos haben Reifendrucksensoren.\nRichtiger Druck verlängert die Lebensdauer der Reifen.",
      },
      image_urls: ["https://picsum.photos/800/600?random=2"],
      date: "2025-07-15",
      source: "1",
    },
  },
  {
    id: "10",
    relevance: 0.91,
    topics: [
      {
        id: "2",
        name: "Environmental",
        score: 0.96,
        keywords: [],
      },
    ],
    article: {
      article_url: "",
      headline: {
        en: "Renewable Energy Hits Record Output",
        de: "Erneuerbare Energien erreichen Rekordproduktion",
      },
      summary: {
        en: "Wind, solar, and hydro combined for a new record.\nFossil fuel use continues to decline globally.\nMore countries are adopting clean energy goals.\nInvestment in renewables is at an all-time high.\nExperts predict further growth in the coming years.",
        de: "Wind, Sonne und Wasser erzielen neue Rekorde.\nFossile Brennstoffe werden weniger genutzt.\nImmer mehr Länder setzen auf saubere Energie.\nInvestitionen in Erneuerbare erreichen Höchstwerte.\nExperten erwarten weiteres Wachstum.",
      },
      image_urls: ["https://picsum.photos/800/600?random=1"],
      date: "2025-06-28",
      source: "3",
    },
  },
];

export const carKeywords = [
  "Tires",
  "Engine",
  "Transmission",
  "Brakes",
  "Fuel system",
  "Suspension",
  "Battery",
  "Radiator",
  "Exhaust",
  "Spark plugs",
  "Air filter",
  "Oil change",
  "Alternator",
  "Starter motor",
  "Catalytic converter",
  "Timing belt",
  "Dashboard",
  "Windshield",
  "Headlights",
  "Steering system",
  "Drive shaft",
  "Chassis",
  "Turbocharger",
  "Infotainment system",
  "Cruise control",
];

export const environmentKeywords = [
  "CO2",
  "Renewable energy",
  "Carbon footprint",
  "Greenhouse gases",
  "Solar power",
  "Wind energy",
  "Climate change",
  "Carbon offset",
  "Sustainability",
  "Hydropower",
  "Energy efficiency",
  "Emissions reduction",
  "Geothermal energy",
  "Biofuels",
  "Recycling",
  "Composting",
  "Environmental policy",
  "Clean energy",
  "Net zero",
  "Carbon neutrality",
  "Air pollution",
  "Green energy",
  "Deforestation",
  "Ocean acidification",
  "Eco-friendly technologies",
];
