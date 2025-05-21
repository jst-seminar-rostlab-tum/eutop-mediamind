import { useQuery } from "@tanstack/react-query";

function getSearchProfiles(){
  return [
    {
      id: 1,
      name: "Lufthansa",
      lastUpdated: "2 hours ago",
      newArticles: 4,
      imageUrl: "https://www.lufthansa.com/content/dam/lh/images/frontify_variations/3/c-820586478-42548236.jpg.transform/lh-dcep-transform-width-1440/img.jpg"
    },
    {
      id: 2,
      name: "BMW",
      lastUpdated: "5 hours ago",
      newArticles: 9,
      imageUrl: "https://blog.logomaster.ai/hs-fs/hubfs/bmw-logo-1963.jpg?width=672&height=454&name=bmw-logo-1963.jpg"
    },
    {
      id: 2,
      name: "BMW",
      lastUpdated: "5 hours ago",
      newArticles: 9,
      imageUrl: "https://blog.logomaster.ai/hs-fs/hubfs/bmw-logo-1963.jpg?width=672&height=454&name=bmw-logo-1963.jpg"
    },
    {
      id: 2,
      name: "BMW",
      lastUpdated: "5 hours ago",
      newArticles: 9,
      imageUrl: "https://blog.logomaster.ai/hs-fs/hubfs/bmw-logo-1963.jpg?width=672&height=454&name=bmw-logo-1963.jpg"
    },
    {
      id: 2,
      name: "BMW",
      lastUpdated: "5 hours ago",
      newArticles: 9,
      imageUrl: "https://blog.logomaster.ai/hs-fs/hubfs/bmw-logo-1963.jpg?width=672&height=454&name=bmw-logo-1963.jpg"
    },
    {
      id: 2,
      name: "BMW",
      lastUpdated: "5 hours ago",
      newArticles: 9,
      imageUrl: "https://blog.logomaster.ai/hs-fs/hubfs/bmw-logo-1963.jpg?width=672&height=454&name=bmw-logo-1963.jpg"
    }
  ];
}

export function useSearchProfiles(){
  return useQuery({queryKey: ["searchProfiles"], queryFn: getSearchProfiles});
}