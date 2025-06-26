export interface NewsArticle {
  id: string;
  title: string;
  summary: string;
  image_url: string;
  url: string;
  published_at: string; // ISO 8601 datetime string
}

export interface BreakingNewsResponse {
  results: NewsArticle[];
}
