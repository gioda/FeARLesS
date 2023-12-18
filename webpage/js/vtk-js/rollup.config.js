import * as path from 'path';
import * as glob from 'glob';

import autoprefixer from 'autoprefixer';

import alias from '@rollup/plugin-alias';
import { babel } from '@rollup/plugin-babel';
import commonjs from '@rollup/plugin-commonjs';
import eslint from '@rollup/plugin-eslint';
import ignore from 'rollup-plugin-ignore';
import json from '@rollup/plugin-json';
import nodePolyfills from 'rollup-plugin-polyfill-node';
import { nodeResolve } from '@rollup/plugin-node-resolve';
import postcss from 'rollup-plugin-postcss';
import { string } from 'rollup-plugin-string';
import svgo from 'rollup-plugin-svgo';
import webworkerLoader from 'rollup-plugin-web-worker-loader';
import copy from 'rollup-plugin-copy';
import autoExternal from 'rollup-plugin-auto-external';

import packageJSON from './package.json';

import { rewriteFilenames } from './Utilities/rollup/plugin-rewrite-filenames';

const absolutifyImports = require('./Utilities/build/absolutify-imports.js');

const IGNORE_LIST = [
  /[/\\]example_?[/\\]/,
  /[/\\]test/,
  /^Sources[/\\](Testing|ThirdParty)/,
];

function ignoreFile(name, ignoreList = IGNORE_LIST) {
  return ignoreList.some((toMatch) => {
    if (toMatch instanceof RegExp) {
      return toMatch.test(name);
    }
    if (toMatch instanceof String) {
      return toMatch === name;
    }
    return false;
  });
}

const entryPoints = [
  path.join('Sources', 'macros.js'),
  path.join('Sources', 'vtk.js'),
  path.join('Sources', 'favicon.js'),
  ...glob.sync('Sources/**/*.js').filter((file) => !ignoreFile(file)),
];

const entries = {};
entryPoints.forEach((entry) => {
  entries[entry.replace(/^Sources[/\\]/, '')] = entry;
});

const outputDir = path.resolve('dist', 'esm');

export default {
  input: entries,
  output: {
    dir: outputDir,
    format: 'es',
    hoistTransitiveImports: false,
    entryFileNames(chunkInfo) {
      const name = chunkInfo.name;

      // rewrite vtk.js files from Sources/.../<NAME>/index.js to .../<NAME>.js
      const sourcesMatch = /^(.*?)[/\\]([A-Z]\w+)[/\\]index\.js$/.exec(name);
      if (sourcesMatch) {
        return path.join(sourcesMatch[1], `${sourcesMatch[2]}.js`);
      }

      return name;
    },
    manualChunks(id) {
      // strip out full path to project root
      return id.replace(`${path.resolve(__dirname)}${path.sep}`, '');
    },
    chunkFileNames(chunkInfo) {
      let name = chunkInfo.name;

      if (!name.endsWith('.js')) {
        name += '.js';
      }

      if (name.includes('node_modules')) {
        return name.replace('node_modules', 'vendor');
      }

      // throw all subscript prefixed chunks into a virtual folder
      if (name.startsWith('_')) {
        return name.replace(/^_/, `_virtual${path.sep}`);
      }

      // rewrite Sources/ chunks
      return name.replace(/^Sources[/\\]/, '');
    },
  },
  external: Object.keys(packageJSON.dependencies).map((name) => new RegExp(`^${name}`)),
  plugins: [
    autoExternal(),
    alias({
      entries: [
        { find: 'vtk.js', replacement: path.resolve(__dirname) },
      ],
    }),
    // ignore crypto module
    ignore(['crypto']),
    // needs to be before nodeResolve
    webworkerLoader({
      targetPlatform: 'browser',
      // needs to match the full import statement path
      pattern: /^.+\.worker(?:\.js)?$/,
      // inline: true,
      // preserveSource: true,
      // outputFolder: 'WebWorkers',
    }),
    nodeResolve({
      // don't rely on node builtins for web
      preferBuiltins: false,
      browser: true,
    }),
    !process.env.NOLINT &&
      eslint({
        include: '**/*.js',
        exclude: 'node_modules/**',
      }),
    // commonjs should be before babel
    commonjs({
      transformMixedEsModules: true,
    }),
    // should be after commonjs
    nodePolyfills(),
    babel({
      include: 'Sources/**',
      exclude: 'node_modules/**',
      extensions: ['.js'],
      babelHelpers: 'runtime',
    }),
    string({
      include: '**/*.glsl',
    }),
    json(),
    svgo(),
    postcss({
      modules: true,
      plugins: [autoprefixer],
    }),
    // windows ntfs hates colons in filenames,
    // and node-resolve and web-worker-loader are notorious for
    // inserting them into virtual modules that are written out
    // to the filesystem via preserveModules: true.
    rewriteFilenames({
      find: /:/g,
      replace: '_',
    }),
    // copy package assets
    copy({
      flatten: false,
      targets: [
        {
          src: 'Sources/**/*.d.ts',
          dest: outputDir,
          rename(name, ext, fullPath) {
            const filename = `${name}.${ext}`;
            if (filename === 'index.d.ts') {
              const moduleName = path.basename(path.dirname(fullPath));
              return `../${moduleName}.d.ts`;
            }
            return `${name}.${ext}`;
          },
          transform(content, base) {
            // transforms typescript defs to use absolute package imports
            if (base.endsWith('.d.ts')) {
              return absolutifyImports(content.toString(), (relImport) => {
                const importPath = path.join(path.dirname(base), relImport);
                const relativeStart = path.join(__dirname, 'Sources');
                // rollup builds are for the @kitware/vtk.js package
                return path.join(
                  '@kitware/vtk.js',
                  path.relative(relativeStart, importPath)
                );
              });
            }
            return content;
          },
        },
      ],
    }),
    copy({
      flatten: true,
      targets: [
        { src: 'Utilities/XMLConverter', dest: `${outputDir}/Utilities` },
        { src: 'Utilities/DataGenerator', dest: `${outputDir}/Utilities` },
        { src: 'Utilities/prepare.js', dest: `${outputDir}/Utilities` },
        { src: 'Utilities/config/*', dest: `${outputDir}/Utilities/config` },
        { src: 'Utilities/build/macro-shim.d.ts', dest: outputDir, rename: 'macro.d.ts' },
        { src: 'Utilities/build/macro-shim.js', dest: outputDir, rename: 'macro.js' },
        { src: '*.txt', dest: outputDir },
        { src: '*.md', dest: outputDir },
        { src: '.npmignore', dest: outputDir },
        { src: 'LICENSE', dest: outputDir },
        {
          src: 'package.json',
          dest: outputDir,
          transform(content) {
            const pkg = JSON.parse(content);
            pkg.name = '@kitware/vtk.js';
            pkg.main = './index.js';
            pkg.module = './index.js';
            return JSON.stringify(pkg, null, 2);
          },
        },
      ],
    }),
  ],
};
