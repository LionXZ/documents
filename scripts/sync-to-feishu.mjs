#!/usr/bin/env node
/**
 * 同步本仓库 Markdown 文档到飞书知识库（保持目录结构 1:1）
 *
 * 用法：
 *   node scripts/sync-to-feishu.mjs --check     仅验证凭证与知识库访问权限
 *   node scripts/sync-to-feishu.mjs --dry-run   仅本地扫描比对，不调用写接口
 *   node scripts/sync-to-feishu.mjs             增量同步（hash 未变的跳过）
 *   node scripts/sync-to-feishu.mjs --changed   只同步上次同步以来 git 变更过的文档
 *   node scripts/sync-to-feishu.mjs --force     忽略 hash，全部重新导入
 *   node scripts/sync-to-feishu.mjs --prune     额外删除远端有、本地无的节点
 *
 * 依赖：Node 18+（原生 fetch / FormData / Blob），无第三方包
 * 凭证：仓库根目录 .env（已 gitignore，绝不入库）
 * 映射：.feishu-sync-map.json 记录 路径 → 节点 token + 内容 hash，用于增量与更新；
 *       另记录 syncedGitHead（上次同步成功时的 git HEAD），供 --changed 圈定差异
 * --changed 语义：对比上次 HEAD 与当前工作区（含未提交修改），只同步变更过的文档；
 *   映射里有记录但本地已不存在的文档会被删除（镜像语义）；全部成功才推进 HEAD
 *
 * 导入链路：上传 md 到云空间根目录 → 服务端 md→docx 转换任务 →
 *           轮询拿到 document_id → 移动进知识库挂到父目录下
 * 更新策略：先导入新文档并挂节点，成功后再把旧文档与云空间源文件移入回收站（中途失败不丢旧文档）
 */

import { readFile, writeFile, readdir } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { execFile } from 'node:child_process';
import path from 'node:path';

const ROOT = path.resolve(import.meta.dirname, '..');
const MAP_FILE = path.join(ROOT, '.feishu-sync-map.json');
const ENV_FILE = path.join(ROOT, '.env');
const BASE_URL = 'https://open.feishu.cn/open-apis';

// 不进知识库的目录（scripts 存放本工具自身；隐藏目录在扫描时统一跳过）
const IGNORED_DIRS = new Set(['.git', 'node_modules', 'scripts', '.vscode', '.idea']);
const MIN_REQUEST_GAP_MS = 120;   // 相邻请求最小间隔，避免触发限流
const POLL_INTERVAL_MS = 500;     // 导入任务轮询间隔
const POLL_MAX_ATTEMPTS = 120;    // 轮询上限 120×500ms = 60s

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

// ---------- 命令行参数 ----------
function parseArgs() {
  const flags = { dryRun: false, force: false, prune: false, check: false, changed: false };
  for (const arg of process.argv.slice(2)) {
    if (arg === '--dry-run') flags.dryRun = true;
    else if (arg === '--changed') flags.changed = true;
    else if (arg === '--force') flags.force = true;
    else if (arg === '--prune') flags.prune = true;
    else if (arg === '--check') flags.check = true;
    else {
      console.error(`未知参数：${arg}`);
      process.exit(1);
    }
  }
  return flags;
}

// ---------- .env 解析（零依赖，仅支持 KEY=VALUE 与 # 注释行） ----------
async function loadEnv() {
  let raw;
  try {
    raw = await readFile(ENV_FILE, 'utf8');
  } catch {
    throw new Error(`未找到 ${ENV_FILE}，请参考 .env.example 创建并填入凭证`);
  }
  const env = {};
  for (const line of raw.split('\n')) {
    const matched = line.match(/^\s*([A-Z_]+)\s*=\s*(.+?)\s*$/);
    if (matched) env[matched[1]] = matched[2];
  }
  for (const key of ['FEISHU_APP_ID', 'FEISHU_APP_SECRET', 'FEISHU_SPACE_ID']) {
    if (!env[key]) throw new Error(`.env 缺少 ${key}`);
  }
  return env;
}

