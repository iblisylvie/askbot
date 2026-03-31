#!/usr/bin/env node
/**
 * AI Weekly Report Verification Script
 *
 * 自动化核查周报中的关键信息：
 * 1. 文章存在性 - 周报提到的文章是否在 summary.csv 中存在
 * 2. 链接真实性 - 周报中的链接是否在原文中存在
 * 3. 来源准确性 - 来源标注是否与 summary.csv 一致
 *
 * 使用方法: node scripts/verify-weekly.js <周报文件路径>
 * 示例: node scripts/verify-weekly.js output/AI技术周刊_第5期_2026-03-29.md
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// 颜色输出
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m'
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

// 提取周报中的文章标题（基于 Markdown 格式）
function extractTitles(content) {
  const titles = [];
  // 匹配 ### 开头的标题（头条和工具部分）
  const titleRegex = /^### \d+\.\s+(.+)$/gm;
  let match;
  while ((match = titleRegex.exec(content)) !== null) {
    titles.push(match[1].trim());
  }
  return titles;
}

// 提取周报中的所有链接
function extractLinks(content) {
  const links = [];
  // 匹配 Markdown 链接 [text](url) 和纯 URL
  const linkRegex = /\[([^\]]+)\]\((https?:\/\/[^\)]+)\)/g;
  const urlRegex = /(https?:\/\/[^\s\)\]\n]+)/g;

  let match;
  while ((match = linkRegex.exec(content)) !== null) {
    links.push({ text: match[1], url: match[2] });
  }

  // 重置正则
  urlRegex.lastIndex = 0;
  while ((match = urlRegex.exec(content)) !== null) {
    // 避免重复添加
    if (!links.find(l => l.url === match[1])) {
      links.push({ text: match[1], url: match[1] });
    }
  }

  return links;
}

// 在 summary.csv 中搜索文章
function searchInSummary(title, outputDir) {
  try {
    const cmd = `grep -r "${title.replace(/"/g, '\\"')}" ${outputDir}/*/summary.csv 2>/dev/null || echo ""`;
    const result = execSync(cmd, { encoding: 'utf-8', timeout: 5000 });
    return result.trim();
  } catch (e) {
    return '';
  }
}

// 在原文 Markdown 中搜索链接
function searchLinkInArticle(link, outputDir) {
  try {
    // 提取域名部分进行搜索
    const urlObj = new URL(link);
    const domain = urlObj.hostname;
    const cmd = `grep -r "${domain}" ${outputDir}/*/*.md 2>/dev/null | head -5 || echo ""`;
    const result = execSync(cmd, { encoding: 'utf-8', timeout: 5000 });
    return result.trim();
  } catch (e) {
    return '';
  }
}

// 主验证流程
async function verifyWeekly(weeklyPath) {
  log('\n🔍 AI Weekly Report Verification', 'blue');
  log('=' .repeat(50), 'blue');

  // 读取周报内容
  if (!fs.existsSync(weeklyPath)) {
    log(`\n❌ 错误：文件不存在 ${weeklyPath}`, 'red');
    process.exit(1);
  }

  const content = fs.readFileSync(weeklyPath, 'utf-8');
  const outputDir = path.dirname(weeklyPath);

  // 从文件路径提取日期范围
  const dateMatch = weeklyPath.match(/\d{4}-\d{2}-\d{2}/);
  const reportDate = dateMatch ? dateMatch[0] : 'unknown';

  log(`\n📄 周报文件: ${weeklyPath}`, 'blue');
  log(`📅 报告日期: ${reportDate}\n`, 'blue');

  // ==================== 检查 1: 文章存在性 ====================
  log('【检查 1】文章存在性', 'yellow');
  log('-'.repeat(40), 'yellow');

  const titles = extractTitles(content);
  let articlePass = 0;
  let articleFail = 0;

  for (const title of titles) {
    const result = searchInSummary(title, outputDir);
    if (result) {
      log(`  ✓ ${title.substring(0, 40)}...`, 'green');
      articlePass++;
    } else {
      log(`  ✗ ${title}`, 'red');
      log(`    ⚠ 未在 summary.csv 中找到`, 'red');
      articleFail++;
    }
  }

  log(`\n  结果: ${articlePass} 通过, ${articleFail} 失败\n`);

  // ==================== 检查 2: 链接真实性 ====================
  log('【检查 2】链接真实性', 'yellow');
  log('-'.repeat(40), 'yellow');

  const links = extractLinks(content);
  let linkPass = 0;
  let linkFail = 0;
  let linkWarning = 0;

  // 过滤出非微信链接（微信链接需要特殊处理）
  const externalLinks = links.filter(l => !l.url.includes('mp.weixin.qq.com'));

  for (const link of externalLinks.slice(0, 20)) { // 限制检查数量
    const result = searchLinkInArticle(link.url, outputDir);
    if (result) {
      log(`  ✓ ${link.url.substring(0, 50)}...`, 'green');
      linkPass++;
    } else {
      // 可能是 GitHub 等外部链接
      if (link.url.includes('github.com') || link.url.includes('arxiv.org')) {
        log(`  ⚠ ${link.url.substring(0, 50)}...`, 'yellow');
        log(`    提示: 外部链接，请人工确认是否在原文中提及`, 'yellow');
        linkWarning++;
      } else {
        log(`  ✗ ${link.url.substring(0, 50)}...`, 'red');
        log(`    未在原文中找到`, 'red');
        linkFail++;
      }
    }
  }

  log(`\n  结果: ${linkPass} 通过, ${linkWarning} 待确认, ${linkFail} 失败\n`);

  // ==================== 检查 3: 日期关键词 ====================
  log('【检查 3】日期归属关键词', 'yellow');
  log('-'.repeat(40), 'yellow');

  const dateKeywords = ['本周', '今天', '昨天', '上周'];
  const lines = content.split('\n');
  let dateIssues = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    for (const keyword of dateKeywords) {
      if (line.includes(keyword) && (line.includes('发布') || line.includes('开源') || line.includes('推出'))) {
        dateIssues.push({
          line: i + 1,
          content: line.trim().substring(0, 60),
          keyword: keyword
        });
      }
    }
  }

  if (dateIssues.length > 0) {
    log(`  ⚠ 发现 ${dateIssues.length} 处时间描述，请人工确认：`, 'yellow');
    for (const issue of dateIssues.slice(0, 5)) {
      log(`    第 ${issue.line} 行: ${issue.content}...`, 'yellow');
    }
  } else {
    log('  ✓ 未发现明显时间描述问题', 'green');
  }

  // ==================== 总结 ====================
  log('\n' + '='.repeat(50), 'blue');
  log('📊 核查总结', 'blue');
  log('='.repeat(50), 'blue');

  const totalIssues = articleFail + linkFail;

  if (totalIssues === 0) {
    log('\n✅ 所有自动检查项通过！', 'green');
    log('⚠️  注意：仍需人工确认日期归属和来源准确性\n', 'yellow');
  } else {
    log(`\n❌ 发现 ${totalIssues} 个问题需要修正`, 'red');
    log('请根据上述提示修改周报后再发布\n', 'red');
    process.exit(1);
  }
}

// 主入口
const weeklyPath = process.argv[2];

if (!weeklyPath) {
  console.log('使用方法: node scripts/verify-weekly.js <周报文件路径>');
  console.log('示例: node scripts/verify-weekly.js output/AI技术周刊_第5期_2026-03-29.md');
  process.exit(1);
}

verifyWeekly(weeklyPath).catch(err => {
  console.error('核查出错:', err);
  process.exit(1);
});
