import { Injectable, PLATFORM_ID, inject } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';

export interface ExportColumn {
  header: string;
  field: string;
  width?: number;
}

export interface ExportOptions {
  title?: string;
  subtitle?: string;
  filename: string;
  orientation?: 'portrait' | 'landscape';
  includeDate?: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class ExportService {
  private platformId = inject(PLATFORM_ID);
  private jsPDFLib: any = null;
  private autoTableLib: any = null;
  private xlsxLib: any = null;
  private fileSaverLib: any = null;

  async exportToPDF(data: any[], columns: ExportColumn[], options: ExportOptions) {
    if (!isPlatformBrowser(this.platformId)) {
      return;
    }

    try {
      // Cargar librerías solo una vez
      if (!this.jsPDFLib || !this.autoTableLib) {
        const [jsPDFModule, autoTableModule] = await Promise.all([
          import('jspdf'),
          import('jspdf-autotable')
        ]);
        this.jsPDFLib = jsPDFModule.default;
        this.autoTableLib = autoTableModule.default;
      }

      const jsPDF = this.jsPDFLib;
      const autoTable = this.autoTableLib;

      const doc = new jsPDF({
        orientation: options.orientation || 'portrait',
        unit: 'mm',
        format: 'a4'
      });

      doc.setFontSize(20);
      doc.setFont('helvetica', 'bold');

      if (options.title) {
        doc.text(options.title, 14, 20);
      }

      if (options.subtitle) {
        doc.setFontSize(12);
        doc.setFont('helvetica', 'normal');
        doc.text(options.subtitle, 14, 28);
      }

      if (options.includeDate !== false) {
        const date = new Date().toLocaleDateString('es-HN');
        doc.setFontSize(10);
        doc.setTextColor(100);
        doc.text(`Fecha: ${date}`, 14, options.subtitle ? 35 : 28);
      }

      const tableHeaders = columns.map(col => col.header);
      const tableData = data.map(row => 
        columns.map(col => {
          const value = this.getNestedValue(row, col.field);
          return this.formatValue(value);
        })
      );

      autoTable(doc, {
        head: [tableHeaders],
        body: tableData,
        startY: options.subtitle ? 40 : (options.includeDate !== false ? 33 : 25),
        theme: 'grid',
        styles: {
          fontSize: 9,
          cellPadding: 3,
          font: 'helvetica'
        },
        headStyles: {
          fillColor: [102, 126, 234],
          textColor: [255, 255, 255],
          fontStyle: 'bold',
          halign: 'center'
        },
        alternateRowStyles: {
          fillColor: [245, 247, 250]
        },
        margin: { top: 10, left: 14, right: 14 }
      });

      const pageCount = (doc as any).internal.getNumberOfPages();
      for (let i = 1; i <= pageCount; i++) {
        doc.setPage(i);
        doc.setFontSize(8);
        doc.setTextColor(150);
        doc.text(
          `Página ${i} de ${pageCount}`,
          doc.internal.pageSize.getWidth() / 2,
          doc.internal.pageSize.getHeight() - 10,
          { align: 'center' }
        );
      }

      doc.save(`${options.filename}.pdf`);
    } catch (error) {
      console.error('Error exporting to PDF:', error);
      throw error;
    }
  }

  async exportToExcel(data: any[], columns: ExportColumn[], options: ExportOptions) {
    if (!isPlatformBrowser(this.platformId)) {
      return;
    }

    try {
      // Cargar librerías solo una vez
      if (!this.xlsxLib || !this.fileSaverLib) {
        const [xlsxModule, fileSaverModule] = await Promise.all([
          import('xlsx'),
          import('file-saver')
        ]);
        this.xlsxLib = xlsxModule;
        this.fileSaverLib = fileSaverModule.saveAs;
      }

      const XLSX = this.xlsxLib;
      const saveAs = this.fileSaverLib;

      const worksheetData: any[] = [];

      if (options.title) {
        worksheetData.push([options.title]);
        worksheetData.push([]);
      }

      if (options.subtitle) {
        worksheetData.push([options.subtitle]);
        worksheetData.push([]);
      }

      if (options.includeDate !== false) {
        const date = new Date().toLocaleDateString('es-HN');
        worksheetData.push([`Fecha: ${date}`]);
        worksheetData.push([]);
      }

      const headers = columns.map(col => col.header);
      worksheetData.push(headers);

      data.forEach(row => {
        const rowData = columns.map(col => {
          const value = this.getNestedValue(row, col.field);
          return this.formatValue(value);
        });
        worksheetData.push(rowData);
      });

      const worksheet = XLSX.utils.aoa_to_sheet(worksheetData);

      const columnWidths = columns.map(col => ({ wch: col.width || 15 }));
      worksheet['!cols'] = columnWidths;

      const workbook = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(workbook, worksheet, 'Reporte');

      const excelBuffer = XLSX.write(workbook, {
        bookType: 'xlsx',
        type: 'array'
      });

      const blob = new Blob([excelBuffer], {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      });
      saveAs(blob, `${options.filename}.xlsx`);
    } catch (error) {
      console.error('Error exporting to Excel:', error);
      throw error;
    }
  }

  private getNestedValue(obj: any, path: string): any {
    return path.split('.').reduce((acc, part) => acc && acc[part], obj);
  }

  private formatValue(value: any): string {
    if (value === null || value === undefined) return '';
    if (typeof value === 'number' && value > 1000) {
      return new Intl.NumberFormat('es-HN', {
        style: 'currency',
        currency: 'HNL'
      }).format(value);
    }
    if (value instanceof Date) return value.toLocaleDateString('es-HN');
    if (typeof value === 'boolean') return value ? 'Sí' : 'No';
    return String(value);
  }
}