// ---------- API 客户端：token 懒获取 + 全局限速 + 请求计数 ----------
// dry-run 模式不触发任何请求，token 也就不会获取
function createClient({ appId, appSecret }) {
  let token = null;
  let rootFolderToken = null; // 云空间根目录 token，懒获取（导入链路的挂载点）
  let lastRequestAt = 0;
  const stats = { requests: 0 };

  async function fetchToken() {
    const res = await fetch(`${BASE_URL}/auth/v3/tenant_access_token/internal`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ app_id: appId, app_secret: appSecret }),
    });
    const data = await res.json();
    if (data.code !== 0) throw new Error(`获取 tenant_access_token 失败：${data.msg}`);
    return data.tenant_access_token;
  }

  async function request(method, apiPath, { json, formData, query } = {}) {
    if (!token) token = await fetchToken();
    const gap = lastRequestAt + MIN_REQUEST_GAP_MS - Date.now();
    if (gap > 0) await sleep(gap);
    lastRequestAt = Date.now();
    stats.requests++;

    const url = new URL(BASE_URL + apiPath);
    if (query) for (const [key, value] of Object.entries(query)) url.searchParams.set(key, value);
    const headers = { Authorization: `Bearer ${token}` };
    let body;
    if (json !== undefined) {
      headers['Content-Type'] = 'application/json';
      body = JSON.stringify(json);
    } else if (formData) {
      body = formData;
    }
    const res = await fetch(url, { method, headers, body });
    // 个别接口（如删除文件）返回空 body，需兼容
    const text = await res.text();
    const data = text ? JSON.parse(text) : {};
    if (data.code !== 0) {
      throw new Error(`飞书 API ${method} ${apiPath} 失败 [${data.code}] ${data.msg}`);
    }
    return data.data ?? {};
  }

  // 云空间根目录 token（导入文件的上传点与导入产物落点），首次使用时获取并缓存
  async function getRootFolderToken() {
    if (!rootFolderToken) {
      const { token: folderToken } = await request('GET', '/drive/explorer/v2/root_folder/meta');
      rootFolderToken = folderToken;
    }
    return rootFolderToken;
  }

  return { request, stats, getRootFolderToken };
}

// ---------- 本地扫描：收集全部 md 及其祖先目录（相对路径，POSIX 分隔符） ----------
function ancestorDirs(relFile) {
  const parts = relFile.split('/');
  const list = [];
  for (let i = 1; i < parts.length; i++) list.push(parts.slice(0, i).join('/'));
  return list;
}

async function scanMarkdown(root) {
  const files = [];

  async function walk(relDir) {
    const entries = (
      await readdir(path.join(root, relDir), { withFileTypes: true })
    ).sort((a, b) => a.name.localeCompare(b.name, 'zh'));
    for (const entry of entries) {
      if (entry.name.startsWith('.')) continue; // 隐藏文件 / .git / .DS_Store
      const rel = relDir ? `${relDir}/${entry.name}` : entry.name;
      if (entry.isDirectory()) {
        if (!IGNORED_DIRS.has(entry.name)) await walk(rel);
      } else if (entry.isFile() && entry.name.toLowerCase().endsWith('.md')) {
        files.push(rel);
      }
    }
  }

  await walk('');
  // 只为"子树里确有 md"的目录建节点，空目录链不上知识库
  const dirSet = new Set();
  for (const file of files) for (const dir of ancestorDirs(file)) dirSet.add(dir);
  return { files: files.sort(), dirs: [...dirSet].sort() };
}

// ---------- git 差异（--changed 模式用） ----------
const git = (args) =>
  new Promise((resolve, reject) => {
    execFile('git', args, { cwd: ROOT, maxBuffer: 16 * 1024 * 1024 }, (error, stdout) => {
      if (error) reject(new Error(`git ${args.join(' ')} 执行失败（当前目录不是 git 仓库？）`));
      else resolve(stdout);
    });
  });

