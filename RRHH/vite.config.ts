import { defineConfig } from 'vite';

export default defineConfig({
  optimizeDeps: {
    include: ['jspdf', 'jspdf-autotable', 'xlsx', 'file-saver']
  },
  ssr: {
    noExternal: ['jspdf', 'jspdf-autotable', 'xlsx', 'file-saver']
  }
});

