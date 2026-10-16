/**
 * Export dashboard data to CSV or JSON format and trigger download
 */

export function exportToCSV(data: Record<string, unknown>[], filename = 'landagri-dataset.csv'): void {
  if (!data.length) return;

  const headers = Object.keys(data[0]);
  const csvContent = [
    headers.join(','),
    ...data.map((row) =>
      headers
        .map((h) => {
          const val = row[h];
          if (val === null || val === undefined) return '';
          const str = String(val);
          // Escape quotes and wrap in quotes if contains comma, quote, or newline
          return str.includes(',') || str.includes('"') || str.includes('\n')
            ? `"${str.replace(/"/g, '""')}"`
            : str;
        })
        .join(','),
    ),
  ].join('\n');

  downloadBlob(csvContent, filename, 'text/csv;charset=utf-8;');
}

export function exportToJSON(data: unknown, filename = 'landagri-dataset.json'): void {
  const jsonContent = JSON.stringify(data, null, 2);
  downloadBlob(jsonContent, filename, 'application/json;charset=utf-8;');
}

function downloadBlob(content: string, filename: string, mimeType: string): void {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
