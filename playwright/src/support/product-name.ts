/**
 * Reduces product text to comparable characters, so a search term matches a
 * result title and two renderings of one product name compare equal.
 */
export function normalizeForProductMatch(value: string): string {
  return value
    .normalize("NFKC")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "");
}
