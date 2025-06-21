import { SearchProfileOverview } from "~/pages/search-profile/search-profile";

export function meta() {
  return [
    { title: "MediaMind | Search Profile Overview" },
    { name: "description", content: "Search Profile Overview" },
  ];
}

export default function SearchProfile() {
  return <SearchProfileOverview />;
}
