import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
} from "~/components/ui/table";
import type { Article } from "../../../types/model";

interface ArticleMetaDataTableProps {
  article: Article;
}

export function ArticleMetaDataTable({ article }: ArticleMetaDataTableProps) {
  const formatDate = (dateString: string): string => {
    try {
      const date = new Date(dateString);

      if (isNaN(date.getTime())) {
        return "Invalid Date";
      }

      return date.toLocaleDateString("en-US", {
        year: "numeric",
        month: "long",
        day: "numeric",
      });
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
    } catch (error) {
      return "Invalid Date";
    }
  };

  return (
    <div className="border border-gray-200 rounded-2xl p-4">
      <Table>
        <TableHead>Meta Data</TableHead>
        <TableBody>
          <TableRow>
            <TableCell>Published</TableCell>
            <TableCell>{formatDate(article.published_at)}</TableCell>
          </TableRow>
          <TableRow>
            <TableCell>Crawled</TableCell>
            <TableCell>{formatDate(article.crawled_at)}</TableCell>
          </TableRow>
          <TableRow>
            <TableCell>Language</TableCell>
            <TableCell>{article.language}</TableCell>
          </TableRow>
          <TableRow>
            <TableCell>Status</TableCell>
            <TableCell>{article.status}</TableCell>
          </TableRow>
          <TableRow>
            <TableCell>Category</TableCell>
            <TableCell>{article.category}</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </div>
  );
}
