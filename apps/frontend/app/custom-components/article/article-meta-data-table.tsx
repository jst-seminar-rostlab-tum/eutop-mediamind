import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
} from "~/components/ui/table";
import type { ArticleMatch } from "../../../types/model";
import { formatDate } from "~/lib/utils";
import { useTranslation } from "react-i18next";

interface ArticleMetaDataTableProps {
  article: ArticleMatch;
}

export function ArticleMetaDataTable({ article }: ArticleMetaDataTableProps) {
  const { t } = useTranslation();

  return (
    <div className="border border-gray-200 rounded-xl p-3">
      <Table>
        <TableHead>{t("article-page.meta_data_header")}</TableHead>
        <TableBody>
          <TableRow>
            <TableCell>{t("article-page.meta_data_published")}</TableCell>
            <TableCell className="text-right">
              {formatDate(article.article.published)}
            </TableCell>
          </TableRow>

          <TableRow>
            <TableCell>{t("article-page.meta_data_crawled")}</TableCell>
            <TableCell className="text-right">
              {formatDate(article.article.crawled)}
            </TableCell>
          </TableRow>

          {article.article.language && (
            <TableRow>
              <TableCell>{t("article-page.meta_data_language")}</TableCell>
              <TableCell className="text-right">
                {article.article.language}
              </TableCell>
            </TableRow>
          )}

          {article.article.status && (
            <TableRow>
              <TableCell>{t("article-page.meta_data_status")}</TableCell>
              <TableCell className="text-right">
                {article.article.status}
              </TableCell>
            </TableRow>
          )}

          {article.article.categories &&
            article.article.categories.length > 0 && (
              <TableRow>
                <TableCell>{t("article-page.meta_data_category")}</TableCell>
                <TableCell className="text-right">
                  {article.article.categories.join(", ")}
                </TableCell>
              </TableRow>
            )}
        </TableBody>
      </Table>
    </div>
  );
}
