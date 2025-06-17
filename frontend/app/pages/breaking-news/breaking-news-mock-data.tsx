export interface BreakingNewsItem {
  title: string;
  description: string;
  date: string;
  image: string;
}

const breakingNews = [
  {
    title: "World Bank sharply cuts global growth outlook on trade turbulence",
    description:
      "The World Bank has significantly revised its global economic projections downward, citing escalating trade tensions and geopolitical uncertainties as primary factors. This would mark the slowest rate of global growth since 2008, aside from outright global recessions. The institution now expects the global economy to expand by 2.3% in 2025, down from an earlier forecast of 2.7%. The revision reflects concerns over supply chain disruptions, rising protectionist policies, and weakening consumer confidence across major economies. Developing nations are expected to bear the brunt of the slowdown, with commodity-dependent countries facing particular challenges.",
    date: "2025-06-17T19:28:36.342Z",
    image: "https://picsum.photos/200",
  },
  {
    title: "Uber brings forward trialling driverless taxis in UK",
    description:
      "Uber has accelerated its timeline for autonomous vehicle testing in the United Kingdom, partnering with British AI startup Wayve to deploy self-driving taxis on London streets by early 2025. The ride-hailing app will work with the UK artificial intelligence firm Wayve, which has been testing the technology on the city's streets with human oversight, in line with current legislation. The trials will initially cover select routes in central London, with safety drivers present during all journeys. This move positions the UK as a key testing ground for autonomous vehicle technology, potentially giving it a competitive edge over other European markets where regulatory frameworks remain more restrictive.",
    date: "2025-06-17T18:45:12.156Z",
    image: "https://picsum.photos/200",
  },
  {
    title: "US and China meet for trade talks in London",
    description:
      "High-level trade negotiations between the United States and China resumed in London this week, marking the first formal diplomatic engagement between the two economic superpowers in over six months. A senior US delegation including Commerce Secretary Howard Lutnick met Chinese representatives such as Vice Premier He Lifeng at Lancaster House to resolve mounting tensions over technology transfers, agricultural imports, and tariff structures. The talks come amid growing pressure from business communities in both countries to establish more predictable trade relationships. Sources close to the negotiations suggest that while significant differences remain, both sides have expressed cautious optimism about finding common ground on several key issues.",
    date: "2025-06-17T17:32:48.789Z",
    image: "https://picsum.photos/200",
  },
  {
    title: "Europe heaps harsh sanctions on Russia",
    description:
      "The European Union announced its most comprehensive sanctions package against Russia since the conflict began, targeting key sectors of the Russian economy including energy, technology, and financial services. The new measures include restrictions on 200 additional individuals and entities, expanded export controls on dual-use technologies, and further limitations on Russian energy imports. European Commission President Ursula von der Leyen emphasized that the sanctions aim to further isolate Russia economically while maintaining humanitarian corridors. The package also includes provisions for enhanced enforcement mechanisms and coordination with international partners to prevent sanctions evasion through third countries.",
    date: "2025-06-17T16:15:23.901Z",
    image: "https://picsum.photos/200",
  },
  {
    title: "Massive Russian drone attack slams Kyiv",
    description:
      "Russia launched one of its most intensive aerial assaults on Ukraine's capital in months, deploying 315 drones in a coordinated overnight attack that targeted critical infrastructure and residential areas across Kyiv. Ukrainian President Volodymyr Zelensky described it as 'one of the largest' attacks on the capital since the conflict escalated. Ukrainian air defense systems successfully intercepted approximately 280 of the incoming drones, but the remaining strikes caused significant damage to power facilities and transportation networks. The attack prompted emergency evacuations in several districts and left thousands of residents without electricity. International observers have condemned the assault as a deliberate targeting of civilian infrastructure.",
    date: "2025-06-17T14:52:07.234Z",
    image: "https://picsum.photos/200",
  },
  {
    title:
      "Greta Thunberg departs Israel on flight to Paris after detention aboard aid ship",
    description:
      "Swedish climate and human rights activist Greta Thunberg departed Israel on a commercial flight to France following her release from detention by Israeli naval forces. Thunberg was aboard a humanitarian aid vessel attempting to deliver supplies to Gaza when it was intercepted in international waters. The activist, who has become increasingly vocal about human rights issues beyond climate change, spent 48 hours in Israeli custody before diplomatic pressure from Swedish officials secured her release. The incident has sparked international debate about the rights of humanitarian workers and activists in conflict zones. Thunberg is expected to address the European Parliament next week about both climate action and human rights concerns in the region.",
    date: "2025-06-17T13:08:41.567Z",
    image: "https://picsum.photos/200",
  },
];

export function getBreakingNews() {
  return breakingNews;
}
