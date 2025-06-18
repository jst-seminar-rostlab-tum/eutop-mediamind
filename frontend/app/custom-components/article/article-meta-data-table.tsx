import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
} from "~/components/ui/table";
import type { Article } from "../../../types/model";
import { formatDate } from "~/lib/utils";

interface ArticleMetaDataTableProps {
  article: Article;
}

export function ArticleMetaDataTable({ article }: ArticleMetaDataTableProps) {
  return (
    <div className="border border-gray-200 rounded-3xl p-3">
      <Table>
        <TableHead>Meta Data</TableHead>
        <TableBody>
          <TableRow>
            <TableCell>Published</TableCell>
            <TableCell className="text-right">
              {formatDate(article.published_at)}
            </TableCell>
          </TableRow>
          <TableRow>
            <TableCell>Crawled</TableCell>
            <TableCell className="text-right">
              {formatDate(article.crawled_at)}
            </TableCell>
          </TableRow>
          <TableRow>
            <TableCell>Language</TableCell>
            <TableCell className="text-right">{article.language}</TableCell>
          </TableRow>
          <TableRow>
            <TableCell>Status</TableCell>
            <TableCell className="text-right">{article.status}</TableCell>
          </TableRow>
          <TableRow>
            <TableCell>Category</TableCell>
            <TableCell className="text-right">{article.category}</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </div>
  );
}