// 判断 git 输出的路径是否属于同步范围（与 scanMarkdown 的过滤规则一致）
function isSyncable(relPath) {
  if (!relPath.toLowerCase().endsWith('.md')) return false;
  return relPath.split('/').every((part) => !part.startsWith('.') && !IGNORED_DIRS.has(part));
}

// 上次同步 HEAD 以来内容有变的文件集合
// git diff 不带第二个提交时对比的是工作区，天然包含未提交的修改；
// untracked 新文件不出现在 diff 里，用 ls-files 单独补上
async function changedFilesSince(oldHead) {
  const changed = new Set();
  const diff = await git(['-c', 'core.quotepath=false', 'diff', '--name-status', oldHead]);
  for (const line of diff.split('\n').filter(Boolean)) {
    const [statusCol, ...paths] = line.split('\t');
    const status = statusCol[0];
    if (status === 'D') continue; // 删除走"本地缺失"统一判定，这里只关心要上传的
    if (status === 'R') {
      if (isSyncable(paths[1])) changed.add(paths[1]); // 重命名取新路径
    } else if (isSyncable(paths[0])) {
      changed.add(paths[0]); // A / M
    }
  }
  const untracked = await git(['-c', 'core.quotepath=false', 'ls-files', '--others', '--exclude-standard']);
  for (const line of untracked.split('\n').filter(Boolean)) {
    if (isSyncable(line)) changed.add(line);
  }
  return changed;
}

// ---------- 映射文件：{ spaceId, nodes: { "<相对路径>": { kind, node_token, obj_token?, hash? } } } ----------
async function loadMap() {
  try {
    return JSON.parse(await readFile(MAP_FILE, 'utf8'));
  } catch {
    return { spaceId: null, nodes: {} };
  }
}

const saveMap = (map) => writeFile(MAP_FILE, JSON.stringify(map, null, 2) + '\n', 'utf8');

// ---------- 飞书导入链路 ----------
const sha256Hex = (buf) => createHash('sha256').update(buf).digest('hex');

// 上传 md 到云空间根目录（作为导入任务的文件来源），返回 file_token
// 注：checksum 为可选参数，服务端校验不接受 md5（会报 1062008），不传即可
async function uploadForImport(client, fileName, buf) {
  const form = new FormData();
  form.append('file_name', fileName);
  form.append('parent_type', 'explorer');
  form.append('parent_node', await client.getRootFolderToken());
  form.append('size', String(buf.length));
  form.append('file', new Blob([buf]), fileName);
  const data = await client.request('POST', '/drive/v1/files/upload_all', { formData: form });
  return data.file_token;
}

// 创建 md→docx 服务端转换任务并轮询到终态，返回 docx 的 document_id
// 注：file_name 必须传与上传时一致的完整文件名（含 .md 扩展名），
//     否则服务端不做内容转换，会生成无内容的空文档
async function importAsDocx(client, fileToken, fileName) {
  const { ticket } = await client.request('POST', '/drive/v1/import_tasks', {
    json: {
      file_extension: 'md',
      file_token: fileToken,
      file_name: fileName,
      type: 'docx',
      // 先落到云空间根目录，拿到 document_id 后再挂进知识库
      point: { mount_type: 1, mount_key: await client.getRootFolderToken() },
    },
  });
  for (let attempt = 0; attempt < POLL_MAX_ATTEMPTS; attempt++) {
    await sleep(POLL_INTERVAL_MS);
    // 任务状态与产物 token 均在 result 字段内；小文件可能在首次轮询时就绪
    const { result } = await client.request('GET', `/drive/v1/import_tasks/${ticket}`);
    if (result?.job_status === 3) throw new Error(`导入任务失败：${result?.job_error_msg}`);
    if (result?.token) return result.token;
  }
  throw new Error(`导入任务超时（ticket=${ticket}）`);
}

// 在知识库新建空文档节点（充当目录）
async function createDirNode(client, spaceId, { title, parentNodeToken }) {
  const body = { obj_type: 'docx', node_type: 'origin', title };
  if (parentNodeToken) body.parent_node_token = parentNodeToken;
  const { node } = await client.request('POST', `/wiki/v2/spaces/${spaceId}/nodes`, { json: body });
  return node;
}

