import { useParams } from "react-router";

export function SearchProfileOverview() {
  const { id } = useParams<{ id: string }>();

  console.log("Search Profile ID:", id);

  return <h1>Search Profile Overview</h1>;
}
