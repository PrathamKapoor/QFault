import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { root, modules } from './web-tools.mjs';
const { default: ts } = await import(pathToFileURL(path.join(modules, 'typescript/lib/typescript.js')).href);
const options = { noEmit: true, strict: true, target: ts.ScriptTarget.ES2022,
  module: ts.ModuleKind.ESNext, moduleResolution: ts.ModuleResolutionKind.Bundler,
  jsx: ts.JsxEmit.React, esModuleInterop: true, skipLibCheck: true,
  types: ['react','react-dom'], typeRoots: [path.join(modules,'@types')],
  baseUrl: root, ignoreDeprecations: '6.0', paths: {
    react: [path.join(modules,'@types/react/index.d.ts')],
    'react-dom/client': [path.join(modules,'@types/react-dom/client.d.ts')]
  }};
const program = ts.createProgram([path.join(root,'src/entry.tsx'),path.join(root,'src/styles.d.ts')], options);
const errors = ts.getPreEmitDiagnostics(program);
for (const e of errors) console.error(ts.flattenDiagnosticMessageText(e.messageText,'\n'));
console.log(errors.length ? String(errors.length)+' TypeScript errors' : 'TypeScript check passed');
process.exitCode = errors.length ? 1 : 0;