// 把云空间已有文档移动进知识库（挂到指定父节点下），返回新节点的 node_token
// 注：创建节点接口（POST .../nodes）会忽略 obj_token、总是新建空文档，
//     挂接已有文档必须走 move 接口（同步返回新节点的 wiki_token）
async function moveDocToWiki(client, spaceId, { objToken, parentNodeToken, title }) {
  const data = await client.request(
    'POST',
    `/wiki/v2/spaces/${spaceId}/nodes/move_docs_to_wiki`,
    {
      json: {
        obj_type: 'docx',
        obj_token: objToken,
        parent_wiki_token: parentNodeToken || '', // 为空默认挂到知识库根节点
      },
    }
  );
  // 接口为异步语义，wiki_token 有三种来源（按出现顺序取用）：
  // ① 移动瞬时完成：响应顶层直接返回 wiki_token；
  // ② 数组结构：move_docs_to_wiki_results[0].wiki_token；
  // ③ 未完成：仅返回 task_id，需轮询 GET /wiki/v2/tasks/:task_id 拿 move_result
  let nodeToken = data.wiki_token ?? data.move_docs_to_wiki_results?.[0]?.wiki_token;
  if (!nodeToken && data.task_id) nodeToken = await pollMoveTask(client, data.task_id);
  if (!nodeToken) {
    throw new Error(`move_docs_to_wiki 响应中未找到 wiki_token，原始响应：${JSON.stringify(data)}`);
  }
  // move 后节点标题沿用文档标题（带 .md 后缀），改回干净的展示标题
  await client.request('POST', `/wiki/v2/spaces/${spaceId}/nodes/${nodeToken}/update_title`, {
    json: { title },
  });
  return nodeToken;
}

// 轮询 move 异步任务直到完成，返回新节点的 node_token
// 响应结构：data.task.move_result[0].node.node_token（任务完成前 move_result 为空）
async function pollMoveTask(client, taskId) {
  for (let attempt = 0; attempt < POLL_MAX_ATTEMPTS; attempt++) {
    await sleep(POLL_INTERVAL_MS);
    const data = await client.request('GET', `/wiki/v2/tasks/${taskId}`, {
      query: { task_type: 'move' },
    });
    const nodeToken = data.task?.move_result?.[0]?.node?.node_token;
    if (nodeToken) return nodeToken;
  }
  throw new Error(`move 异步任务轮询超时（task_id=${taskId}，${POLL_MAX_ATTEMPTS * POLL_INTERVAL_MS / 1000}s）`);
}

// 把文件移入回收站（docx 文档、上传的源文件均适用，知识库内文档删除后节点随之消失）
async function deleteFile(client, token, type) {
  await client.request('DELETE', `/drive/v1/files/${token}`, { query: { type } });
}

// 确保目录节点存在（递归向上补齐祖先），返回该目录的 node_token
async function ensureDirNode(client, spaceId, map, relDir) {
  const existing = map.nodes[relDir];
  if (existing?.node_token) return existing.node_token;
  const parentRel = relDir.includes('/') ? relDir.slice(0, relDir.lastIndexOf('/')) : '';
  const parentNodeToken = parentRel ? await ensureDirNode(client, spaceId, map, parentRel) : undefined;
  const node = await createDirNode(client, spaceId, {
    title: path.basename(relDir),
    parentNodeToken,
  });
  map.nodes[relDir] = { kind: 'dir', node_token: node.node_token, obj_token: node.obj_token };
  console.log(`  + 目录：${relDir}`);
  return node.node_token;
}

