import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
export const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../web');
const requested = process.env.QFAULT_NODE_MODULES || process.argv[2];
export const modules = requested ? path.resolve(requested) : path.join(root, 'node_modules');
if (!fs.existsSync(path.join(modules, 'vite/package.json'))) throw new Error('Install web dependencies, or set QFAULT_NODE_MODULES to a verified existing node_modules directory.');
