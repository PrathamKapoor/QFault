import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { root, modules } from './web-tools.mjs';
const { build } = await import(pathToFileURL(path.join(modules, 'vite/dist/node/index.js')).href);
await build({ root, configFile: false, resolve: { alias: [
  { find: /^react-dom(\/.*)?$/, replacement: path.join(modules, 'react-dom') + '$1' },
  { find: /^react(\/.*)?$/, replacement: path.join(modules, 'react') + '$1' }
]}, build: { outDir: 'dist', emptyOutDir: false }});