// 同步单个 md：导入新文档 → 挂节点 → 清理源文件与旧文档，返回结果分类
async function syncFile(client, spaceId, map, relFile, buf) {
  const fileName = path.basename(relFile);
  const title = fileName.replace(/\.md$/i, '');
  const parentRel = relFile.includes('/') ? relFile.slice(0, relFile.lastIndexOf('/')) : '';
  const parentNodeToken = parentRel
    ? await ensureDirNode(client, spaceId, map, parentRel)
    : undefined;

  const fileToken = await uploadForImport(client, fileName, buf);
  const documentId = await importAsDocx(client, fileToken, fileName);
  const nodeToken = await moveDocToWiki(client, spaceId, {
    objToken: documentId,
    parentNodeToken,
    title,
  });

  // 导入产物已挂进知识库，云空间里的源文件失去用途，删掉避免累积
  try {
    await deleteFile(client, fileToken, 'file');
  } catch (error) {
    console.warn(`  ⚠ 源文件清理失败（可在云空间手动删除）：${error.message}`);
  }

  const old = map.nodes[relFile];
  map.nodes[relFile] = {
    kind: 'doc',
    node_token: nodeToken,
    obj_token: documentId,
    hash: sha256Hex(buf),
  };
  if (old?.obj_token && old.obj_token !== documentId) {
    try {
      await deleteFile(client, old.obj_token, 'docx');
      return 'updated';
    } catch (error) {
      console.warn(`  ⚠ 新文档已挂载，但旧文档删除失败（请手动清理）：${error.message}`);
      return 'updated-old-left';
    }
  }
  return 'added';
}

// 删除远端有、本地无的映射节点（--prune 时执行；深度优先，先子后父）
async function pruneRemote(client, map, localKeys) {
  const doomed = Object.keys(map.nodes)
    .filter((key) => !localKeys.has(key))
    .sort((a, b) => b.split('/').length - a.split('/').length || b.localeCompare(a));
  for (const key of doomed) {
    const record = map.nodes[key];
    try {
      await deleteFile(client, record.obj_token, 'docx');
      delete map.nodes[key];
      console.log(`  - 已删除：${key}`);
    } catch (error) {
      console.warn(`  ⠂ 未删除 ${key}（目录非空或无权限）：${error.message}`);
      break; // 父目录还没清空时继续删没有意义
    }
  }
  return doomed.length;
}

// ---------- 主流程 ----------
async function main() {
  const flags = parseArgs();
  const env = await loadEnv();
  const client = createClient({ appId: env.FEISHU_APP_ID, appSecret: env.FEISHU_APP_SECRET });
  const map = await loadMap();

  if (map.spaceId && map.spaceId !== env.FEISHU_SPACE_ID) {
    throw new Error(
      `映射文件记录的知识库（${map.spaceId}）与 .env（${env.FEISHU_SPACE_ID}）不一致；` +
        `确认要换库请删除 ${MAP_FILE} 后重跑`
    );
  }
  map.spaceId = env.FEISHU_SPACE_ID;

  if (flags.check) {
    const { space } = await client.request('GET', `/wiki/v2/spaces/${env.FEISHU_SPACE_ID}`);
    console.log(`✓ 凭证有效，知识库《${space.name}》可访问`);
    console.log(`  API 请求消耗：${client.stats.requests} 次`);
    return;
  }

  const { files, dirs } = await scanMarkdown(ROOT);
  console.log(`本地扫描：${files.length} 个 md，${dirs.length} 个目录`);

  // --changed：以上次同步记录的 HEAD 圈定候选集（无记录则退化为全量比对）
  let targets = files;
  if (flags.changed) {
    const oldHead = map.syncedGitHead;
    const oldHeadValid = oldHead
      ? await git(['rev-parse', '--verify', '--quiet', `${oldHead}^{commit}`]).then(
          () => true,
          () => false
        )
      : false;
    if (!oldHeadValid) {
      console.log(
        `未找到可用的上次同步 HEAD${oldHead ? '（记录的提交已不存在，可能被 rebase）' : ''}，本次按内容全量比对\n`
      );
    } else {
      const changed = await changedFilesSince(oldHead);
      // hash 兜底：git 差异表达不了「同步后本地内容又改回旧值」这类情况，
      // 凡内容与上次同步记录不一致的也进候选集（主循环内还会再校验一次）
      const mismatched = new Set();
      for (const f of files) {
        if (map.nodes[f]?.hash === undefined) continue; // 新文件已被 git untracked 覆盖
        const buf = await readFile(path.join(ROOT, f));
        if (map.nodes[f].hash !== sha256Hex(buf)) mismatched.add(f);
      }
      targets = files.filter((f) => changed.has(f) || mismatched.has(f));
      console.log(
        `git 差异（${oldHead.slice(0, 8)} 以来）：需同步 ${targets.length} 篇` +
          `${mismatched.size ? `（含 ${mismatched.size} 篇内容与上次同步记录不一致）` : ''}，其余跳过\n`
      );
    }
  } else {
    console.log('');
  }

  const counts = { added: 0, updated: 0, 'updated-old-left': 0, skipped: 0, failed: 0 };
  for (const relFile of targets) {
    const buf = await readFile(path.join(ROOT, relFile));
    if (buf.length === 0) {
      console.warn(`  ⚠ 跳过空文件：${relFile}`);
      continue;
    }
    const old = map.nodes[relFile];
    if (!flags.force && old?.hash === sha256Hex(buf)) {
      counts.skipped++;
      continue;
    }
    if (flags.dryRun) {
      console.log(`[dry-run] 将${old ? '更新' : '新增'}：${relFile}`);
      counts[old ? 'updated' : 'added']++;
      continue;
    }
    try {
      const outcome = await syncFile(client, env.FEISHU_SPACE_ID, map, relFile, buf);
      counts[outcome]++;
      console.log(`  ✓ ${old ? '更新' : '新增'}：${relFile}`);
    } catch (error) {
      counts.failed++;
      console.error(`  ✗ 失败：${relFile} —— ${error.message}`);
    }
    // 每处理一篇就落盘映射，中断后可续跑
    await saveMap(map);
  }

  let pruned = 0;
  if (flags.prune && !flags.dryRun) {
    pruned = await pruneRemote(client, map, new Set([...files, ...dirs]));
    await saveMap(map);
  }

  // --changed 镜像语义：映射里有记录、本地已不存在的文档删除（覆盖 git 删除/重命名旧路径，
  // 以及 untracked 文件同步后又被直接删除这种 git 无差异记录的情况）
  let removed = 0;
  if (flags.changed) {
    const localFiles = new Set(files);
    const doomed = Object.keys(map.nodes).filter(
      (key) => map.nodes[key].kind === 'doc' && !localFiles.has(key)
    );
    for (const relFile of doomed) {
      if (flags.dryRun) {
        console.log(`[dry-run] 将删除：${relFile}`);
        removed++;
        continue;
      }
      try {
        await deleteFile(client, map.nodes[relFile].obj_token, 'docx');
        delete map.nodes[relFile];
        removed++;
        console.log(`  - 已删除：${relFile}`);
      } catch (error) {
        counts.failed++;
        console.error(`  ✗ 删除失败：${relFile} —— ${error.message}`);
      }
    }
    if (removed > 0) await saveMap(map);
  }

  // 全部成功才推进「上次同步的 git HEAD」，失败/预览不推进（下次重跑仍会覆盖这些差异）
  if (!flags.dryRun && counts.failed === 0) {
    map.syncedGitHead = (await git(['rev-parse', 'HEAD'])).trim();
    await saveMap(map);
  }

  console.log(
    `\n完成：新增 ${counts.added}｜更新 ${counts.updated}` +
      `${counts['updated-old-left'] ? `（${counts['updated-old-left']} 篇旧文档待手删）` : ''}` +
      `｜跳过 ${counts.skipped}｜失败 ${counts.failed}` +
      `${pruned ? `｜删除 ${pruned}` : ''}${removed ? `｜删除 ${removed}` : ''}`
  );
  console.log(`API 请求消耗：${client.stats.requests} 次（免费额度 10,000 次/月）`);
  if (counts.failed > 0) process.exitCode = 1;
}

main().catch((error) => {
  console.error(`\n✗ ${error.message}`);
  process.exit(1);
});
